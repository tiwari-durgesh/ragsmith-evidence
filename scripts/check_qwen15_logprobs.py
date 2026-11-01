"""One synthetic loopback-only token-likelihood check; no evaluation inputs."""

import ctypes
import hashlib
import json
import math
import re
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
from ctypes import wintypes

from smoke_local_qwen import Counters, EXPECTED, MODEL, WORK, physical_memory


def value_likelihood(response):
    text = response["content"]
    match = re.search(r'"value"\s*:\s*"([^"\\]*)"', text)
    if not match or not match[1]:
        raise ValueError("No complete nonempty generated JSON value string")
    start = len(text[:match.start(1)].encode("utf-8"))
    end = len(text[:match.end(1)].encode("utf-8"))
    field = "completion_probabilities" if "completion_probabilities" in response else "probs"
    rows = response[field]
    position, reconstructed, selected = 0, bytearray(), []
    for row in rows:
        piece = bytes(row["bytes"])
        stop = position+len(piece)
        reconstructed.extend(piece)
        if position < end and stop > start:
            lp = float(row["logprob"])
            if not math.isfinite(lp) or lp > 0:
                raise ValueError("Invalid token log probability")
            selected.append({"id":row["id"],"token":row["token"],"bytes":row["bytes"],
                             "byte_start":position,"byte_end":stop,"logprob":lp})
        position = stop
    if not bytes(reconstructed).startswith(text.encode("utf-8")) or not selected:
        raise ValueError("Token bytes do not reconstruct the generated content")
    if not any(row["logprob"] < 0 for row in selected):
        raise ValueError("Only zero log probabilities; raw confidence not established")
    mean = sum(row["logprob"] for row in selected)/len(selected)
    return {"probability_field":field,"generated_value":match[1],
            "value_content_byte_span":[start,end],"value_tokens":selected,
            "mean_value_token_logprob":mean,"exp_mean_value_token_logprob":math.exp(mean),
            "interpretation":"uncalibrated likelihood ranking signal, not probability of correctness"}


def main():
    with MODEL.open("rb") as stream:
        if hashlib.file_digest(stream,"sha256").hexdigest()!=EXPECTED:
            raise ValueError("Approved model checksum mismatch")
    output = WORK / ("qwen15-logprobs-"+time.strftime("%Y%m%d-%H%M%S"))
    output.mkdir(exist_ok=False)
    runtime = WORK / "runtime/llama-server.exe"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0))
        port=sock.getsockname()[1]
    base=f"http://127.0.0.1:{port}"
    prompt=("<|im_start|>system\nRead the invented record. Reply only with JSON containing "
            "one string field named value.\n<|im_end|>\n<|im_start|>user\n"
            "Synthetic Cedar reserve is 2745.63 units in 2025. What is its reserve value?"
            "\n<|im_end|>\n<|im_start|>assistant\n")
    payload={"prompt":prompt,"n_predict":64,"temperature":0,"seed":1729,
             "n_probs":5,"post_sampling_probs":False,"return_tokens":True,
             "cache_prompt":False,"stream":False}
    (output/"request.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    report={"purpose":"one non-evaluation synthetic token-likelihood capability check",
            "model":"Qwen2.5-1.5B-Instruct Q4_K_M","model_sha256":EXPECTED,
            "server_sha256":hashlib.sha256(runtime.read_bytes()).hexdigest(),
            "host_memory_before":physical_memory(),"inference_requests":0,
            "remote_inference_requests":0,"evaluation_questions_used":0,
            "quality_scored":False,"peak_working_set_bytes":0,"aborted":None,
            "minimum_available_ram_bytes":physical_memory()["available_ram_bytes"],
            "post_sampling_probs":False,"success":False}
    kernel,psapi=ctypes.WinDLL("kernel32",use_last_error=True),ctypes.WinDLL("psapi",use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    done=threading.Event()
    started=time.perf_counter()
    with (output/"server.stdout").open("wb") as stdout,(output/"server.stderr").open("wb") as stderr:
        process=subprocess.Popen([str(runtime),"-m",str(MODEL),"--host","127.0.0.1","--port",str(port),
                                  "-c","4096","-t","6","-tb","6","-b","128","-ub","128",
                                  "--parallel","1","--no-warmup"],stdout=stdout,stderr=stderr,
                                 stdin=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        handle=kernel.OpenProcess(0x0410,False,process.pid)
        def monitor():
            while not done.wait(.05) and process.poll() is None:
                counters=Counters()
                counters.cb=ctypes.sizeof(counters)
                if handle and psapi.GetProcessMemoryInfo(handle,ctypes.byref(counters),counters.cb):
                    report["peak_working_set_bytes"]=max(report["peak_working_set_bytes"],int(counters.PeakWorkingSetSize))
                available=physical_memory()["available_ram_bytes"]
                report["minimum_available_ram_bytes"]=min(report["minimum_available_ram_bytes"],available)
                if available < 64*1024**2:
                    report["aborted"]="host available RAM below 64 MiB"
                elif report["peak_working_set_bytes"] > 6*1024**3:
                    report["aborted"]="6 GiB child working-set ceiling"
                elif time.perf_counter()-started > 240:
                    report["aborted"]="240-second capability-check timeout"
                if report["aborted"]:
                    process.terminate()
                    break
        thread=threading.Thread(target=monitor,daemon=True)
        thread.start()
        try:
            if not handle:
                raise OSError("Cannot measure local server process memory")
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            while True:
                if process.poll() is not None:
                    raise RuntimeError("Local server stopped before readiness")
                try:
                    with opener.open(base+"/health",timeout=2) as response:
                        if response.status==200:
                            break
                except (urllib.error.URLError,TimeoutError):
                    time.sleep(.2)
            report["inference_requests"]=1
            request=urllib.request.Request(base+"/completion",data=json.dumps(payload).encode(),
                                           headers={"Content-Type":"application/json"})
            with opener.open(request,timeout=180) as response:
                result=json.load(response)
            (output/"response.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
            report["response_sha256"]=hashlib.sha256((output/"response.json").read_bytes()).hexdigest()
            report["value_likelihood"]=value_likelihood(result)
            report["success"]=True
        except Exception as exc:
            report["error"]=type(exc).__name__+": "+str(exc)
        finally:
            done.set()
            thread.join(timeout=2)
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            if handle:
                kernel.CloseHandle(handle)
    report["wall_seconds_including_load"]=time.perf_counter()-started
    report["host_memory_after"]=physical_memory()
    (output/"capability.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
