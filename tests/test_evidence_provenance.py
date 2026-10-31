
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.provenance import (
    build_evidence_provenance,
)
from ragsmith.sufficiency.pipeline import (
    generate_structured_assessment_report,
)


def make_evidence(evidence_id, row_index=1):
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-001",
        document_version="v1",
        kind="table_row",
        content="Metric: Revenue (million USD); 2025: 145",
        locator=f"table:1/row:{row_index}",
        page_number=3,
        table_id="table-1",
        row_index=row_index,
        extraction_method="pdfplumber",
    )


def test_provenance_contains_source_details():
    evidence = make_evidence("ev-001")
    report = {
        "requirements": [
            {"evidence_ids": ["ev-001"]},
        ],
    }

    result = build_evidence_provenance(report, [evidence])

    assert len(result) == 1
    assert result[0]["evidence_id"] == "ev-001"
    assert result[0]["document_id"] == "doc-001"
    assert result[0]["document_version"] == "v1"
    assert result[0]["page_number"] == 3
    assert result[0]["table_id"] == "table-1"
    assert result[0]["row_index"] == 1
    assert result[0]["extraction_method"] == "pdfplumber"


def test_unreferenced_evidence_is_excluded():
    report = {
        "requirements": [
            {"evidence_ids": ["ev-001"]},
        ],
    }

    result = build_evidence_provenance(
        report,
        [
            make_evidence("ev-001"),
            make_evidence("ev-002", 2),
        ],
    )

    assert [item["evidence_id"] for item in result] == [
        "ev-001"
    ]


def test_repeated_references_produce_one_record():
    report = {
        "requirements": [
            {"evidence_ids": ["ev-001"]},
            {"evidence_ids": ["ev-001"]},
        ],
    }

    result = build_evidence_provenance(
        report,
        [make_evidence("ev-001")],
    )

    assert len(result) == 1


def test_unknown_evidence_id_is_rejected():
    report = {
        "requirements": [
            {"evidence_ids": ["missing-id"]},
        ],
    }

    with pytest.raises(
        ValueError,
        match="Unknown evidence ID",
    ):
        build_evidence_provenance(report, [])


def test_empty_references_produce_empty_provenance():
    report = {
        "requirements": [
            {"evidence_ids": []},
        ],
    }

    assert build_evidence_provenance(report, []) == []


def test_pipeline_includes_evidence_provenance():
    evidence = make_evidence("ev-001")

    report = generate_structured_assessment_report(
        requirements=[
            ("req-001", "Revenue (million USD)", 2025, "145"),
        ],
        evidence_items=[evidence],
    )

    assert "evidence_provenance" in report
    assert any(
        item["evidence_id"] == "ev-001"
        for item in report["evidence_provenance"]
    )
