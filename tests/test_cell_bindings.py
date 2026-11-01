"""Source binding validation and unchanged-verifier integration on synthetic cells."""

import json

import pytest

from ragsmith.evaluation.cell_bindings import canonicalize_decisions, decision_templates
from ragsmith.evaluation.lineage import SourceManifest
from ragsmith.evaluation.records import FrozenEvidenceRecord
from ragsmith.evaluation.tatqa_adapter import REVISION, prepare_screening
from ragsmith.lookup_config import LookupConfig
from ragsmith.lookup_pipeline import assess_lookup_question
from ragsmith.value_lookup import LookupQuestion


@pytest.fixture
def screening():
    context = {"table": {"uid": "ctx", "table": [
        ["USD million", "2025"], ["Revenue", " 145.00 "], ["Profit", "30"]]},
        "paragraphs": [], "questions": [
            {"uid": "q1", "question": "Revenue in 2025?", "answer_type": "span", "answer_from": "table",
             "answer": ["GOLD-SENTINEL"], "scale": "million", "req_comparison": False},
            {"uid": "q2", "question": "Profit in 2025?", "answer_type": "span", "answer_from": "table",
             "answer": ["ANOTHER-SENTINEL"], "scale": "million", "req_comparison": False}]}
    return prepare_screening([context], {"revision": REVISION, "split": "train", "sha256": "a" * 64,
                                        "url": "fixture://synthetic-table"})


def accepted(screening, index=0):
    row = decision_templates(screening)[index]
    r = index + 1
    row.update(decision="accept", reviewer_id="synthetic-author", notes="Synthetic explicit source cells.",
               binding={"metric_cell_locator": f"table:ctx/row:{r}/column:0",
                        "year_cell_locator": "table:ctx/row:0/column:1",
                        "unit_cell_locator": "table:ctx/row:0/column:0",
                        "value_cell_locator": f"table:ctx/row:{r}/column:1"})
    return row


def test_templates_pending_and_empty_compilation_creates_no_gold(screening):
    templates = decision_templates(screening)
    result = canonicalize_decisions(screening, templates)
    assert all(row["decision"] == "pending" and row["binding"] is None for row in templates)
    assert result["summary"]["pending_questions"] == 2
    assert result["inputs"] == result["evidence"] == []
    assert result["summary"]["gold_generated"] is False


def test_accepted_source_value_flows_through_original_verifier(screening):
    result = canonicalize_decisions(screening, [accepted(screening), accepted(screening, 1)])
    manifest = SourceManifest.from_payload(result["lineage"])
    assert len(manifest.sources) == 2
    assert {row.transformation for row in manifest.sources} == {"original", "canonicalization"}
    assert "GOLD-SENTINEL" not in json.dumps(result)
    for raw_request, raw_evidence in zip(result["inputs"], result["evidence"]):
        request = LookupQuestion.from_payload(raw_request)
        evidence = list(FrozenEvidenceRecord.from_payload(raw_evidence).evidence)
        manifest.validate_evidence(evidence)
        assessment = assess_lookup_question(request, evidence, LookupConfig(value_lookup_enabled=True))
        assert assessment["assessment"]["answerability"] == "full"
    assert result["evidence"][0]["evidence"][0]["metadata"]["unit"] == "USD million"
    assert any(item["content"] == "Metric: Revenue; 2025: 145.00" for item in result["evidence"][0]["evidence"])
    assert result["summary"]["pilot_selected"] is False


def test_compilation_order_deterministic(screening):
    decisions = [accepted(screening), accepted(screening, 1)]
    first = canonicalize_decisions(screening, decisions)
    second = canonicalize_decisions(screening, list(reversed(decisions)))
    for key in ("inputs", "evidence", "lineage", "transformations", "summary"):
        assert first[key] == second[key]


@pytest.mark.parametrize("mutation", [
    {"source_content_sha256": "b" * 64}, {"question_sha256": "b" * 64},
    {"annotation_status": "reviewed"}, {"reviewer_id": ""}, {"notes": ""},
    {"decision": "guessed"}, {"rejection_reasons": ["unexpected"]}, {"expected_value": "145"},
])
def test_bad_decisions_fail_closed(screening, mutation):
    decision = accepted(screening)
    decision.update(mutation)
    with pytest.raises(ValueError):
        canonicalize_decisions(screening, [decision])


@pytest.mark.parametrize("key,value", [
    ("value_cell_locator", "table:other/row:1/column:1"),
    ("metric_cell_locator", "table:ctx/row:2/column:0"),
    ("year_cell_locator", "table:ctx/row:0/column:0"),
    ("unit_cell_locator", "table:ctx/row:1/column:0"),
])
def test_bad_cell_bindings_fail_closed(screening, key, value):
    decision = accepted(screening)
    decision["binding"][key] = value
    with pytest.raises(ValueError):
        canonicalize_decisions(screening, [decision])


