"""Synthetic tests: no real pilot labels or source questions are committed."""

import copy
import hashlib
import json

import pytest

from ragsmith.evaluation.corpus_audit import FILES, REVISION
from ragsmith.evaluation.tatqa_adapter import load_pinned_split, prepare_screening


def question(uid, answer_type="span", answer_from="table"):
    return {"uid": uid, "question": "What was revenue in 2025?",
            "answer_type": answer_type, "answer_from": answer_from,
            "answer": ["GOLD-ONLY-SENTINEL"], "scale": "million", "req_comparison": False}


def context(uid="ctx-a"):
    return {"table": {"uid": uid, "table": [["Metric", "2025"], ["Revenue", "145"]]},
            "paragraphs": [{"uid": uid + "-p", "order": 1, "text": "Original source prose."}],
            "questions": [question(uid + "-q1"), question(uid + "-q2"),
                          question(uid + "-q3", "arithmetic")]}


def provenance():
    return {"revision": REVISION, "split": "train", "sha256": "a" * 64,
            "url": "fixture://synthetic", "trusted_audit_sha256": "b" * 64}


@pytest.fixture
def pinned_source(tmp_path):
    data = json.dumps([context()]).encode("utf-8")
    (tmp_path / FILES["train"]).write_bytes(data)
    audit = {"source_revision": REVISION, "source_manifest": {"revision": REVISION,
             "files": [{"path": FILES["train"], "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "url": f"https://raw.githubusercontent.com/NExTplusplus/TAT-QA/{REVISION}/dataset_raw/{FILES['train']}"}]}}
    path = tmp_path / "trusted-audit.json"
    path.write_text(json.dumps(audit), encoding="utf-8")
    return tmp_path, path


def test_pinned_loader_uses_trusted_audit_not_adjacent_manifest(pinned_source):
    directory, audit = pinned_source
    (directory / "source_manifest.json").write_text("not valid JSON", encoding="utf-8")
    rows, source = load_pinned_split(directory, audit)
    assert len(rows) == 1
    assert source["split"] == "train"
    assert source["sha256"] == hashlib.sha256((directory / FILES["train"]).read_bytes()).hexdigest()


def test_pinned_loader_rejects_tampering(pinned_source):
    directory, audit = pinned_source
    (directory / FILES["train"]).write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="trusted audit"):
        load_pinned_split(directory, audit)


@pytest.mark.parametrize("field,value", [("url", "https://example.org/unpinned"), ("bytes", 0)])
def test_pinned_loader_rejects_bad_source_declaration(pinned_source, field, value):
    directory, audit = pinned_source
    payload = json.loads(audit.read_text(encoding="utf-8"))
    payload["source_manifest"]["files"][0][field] = value
    audit.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        load_pinned_split(directory, audit)


def test_sources_preserve_cells_without_upstream_answers():
    result = prepare_screening([context()], provenance())
    assert "GOLD-ONLY-SENTINEL" not in json.dumps(result["sources"])
    assert "GOLD-ONLY-SENTINEL" not in json.dumps(result["screening_ledger"])
    assert "GOLD-ONLY-SENTINEL" in json.dumps(result["coordinator_annotation_aids"])
    cell = result["sources"][0]["table_cells"][3]
    assert cell == {"row": 1, "column": 1, "text": "145", "locator": "table:ctx-a/row:1/column:1"}
    assert result["sources"][0]["table_shape"] == [2, 2]
    assert result["sources"][0]["paragraphs"][0]["text"] == "Original source prose."


def test_label_gate_does_not_accept_semantic_eligibility():
    result = prepare_screening([context()], provenance())
    assert result["summary"]["label_gate_pass"] == 2
    assert result["summary"]["label_gate_excluded"] == 1
    assert result["summary"]["semantic_accepted_fraction"] is None
    assert result["summary"]["semantic_accepted"] is None
    assert result["sampling_manifest"]["accepted_families"] == 0
    assert result["sampling_manifest"]["families"][0]["partition"] == "pending"
    assert result["screening_ledger"][0]["binding"]["year"] is None


def test_every_context_and_question_has_screening_disposition():
    second = context("ctx-b")
    second["questions"] = [question("only", "span", "text")]
    result = prepare_screening([context(), second], provenance())
    assert len(result["screening_ledger"]) == 4
    assert len(result["context_screening_ledger"]) == 2
    assert result["context_screening_ledger"][1]["reasons"] == ["fewer_than_two_table_single_spans"]
    assert len(result["sampling_manifest"]["families"]) == 1


def test_duplicate_tables_grouped_and_order_independent():
    rows = [context("ctx-c"), context("ctx-a"), context("ctx-b")]
    rows[1]["table"]["table"][1][1] = "  145 "
    rows[2]["table"]["table"][1][1] = "999"
    first = prepare_screening(rows, provenance())
    second = prepare_screening(list(reversed(rows)), provenance())
    assert first["sampling_manifest"] == second["sampling_manifest"]
    queue = first["sampling_manifest"]["families"]
    mapping = {row["context_id"]: row["duplicate_table_group"] for row in queue}
    assert mapping["ctx-c"] == mapping["ctx-a"] != mapping["ctx-b"]
    assert first["summary"]["duplicate_table_groups"] == 2
    assert first["summary"]["report_identities_verified"] == 0


def test_source_digest_ignores_upstream_answers():
    first = context()
    second = copy.deepcopy(first)
    second["questions"][0]["answer"] = ["DIFFERENT-GOLD"]
    assert prepare_screening([first], provenance())["sources"] == prepare_screening([second], provenance())["sources"]


@pytest.mark.parametrize("mutate", [
    lambda rows: rows.append(copy.deepcopy(rows[0])),
    lambda rows: rows[0]["questions"].append(copy.deepcopy(rows[0]["questions"][0])),
    lambda rows: rows[0]["table"].update(table=[[145]]),
    lambda rows: rows[0]["questions"][0].update(answer_type="unknown"),
])
def test_malformed_source_rejected(mutate):
    rows = [context()]
    mutate(rows)
    with pytest.raises(ValueError):
        prepare_screening(rows, provenance())


@pytest.mark.parametrize("options", [{"target_families": 0}, {"development_families": 60}, {"seed": True}])
def test_invalid_sampling_parameters(options):
    with pytest.raises(ValueError):
        prepare_screening([context()], provenance(), **options)


def test_official_dev_not_silently_used_for_custom_pilot():
    source = provenance()
    source["split"] = "dev"
    with pytest.raises(ValueError, match="training"):
        prepare_screening([context()], source)
