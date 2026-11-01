"""Isolated-process resource diagnostics, without gold access or cache claims."""

import ctypes
import hashlib
import json
import math
import os
import random
import sqlite3
import statistics
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from ragsmith.evaluation.instrumentation import run_environment
from ragsmith.evaluation.preparation import load_bundle
from ragsmith.evaluation.records import evidence_fingerprint, strict_json
from ragsmith.lookup_config import LookupConfig
from ragsmith.lookup_pipeline import assess_lookup_question
from ragsmith.response import render_lookup_response
from ragsmith.retrieval import RetrievalConfig, retrieve_question_evidence


@dataclass(frozen=True)
class TrialConfig:
    repeats: int = 5
    warmups: int = 1
    seed: int = 1729
    top_k: int = 10
    timeout_seconds: int = 30

    def __post_init__(self):
        for name, low, high in (("repeats", 1, 50), ("warmups", 1, 10),
                                ("top_k", 1, 100), ("timeout_seconds", 1, 60)):
            value = getattr(self, name)
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} must be an integer from {low} to {high}")
        if type(self.seed) is not int:
            raise ValueError("seed must be an integer")


def process_memory() -> dict:
    """Current/OS lifetime-peak resident bytes; unavailable is explicitly null."""
    result = {"method": "unavailable", "current_rss_bytes": None,
              "process_lifetime_peak_rss_bytes": None, "scope": "worker_process_only"}
    try:
        if sys.platform == "win32":
            from ctypes import wintypes

            class Counters(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                    (name, ctypes.c_size_t) for name in (
                        "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                        "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
                        "PagefileUsage", "PeakPagefileUsage")]

            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel.GetCurrentProcess.restype = wintypes.HANDLE
            kernel.GetCurrentProcess.argtypes = []
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            counters = Counters()
            counters.cb = ctypes.sizeof(counters)
            if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
                raise OSError("GetProcessMemoryInfo failed")
            result.update(method="win32_GetProcessMemoryInfo_working_set",
                          current_rss_bytes=int(counters.WorkingSetSize),
                          process_lifetime_peak_rss_bytes=int(counters.PeakWorkingSetSize))
        elif sys.platform == "linux":
            import resource

            result.update(method="linux_getrusage_maxrss_and_proc_statm",
                          process_lifetime_peak_rss_bytes=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024))
            try:
                pages = int(Path("/proc/self/statm").read_text().split()[1])
                result["current_rss_bytes"] = pages * os.sysconf("SC_PAGE_SIZE")
            except (OSError, ValueError, IndexError):
                result["current_rss_status"] = "unavailable"
        else:
            result["reason"] = "unsupported_platform"
    except (OSError, AttributeError, ValueError) as exc:
        result.update(method="unavailable", current_rss_bytes=None,
                      process_lifetime_peak_rss_bytes=None, reason=type(exc).__name__)
    return result