def test_duplicate_and_unknown_decisions_rejected(screening):
    decision = accepted(screening)
    with pytest.raises(ValueError, match="Duplicate"):
        canonicalize_decisions(screening, [decision, decision])
    decision["question_id"] = "unknown"
    with pytest.raises(ValueError, match="unknown"):
        canonicalize_decisions(screening, [decision])


def test_rejected_decisions_need_reason_and_never_emit_evidence(screening):
    decision = decision_templates(screening)[0]
    decision.update(decision="reject", reviewer_id="synthetic-author", notes="Ambiguous source year.")
    with pytest.raises(ValueError, match="rejection reasons"):
        canonicalize_decisions(screening, [decision])
    decision["rejection_reasons"] = ["ambiguous_year"]
    result = canonicalize_decisions(screening, [decision])
    assert result["summary"]["rejected_questions"] == 1
    assert result["summary"]["pending_questions"] == 1
    assert not result["evidence"]


def test_source_mutation_after_screening_detected(screening):
    decision = accepted(screening)
    screening["sources"][0]["table_cells"][3]["text"] = "999"
    with pytest.raises(ValueError, match="Source content hash"):
        canonicalize_decisions(screening, [decision])


def test_source_answers_not_used_to_construct_candidates(screening):
    decisions = [accepted(screening)]
    first = canonicalize_decisions(screening, decisions)
    screening["coordinator_annotation_aids"][0]["upstream_answer"] = ["999"]
    assert canonicalize_decisions(screening, decisions) == first


def test_unknown_binding_fields_rejected(screening):
    decision = accepted(screening)
    decision["binding"]["value"] = "999"
    with pytest.raises(ValueError, match="cell binding"):
        canonicalize_decisions(screening, [decision])


def test_pending_cannot_hide_binding(screening):
    decision = accepted(screening)
    decision["decision"] = "pending"
    with pytest.raises(ValueError, match="Only accepted"):
        canonicalize_decisions(screening, [decision])


def test_same_metric_year_inconsistent_units_rejected(screening):
    # Regenerate a real-shaped source so all source hashes remain valid.
    from ragsmith.evaluation.tatqa_adapter import digest

    source = screening["sources"][0]
    source["table_cells"][4]["text"] = "Revenue"
    # Unit above both values: put another explicit unit in a new column of header.
    source["table_cells"] = source["table_cells"][:6] + [
        {"row": 0, "column": 2, "text": "EUR million", "locator": "table:ctx/row:0/column:2"}]
    source["table_shape"] = [3, 2, 2]
    source["source_content_sha256"] = digest({key: source[key] for key in ("context_id", "table_cells", "table_shape", "paragraphs")})
    a, b = accepted(screening), accepted(screening, 1)
    b["binding"]["unit_cell_locator"] = "table:ctx/row:0/column:2"
    with pytest.raises(ValueError, match="inconsistent bound units"):
        canonicalize_decisions(screening, [a, b])


@pytest.mark.parametrize("index,text", [(2, "Revenue; Profit"), (1, "Year 2025"), (3, "145\n999")])
def test_unsupported_cell_format_not_silently_rewritten(screening, index, text):
    from ragsmith.evaluation.tatqa_adapter import digest

    source = screening["sources"][0]
    source["table_cells"][index]["text"] = text
    source["source_content_sha256"] = digest({key: source[key] for key in ("context_id", "table_cells", "table_shape", "paragraphs")})
    with pytest.raises(ValueError):
        canonicalize_decisions(screening, [accepted(screening)])


def test_label_gate_cannot_be_overridden(screening):
    screening["screening_ledger"][0]["label_gate"] = "exclude"
    decision = decision_templates(screening)[0]
    decision["question_id"] = "q1"
    with pytest.raises(ValueError, match="label gate"):
        canonicalize_decisions(screening, [decision])


def test_conflicting_bound_cells_reach_existing_contradiction_policy(screening):
    from ragsmith.evaluation.tatqa_adapter import digest

    source = screening["sources"][0]
    source["table_cells"][4]["text"] = "Revenue"
    source["source_content_sha256"] = digest({key: source[key] for key in ("context_id", "table_cells", "table_shape", "paragraphs")})
    result = canonicalize_decisions(screening, [accepted(screening), accepted(screening, 1)])
    request = LookupQuestion.from_payload(result["inputs"][0])
    evidence = list(FrozenEvidenceRecord.from_payload(result["evidence"][0]).evidence)
    response = assess_lookup_question(request, evidence, LookupConfig(value_lookup_enabled=True))
    assert response["assessment"]["answerability"] == "abstain"
    assert response["answers"] == []
