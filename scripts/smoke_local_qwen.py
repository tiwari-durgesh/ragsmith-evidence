"""Five synthetic questions: local CPU speed/memory only, never evaluation scoring."""

import ctypes
import hashlib
import json
import os
import re
import subprocess
import time
from ctypes import wintypes
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "data/evaluation/generated/local-smoke"
MODEL = WORK / "qwen15-assets/qwen2.5-1.5b-instruct-q4_k_m.gguf"
EXPECTED = "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e"


class Counters(ctypes.Structure):
    _fields_ = [("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD)] + [
        (name,ctypes.c_size_t) for name in ("PeakWorkingSetSize","WorkingSetSize",
        "QuotaPeakPagedPoolUsage","QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage",
        "QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage")]


class Memory(ctypes.Structure):
    _fields_ = [("dwLength",wintypes.DWORD),("dwMemoryLoad",wintypes.DWORD)] + [
        (name,ctypes.c_ulonglong) for name in ("ullTotalPhys","ullAvailPhys","ullTotalPageFile",
        "ullAvailPageFile","ullTotalVirtual","ullAvailVirtual","ullAvailExtendedVirtual")]


def physical_memory():
    value = Memory()
    value.dwLength = ctypes.sizeof(value)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)):
        raise OSError("Cannot read physical memory")
    return {"total_ram_bytes":value.ullTotalPhys,"available_ram_bytes":value.ullAvailPhys}


def main():
    with MODEL.open("rb") as stream:
        if hashlib.file_digest(stream,"sha256").hexdigest()!=EXPECTED:
            raise ValueError("Fixed model checksum mismatch")
    runtime = WORK / "runtime/llama-cli.exe"
    output = WORK / ("qwen15-five-synthetic-questions-"+time.strftime("%Y%m%d-%H%M%S"))
    output.mkdir(exist_ok=False)
    kernel,psapi = ctypes.WinDLL("kernel32",use_last_error=True),ctypes.WinDLL("psapi",use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    questions = [
        ("What is synthetic Aurora revenue for 2025?", "Aurora | revenue | 2025 | 145 | USD million"),
        ("What is synthetic Birch operating cost for 2024?", "Birch | operating cost | 2024 | 73 | USD million"),
        ("Give synthetic Coral cash and assets for 2023.", "Coral | cash | 2023 | 12 | USD million\nCoral | assets | 2023 | 80 | USD million"),
        ("Give synthetic Delta revenue and profit for 2025.", "Delta | revenue | 2025 | 40 | USD million"),
        ("What is synthetic Ember revenue for 2025?", "Ember | revenue | 2025 | 60 | USD million\nEmber | revenue | 2025 | 65 | USD million"),
    ]
    report = {"purpose":"hardware smoke only; no answer quality or evaluation score",
              "model":"Qwen2.5-1.5B-Instruct Q4_K_M","model_sha256":EXPECTED,
              "runtime":"llama.cpp b6096 Windows CPU x64","runtime_sha256":hashlib.sha256(runtime.read_bytes()).hexdigest(),
              "cpu_identifier":os.environ.get("PROCESSOR_IDENTIFIER"),"logical_processors":os.cpu_count(),
              "host_memory_before":physical_memory(),"ctx_size":4096,"threads":6,
              "batch_size":128,"maximum_generated_tokens":64,"temperature":0,"seed":1729,
              "planned_questions":5,
              "conditions":"planned five fresh processes; OS cache uncontrolled; short synthetic prompts, not full 3200-token workload",
              "memory_method":"Win32 GetProcessMemoryInfo OS lifetime peak working set, sampled every 50 ms; child process only",
              "paid_api_calls":0,"evaluation_questions_used":0,"quality_scored":False,"trials":[]}
    for index,(question,facts) in enumerate(questions,1):
        distractors = "\n".join(f"Unrelated item {n} | 2022 | {n+10} | units" for n in range(20))
        prompt = ("<|im_start|>system\nUse only the supplied synthetic records. Reply briefly in JSON.\n<|im_end|>\n"
                  "<|im_start|>user\n"+facts+"\n"+distractors+"\nQuestion: "+question+
                  "\n<|im_end|>\n<|im_start|>assistant\n")
        prompt_file = output/f"synthetic-{index}.txt"
        prompt_file.write_text(prompt,encoding="utf-8")
        command = [str(runtime),"-m",str(MODEL),"-f",str(prompt_file),"-n","64","-c","4096",
                   "-t","6","-tb","6","-b","128","-ub","128","--temp","0","--seed","1729",
                   "--no-conversation","--no-display-prompt","--simple-io","--no-warmup"]
        started = time.perf_counter()
        peak,current,last_available = 0,0,None
        before_trial=physical_memory()
        minimum_available=before_trial["available_ram_bytes"]
        aborted = None
        with (output/f"synthetic-{index}.stdout").open("wb") as stdout, (output/f"synthetic-{index}.stderr").open("wb") as stderr:
            process = subprocess.Popen(command,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            handle = kernel.OpenProcess(0x0410,False,process.pid)
            try:
                while process.poll() is None:
                    counters = Counters()
                    counters.cb = ctypes.sizeof(counters)
                    if handle and psapi.GetProcessMemoryInfo(handle,ctypes.byref(counters),counters.cb):
                        current = int(counters.WorkingSetSize)
                        peak = max(peak,int(counters.PeakWorkingSetSize))
                    last_available = physical_memory()["available_ram_bytes"]
                    minimum_available=min(minimum_available,last_available)
                    if time.perf_counter()-started > 240:
                        aborted="240-second per-question timeout"
                    if current > 6*1024**3:
                        aborted="6 GiB child working-set ceiling"
                    if last_available < 64*1024**2:
                        aborted="host available RAM below 64 MiB"
                    if aborted:
                        process.terminate()
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                        break
                    time.sleep(.05)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                if handle:
                    kernel.CloseHandle(handle)
        elapsed = time.perf_counter()-started
        log = (output/f"synthetic-{index}.stderr").read_text(encoding="utf-8",errors="replace")
        def timing(name):
            match = re.search(name+r"\s*=\s*([\d.]+) ms\s*/\s*(\d+) (?:tokens|runs).*?([\d.]+) tokens per second",log)
            return {"milliseconds":float(match[1]),"tokens":int(match[2]),"tokens_per_second":float(match[3])} if match else None
        trial={"question":"synthetic-"+str(index),"wall_seconds_including_load":elapsed,
               "exit_code":process.returncode,"aborted":aborted,"peak_working_set_bytes":peak or None,
               "host_memory_before_trial":before_trial,"minimum_available_ram_bytes":minimum_available,
               "last_available_ram_bytes":last_available,"prompt_eval":timing("prompt eval time"),
               "generation":timing(r"(?<!prompt )eval time")}
        report["trials"].append(trial)
        (output/"hardware-smoke.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        print(json.dumps(trial),flush=True)
        if aborted or process.returncode != 0:
            print("Stopped remaining synthetic questions after a failed trial; no inference retry.",flush=True)
            break
    report["host_memory_after"]=physical_memory()
    report["completed_questions"]=sum(row["exit_code"]==0 for row in report["trials"])
    (output/"hardware-smoke.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return 0 if report["completed_questions"]==5 else 1


if __name__=="__main__":
    raise SystemExit(main())
