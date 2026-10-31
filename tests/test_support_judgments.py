
import pytest

from ragsmith.sufficiency.judgments import SupportJudgment


def test_valid_support_judgment():
    judgment = SupportJudgment(
        requirement_id="req-1",
        evidence_id="ev-001",
        verdict="supports",
        reason="Evidence directly supports the requirement",
    )

    assert judgment.requirement_id == "req-1"
    assert judgment.evidence_id == "ev-001"
    assert judgment.verdict == "supports"
    assert judgment.reason == "Evidence directly supports the requirement"


@pytest.mark.parametrize(
    "verdict",
    ["supports", "insufficient", "contradicts", "unverified"],
)
def test_valid_verdicts(verdict):
    judgment = SupportJudgment("req-1", "ev-001", verdict)

    assert judgment.verdict == verdict


@pytest.mark.parametrize(
    "field,value",
    [
        ("requirement_id", ""),
        ("requirement_id", "   "),
        ("evidence_id", ""),
        ("evidence_id", "   "),
        ("verdict", "invalid"),
        ("reason", 123),
    ],
)
def test_invalid_support_judgments(field, value):
    data = {
        "requirement_id": "req-1",
        "evidence_id": "ev-001",
        "verdict": "unverified",
    }

    data[field] = value

    with pytest.raises(ValueError):
        SupportJudgment(**data)


def test_default_reason():
    judgment = SupportJudgment(
        "req-1",
        "ev-001",
        "unverified",
    )

    assert judgment.reason == ""
