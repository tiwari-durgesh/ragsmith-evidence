
import pytest

from ragsmith.sufficiency.models import Requirement
from ragsmith.sufficiency.assessment import record_assessment


def test_record_supported_assessment():
    requirement = Requirement("req-1", "Find revenue for 2025")

    result = record_assessment(
        requirement,
        "supported",
        ["ev-001"],
        "Manually verified against source",
    )

    assert result.status == "supported"
    assert result.evidence_ids == ["ev-001"]
    assert result.reason == "Manually verified against source"


def test_original_requirement_unchanged():
    requirement = Requirement("req-1", "Find revenue")
    evidence_ids = ["ev-001"]

    result = record_assessment(
        requirement,
        "supported",
        evidence_ids,
        "Verified",
    )

    evidence_ids.append("ev-002")

    assert requirement.status == "unverified"
    assert requirement.evidence_ids == []
    assert result.evidence_ids == ["ev-001"]


@pytest.mark.parametrize(
    "status",
    ["supported", "missing", "contradicted", "unverified"],
)
def test_valid_assessment_statuses(status):
    requirement = Requirement("req-1", "Find revenue")

    result = record_assessment(
        requirement,
        status,
        [],
        "Assessment recorded",
    )

    assert result.status == status


def test_invalid_assessment_status():
    requirement = Requirement("req-1", "Find revenue")

    with pytest.raises(ValueError):
        record_assessment(
            requirement,
            "incorrect",
            [],
            "Invalid status",
        )


def test_invalid_evidence_ids():
    requirement = Requirement("req-1", "Find revenue")

    with pytest.raises(ValueError):
        record_assessment(
            requirement,
            "supported",
            [""],
            "Invalid evidence ID",
        )
