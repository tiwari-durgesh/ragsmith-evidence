
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.quality_summary import (
    build_quality_summary,
)
from ragsmith.sufficiency.pipeline import (
    generate_structured_assessment_report,
)


def make_record(evidence_id, score, level):
    return {
        "evidence_id": evidence_id,
        "completeness_score": score,
        "completeness_level": level,
    }


def test_empty_quality_summary():
    result = build_quality_summary({
        "evidence_quality": [],
    })

    assert result["total_evidence"] == 0
    assert result["average_completeness"] is None
    assert result["incomplete_evidence_ids"] == []
    assert result["quality_distribution"] == {
        "high": 0,
        "medium": 0,
        "low": 0,
    }


def test_single_complete_evidence():
    report = {
        "evidence_quality": [
            make_record("ev-001", 1.0, "high"),
        ],
    }

    result = build_quality_summary(report)

    assert result["average_completeness"] == 1.0
    assert result["quality_distribution"]["high"] == 1
    assert result["incomplete_evidence_ids"] == []


def test_multiple_quality_levels():
    report = {
        "evidence_quality": [
            make_record("ev-001", 1.0, "high"),
            make_record("ev-002", 0.5, "medium"),
            make_record("ev-003", 0.0, "low"),
        ],
    }

    result = build_quality_summary(report)

    assert result["total_evidence"] == 3
    assert result["average_completeness"] == 0.5
    assert result["quality_distribution"] == {
        "high": 1,
        "medium": 1,
        "low": 1,
    }
    assert result["incomplete_evidence_ids"] == [
        "ev-002",
        "ev-003",
    ]


def test_duplicate_quality_records_rejected():
    report = {
        "evidence_quality": [
            make_record("ev-001", 1.0, "high"),
            make_record("ev-001", 0.5, "medium"),
        ],
    }

    with pytest.raises(
        ValueError,
        match="Duplicate evidence quality records",
    ):
        build_quality_summary(report)


def test_pipeline_includes_quality_summary():
    evidence = Evidence(
        evidence_id="ev-001",
        document_id="doc-001",
        document_version="v1",
        kind="table_row",
        content="Metric: Revenue (million USD); 2025: 145",
        locator="table:1/row:1",
        page_number=3,
    )

    report = generate_structured_assessment_report(
        requirements=[
            ("req-001", "Revenue (million USD)", 2025, "145"),
        ],
        evidence_items=[evidence],
    )

    assert "quality_summary" in report
    assert report["quality_summary"]["total_evidence"] == 1
    assert report["quality_summary"]["average_completeness"] == 0.25
    assert report["quality_summary"]["incomplete_evidence_ids"] == [
        "ev-001"
    ]
