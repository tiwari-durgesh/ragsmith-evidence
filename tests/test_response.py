"""Evidence-bounded presentation and complete ingestion-to-response behavior."""

import copy
import json
import sys

import pytest

from ragsmith.cli import main
from ragsmith.core import ingest
from ragsmith.evidence.models import Evidence
from ragsmith.lookup_config import LookupConfig
from ragsmith.lookup_pipeline import assess_lookup_question
from ragsmith.response import render_lookup_response
from ragsmith.retrieval import RetrievalConfig, answer_from_database
from ragsmith.value_lookup import LookupQuestion, MetricLookup


def row(eid="revenue", metric="Revenue", value="145", kind="table_row"):
    return Evidence(eid, f"doc-{eid}", "v1", kind,
                    f"Metric: {metric}; 2025: {value}", "table:1/row:2",
                    page_number=4, table_id="table:1", row_index=2)


def lookup(items, metrics=("Revenue",), enabled=True):
    question = LookupQuestion("q1", "What were these facts in 2025?", tuple(
        MetricLookup(f"r{i}", metric, 2025) for i, metric in enumerate(metrics)
    ))
    return assess_lookup_question(question, items, LookupConfig(enabled))


def test_full_response_contains_supported_facts_and_traceable_sources():
    result = lookup([row(), row("profit", "Profit", "30")], ("Revenue", "Profit"))
    original = copy.deepcopy(result)
    response = render_lookup_response(result)
    assert response["answerability"] == "full"
    assert "Revenue in 2025: 145. [1]" in response["text"]
    assert "Profit in 2025: 30. [2]" in response["text"]
    assert "[1] doc-revenue; table:1/row:2; page 4" in response["text"]
    assert response["citations"][0]["document_version"] == "v1"
    assert response["unsupported_requirements"] == []
    assert response["warnings"] == []
    assert json.loads(json.dumps(response)) == response
    assert result == original


def test_partial_response_explains_missing_without_displaying_candidates():
    result = lookup([row()], ("Revenue", "Employees"))
    result["discovery"][1]["candidates"] = [{"value": "98765", "evidence_ids": []}]
    response = render_lookup_response(result)
    assert "Revenue in 2025: 145. [1]" in response["text"]
    assert "Employees in 2025: no matching value" in response["text"]
    assert "98765" not in response["text"]
    assert response["unsupported_requirements"][0]["status"] == "missing"
    assert len(response["citations"]) == 1


def test_unverified_is_not_claimed_as_missing_from_documents():
    response = render_lookup_response(lookup([row(kind="text")]))
    assert response["answerability"] == "abstain"
    assert "could not be verified using the supported evidence formats" in response["text"]
    assert "145" not in response["text"]
    assert "no matching value" not in response["text"]
    assert response["citations"] == []


def test_conflict_suppresses_even_other_supported_values_and_stale_answers():
    result = lookup([row(), row("conflict", value="150"), row("profit", "Profit", "30")],
                    ("Revenue", "Profit"))
    result["answers"] = [{"requirement_id": "r1", "value": "99999"}]
    response = render_lookup_response(result)
    assert response["answerability"] == "abstain"
    assert "conflicting evidence" in response["text"]
    assert "99999" not in response["text"]
    assert "145" not in response["text"]
    assert "150" not in response["text"]
    assert "Profit in 2025: 30" not in response["text"]
    assert response["citations"] == []
    assert "Sources:" not in response["text"]


def test_disabled_lookup_explains_abstention_without_implying_corpus_absence():
    response = render_lookup_response(lookup([row()], enabled=False))
    assert "Value lookup is disabled" in response["text"]
    assert "not checked" in response["text"]
    assert "no matching value" not in response["text"]
    assert "145" not in response["text"]


def test_missing_all_requirements_abstains_with_explicit_gaps():
    response = render_lookup_response(lookup([], ("Revenue", "Employees")))
    assert response["answerability"] == "abstain"
    assert len(response["unsupported_requirements"]) == 2
    assert response["text"].count("no matching value") == 2


def test_repeated_source_uses_one_number_and_one_source_record():
    response = render_lookup_response(lookup([row()], ("Revenue", "Revenue")))
    assert response["text"].count("145. [1]") == 2
    assert len(response["citations"]) == 1
    assert response["text"].count("[1] doc-revenue;") == 1


