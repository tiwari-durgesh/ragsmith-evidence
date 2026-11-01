"""Only offline pilot guards: no pilot inference or real API calls occur here."""

import importlib.util
import io
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


workflow = module("pilot36")
llm = module("label_pilot36_llm")


def case(label=None, basis="needs_your_judgment"):
    return {"case_id":"Q01", "label_basis":basis, "label":label, "notes":""}


def sheet(row):
    return {"annotation_status":"provisional, single-annotator", "annotator_id":"synthetic-test", "cases":[row]}


def test_incomplete_human_label_cannot_lock():
    with pytest.raises(ValueError, match="Missing or invalid"):
        workflow.validate_sheet(sheet(case()), [case()])


def test_construction_labels_cannot_be_silently_changed():
    row = case("full", "determined_by_construction")
    with pytest.raises(ValueError, match="construction labels"):
        workflow.validate_sheet(sheet(row), [row])


def test_duplicate_case_labels_rejected():
    row = case("full")
    duplicate = sheet(row)
    duplicate["cases"].append(row)
    with pytest.raises(ValueError):
        workflow.validate_sheet(duplicate, [row])


def test_no_results_run_before_label_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(workflow, "verify_freeze", lambda path: ({}, []))
    monkeypatch.setattr(workflow, "predict", lambda *args: pytest.fail("Inference must not run"))
    with pytest.raises(FileNotFoundError):
        workflow.run_once(tmp_path)
    assert not (tmp_path / "results").exists()


def test_results_run_cannot_repeat(tmp_path, monkeypatch):
    monkeypatch.setattr(workflow, "verify_freeze", lambda path: ({}, []))
    monkeypatch.setattr(workflow, "locked_sheet", lambda *args: {})
    (tmp_path / "results").mkdir()
    with pytest.raises(FileExistsError):
        workflow.run_once(tmp_path)


def test_api_request_contains_only_public_case_and_no_tools(monkeypatch):
    captured = []
    visible = {"case_id":"Q01", "question":"Revenue?", "requirements":[], "evidence":[]}
    class Response(io.StringIO):
        headers = {"x-request-id":"mock-only"}
    def mock_open(request, timeout):
        payload = json.loads(request.data)
        captured.append(payload)
        assert "tools" not in payload
        assert payload["store"] is False
        assert json.loads(payload["messages"][1]["content"]) == visible
        assert "HUMAN_ONLY_SENTINEL" not in request.data.decode()
        content = json.dumps({"case_id":"Q01", "label":"abstain", "reason":"No evidence."})
        return Response(json.dumps({"model":llm.MODEL, "choices":[{"message":{"content":content}}]}))
    monkeypatch.setattr(llm.urllib.request, "urlopen", mock_open)
    row, info = llm.label_case(visible, "FAKE-TEST-KEY")
    assert row["label"] == "abstain"
    assert captured[0]["model"] == "gpt-4.1-mini-2025-04-14"
    assert info["request_id"] == "mock-only"


def test_labeler_cannot_start_without_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "label_case", lambda *args: pytest.fail("API must not run"))
    with pytest.raises(FileNotFoundError):
        llm.run(tmp_path/"cases.json", tmp_path/"absent-lock.json", tmp_path/"output")


def test_label_stage_never_opens_human_file(tmp_path, monkeypatch):
    public = tmp_path / "public"
    public.mkdir()
    human = tmp_path / "human-private.json"
    human.write_text("HUMAN_ONLY_SENTINEL", encoding="utf-8")
    packet = public / "cases.json"
    packet.write_text(json.dumps({"notice":"synthetic test", "cases":[
        {"case_id":f"Q{i:02d}", "question":"Fact?", "requirements":[], "evidence":[]} for i in range(1,37)]}), encoding="utf-8")
    receipt = public / "lock.json"
    receipt.write_text(json.dumps({"pipeline_commit":llm.FREEZE, "src_tree":llm.SRC_TREE,
                                  "human_labels_sha256":"synthetic-hash-not-a-path", "locked_at_utc":"synthetic-test",
                                  "public_packet_sha256":llm.sha(packet)}), encoding="utf-8")
    real_read = Path.read_text
    def guarded_read(path, *args, **kwargs):
        if path == human:
            pytest.fail("LLM stage tried to read human labels")
        return real_read(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", guarded_read)
    monkeypatch.setattr(llm.subprocess, "check_output", lambda args, **kwargs: llm.SRC_TREE+"\n" if "rev-parse" in args else b"")
    monkeypatch.setenv("OPENAI_API_KEY", "FAKE-TEST-KEY")
    monkeypatch.setattr(llm, "label_case", lambda row,key:
                        ({"case_id":row["case_id"], "label":"abstain", "reason":"Synthetic mocked call."}, {}))
    llm.run(packet, receipt, tmp_path / "llm-only")
    assert (tmp_path / "llm-only/labels.json").is_file()
