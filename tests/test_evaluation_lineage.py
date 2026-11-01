"""Adversarial record validation and source-lineage checks for evaluation only."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from ragsmith.evaluation.harness import run_suite
from ragsmith.evaluation.lineage import SourceManifest
from ragsmith.evaluation.records import (
    FrozenEvidenceRecord, GoldFact, GoldRecord, evidence_fingerprint, read_jsonl,
    strict_json,
)
from ragsmith.value_lookup import LookupQuestion


FIXTURES = Path(__file__).resolve().parents[1] / "data/evaluation/fixtures"


def copy_fixture(tmp_path):
    for name in ("inputs.jsonl", "evidence.jsonl", "gold.jsonl", "lineage.json"):
        (tmp_path / name).write_text((FIXTURES / name).read_text(encoding="utf-8"),
                                     encoding="utf-8")


def suite(path):
    return run_suite(path / "inputs.jsonl", path / "evidence.jsonl", path / "gold.jsonl")


def edit_rows(path, transform):
    rows = read_jsonl(path)
    transform(rows)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def edit_manifest(path, transform):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    transform(manifest)
    path.write_text(json.dumps(manifest), encoding="utf-8")


def test_typed_records_preserve_fixture_decisions_and_are_frozen():
    gold = GoldRecord.from_payload(read_jsonl(FIXTURES / "gold.jsonl")[0])
    request = LookupQuestion.from_payload(read_jsonl(FIXTURES / "inputs.jsonl")[0])
    assert gold.validate_request(request) == "full"
    assert isinstance(gold.requirements[0], GoldFact)
    with pytest.raises(FrozenInstanceError):
        gold.group_id = "changed"
    report = suite(FIXTURES)
    assert report["evaluation_version"] == "0.3"
    assert report["lineage_status"] == "validated_internal_consistency"
    assert "lineage" in report["file_hashes"]
    assert report["metrics"]["graded_sufficiency"]["answerability_accuracy"] == 5 / 6


@pytest.mark.parametrize("field,value", [
    ("question_id", None), ("group_id", []), ("origin", []),
    ("partition", {}), ("requirements", [None]), ("requirements", "facts"),
])
def test_invalid_gold_shapes_fail_with_value_error(field, value):
    row = read_jsonl(FIXTURES / "gold.jsonl")[0]
    row[field] = value
    with pytest.raises(ValueError):
        GoldRecord.from_payload(row)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_gold_values_rejected(value):
    row = read_jsonl(FIXTURES / "gold.jsonl")[0]
    row["requirements"][0]["acceptable_values"] = [value]
    with pytest.raises(ValueError, match="Nonfinite"):
        GoldRecord.from_payload(row)


def test_gold_cannot_claim_missing_with_support_or_conflict_with_one_source():
    with pytest.raises(ValueError, match="Missing"):
        GoldFact("r1", "missing", (), ("e1",))
    with pytest.raises(ValueError, match="at least two"):
        GoldFact("r1", "conflicted", (), ("e1",))


@pytest.mark.parametrize("raw", [
    '{"question_id":"a","question_id":"b"}',
    '{"metadata":{"expected":NaN}}',
    '{"metadata":{"expected":Infinity}}',
])
def test_json_rejects_duplicate_keys_and_nonfinite_constants(raw):
    with pytest.raises(ValueError):
        strict_json(raw)


@pytest.mark.parametrize("line", ['[]', 'null', '{bad json}'])
def test_jsonl_errors_have_filename_and_line_number(tmp_path, line):
    path = tmp_path / "bad.jsonl"
    path.write_text("\n" + line, encoding="utf-8")
    with pytest.raises(ValueError, match="bad.jsonl:2:"):
        read_jsonl(path)


@pytest.mark.parametrize("payload", [
    {"question_id": "q1", "evidence": [None]},
    {"question_id": "q1", "evidence": {}},
    {"question_id": "q1", "evidence": [{"unexpected": "field"}]},
])
def test_frozen_evidence_shape_errors_are_explicit(payload):
    with pytest.raises(ValueError):
        FrozenEvidenceRecord.from_payload(payload)


def test_duplicate_evidence_and_reserved_metadata_labels_rejected():
    row = read_jsonl(FIXTURES / "evidence.jsonl")[0]
    row["evidence"].append(row["evidence"][0])
    with pytest.raises(ValueError, match="Duplicate frozen evidence"):
        FrozenEvidenceRecord.from_payload(row)
    row = read_jsonl(FIXTURES / "evidence.jsonl")[0]
    row["evidence"][0]["metadata"] = {"nested": [{"gold_answer": "145"}]}
    with pytest.raises(ValueError, match="Gold annotation"):
        FrozenEvidenceRecord.from_payload(row)


@pytest.mark.parametrize("field,value", [
    ("content", "Metric: Revenue; 2025: 999"),
    ("document_version", "stale"), ("locator", "row:999"),
    ("metadata", {"cells": {"2025": "999"}}),
])
def test_evidence_tampering_rejected_before_inference(tmp_path, monkeypatch, field, value):
    import ragsmith.evaluation.harness as harness
    copy_fixture(tmp_path)
    edit_rows(tmp_path / "evidence.jsonl", lambda rows: rows[0]["evidence"][0].update(
        {field: value}
    ))
    monkeypatch.setattr(harness, "predict", lambda *_: pytest.fail("must fail before inference"))
    with pytest.raises(ValueError, match="fingerprint/source"):
        suite(tmp_path)


def test_unknown_evidence_and_wrong_gold_question_rejected(tmp_path):
    copy_fixture(tmp_path)
    edit_rows(tmp_path / "gold.jsonl", lambda rows: rows[0]["requirements"][0].update(
        {"evidence_ids": ["not-in-frozen-set"]}
    ))
    with pytest.raises(ValueError, match="absent from the frozen"):
        suite(tmp_path)
    gold = GoldRecord.from_payload(read_jsonl(FIXTURES / "gold.jsonl")[0])
    request = LookupQuestion.from_payload(read_jsonl(FIXTURES / "inputs.jsonl")[1])
    with pytest.raises(ValueError, match="match the system input"):
        gold.validate_request(request)


def test_gold_source_links_obey_per_requirement_scope(tmp_path):
    copy_fixture(tmp_path)

    def scope(rows):
        # Profit is from synthetic-report; it cannot support a requirement
        # scoped only to the separately declared synthetic-second-report.
        rows[0]["requirements"][1]["document_ids"] = ["synthetic-second-report"]

    edit_rows(tmp_path / "inputs.jsonl", scope)
    with pytest.raises(ValueError, match="requirement document scope"):
        suite(tmp_path)


def test_unknown_requested_scope_rejected_even_without_evidence(tmp_path):
    copy_fixture(tmp_path)
    edit_rows(tmp_path / "inputs.jsonl", lambda rows: rows[2]["requirements"][0].update(
        {"document_ids": ["undeclared-source"]}
    ))
    with pytest.raises(ValueError, match="absent from the source manifest"):
        suite(tmp_path)


@pytest.mark.parametrize("case", ["cycle", "unknown_parent", "duplicate_source",
                                  "duplicate_link", "unknown_source", "bad_digest",
                                  "parent_group", "schema", "missing_parent"])
def test_lineage_manifest_rejects_invalid_graphs_and_identifiers(case):
    manifest = json.loads((FIXTURES / "lineage.json").read_text(encoding="utf-8"))
    first, second = manifest["sources"]
    if case == "cycle":
        first.update({"parent_source_ids": [second["source_id"]],
                      "transformation": "canonicalization"})
    elif case == "unknown_parent":
        second["parent_source_ids"] = ["unknown"]
    elif case == "duplicate_source":
        manifest["sources"].append(first)
    elif case == "duplicate_link":
        manifest["evidence_links"].append(manifest["evidence_links"][0])
    elif case == "unknown_source":
        manifest["evidence_links"][0]["source_id"] = "unknown"
    elif case == "bad_digest":
        manifest["evidence_links"][0]["fingerprint"] = "not-a-hash"
    elif case == "parent_group":
        second["group_id"] = "another-family"
    elif case == "schema":
        manifest["schema_version"] = "99.0"
    else:
        second["parent_source_ids"] = []
    with pytest.raises(ValueError):
        SourceManifest.from_payload(manifest)


def test_group_labels_cannot_override_source_lineage_group(tmp_path):
    copy_fixture(tmp_path)
    edit_rows(tmp_path / "gold.jsonl", lambda rows: rows[0].update({"group_id": "fake-group"}))
    with pytest.raises(ValueError, match="family groups differ"):
        suite(tmp_path)


def test_mutating_evidence_during_inference_is_detected(monkeypatch):
    import ragsmith.evaluation.harness as harness
    original = harness.predict

    def mutate(request, evidence):
        predictions = original(request, evidence)
        if evidence:
            evidence[0].metadata = {"changed": True}
        return predictions

    monkeypatch.setattr(harness, "predict", mutate)
    with pytest.raises(ValueError, match="fingerprint/source"):
        suite(FIXTURES)


def test_file_changes_during_inference_are_detected(tmp_path, monkeypatch):
    import ragsmith.evaluation.harness as harness
    copy_fixture(tmp_path)
    original = harness.predict

    def mutate(request, evidence):
        predictions = original(request, evidence)
        (tmp_path / "inputs.jsonl").write_text("changed", encoding="utf-8")
        return predictions

    monkeypatch.setattr(harness, "predict", mutate)
    with pytest.raises(ValueError, match="changed during inference"):
        suite(tmp_path)


def test_fingerprint_is_stable_but_includes_metadata():
    row = FrozenEvidenceRecord.from_payload(read_jsonl(FIXTURES / "evidence.jsonl")[0])
    first = row.evidence[0]
    same = FrozenEvidenceRecord.from_payload(read_jsonl(FIXTURES / "evidence.jsonl")[0]).evidence[0]
    assert evidence_fingerprint(first) == evidence_fingerprint(same)
    same.metadata = {"cells": {"Metric": "Revenue", "2025": "145"}}
    assert evidence_fingerprint(first) != evidence_fingerprint(same)


def test_missing_case_still_needs_a_declared_source_family(tmp_path):
    copy_fixture(tmp_path)
    edit_rows(tmp_path / "gold.jsonl", lambda rows: rows[2].update({"group_id": "invented"}))
    with pytest.raises(ValueError, match="family groups differ"):
        suite(tmp_path)


def test_unlinked_versions_cannot_evade_document_grouping():
    manifest = json.loads((FIXTURES / "lineage.json").read_text(encoding="utf-8"))
    added = dict(manifest["sources"][0])
    added.update({"source_id": "another-version", "document_version": "v2",
                  "group_id": "leaked-test-group"})
    manifest["sources"].append(added)
    with pytest.raises(ValueError, match="Versions of a document"):
        SourceManifest.from_payload(manifest)
