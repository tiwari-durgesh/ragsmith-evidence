"""Preparation never reads gold; native retrieval and masking stay auditable."""

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

import pytest

from ragsmith.evaluation.preparation import (
    calibration_packets, export_rankings, load_bundle, write_new_bundle,
)
from ragsmith.evaluation.records import evidence_fingerprint, read_jsonl
from ragsmith.evaluation.retrieval_metrics import RankingRecord
from ragsmith.evidence.models import Evidence


FIXTURES = Path(__file__).resolve().parents[1] / "data/evaluation/fixtures"


def paths(directory=FIXTURES):
    return tuple(directory / name for name in ("inputs.jsonl", "evidence.jsonl", "lineage.json"))


def test_masked_packet_no_gold_or_condition_identifiers():
    result = calibration_packets(*paths())
    encoded = json.dumps(result["packet"])
    assert "synthetic-partial" not in encoded
    assert "ev-conflict" not in encoded
    assert "synthetic_conflict" not in encoded
    assert "acceptable_values" not in encoded
    assert len(result["packet"]["items"]) == 6
    assert result == calibration_packets(*paths())
    assert all(row["label"] == "" for rows in result["templates"].values() for row in rows)
    assert {row["question_id"] for row in result["coordinator_only"]["mapping"]} == {
        row["question_id"] for row in read_jsonl(FIXTURES / "inputs.jsonl")}


def test_packet_maps_every_requirement_scope_and_evidence():
    result = calibration_packets(*paths())
    _, universe, _, _ = load_bundle(*paths())
    for item, mapping in zip(result["packet"]["items"], result["coordinator_only"]["mapping"]):
        assert {row["evidence_id"] for row in item["evidence"]} == set(mapping["evidence_ids"].values())
        original = {row.evidence_id: row for row in universe[mapping["question_id"]]}
        visible = {row["evidence_id"]: row for row in item["evidence"]}
        for eid, masked in mapping["evidence_ids"].items():
            assert visible[masked]["content"] == original[eid].content
            assert visible[masked]["locator"] == original[eid].locator


@pytest.mark.parametrize("annotators", [("a", "a"), ("", "b"), ("a",)])
def test_invalid_authors(annotators):
    with pytest.raises(ValueError):
        calibration_packets(*paths(), annotators=annotators)


def test_gold_absent_during_preparation(tmp_path):
    for source in paths():
        (tmp_path / source.name).write_bytes(source.read_bytes())
    assert not (tmp_path / "gold.jsonl").exists()
    assert calibration_packets(*paths(tmp_path))["coordinator_only"]["gold_read"] is False


def test_writer_preserves_existing_annotations(tmp_path):
    output = tmp_path / "review"
    write_new_bundle(output, {"labels.jsonl": [{"label": "full"}]})
    with pytest.raises(FileExistsError):
        write_new_bundle(output, {"labels.jsonl": []})
    assert read_jsonl(output / "labels.jsonl") == [{"label": "full"}]


def test_writer_rejects_escape_and_nonfinite_before_creation(tmp_path):
    with pytest.raises(ValueError):
        write_new_bundle(tmp_path / "bad", {"../escape.json": {}})
    with pytest.raises(ValueError):
        write_new_bundle(tmp_path / "bad", {"values.json": {"value": float("nan")}})
    assert not (tmp_path / "bad").exists()


