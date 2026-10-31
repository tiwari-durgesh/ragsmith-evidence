
import pytest

from ragsmith.sufficiency.results import SufficiencyResult


def test_default_sufficiency_result():
    result = SufficiencyResult("req-1")

    assert result.requirement_id == "req-1"
    assert result.status == "unverified"
    assert result.evidence_ids == []
    assert result.reason == ""


def test_supported_sufficiency_result():
    result = SufficiencyResult(
        requirement_id="req-1",
        status="supported",
        evidence_ids=["ev-001"],
        reason="Evidence verified",
    )

    assert result.status == "supported"
    assert result.evidence_ids == ["ev-001"]
    assert result.reason == "Evidence verified"


@pytest.mark.parametrize(
    "status",
    ["unverified", "supported", "missing", "contradicted"],
)
def test_valid_sufficiency_statuses(status):
    result = SufficiencyResult("req-1", status=status)

    assert result.status == status


@pytest.mark.parametrize(
    "field,value",
    [
        ("requirement_id", ""),
        ("requirement_id", "   "),
        ("status", "invalid"),
        ("evidence_ids", "ev-001"),
        ("evidence_ids", [""]),
        ("evidence_ids", [123]),
        ("reason", 123),
    ],
)
def test_invalid_sufficiency_result(field, value):
    data = {"requirement_id": "req-1"}
    data[field] = value

    with pytest.raises(ValueError):
        SufficiencyResult(**data)


def test_independent_evidence_lists():
    first = SufficiencyResult("req-1")
    second = SufficiencyResult("req-2")

    first.evidence_ids.append("ev-001")

    assert second.evidence_ids == []
