"""Real ingestion-to-answer integration over the existing SQLite FTS index."""

import hashlib
import json
import sqlite3
import sys

import pytest
from openpyxl import Workbook

from ragsmith.cli import main
from ragsmith.core import ingest, search
from ragsmith.lookup_config import LookupConfig
from ragsmith.retrieval import (
    RetrievalConfig, answer_from_database, retrieve_question_evidence,
)
from ragsmith.value_lookup import LookupQuestion, MetricLookup


ENABLED = LookupConfig(True)


def spreadsheet(tmp_path, name="report.xlsx", rows=None):
    path = tmp_path / name
    workbook = Workbook()
    workbook.active.title = "Finance"
    workbook.active.append(["Metric", "2025"])
    for row in rows or [("Revenue", "145"), ("Profit", "30")]:
        workbook.active.append(row)
    workbook.save(path)
    workbook.close()
    return path


def question(*metrics, documents=()):
    return LookupQuestion("q1", "What were these facts in 2025?", tuple(
        MetricLookup(f"r{i}", metric, 2025, documents)
        for i, metric in enumerate(metrics or ("Revenue",))
    ))


def test_full_workflow_preserves_cells_provenance_scores_and_support(tmp_path):
    source = spreadsheet(tmp_path)
    database = tmp_path / "evidence.db"
    record = ingest(source, database)
    request = question("Revenue", "Profit")
    retrieved = retrieve_question_evidence(database, request)
    assert len(retrieved.evidence) == 2  # Overlapping per-requirement hits deduplicate.
    revenue = next(item for item in retrieved.evidence if "Revenue" in item.content)
    assert revenue.metadata == {"cells": {"Metric": "Revenue", "2025": "145"},
                                "headers": ["Metric", "2025"]}
    assert revenue.document_version == record["sha256"]
    assert revenue.locator == "sheet:Finance/row:2"
    assert revenue.table_id == "sheet:Finance"
    assert revenue.row_index == 2
    assert revenue.extraction_method == "openpyxl"
    result = answer_from_database(database, request, ENABLED)
    assert result["assessment"]["answerability"] == "full"
    assert {item["value"] for item in result["answers"]} == {"145", "30"}
    for answer in result["answers"]:
        assert len(answer["citations"]) == 1
        citation = answer["citations"][0]
        assert citation["document_id"] == record["document_id"]
        assert citation["document_version"] == record["sha256"]
        assert citation["locator"].startswith("sheet:Finance/row:")
    for query in result["retrieval"]["queries"]:
        scores = [item["score"] for item in query["hits"]]
        assert scores == sorted(scores)
        assert all(item["source_path"] == str(source.resolve()) for item in query["hits"])
        assert not query["truncated"]
    assert json.loads(json.dumps(result)) == result


def test_partial_then_missing_without_fabricated_answers(tmp_path):
    database = tmp_path / "evidence.db"
    ingest(spreadsheet(tmp_path), database)
    result = answer_from_database(database, question("Revenue", "Employees"), ENABLED)
    assert result["assessment"]["answerability"] == "partial"
    assert [item["status"] for item in result["assessment"]["requirements"]] == [
        "supported", "missing",
    ]
    assert [item["metric"] for item in result["answers"]] == ["Revenue"]
    result = answer_from_database(database, question("Employees"), ENABLED)
    assert result["assessment"]["answerability"] == "abstain"
    assert result["assessment"]["requirements"][0]["status"] == "missing"
    assert result["answers"] == []


def test_conflicts_across_documents_abstain_and_scope_applies_before_limit(tmp_path):
    database = tmp_path / "evidence.db"
    first = ingest(spreadsheet(tmp_path, "first.xlsx", [("Revenue", "145")]), database)
    ingest(spreadsheet(tmp_path, "second.xlsx", [("Revenue", "999")]), database)
    result = answer_from_database(database, question(), ENABLED)
    assert result["assessment"]["requirements"][0]["status"] == "contradicted"
    assert result["assessment"]["answerability"] == "abstain"
    assert result["answers"] == []
    scoped = question(documents=(first["document_id"],))
    result = answer_from_database(database, scoped, ENABLED, RetrievalConfig(1))
    assert result["assessment"]["answerability"] == "full"
    assert result["answers"][0]["value"] == "145"
    assert not result["retrieval"]["queries"][0]["truncated"]
    assert result["retrieval"]["unique_evidence_count"] == 1


def test_truncation_is_explicit_and_tied_results_are_deterministic(tmp_path):
    database = tmp_path / "evidence.db"
    for index in range(3):
        ingest(spreadsheet(tmp_path, f"report{index}.xlsx", [("Revenue", "145")]), database)
    first = retrieve_question_evidence(database, question(), RetrievalConfig(1))
    second = retrieve_question_evidence(database, question(), RetrievalConfig(1))
    assert first == second
    assert first.audit["queries"][0]["truncated"]
    assert len(first.evidence) == 1
    all_rows = retrieve_question_evidence(database, question(), RetrievalConfig(3))
    assert not all_rows.audit["queries"][0]["truncated"]
    ids = [item.evidence_id for item in all_rows.evidence]
    assert ids == sorted(ids)


