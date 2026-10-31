
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.requirement_quality import (
    build_requirement_quality_report,
)
from ragsmith.sufficiency.pipeline import (
    generate_structured_assessment_report,
)


def make_evidence(evidence_id, **kwargs):
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-001",
        document_version="v1",
        kind="table_row",
        content="Metric: Revenue (million USD); 2025: 145",
        locator="table:1/row:1",
        **kwargs,
    )


def make_report(requirements):
    return {"requirements": requirements}


def test_requirement_with_no_evidence():
    report = make_report([
        {"requirement_id": "req-001", "evidence_ids": []},
    ])

    result = build_requirement_quality_report(report, [])

    assert result[0]["evidence_count"] == 0
    assert result[0]["average_completeness"] is None
    assert result[0]["weakest_evidence_ids"] == []


def test_requirement_with_one_evidence():
    report = make_report([
        {"requirement_id": "req-001", "evidence_ids": ["ev-001"]},
    ])

    result = build_requirement_quality_report(
        report,
        [make_evidence("ev-001", page_number=2)],
    )

    assert result[0]["average_completeness"] == 0.25
    assert result[0]["lowest_completeness"] == 0.25
    assert result[0]["weakest_evidence_ids"] == ["ev-001"]


def test_requirement_with_multiple_evidence():
    report = make_report([
        {
            "requirement_id": "req-001",
            "evidence_ids": ["ev-001", "ev-002"],
        },
    ])

    evidence = [
        make_evidence("ev-001", page_number=2),
        make_evidence(
            "ev-002",
            page_number=2,
            table_id="table-1",
            row_index=1,
            extraction_method="pdfplumber",
        ),
    ]

    result = build_requirement_quality_report(report, evidence)

    assert result[0]["average_completeness"] == 0.62
    assert result[0]["lowest_completeness"] == 0.25
    assert result[0]["weakest_evidence_ids"] == ["ev-001"]


def test_duplicate_references_count_once():
    report = make_report([
        {
            "requirement_id": "req-001",
            "evidence_ids": ["ev-001", "ev-001"],
        },
    ])

    result = build_requirement_quality_report(
        report,
        [make_evidence("ev-001")],
    )

    assert result[0]["evidence_count"] == 1


def test_unknown_evidence_rejected():
    report = make_report([
        {"requirement_id": "req-001", "evidence_ids": ["missing"]},
    ])

    with pytest.raises(
        ValueError,
        match="Unknown evidence ID",
    ):
        build_requirement_quality_report(report, [])


def test_multiple_requirements_are_independent():
    report = make_report([
        {"requirement_id": "req-001", "evidence_ids": ["ev-001"]},
        {"requirement_id": "req-002", "evidence_ids": []},
    ])

    result = build_requirement_quality_report(
        report,
        [make_evidence("ev-001", page_number=2)],
    )

    assert len(result) == 2
    assert result[0]["evidence_count"] == 1
    assert result[1]["evidence_count"] == 0


def test_pipeline_includes_requirement_quality():
    evidence = make_evidence(
        "ev-001",
        page_number=2,
    )

    report = generate_structured_assessment_report(
        requirements=[
            ("req-001", "Revenue (million USD)", 2025, "145"),
        ],
        evidence_items=[evidence],
    )

    assert "requirement_quality" in report
    assert report["requirement_quality"][0]["requirement_id"] == "req-001"
    assert report["requirement_quality"][0]["average_completeness"] == 0.25
