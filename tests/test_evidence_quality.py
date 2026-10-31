
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.evidence_quality import (
    score_evidence_quality,
    build_evidence_quality_report,
)
from ragsmith.sufficiency.pipeline import (
    generate_structured_assessment_report,
)


def make_evidence(evidence_id="ev-001", **kwargs):
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-001",
        document_version="v1",
        kind="table_row",
        content="Metric: Revenue (million USD); 2025: 145",
        locator="table:1/row:1",
        **kwargs,
    )


def test_low_completeness():
    result = score_evidence_quality(make_evidence())
    assert result["completeness_score"] == 0
    assert result["completeness_level"] == "low"


def test_medium_completeness():
    evidence = make_evidence(
        page_number=3,
        table_id="table-1",
    )
    result = score_evidence_quality(evidence)

    assert result["completeness_score"] == 0.5
    assert result["completeness_level"] == "medium"


def test_high_completeness():
    evidence = make_evidence(
        page_number=3,
        section_path="Financial Results",
        table_id="table-1",
        row_index=1,
        extraction_method="pdfplumber",
    )
    result = score_evidence_quality(evidence)

    assert result["completeness_score"] == 1.0
    assert result["completeness_level"] == "high"


def test_zero_row_index_counts_as_present():
    evidence = make_evidence(row_index=0)
    result = score_evidence_quality(evidence)

    assert result["present_fields"] == 1


def test_unused_evidence_excluded():
    report = {
        "requirements": [
            {"evidence_ids": ["ev-001"]},
        ],
    }

    result = build_evidence_quality_report(
        report,
        [
            make_evidence("ev-001"),
            make_evidence("ev-002"),
        ],
    )

    assert len(result) == 1
    assert result[0]["evidence_id"] == "ev-001"


def test_duplicate_references_scored_once():
    report = {
        "requirements": [
            {"evidence_ids": ["ev-001", "ev-001"]},
        ],
    }

    result = build_evidence_quality_report(
        report,
        [make_evidence("ev-001")],
    )

    assert len(result) == 1


def test_unknown_evidence_rejected():
    report = {
        "requirements": [
            {"evidence_ids": ["missing"]},
        ],
    }

    with pytest.raises(
        ValueError,
        match="Unknown evidence ID",
    ):
        build_evidence_quality_report(report, [])


def test_pipeline_includes_quality_report():
    evidence = make_evidence(
        page_number=3,
        table_id="table-1",
    )

    report = generate_structured_assessment_report(
        requirements=[
            ("req-001", "Revenue (million USD)", 2025, "145"),
        ],
        evidence_items=[evidence],
    )

    assert "evidence_quality" in report
    assert report["evidence_quality"][0]["completeness_score"] == 0.5

def test_text_quality_uses_text_fields():
    evidence = make_evidence(
        page_number=2,
        section_path="Introduction",
        extraction_method="pypdf",
    )
    evidence.kind = "text"

    result = score_evidence_quality(evidence)

    assert result["completeness_score"] == 1.0
    assert result["total_fields"] == 3
    assert result["missing_fields"] == []


def test_table_row_quality_reports_missing_fields():
    evidence = make_evidence(page_number=3)

    result = score_evidence_quality(evidence)

    assert result["completeness_score"] == 0.25
    assert result["completeness_level"] == "low"
    assert set(result["missing_fields"]) == {
        "table_id",
        "row_index",
        "extraction_method",
    }


def test_table_quality_uses_table_fields():
    evidence = make_evidence(
        page_number=4,
        table_id="table-1",
        extraction_method="pdfplumber",
    )
    evidence.kind = "table"

    result = score_evidence_quality(evidence)

    assert result["completeness_score"] == 1.0
    assert result["total_fields"] == 3


def test_graph_quality_uses_graph_fields():
    evidence = make_evidence(
        page_number=5,
        section_path="Results",
    )
    evidence.kind = "graph"

    result = score_evidence_quality(evidence)

    assert result["completeness_score"] == 0.67
    assert result["completeness_level"] == "medium"
    assert result["missing_fields"] == ["extraction_method"]


def test_row_index_zero_counts_as_present():
    evidence = make_evidence(
        page_number=2,
        table_id="table-1",
        row_index=0,
        extraction_method="pdfplumber",
    )

    result = score_evidence_quality(evidence)

    assert result["completeness_score"] == 1.0
    assert result["missing_fields"] == []
