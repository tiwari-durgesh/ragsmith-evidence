
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.pipeline import assess_structured_requirement


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
