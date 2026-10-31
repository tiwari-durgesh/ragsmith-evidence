
import pytest

from ragsmith.sufficiency.aggregator import aggregate_judgments
from ragsmith.sufficiency.judgments import SupportJudgment


def make_judgment(
    verdict,
    evidence_id="ev-001",
    requirement_id="req-001",
):
    return SupportJudgment(
        requirement_id=requirement_id,
        evidence_id=evidence_id,
        verdict=verdict,
    )


def test_single_supporting_judgment():
    result = aggregate_judgments(
        "req-001",
        [make_judgment("supports")],
    )

    assert result.status == "supported"
    assert result.evidence_ids == ["ev-001"]


def test_multiple_supporting_judgments():
    result = aggregate_judgments(
        "req-001",
        [
            make_judgment("supports", "ev-001"),
            make_judgment("supports", "ev-002"),
        ],
    )

    assert result.status == "supported"
    assert result.evidence_ids == ["ev-001", "ev-002"]


def test_single_contradiction():
    result = aggregate_judgments(
        "req-001",
        [make_judgment("contradicts")],
    )

    assert result.status == "contradicted"


def test_contradiction_takes_priority():
    result = aggregate_judgments(
        "req-001",
        [
            make_judgment("supports", "ev-001"),
            make_judgment("contradicts", "ev-002"),
        ],
    )

    assert result.status == "contradicted"
    assert result.evidence_ids == ["ev-001", "ev-002"]


def test_insufficient_judgment_unverified():
    result = aggregate_judgments(
        "req-001",
        [make_judgment("insufficient")],
    )

    assert result.status == "unverified"


def test_unverified_judgment():
    result = aggregate_judgments(
        "req-001",
        [make_judgment("unverified")],
    )

    assert result.status == "unverified"


def test_empty_judgments():
    result = aggregate_judgments("req-001", [])

    assert result.status == "unverified"
    assert result.evidence_ids == []


def test_unrelated_requirements_ignored():
    result = aggregate_judgments(
        "req-001",
        [
            make_judgment(
                "contradicts",
                "ev-999",
                "req-002",
            ),
            make_judgment("supports", "ev-001"),
        ],
    )

    assert result.status == "supported"
    assert result.evidence_ids == ["ev-001"]


def test_duplicate_evidence_ids_removed():
    result = aggregate_judgments(
        "req-001",
        [
            make_judgment("supports", "ev-001"),
            make_judgment("supports", "ev-001"),
        ],
    )

    assert result.evidence_ids == ["ev-001"]


@pytest.mark.parametrize(
    "requirement_id",
    ["", "   ", None],
)
def test_invalid_requirement_id(requirement_id):
    with pytest.raises(ValueError):
        aggregate_judgments(requirement_id, [])
