"""Fetch only the approved official 1.5B artifact into isolated local storage."""

from pathlib import Path

import download_smoke_assets as download


download.ROOT = Path(__file__).resolve().parents[1] / "data/evaluation/generated/local-smoke/qwen15-assets"
download.MODEL = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
download.EXPECTED = "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e"
download.ASSETS = {
    download.MODEL: "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/"
    "a615a81362316d7b9f5a7a9c4313adfdf9b54588/"+download.MODEL,
}


if __name__ == "__main__":
    download.main()
