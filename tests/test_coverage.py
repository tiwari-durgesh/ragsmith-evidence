
import pytest

from ragsmith.sufficiency.coverage import calculate_coverage
from ragsmith.sufficiency.results import SufficiencyResult


def make_result(requirement_id, status):
    return SufficiencyResult(
        requirement_id=requirement_id,
        status=status,
    )


def test_all_requirements_supported():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "supported"),
    ]

    assert calculate_coverage(results) == 1.0


def test_partial_coverage():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "supported"),
        make_result("req-003", "supported"),
        make_result("req-004", "unverified"),
    ]

    assert calculate_coverage(results) == 0.75


def test_no_requirements_supported():
    results = [
        make_result("req-001", "missing"),
        make_result("req-002", "unverified"),
    ]

    assert calculate_coverage(results) == 0.0


def test_empty_results():
    assert calculate_coverage([]) == 0.0


def test_single_supported_requirement():
    results = [make_result("req-001", "supported")]

    assert calculate_coverage(results) == 1.0


def test_single_unverified_requirement():
    results = [make_result("req-001", "unverified")]

    assert calculate_coverage(results) == 0.0


def test_contradicted_requirement_not_counted():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "contradicted"),
    ]

    assert calculate_coverage(results) == 0.5


@pytest.mark.parametrize(
    "status",
    ["missing", "unverified", "contradicted"],
)
def test_non_supported_statuses(status):
    results = [make_result("req-001", status)]

    assert calculate_coverage(results) == 0.0
