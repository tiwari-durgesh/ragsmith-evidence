
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.pipeline import (
    assess_structured_requirement,
    assess_multiple_requirements,
    generate_structured_assessment_report,
)


def make_evidence(
    evidence_id="ev-001",
    value="145",
    kind="table_row",
):
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-001",
        document_version="version-001",
        kind=kind,
        content=f"Metric: Revenue (million USD); 2025: {value}",
        locator="table:1/row:2",
    )


def assess(evidence_items, expected_value="145"):
    return assess_structured_requirement(
        requirement_id="req-001",
        metric="Revenue (million USD)",
        year=2025,
        expected_value=expected_value,
        evidence_items=evidence_items,
    )


def test_matching_evidence_full():
    result = assess([make_evidence()])

    assert result.total_requirements == 1
    assert result.supported_requirements == 1
    assert result.coverage == 1.0
    assert result.answerability == "full"


def test_equivalent_numeric_value_full():
    result = assess(
        [make_evidence(value="145")],
        expected_value="145.00",
    )

    assert result.answerability == "full"


def test_conflicting_value_abstain():
    result = assess(
        [make_evidence(value="150")],
    )

    assert result.supported_requirements == 0
    assert result.coverage == 0.0
    assert result.answerability == "abstain"


def test_mixed_evidence_abstain():
    result = assess([
        make_evidence("ev-001", "145"),
        make_evidence("ev-002", "150"),
    ])

    assert result.answerability == "abstain"
    assert result.coverage == 0.0


def test_no_evidence_abstain():
    result = assess([])

    assert result.total_requirements == 1
    assert result.supported_requirements == 0
    assert result.coverage == 0.0
    assert result.answerability == "abstain"


def test_unsupported_evidence_format_abstain():
    result = assess([
        make_evidence(kind="text"),
    ])

    assert result.answerability == "abstain"


def test_multiple_matching_evidence_full():
    result = assess([
        make_evidence("ev-001", "145"),
        make_evidence("ev-002", "145.0"),
    ])

    assert result.supported_requirements == 1
    assert result.coverage == 1.0
    assert result.answerability == "full"

def test_multiple_requirements_full():
    requirements = [
        ("req-001", "Revenue (million USD)", 2025, "145"),
        ("req-002", "Revenue (million USD)", 2025, "145.00"),
    ]

    result = assess_multiple_requirements(
        requirements,
        [make_evidence()],
    )

    assert result.total_requirements == 2
    assert result.supported_requirements == 2
    assert result.coverage == 1.0
    assert result.answerability == "full"


def test_multiple_requirements_partial():
    requirements = [
        ("req-001", "Revenue (million USD)", 2025, "145"),
        ("req-002", "Profit (million USD)", 2025, "20"),
    ]

    result = assess_multiple_requirements(
        requirements,
        [make_evidence()],
    )

    assert result.total_requirements == 2
    assert result.supported_requirements == 1
    assert result.coverage == 0.5
    assert result.answerability == "partial"


def test_multiple_requirements_contradiction():
    requirements = [
        ("req-001", "Revenue (million USD)", 2025, "145"),
        ("req-002", "Revenue (million USD)", 2025, "150"),
    ]

    result = assess_multiple_requirements(
        requirements,
        [make_evidence()],
    )

    assert result.total_requirements == 2
    assert result.supported_requirements == 1
    assert result.coverage == 0.5
    assert result.answerability == "abstain"


def test_multiple_requirements_empty():
    result = assess_multiple_requirements([], [])

    assert result.total_requirements == 0
    assert result.supported_requirements == 0
    assert result.coverage == 0.0
    assert result.answerability == "abstain"


def test_multiple_requirements_duplicate_ids():
    requirements = [
        ("req-001", "Revenue (million USD)", 2025, "145"),
        ("req-001", "Profit (million USD)", 2025, "20"),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate requirement IDs",
    ):
        assess_multiple_requirements(
            requirements,
            [make_evidence()],
        )

def test_structured_report_full():
    requirements = [
        ("req-001", "Revenue (million USD)", 2025, "145"),
    ]

    report = generate_structured_assessment_report(
        requirements,
        [make_evidence()],
    )

    assert report["total_requirements"] == 1
    assert report["supported_requirements"] == 1
    assert report["coverage"] == 1.0
    assert report["answerability"] == "full"
    assert report["requirements"][0]["status"] == "supported"


def test_structured_report_partial():
    requirements = [
        ("req-001", "Revenue (million USD)", 2025, "145"),
        ("req-002", "Profit (million USD)", 2025, "20"),
    ]

    report = generate_structured_assessment_report(
        requirements,
        [make_evidence()],
    )

    assert report["coverage"] == 0.5
    assert report["answerability"] == "partial"
    assert report["requirements"][0]["status"] == "supported"
    assert report["requirements"][1]["status"] == "unverified"


def test_structured_report_contradiction():
    requirements = [
        ("req-001", "Revenue (million USD)", 2025, "150"),
    ]

    report = generate_structured_assessment_report(
        requirements,
        [make_evidence()],
    )

    assert report["answerability"] == "abstain"
    assert report["requirements"][0]["status"] == "contradicted"


def test_structured_report_empty():
    report = generate_structured_assessment_report([], [])

    assert report["total_requirements"] == 0
    assert report["coverage"] == 0.0
    assert report["answerability"] == "abstain"
    assert report["requirements"] == []


def test_structured_report_duplicate_ids():
    requirements = [
        ("req-001", "Revenue (million USD)", 2025, "145"),
        ("req-001", "Profit (million USD)", 2025, "20"),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate requirement IDs",
    ):
        generate_structured_assessment_report(
            requirements,
            [make_evidence()],
        )
