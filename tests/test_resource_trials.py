"""Resource contracts and real isolated-worker diagnostics on synthetic inputs."""

import subprocess
import sys
from pathlib import Path

import pytest

from ragsmith.evaluation import resource_trials as resources
from ragsmith.evaluation.resource_trials import TrialConfig, process_memory, run_resource_trials, summarize, worker

# Reuse the existing original synthetic SQLite/source-registration fixture.
from test_evaluation_preparation import native_bundle


FIXTURES = Path(__file__).resolve().parents[1] / "data/evaluation/fixtures"


def test_os_memory_is_positive_or_explicitly_unavailable():
    report = process_memory()
    assert report["scope"] == "worker_process_only"
    if sys.platform in {"win32", "linux"}:
        assert report["method"] != "unavailable"
        assert report["current_rss_bytes"] > 0
        assert report["process_lifetime_peak_rss_bytes"] >= report["current_rss_bytes"]
    else:
        assert report["current_rss_bytes"] is None


def test_unsupported_memory_platform_is_null(monkeypatch):
    monkeypatch.setattr(resources.sys, "platform", "unsupported")
    report = process_memory()
    assert report["current_rss_bytes"] is None
    assert report["process_lifetime_peak_rss_bytes"] is None
    assert report["reason"] == "unsupported_platform"


def test_memory_api_failure_does_not_invent_zero(monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("synthetic API failure")
    monkeypatch.setattr(resources.sys, "platform", "win32")
    monkeypatch.setattr(resources.ctypes, "WinDLL", fail, raising=False)
    report = process_memory()
    assert report["method"] == "unavailable"
    assert report["process_lifetime_peak_rss_bytes"] is None


def test_nearest_rank_p95_and_median():
    assert summarize(list(range(20))) == {"n":20, "median_seconds":9.5, "p95_seconds":18,
                                        "min_seconds":0, "max_seconds":19}
    assert summarize([])["p95_seconds"] is None
    assert summarize([.2])["median_seconds"] == .2


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, True])
def test_bad_timing_samples_rejected(value):
    with pytest.raises(ValueError):
        summarize([value])


@pytest.mark.parametrize("options", [{"repeats":0}, {"repeats":51}, {"warmups":0},
                                    {"warmups":True}, {"top_k":101}, {"seed":False}, {"timeout_seconds":61}])
def test_bad_trial_config_rejected(options):
    with pytest.raises(ValueError):
        TrialConfig(**options)


def test_fixed_evidence_trials_are_separate_processes_with_no_gold(tmp_path):
    for name in ("inputs.jsonl", "evidence.jsonl", "lineage.json"):
        (tmp_path / name).write_bytes((FIXTURES / name).read_bytes())
    assert not (tmp_path / "gold.jsonl").exists()
    result = run_resource_trials(tmp_path, config=TrialConfig(repeats=2, warmups=1))
    assert len(result["workers"]) == 3
    assert result["gold_read"] is False
    assert result["research_evidence"] is False
    assert result["workload"] == "fixed_evidence_lookup_render"
    assert len({trial["output_sha256"] for process in result["workers"] for trial in process["trials"]}) == 1
    for process in result["workers"]:
        assert process["pid"] != __import__("os").getpid()
        assert process["parent_launch_to_result_seconds"] > 0
        expected = 2 if process["condition"] == "warmed_process" else 1
        assert len(process["trials"]) == expected
        for trial in process["trials"]:
            assert len(trial["queries"]) == 6
            assert trial["retrieval_batch_seconds"] is None
            assert trial["pipeline_batch_seconds"] > 0
            for row in trial["queries"]:
                assert row["retrieval_seconds"] is None
                assert row["pipeline_seconds"] >= row["assessment_seconds"] + row["render_seconds"]
    assert result["summaries"]["warmed_process"]["pipeline_batch"]["n"] == 2
    assert "uncontrolled" in result["conditions"]["os_cache_state"]


def test_native_retrieval_is_timed_and_original_database_unchanged(native_bundle):
    db, directory = native_bundle
    initial = db.read_bytes()
    result = run_resource_trials(directory, database=db, config=TrialConfig(repeats=1))
    assert db.read_bytes() == initial
    assert result["workload"] == "sqlite_snapshot_lookup_render"
    assert len(result["database_snapshot_sha256"]) == 64
    for process in result["workers"]:
        trial = process["trials"][0]
        assert trial["retrieval_batch_seconds"] > 0
        assert trial["queries"][0]["evidence_count"] == 1
        assert trial["queries"][0]["retrieval_truncated"] is False


def test_worker_bundle_hash_mismatch_rejected():
    with pytest.raises(ValueError, match="parent input hashes"):
        worker({"config": {}, "directory": str(FIXTURES), "expected_hashes": {}})


def test_worker_nonzero_exit_is_reported(monkeypatch):
    monkeypatch.setattr(resources.subprocess, "run", lambda *args, **kwargs:
                        subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="synthetic failure"))
    with pytest.raises(ValueError, match="synthetic failure"):
        resources._launch({}, TrialConfig())


def test_worker_timeout_propagates(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("synthetic", 1)
    monkeypatch.setattr(resources.subprocess, "run", timeout)
    with pytest.raises(subprocess.TimeoutExpired):
        resources._launch({}, TrialConfig())


def test_changed_bundle_during_trials_rejected(tmp_path, monkeypatch):
    for name in ("inputs.jsonl", "evidence.jsonl", "lineage.json"):
        (tmp_path / name).write_bytes((FIXTURES / name).read_bytes())
    real_launch = resources._launch
    calls = 0
    def mutate_after_final_worker(payload, config):
        nonlocal calls
        report = real_launch(payload, config)
        calls += 1
        if calls == 2:
            path = tmp_path / "inputs.jsonl"
            path.write_bytes(path.read_bytes() + b"\n")
        return report
    monkeypatch.setattr(resources, "_launch", mutate_after_final_worker)
    with pytest.raises(ValueError, match="changed during trials"):
        run_resource_trials(tmp_path, config=TrialConfig(repeats=1))
