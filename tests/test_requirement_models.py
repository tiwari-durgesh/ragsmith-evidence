
import pytest

from ragsmith.sufficiency.models import Requirement


def test_valid_requirement():
    requirement = Requirement(
        requirement_id="req-1",
        description="Find revenue for 2025",
    )

    assert requirement.requirement_id == "req-1"
    assert requirement.status == "unverified"
    assert requirement.evidence_ids == []


def test_supported_requirement():
    requirement = Requirement(
        requirement_id="req-2",
        description="Verify revenue growth",
        status="supported",
        evidence_ids=["ev-001"],
        reason="Evidence supports the requirement",
    )

    assert requirement.status == "supported"
    assert requirement.evidence_ids == ["ev-001"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("requirement_id", ""),
        ("requirement_id", " "),
        ("description", ""),
        ("description", " "),
        ("status", "invalid"),
        ("evidence_ids", "ev-001"),
        ("evidence_ids", [""]),
        ("evidence_ids", [123]),
        ("reason", 123),
    ],
)
def test_invalid_requirement(field, value):
    data = {
        "requirement_id": "req-1",
        "description": "Find revenue for 2025",
    }

    data[field] = value

    with pytest.raises(ValueError):
        Requirement(**data)


def test_evidence_lists_are_independent():
    first = Requirement("req-1", "Find revenue")
    second = Requirement("req-2", "Find expenses")

    first.evidence_ids.append("ev-001")

    assert second.evidence_ids == []
