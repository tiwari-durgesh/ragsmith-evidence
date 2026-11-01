
import hashlib
import json
import subprocess
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "data/evaluation/generated/local-smoke"
MODEL = "Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
EXPECTED = "2fde00ce69dd4899c70d020845e2638353015bba0fdf161b3eb965f2bca4464e"
ASSETS = {
    "llama-b6096-bin-win-cpu-x64.zip": "https://github.com/ggml-org/llama.cpp/releases/download/b6096/llama-b6096-bin-win-cpu-x64.zip",
    MODEL: "https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF/resolve/main/" + MODEL,
}


def resume_model(path, url):
    with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"),timeout=60) as response:
        total = int(response.headers["Content-Length"])
    if path.exists() and path.stat().st_size == total:
        return
    prefix = ROOT / (MODEL + ".prefix")
    if path.exists() and not prefix.exists():
        path.rename(prefix)
    offset = prefix.stat().st_size if prefix.exists() else 0
    size = 16 * 1024 * 1024
    ranges = [(i,start,min(total-1,start+size-1)) for i,start in enumerate(range(offset,total,size))]
    chunks = ROOT / "model-chunks"
    chunks.mkdir(exist_ok=True)
    def fetch(item):
        index,start,end = item
        target = chunks / f"{index:04d}.chunk"
        if target.exists() and target.stat().st_size == end-start+1:
            return index
        for attempt in range(20):
            try:
                have = target.stat().st_size if target.exists() else 0
                if have == end-start+1:
                    return index
                if have > end-start+1:
                    raise ValueError("Oversize saved range")
                next_start = start+have
                segment = target.with_suffix(".transfer")
                response = subprocess.run([
                    "curl.exe", "--fail", "--location", "--silent", "--show-error",
                    "--max-time", "60", "--range", f"{next_start}-{end}",
                    "--output", str(segment), "--write-out", "%{http_code}",
                    url+f"?download=true&range_start={next_start}",
                ], capture_output=True, text=True, timeout=70,
                   creationflags=subprocess.CREATE_NO_WINDOW)
                if response.stdout.strip() != "206" or not segment.exists() or not segment.stat().st_size:
                    raise ValueError("Range transfer failed: " + response.stderr[:100])
                if segment.stat().st_size > end-next_start+1:
                    raise ValueError("Oversize transferred range")
                with target.open("ab") as stream, segment.open("rb") as incoming:
                    while data := incoming.read(1024*1024):
                        stream.write(data)
                if target.stat().st_size != end-start+1:
                    continue
                return index
            except (OSError,ValueError) as exc:
                print(f"Range {index} attempt {attempt+1}: {type(exc).__name__}: {str(exc)[:100]}",flush=True)
                if attempt==19:
                    raise
        raise ValueError(f"Model range {index} remained incomplete")
    completed = 0
    with ThreadPoolExecutor(max_workers=16) as pool:
        for future in as_completed([pool.submit(fetch,item) for item in ranges]):
            future.result()
            completed += 1
            if completed % 8 == 0 or completed==len(ranges):
                print(f"Completed model ranges (whole-file SHA pending): {completed}/{len(ranges)}",flush=True)
    assembled = ROOT / (MODEL+".assembling")
    with assembled.open("wb") as stream:
        inputs = ([prefix] if prefix.exists() else []) + [chunks/f"{index:04d}.chunk" for index,_,_ in ranges]
        for source in inputs:
            with source.open("rb") as incoming:
                while data := incoming.read(4*1024*1024):
                    stream.write(data)
    with assembled.open("rb") as stream:
        if hashlib.file_digest(stream,"sha256").hexdigest()!=EXPECTED:
            raise ValueError("Resumed model SHA-256 mismatch")
    assembled.rename(path)
    print("Resumed complete model SHA-256 verified",flush=True)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in ASSETS.items():
        path = ROOT / name
        if name == MODEL:
            resume_model(path,url)
        if not path.exists():
            partial = ROOT / (name + ".part")
            print("Downloading " + name, flush=True)
            started, last = time.monotonic(), time.monotonic()
            with urllib.request.urlopen(url, timeout=60) as response, partial.open("wb") as output:
                size = 0
                while chunk := response.read(4 * 1024 * 1024):
                    output.write(chunk)
                    size += len(chunk)
                    if time.monotonic() - last > 20:
                        print(f"{name}: {size/1e9:.2f} GB downloaded", flush=True)
                        last = time.monotonic()
            partial.rename(path)
            print(f"Download complete in {time.monotonic()-started:.1f}s", flush=True)
        digest = hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
        if name == MODEL and digest != EXPECTED:
            raise ValueError("Model does not match preregistered SHA-256")
        records.append({"file":name, "url":url, "bytes":path.stat().st_size, "sha256":digest})
        if name.endswith(".zip"):
            target = ROOT / "runtime"
            if not target.exists():
                with zipfile.ZipFile(path) as archive:
                    for member in archive.infolist():
                        resolved = (target / member.filename).resolve()
                        if not resolved.is_relative_to(target.resolve()):
                            raise ValueError("Unexpected archive path")
                    archive.extractall(target)
    (ROOT / "assets.json").write_text(json.dumps(records,indent=2),encoding="utf-8")
    print("Fixed model SHA verified; assets ready.",flush=True)


if __name__ == "__main__":
    main()