def summarize(values: list[float]) -> dict:
    if any(type(value) not in (int, float) or not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("Timing samples must be finite nonnegative numbers")
    ordered = sorted(values)
    if not ordered:
        return {"n": 0, "median_seconds": None, "p95_seconds": None, "min_seconds": None, "max_seconds": None}
    # Nearest-rank p95, explicitly descriptive; no confidence interval implied.
    return {"n": len(values), "median_seconds": statistics.median(values),
            "p95_seconds": ordered[math.ceil(.95 * len(ordered)) - 1],
            "min_seconds": ordered[0], "max_seconds": ordered[-1]}


def worker(payload: dict) -> dict:
    config = TrialConfig(**payload["config"])
    directory = Path(payload["directory"])
    requests, evidence, manifest, hashes = load_bundle(
        directory / "inputs.jsonl", directory / "evidence.jsonl", directory / "lineage.json")
    if hashes != payload["expected_hashes"]:
        raise ValueError("Worker bundle differs from parent input hashes")
    db_path = Path(payload["database"]) if payload["database"] else None
    if db_path and hashlib.sha256(db_path.read_bytes()).hexdigest() != payload["database_sha256"]:
        raise ValueError("Worker database snapshot hash mismatch")
    warm = payload["condition"] == "warmed_process"
    if payload["condition"] not in {"fresh_process_first_pass", "warmed_process"}:
        raise ValueError("Unknown trial condition")
    baseline_memory = process_memory()
    rows = []
    passes = list(range(-config.warmups, 0)) + list(range(config.repeats)) if warm else [payload["repeat"]]
    for repeat in passes:
        qids = sorted(requests)
        random.Random(config.seed + repeat).shuffle(qids)
        outcomes, query_rows = [], []
        for qid in qids:
            request = requests[qid]
            start = perf_counter()
            if db_path:
                retrieved = retrieve_question_evidence(db_path, request, RetrievalConfig(config.top_k))
                retrieval_done = perf_counter()
                selected = list(retrieved.evidence)
                manifest.validate_evidence(selected)
                declared = {item.evidence_id: evidence_fingerprint(item) for item in evidence[qid]}
                if any(declared.get(item.evidence_id) != evidence_fingerprint(item) for item in selected):
                    raise ValueError("Retrieved evidence differs from declared universe")
                truncated = any(query["truncated"] for query in retrieved.audit["queries"])
            else:
                selected, truncated = evidence[qid], None
                retrieval_done = start
            assessment_start = perf_counter()
            result = assess_lookup_question(request, selected, LookupConfig(True))
            assessment_done = perf_counter()
            rendered = render_lookup_response(result)
            end = perf_counter()
            outcomes.append({"question_id": qid, "result": result, "rendered": rendered})
            query_rows.append({"question_id": qid,
                               "pipeline_seconds": end - start,
                               "retrieval_seconds": retrieval_done - start if db_path else None,
                               "evidence_validation_seconds": assessment_start - retrieval_done,
                               "assessment_seconds": assessment_done - assessment_start,
                               "render_seconds": end - assessment_done,
                               "retrieval_truncated": truncated, "evidence_count": len(selected)})
        if repeat >= 0:
            fingerprint = hashlib.sha256(json.dumps(sorted(outcomes, key=lambda row: row["question_id"]),
                                                   sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()
            rows.append({"repeat": repeat, "queries": query_rows,
                         "pipeline_batch_seconds": sum(row["pipeline_seconds"] for row in query_rows),
                         "retrieval_batch_seconds": sum(row["retrieval_seconds"] for row in query_rows) if db_path else None,
                         "output_sha256": fingerprint, "memory_after_pass": process_memory()})
    # Gold is never opened; all inference has finished before environment metadata.
    return {"pid": os.getpid(), "condition": payload["condition"], "file_hashes": hashes,
            "warmup_passes": config.warmups if warm else 0, "memory_after_loading": baseline_memory,
            "trials": rows, "memory_at_end": process_memory()}


def _launch(payload: dict, config: TrialConfig) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(str(Path(path or ".").resolve()) for path in sys.path if Path(path or ".").is_dir())
    start = perf_counter()
    completed = subprocess.run([sys.executable, "-m", "ragsmith.evaluation.resource_trials"],
                               input=json.dumps(payload), capture_output=True, text=True, encoding="utf-8",
                               timeout=config.timeout_seconds, env=env, check=False)
    elapsed = perf_counter() - start
    if completed.returncode:
        raise ValueError("Resource worker failed: " + completed.stderr.strip()[-1200:])
    result = strict_json(completed.stdout)
    result["parent_launch_to_result_seconds"] = elapsed
    return result


def run_resource_trials(directory: Path, *, database: Path | None = None,
                        config: TrialConfig = TrialConfig()) -> dict:
    if not isinstance(config, TrialConfig):
        raise ValueError("config must be a TrialConfig")
    started_at = datetime.now(timezone.utc).isoformat()
    directory = directory.resolve()
    _, _, _, hashes = load_bundle(directory / "inputs.jsonl", directory / "evidence.jsonl", directory / "lineage.json")
    workers = []
    with tempfile.TemporaryDirectory(prefix="ragsmith-resources-") as folder:
        snapshot = None
        snapshot_hash = None
        if database is not None:
            snapshot = Path(folder) / "snapshot.sqlite"
            source = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)
            target = sqlite3.connect(snapshot)
            try:
                source.backup(target)
            finally:
                target.close()
                source.close()
            snapshot_hash = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        base = {"directory": str(directory), "expected_hashes": hashes,
                "database": str(snapshot) if snapshot else None, "database_sha256": snapshot_hash,
                "config": asdict(config)}
        for repeat in range(config.repeats):
            workers.append(_launch({**base, "condition": "fresh_process_first_pass", "repeat": repeat}, config))
        workers.append(_launch({**base, "condition": "warmed_process", "repeat": 0}, config))
    final_hashes = {name: hashlib.sha256((directory / filename).read_bytes()).hexdigest()
                    for name, filename in (("inputs", "inputs.jsonl"), ("evidence", "evidence.jsonl"), ("lineage", "lineage.json"))}
    if hashes != final_hashes:
        raise ValueError("Resource bundle changed during trials")
    fingerprints = {trial["output_sha256"] for process in workers for trial in process["trials"]}
    if len(fingerprints) != 1:
        raise ValueError("Pipeline outputs changed across resource repetitions")
    summaries = {}
    for condition in ("fresh_process_first_pass", "warmed_process"):
        trials = [trial for process in workers if process["condition"] == condition for trial in process["trials"]]
        summaries[condition] = {"pipeline_batch": summarize([trial["pipeline_batch_seconds"] for trial in trials]),
                                "retrieval_batch": summarize([trial["retrieval_batch_seconds"] for trial in trials]) if database else None}
    return {"resource_version": "1.0", "research_evidence": False, "gold_read": False,
            "started_at_utc": started_at, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "workload": "sqlite_snapshot_lookup_render" if database else "fixed_evidence_lookup_render",
            "config": asdict(config), "file_hashes": hashes, "database_snapshot_sha256": snapshot_hash,
            "workers": workers, "summaries": summaries,
            "environment": run_environment(Path(__file__).resolve().parents[3]),
            "conditions": {"order": "fresh workers first, then one warmed worker; not randomized",
                           "cold_definition": "fresh process first timed pass after imports and input loading",
                           "os_cache_state": "uncontrolled; no cold-disk or cache-eviction claim",
                           "memory_scope": "worker OS lifetime peak includes imports, loading, warmups and retained result records; excludes parent and children",
                           "timing_scope": "per-question retrieval, validation, assessment and rendering; excludes imports, loading, warmup and output hashing",
                           "launch_timing_scope": "parent wall time includes process launch, initialization, work and serialization",
                           "pipeline": "graded lookup enabled; no per-baseline cost comparison",
                           "limitations": "snapshot creation can warm OS pages; SQLite connection reopened per question; worker memory is not total deployment RAM"}}


if __name__ == "__main__":
    payload = strict_json(sys.stdin.read())
    print(json.dumps(worker(payload), ensure_ascii=False, allow_nan=False))