def test_irrelevant_examined_evidence_never_becomes_a_rendered_source():
    response = render_lookup_response(lookup([row(), row("irrelevant", "Assets", "500")]))
    assert len(response["citations"]) == 1
    assert "irrelevant" not in response["text"]
    assert "500" not in response["text"]


@pytest.mark.parametrize("case", ["no_citations", "wrong_locator", "unknown_evidence",
                                  "wrong_metric", "empty_value", "omitted_answer",
                                  "duplicate_answer", "wrong_decision"])
def test_inconsistent_presentation_contract_fails_closed(case):
    result = lookup([row()])
    answer = result["answers"][0]
    if case == "no_citations":
        answer["citations"] = []
    elif case == "wrong_locator":
        answer["citations"][0]["locator"] = "page:999"
    elif case == "unknown_evidence":
        answer["citations"][0]["evidence_id"] = "invented"
    elif case == "wrong_metric":
        answer["metric"] = "Employees"
    elif case == "empty_value":
        answer["value"] = " "
    elif case == "omitted_answer":
        result["answers"] = []
    elif case == "duplicate_answer":
        result["answers"].append(copy.deepcopy(answer))
    else:
        result["assessment"]["answerability"] = "abstain"
    with pytest.raises(ValueError):
        render_lookup_response(result)


def test_source_derived_newlines_are_plain_text_not_extra_statements():
    response = render_lookup_response(lookup([row(value="145\nUSD")]))
    assert "Revenue in 2025: 145 USD. [1]" in response["text"]


def html_document(tmp_path, name="report.html", value="145"):
    path = tmp_path / name
    path.write_text(
        "<table><tr><th>Metric</th><th>2025</th></tr>"
        f"<tr><td>Revenue</td><td>{value}</td></tr></table>", encoding="utf-8",
    )
    return path


def test_database_response_resolves_actual_source_path(tmp_path):
    source = html_document(tmp_path)
    db = tmp_path / "evidence.db"
    record = ingest(source, db)
    request = LookupQuestion("q1", "Revenue?", (MetricLookup("r1", "Revenue", 2025),))
    result = answer_from_database(db, request, LookupConfig(True))
    response = result["response"]
    assert "Based on the retrieved evidence" in response["text"]
    assert str(source.resolve()) in response["text"]
    assert response["citations"][0]["source_path"] == str(source.resolve())
    assert response["citations"][0]["document_version"] == record["sha256"]
    assert result["answers"][0]["citations"][0].get("source_path") is None


def test_truncated_retrieval_reports_risk_without_changing_existing_policy(tmp_path):
    db = tmp_path / "evidence.db"
    ingest(html_document(tmp_path, "first.html", "145"), db)
    ingest(html_document(tmp_path, "second.html", "150"), db)
    request = LookupQuestion("q1", "Revenue?", (MetricLookup("r1", "Revenue", 2025),))
    limited = answer_from_database(db, request, LookupConfig(True), RetrievalConfig(1))
    assert limited["assessment"]["answerability"] == "full"
    assert "Retrieval was truncated" in limited["response"]["text"]
    complete = answer_from_database(db, request, LookupConfig(True), RetrievalConfig(2))
    assert complete["assessment"]["answerability"] == "abstain"
    assert complete["response"]["citations"] == []
    assert "conflicting evidence" in complete["response"]["text"]
    assert complete["response"]["warnings"] == []


@pytest.mark.parametrize("enabled", [True, False])
def test_text_cli_runs_complete_workflow(tmp_path, monkeypatch, capsys, enabled):
    db = tmp_path / "evidence.db"
    ingest(html_document(tmp_path), db)
    request = tmp_path / "request.json"
    request.write_text(json.dumps({
        "question_id": "q1", "question": "Revenue?",
        "requirements": [{"requirement_id": "r1", "metric": "Revenue", "year": 2025}],
    }), encoding="utf-8")
    config = tmp_path / "lookup.json"
    config.write_text(json.dumps({"value_lookup_enabled": enabled}), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["ragsmith", "--db", str(db), "ask", str(request),
                        "--lookup-config", str(config), "--format", "text"])
    main()
    text = capsys.readouterr().out
    if enabled:
        assert "Revenue in 2025: 145. [1]" in text
        assert "Sources:" in text
    else:
        assert "Value lookup is disabled" in text
        assert "145" not in text


def test_renderer_rejects_assertion_report_mode():
    with pytest.raises(ValueError, match="value_lookup"):
        render_lookup_response({"mode": "assertion_verification"})