@pytest.fixture
def native_bundle(tmp_path):
    """A real SQLite FTS index and independently registered synthetic universe."""
    db_path = tmp_path / "native.sqlite"
    item = Evidence("ev1", "doc1", "a" * 64, "table_row", "Metric: Revenue; 2025: 145", "table1:row1", metadata={})
    db = sqlite3.connect(db_path)
    db.executescript('''CREATE TABLE documents(document_id TEXT, source_path TEXT, sha256 TEXT);
        CREATE TABLE evidence(evidence_id TEXT, document_id TEXT, document_version TEXT,
        kind TEXT, content TEXT, locator TEXT, page_number INTEGER, section_path TEXT,
        table_id TEXT, row_index INTEGER, extraction_method TEXT, metadata_json TEXT);
        CREATE VIRTUAL TABLE evidence_fts USING fts5(evidence_id UNINDEXED, content);''')
    db.execute("INSERT INTO documents VALUES (?, ?, ?)", (item.document_id, "synthetic.txt", item.document_version))
    db.execute("INSERT INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (item.evidence_id, item.document_id, item.document_version, item.kind,
                item.content, item.locator, None, None, None, None, "", "{}"))
    db.execute("INSERT INTO evidence_fts VALUES (?, ?)", (item.evidence_id, item.content))
    db.commit()
    db.close()
    request = {"question_id": "q", "question": "Revenue?", "requirements": [
        {"requirement_id": "r", "metric": "Revenue", "year": 2025, "document_ids": ["doc1"]}]}
    write_new_bundle(tmp_path / "bundle", {
        "inputs.jsonl": [request], "evidence.jsonl": [{"question_id": "q", "evidence": [asdict(item)]}],
        "lineage.json": {"schema_version": "1.0", "sources": [{
            "source_id": "s", "document_id": "doc1", "document_version": item.document_version,
            "group_id": "g", "source_uri": "fixture://native", "source_sha256": "b" * 64,
            "license": "synthetic", "parent_source_ids": [], "transformation": "original"}],
            "evidence_links": [{"evidence_id": "ev1", "source_id": "s", "fingerprint": evidence_fingerprint(item)}]}})
    return db_path, tmp_path / "bundle"


def test_native_export_rankings_compatible_and_database_unchanged(native_bundle):
    db, directory = native_bundle
    before = db.read_bytes()
    result = export_rankings(db, *paths(directory), limit=1)
    assert db.read_bytes() == before
    assert result["rankings"][0]["rankings"][0]["evidence_ids"] == ["ev1"]
    assert len(result["database_snapshot_sha256"]) == 64
    assert result["audit"][0]["queries"][0]["hits"][0]["rank"] == 1
    requests, universe, _, _ = load_bundle(*paths(directory))
    assert RankingRecord.from_payload(result["rankings"][0]).select(requests["q"], universe["q"], 1)


def test_native_export_rejects_changed_source(native_bundle):
    db, directory = native_bundle
    with sqlite3.connect(db) as connection:
        connection.execute("UPDATE evidence SET content='Metric: Revenue; 2025: 999'")
    with pytest.raises(ValueError, match="fingerprint"):
        export_rankings(db, *paths(directory))


def test_native_export_rejects_hit_missing_from_universe(native_bundle):
    db, directory = native_bundle
    (directory / "evidence.jsonl").write_text('{"question_id":"q","evidence":[]}\n')
    with pytest.raises(ValueError, match="declared universe"):
        export_rankings(db, *paths(directory))


def test_snapshot_is_stable_if_live_database_changes(native_bundle, monkeypatch):
    from ragsmith.evaluation import preparation

    db, directory = native_bundle
    real_retrieve = preparation.retrieve_question_evidence

    def change_live_then_read_snapshot(snapshot, request, config):
        with sqlite3.connect(db) as connection:
            connection.execute("DELETE FROM evidence_fts")
        return real_retrieve(snapshot, request, config)

    monkeypatch.setattr(preparation, "retrieve_question_evidence", change_live_then_read_snapshot)
    result = export_rankings(db, *paths(directory))
    assert result["rankings"][0]["rankings"][0]["evidence_ids"] == ["ev1"]


def test_native_export_empty_rankings_are_retained(native_bundle):
    db, directory = native_bundle
    with sqlite3.connect(db) as connection:
        connection.execute("DELETE FROM evidence_fts")
    result = export_rankings(db, *paths(directory))
    assert result["rankings"][0]["rankings"][0]["evidence_ids"] == []
    assert result["audit"][0]["unique_evidence_count"] == 0


@pytest.mark.parametrize("limit", [0, 101, True])
def test_invalid_export_budget(native_bundle, limit):
    db, directory = native_bundle
    with pytest.raises(ValueError):
        export_rankings(db, *paths(directory), limit=limit)
