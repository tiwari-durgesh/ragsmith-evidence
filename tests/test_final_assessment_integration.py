
import json

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.pipeline import (
    generate_structured_assessment_report,
)


def make_evidence(evidence_id, metric, value, row_index):
    return Evidence(
        evidence_id=evidence_id,
        document_id="annual-report-2025",
        document_version="v1",
        kind="table_row",
        content=f"Metric: {metric}; 2025: {value}",
        locator=f"table:1/row:{row_index}",
        page_number=4,
        table_id="table-1",
        row_index=row_index,
        extraction_method="pdfplumber",
    )


def test_complete_supported_report():
    evidence = make_evidence(
        "ev-001",
        "Revenue (million USD)",
        "145",
        1,
    )

    report = generate_structured_assessment_report(
        requirements=[
            ("req-001", "Revenue (million USD)", 2025, "145"),
        ],
        evidence_items=[evidence],
    )

    assert report["answerability"] == "full"
    assert report["coverage"] == 1.0
    assert report["requirements"][0]["status"] == "supported"

    assert report["evidence_provenance"][0]["document_id"] == (
        "annual-report-2025"
    )
    assert report["evidence_provenance"][0]["row_index"] == 1

    assert report["evidence_quality"][0]["completeness_score"] == 1.0
    assert report["requirement_quality"][0]["average_completeness"] == 1.0
    assert report["quality_summary"]["average_completeness"] == 1.0

    json.dumps(report)


def test_missing_evidence_report():
    report = generate_structured_assessment_report(
        requirements=[
            ("req-001", "Revenue (million USD)", 2025, "145"),
        ],
        evidence_items=[],
    )

    assert report["answerability"] == "abstain"
    assert report["coverage"] == 0.0
    assert report["evidence_provenance"] == []
    assert report["evidence_quality"] == []
    assert report["quality_summary"]["total_evidence"] == 0
    assert report["quality_summary"]["average_completeness"] is None

    json.dumps(report)


def test_multiple_requirement_report():
    evidence = [
        make_evidence(
            "ev-001", "Revenue (million USD)", "145", 1
        ),
        make_evidence(
            "ev-002", "Profit (million USD)", "30", 2
        ),
    ]

    report = generate_structured_assessment_report(
        requirements=[
            ("req-001", "Revenue (million USD)", 2025, "145"),
            ("req-002", "Profit (million USD)", 2025, "30"),
        ],
        evidence_items=evidence,
    )

    assert report["answerability"] == "full"
    assert report["coverage"] == 1.0
    assert len(report["requirements"]) == 2
    assert len(report["evidence_provenance"]) == 2
    assert len(report["evidence_quality"]) == 2
    assert len(report["requirement_quality"]) == 2
    assert report["quality_summary"]["total_evidence"] == 2

    json.dumps(report)