def test_text_only_evidence_remains_unverified(tmp_path):
    database = tmp_path / "evidence.db"
    path = tmp_path / "report.txt"
    path.write_text("Revenue was 145 in 2025.", encoding="utf-8")
    ingest(path, database)
    result = answer_from_database(database, question(), ENABLED)
    assert result["assessment"]["requirements"][0]["status"] == "unverified"
    assert result["answers"] == []


def test_html_table_works_without_rewriting_evidence(tmp_path):
    database = tmp_path / "evidence.db"
    path = tmp_path / "report.html"
    path.write_text("<table><tr><th>Metric</th><th>2025</th></tr>"
                    "<tr><td>Revenue</td><td>145</td></tr></table>", encoding="utf-8")
    ingest(path, database)
    result = answer_from_database(database, question(), ENABLED)
    assert result["answers"][0]["value"] == "145"
    assert result["answers"][0]["citations"][0]["extraction_method"] == "beautifulsoup"


def test_disabled_lookup_keeps_identical_retrieval(tmp_path):
    database = tmp_path / "evidence.db"
    ingest(spreadsheet(tmp_path), database)
    enabled = answer_from_database(database, question(), ENABLED)
    disabled = answer_from_database(database, question())
    assert enabled["retrieval"] == disabled["retrieval"]
    assert disabled["assessment"]["requirements"][0]["status"] == "unverified"
    assert disabled["answers"] == []


def test_reingestion_does_not_retrieve_obsolete_versions(tmp_path):
    database = tmp_path / "evidence.db"
    path = spreadsheet(tmp_path)
    old = ingest(path, database)
    spreadsheet(tmp_path, rows=[("Revenue", "150")])
    new = ingest(path, database)
    assert old["document_id"] == new["document_id"]
    assert old["sha256"] != new["sha256"]
    result = answer_from_database(database, question(), ENABLED)
    assert result["answers"][0]["value"] == "150"
    assert result["answers"][0]["citations"][0]["document_version"] == new["sha256"]


def test_retrieval_never_creates_or_changes_database(tmp_path):
    missing = tmp_path / "new" / "missing.db"
    with pytest.raises(FileNotFoundError):
        retrieve_question_evidence(missing, question())
    assert not missing.parent.exists()
    database = tmp_path / "evidence.db"
    ingest(spreadsheet(tmp_path), database)
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    answer_from_database(database, question(), ENABLED)
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before


@pytest.mark.parametrize("assignment,value", [
    ("metadata_json", "invalid json"), ("metadata_json", "[]"),
    ("locator", ""), ("document_version", "stale-version"),
])
def test_corrupt_evidence_fails_without_silent_metadata_loss(tmp_path, assignment, value):
    database = tmp_path / "evidence.db"
    ingest(spreadsheet(tmp_path), database)
    with sqlite3.connect(database) as db:
        db.execute(f"UPDATE evidence SET {assignment} = ?", (value,))
    with pytest.raises(ValueError):
        answer_from_database(database, question(), ENABLED)


def test_unknown_document_scope_returns_no_evidence(tmp_path):
    database = tmp_path / "evidence.db"
    ingest(spreadsheet(tmp_path), database)
    result = answer_from_database(database, question(documents=("unknown",)), ENABLED)
    assert result["retrieval"]["unique_evidence_count"] == 0
    assert result["assessment"]["requirements"][0]["status"] == "missing"


@pytest.mark.parametrize("value", [0, 101, True, 1.5, "10"])
def test_invalid_retrieval_budget_rejected(value):
    with pytest.raises(ValueError, match="per_requirement_limit"):
        RetrievalConfig(value)


def test_legacy_search_is_unchanged(tmp_path):
    database = tmp_path / "evidence.db"
    ingest(spreadsheet(tmp_path), database)
    assert len(search(database, "Revenue")) == 1
    assert "metadata" not in search(database, "Revenue")[0]


def test_ask_cli_runs_ingested_document_workflow(tmp_path, monkeypatch, capsys):
    database = tmp_path / "evidence.db"
    ingest(spreadsheet(tmp_path), database)
    request = tmp_path / "request.json"
    request.write_text(json.dumps({
        "question_id": "q1", "question": "What was revenue in 2025?",
        "requirements": [{"requirement_id": "r1", "metric": "Revenue", "year": 2025}],
    }), encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text('{"value_lookup_enabled": true}', encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["ragsmith", "--db", str(database), "ask",
                        str(request), "--lookup-config", str(config), "--top-k", "2"])
    main()
    result = json.loads(capsys.readouterr().out)
    assert result["answers"][0]["value"] == "145"
    assert result["retrieval"]["per_requirement_limit"] == 2


def test_ask_cli_bad_request_exits_cleanly(tmp_path, monkeypatch, capsys):
    path = tmp_path / "bad.json"
    path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["ragsmith", "ask", str(path)])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert "request must contain" in capsys.readouterr().err
