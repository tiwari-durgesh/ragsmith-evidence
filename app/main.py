"""FastAPI transport for local demonstration, without changing the QA source."""

import json
import logging
import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException

from app.models import AskRequest
from app.runtime import LocalRuntime
from app.service import answer


app = FastAPI(title="RAGSmith Evidence — local demo", version="0.1.0")
runtime = LocalRuntime()
SAMPLES = Path(__file__).resolve().parents[1] / "data/evaluation/generated/demo-api/samples.json"


@app.get("/health")
def health():
    return {"status": "ok", "demo_only": True, "confidence_calibrated": False,
            "sample_count": len(json.loads(SAMPLES.read_text(encoding="utf-8"))["cases"]) if SAMPLES.exists() else 0}


@app.get("/samples")
def samples():
    if not SAMPLES.exists():
        raise HTTPException(404, "Prepare local pilot samples with python -m app.prepare_samples")
    return json.loads(SAMPLES.read_text(encoding="utf-8"))


@app.post("/ask")
def ask(payload: AskRequest):
    try:
        return answer(payload, runtime)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as exc:
        logging.getLogger(__name__).warning("Local runtime unavailable: %s", type(exc).__name__)
        raise HTTPException(503, "Local runtime unavailable; no model substitution or retry. Check the local server terminal.") from exc
