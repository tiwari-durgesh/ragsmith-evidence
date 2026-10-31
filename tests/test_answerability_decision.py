
import pytest

from ragsmith.sufficiency.decision import decide_answerability
from ragsmith.sufficiency.results import SufficiencyResult


def make_result(requirement_id, status):
    return SufficiencyResult(
        requirement_id=requirement_id,
        status=status,
    )


def test_all_supported_full():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "supported"),
    ]

    assert decide_answerability(results) == "full"


def test_partially_supported():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "unverified"),
    ]

    assert decide_answerability(results) == "partial"


def test_supported_and_missing_partial():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "missing"),
    ]

    assert decide_answerability(results) == "partial"


def test_none_supported_abstain():
    results = [
        make_result("req-001", "missing"),
        make_result("req-002", "unverified"),
    ]

    assert decide_answerability(results) == "abstain"


def test_contradiction_overrides_support():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "contradicted"),
    ]

    assert decide_answerability(results) == "abstain"


def test_only_contradiction_abstain():
    results = [
        make_result("req-001", "contradicted"),
    ]

    assert decide_answerability(results) == "abstain"


def test_empty_results_abstain():
    assert decide_answerability([]) == "abstain"


def test_single_supported_full():
    results = [
        make_result("req-001", "supported"),
    ]

    assert decide_answerability(results) == "full"


@pytest.mark.parametrize(
    "status",
    ["missing", "unverified", "contradicted"],
)
def test_single_unsupported_abstain(status):
    results = [
        make_result("req-001", status),
    ]

    assert decide_answerability(results) == "abstain"
