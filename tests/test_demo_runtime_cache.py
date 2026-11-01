"""Mocked loopback transport proves cache sharing without running a model."""

import io
import json

import pytest

from app.runtime import LocalRuntime, pack, prompt_for
from tests.test_demo_runtime import generated, question, row


def test_one_generation_shared_and_cache_hit_returns_copy(monkeypatch):
    runtime = LocalRuntime()
    monkeypatch.setattr(runtime, "verify_artifacts", lambda: None)
    calls = []

    def open_request(req, timeout):
        if isinstance(req, str):
            return io.BytesIO(json.dumps({"model_path": str(runtime.model),
                "default_generation_settings": {"n_ctx": 4096}, "total_slots": 1,
                "build_info": "b6096-fd1234cb"}).encode())
        calls.append(json.loads(req.data))
        return io.BytesIO(json.dumps(generated()).encode())

    monkeypatch.setattr(runtime._http, "open", open_request)
    packed = pack(question(), [row(), row("f", "Cash", "4")], lambda x: 100)
    first, audit = runtime.generate(question(), packed)
    first[0]["value"] = "tampered caller copy"
    second, cached = runtime.generate(question(), packed)
    assert second[0]["value"] == "10"
    assert len(calls) == 1
    assert calls[0]["seed"] == 1729 and calls[0]["post_sampling_probs"] is False
    assert audit["inference_requests"] == 1
    assert cached["inference_requests"] == 0 and cached["cache_hit"]


def test_wrong_live_model_or_context_fails_before_generation(monkeypatch):
    runtime = LocalRuntime()
    monkeypatch.setattr(runtime, "verify_artifacts", lambda: None)
    monkeypatch.setattr(runtime._http, "open", lambda *a, **k: io.BytesIO(json.dumps({"model_path": str(runtime.model),
        "default_generation_settings": {"n_ctx": 1024}, "total_slots": 1,
        "build_info": "b6096-fd1234cb"}).encode()))
    packed = pack(question(), [], lambda x: 100)
    with pytest.raises(ValueError, match="fixed manifest"):
        runtime.generate(question(), packed)
