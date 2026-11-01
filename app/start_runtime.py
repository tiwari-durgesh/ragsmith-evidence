"""Start the fixed local model on loopback with the existing resource guards."""

import argparse
import ctypes
import subprocess
import time
from ctypes import wintypes

from app.runtime import LocalRuntime
from scripts.smoke_local_qwen import Counters, physical_memory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8091)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be 1024..65535")
    runtime = LocalRuntime()
    runtime.verify_artifacts()
    kernel, psapi = ctypes.WinDLL("kernel32", use_last_error=True), ctypes.WinDLL("psapi", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    cmd = [str(runtime.server), "-m", str(runtime.model), "--host", "127.0.0.1", "--port", str(args.port),
           "-c", "4096", "-t", "6", "-tb", "6", "-b", "128", "-ub", "128", "--parallel", "1", "--no-warmup"]
    process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    handle = kernel.OpenProcess(0x0410, False, process.pid)
    try:
        if not handle:
            raise RuntimeError("Cannot monitor local model process memory")
        while process.poll() is None:
            counters = Counters()
            counters.cb = ctypes.sizeof(counters)
            if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                raise RuntimeError("Cannot monitor local model process memory")
            if physical_memory()["available_ram_bytes"] < 64 * 1024**2:
                raise RuntimeError("Available RAM below 64 MiB; stopping without retry")
            if counters.PeakWorkingSetSize > 6 * 1024**3:
                raise RuntimeError("Model exceeded 6 GiB working-set limit; stopping without retry")
            time.sleep(0.1)
        if process.returncode:
            raise RuntimeError("Local model server exited with code " + str(process.returncode))
    except KeyboardInterrupt:
        pass
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        if handle:
            kernel.CloseHandle(handle)


if __name__ == "__main__":
    main()
