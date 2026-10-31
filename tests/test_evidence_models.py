
import pytest

from ragsmith.evidence.models import Evidence


def make_evidence(**overrides):
    data = {
        "evidence_id": "ev-001",
        "document_id": "doc-001",
        "document_version": "v1",
        "kind": "text",
        "content": "The company reported revenue growth.",
        "locator": "page:1",
        "page_number": 1,
    }
    data.update(overrides)
    return Evidence(**data)


def test_valid_evidence():
    evidence = make_evidence()
    assert evidence.evidence_id == "ev-001"


@pytest.mark.parametrize(
    "field,value",
    [
        ("evidence_id", ""),
        ("document_id", " "),
        ("document_version", ""),
        ("content", ""),
        ("locator", ""),
        ("kind", "unknown"),
        ("page_number", -1),
        ("page_number", 0),
        ("row_index", -1),
        ("metadata", "invalid"),
    ],
)
def test_invalid_evidence(field, value):
    with pytest.raises(ValueError):
        make_evidence(**{field: value})


def test_search_returns_provenance_fields(tmp_path):
    from ragsmith.core import ingest, search

    source = tmp_path / "sample.txt"
    source.write_text(
        "The company reported revenue growth.",
        encoding="utf-8",
    )

    db_path = tmp_path / "test.db"

    ingest(source, db_path)
    results = search(db_path, "revenue")

    assert len(results) > 0

    evidence = results[0]

    assert evidence["document_version"]
    assert len(evidence["document_version"]) == 64
    assert evidence["kind"] == "text"
    assert evidence["locator"]
    assert "page_number" in evidence
    assert "section_path" in evidence
    assert "table_id" in evidence
    assert "row_index" in evidence
    assert "extraction_method" in evidence

from ragsmith.core import ingest, verify_source_integrity


def test_source_integrity_valid(tmp_path):
    source = tmp_path / "document.txt"
    source.write_text("Original document content.", encoding="utf-8")

    db_path = tmp_path / "evidence.db"
    record = ingest(source, db_path)

    result = verify_source_integrity(db_path, record["document_id"])

    assert result["status"] == "valid"
    assert result["expected_hash"] == result["actual_hash"]


def test_source_integrity_modified(tmp_path):
    source = tmp_path / "document.txt"
    source.write_text("Original document content.", encoding="utf-8")

    db_path = tmp_path / "evidence.db"
    record = ingest(source, db_path)

    source.write_text("Modified document content.", encoding="utf-8")

    result = verify_source_integrity(db_path, record["document_id"])

    assert result["status"] == "modified"
    assert result["expected_hash"] != result["actual_hash"]


def test_source_integrity_missing(tmp_path):
    source = tmp_path / "document.txt"
    source.write_text("Original document content.", encoding="utf-8")

    db_path = tmp_path / "evidence.db"
    record = ingest(source, db_path)

    source.unlink()

    result = verify_source_integrity(db_path, record["document_id"])

    assert result["status"] == "missing"


def test_source_integrity_not_found(tmp_path):
    db_path = tmp_path / "evidence.db"

    result = verify_source_integrity(db_path, "unknown-document")

    assert result["status"] == "not_found"

import sqlite3

from ragsmith.core import verify_evidence_consistency


def make_consistency_fixture(tmp_path):
    source = tmp_path / "document.txt"
    source.write_text(
        "The company reported revenue growth.",
        encoding="utf-8",
    )

    db_path = tmp_path / "evidence.db"
    record = ingest(source, db_path)

    db = sqlite3.connect(db_path)
    evidence_id = db.execute(
        "SELECT evidence_id FROM evidence LIMIT 1"
    ).fetchone()[0]
    db.close()

    return db_path, record["document_id"], evidence_id


def test_evidence_consistent(tmp_path):
    db_path, _, evidence_id = make_consistency_fixture(tmp_path)

    result = verify_evidence_consistency(db_path, evidence_id)

    assert result["status"] == "consistent"
    assert result["evidence_version"] == result["document_hash"]


def test_evidence_version_mismatch(tmp_path):
    db_path, _, evidence_id = make_consistency_fixture(tmp_path)

    with sqlite3.connect(db_path) as db:
        db.execute(
            "UPDATE evidence SET document_version = ? WHERE evidence_id = ?",
            ("incorrect-version", evidence_id),
        )

    result = verify_evidence_consistency(db_path, evidence_id)

    assert result["status"] == "version_mismatch"


def test_evidence_document_missing(tmp_path):
    db_path, document_id, evidence_id = make_consistency_fixture(tmp_path)

    with sqlite3.connect(db_path) as db:
        db.execute(
            "DELETE FROM documents WHERE document_id = ?",
            (document_id,),
        )

    result = verify_evidence_consistency(db_path, evidence_id)

    assert result["status"] == "document_missing"


def test_evidence_not_found(tmp_path):
    db_path, _, _ = make_consistency_fixture(tmp_path)

    result = verify_evidence_consistency(db_path, "unknown-evidence")

    assert result["status"] == "not_found"
