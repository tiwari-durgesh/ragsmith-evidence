"""Optional Python-allocation profiling and read-only run metadata collection."""

import hashlib
import importlib.metadata
import platform
import subprocess
import sys
import tracemalloc
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter


class RunMeasurements:
    """Measure named stages; never label Python heap allocation as process RSS."""

    def __init__(self, profile_memory: bool = False):
        if type(profile_memory) is not bool:
            raise ValueError("profile_memory must be a boolean")
        self.profile_memory = profile_memory
        self.seconds = {}
        self.memory = {"method": "disabled", "python_peak_bytes": None,
                       "process_peak_rss_bytes": None}
        self._owns_trace = False

    def __enter__(self):
        self._start = perf_counter()
        self._checkpoint = self._start
        if self.profile_memory:
            if tracemalloc.is_tracing():
                self.memory["method"] = "unavailable_existing_tracemalloc_session"
            else:
                tracemalloc.start()
                self._owns_trace = True
                self.memory["method"] = "tracemalloc_python_allocations"
        return self

    @contextmanager
    def stage(self, name: str):
        start = perf_counter()
        try:
            yield
        finally:
            self.seconds[name] = self.seconds.get(name, 0.0) + perf_counter() - start

    def __exit__(self, exc_type, exc, traceback):
        if self._owns_trace:
            self.memory["python_peak_bytes"] = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
        self.seconds["total"] = perf_counter() - self._start

    def checkpoint(self, name: str) -> None:
        now = perf_counter()
        self.seconds[name] = now - self._checkpoint
        self._checkpoint = now

    def report(self) -> dict:
        return {
            "clock": "time.perf_counter", "seconds": dict(self.seconds),
            "memory": dict(self.memory), "profile_memory_requested": self.profile_memory,
            "conditions": "single in-process run; no warmup or isolated-process guarantee",
            "live_retrieval_seconds": None,
            "limitations": "No process RSS sampling; profiling overhead affects timings",
        }


def run_environment(repo_path: Path) -> dict:
    """Record interpreter/dependency metadata and hash dirty repository content."""
    dependencies = {}
    for name in ("pytest", "PyMuPDF", "python-docx", "openpyxl", "beautifulsoup4"):
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None
    report = {"python": sys.version, "executable": sys.executable,
              "platform": platform.platform(), "dependency_metadata": dependencies,
              "git_commit": None, "dirty": None, "dirty_content_sha256": None}
    try:
        def git(*args):
            return subprocess.check_output(["git", "-C", str(repo_path), *args],
                                           stderr=subprocess.DEVNULL, timeout=10)

        root = Path(git("rev-parse", "--show-toplevel").decode().strip())
        report["git_commit"] = git("rev-parse", "HEAD").decode().strip()
        diff = git("diff", "--binary", "HEAD", "--")
        untracked = sorted(
            name for name in git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
            if name
        )
        report["dirty"] = bool(diff or untracked)
        digest = hashlib.sha256(diff)
        for raw_name in untracked:
            path = root / raw_name.decode("utf-8")
            digest.update(raw_name + b"\0")
            if path.is_file():
                digest.update(hashlib.sha256(path.read_bytes()).digest())
        report["dirty_content_sha256"] = digest.hexdigest() if report["dirty"] else None
    except (OSError, subprocess.SubprocessError, UnicodeError):
        report["git_metadata_status"] = "unavailable"
    else:
        report["git_metadata_status"] = "recorded"
    return report
