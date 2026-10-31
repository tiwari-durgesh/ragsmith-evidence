
import pytest

from ragsmith.sufficiency.question_assessment import (
    QuestionAssessment,
    assess_question,
)
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

    assessment = assess_question(results)

    assert isinstance(assessment, QuestionAssessment)
    assert assessment.total_requirements == 2
    assert assessment.supported_requirements == 2
    assert assessment.coverage == 1.0
    assert assessment.answerability == "full"


def test_partial_question_coverage():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "supported"),
        make_result("req-003", "supported"),
        make_result("req-004", "unverified"),
    ]

    assessment = assess_question(results)

    assert assessment.total_requirements == 4
    assert assessment.supported_requirements == 3
    assert assessment.coverage == 0.75
    assert assessment.answerability == "partial"


def test_no_supported_requirements():
    results = [
        make_result("req-001", "missing"),
        make_result("req-002", "unverified"),
    ]

    assessment = assess_question(results)

    assert assessment.total_requirements == 2
    assert assessment.supported_requirements == 0
    assert assessment.coverage == 0.0
    assert assessment.answerability == "abstain"


def test_contradiction_causes_abstention():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "contradicted"),
    ]

    assessment = assess_question(results)

    assert assessment.total_requirements == 2
    assert assessment.supported_requirements == 1
    assert assessment.coverage == 0.5
    assert assessment.answerability == "abstain"


def test_empty_requirements():
    assessment = assess_question([])

    assert assessment.total_requirements == 0
    assert assessment.supported_requirements == 0
    assert assessment.coverage == 0.0
    assert assessment.answerability == "abstain"


def test_single_supported_requirement():
    assessment = assess_question([
        make_result("req-001", "supported"),
    ])

    assert assessment.total_requirements == 1
    assert assessment.supported_requirements == 1
    assert assessment.coverage == 1.0
    assert assessment.answerability == "full"


@pytest.mark.parametrize(
    "status",
    ["missing", "unverified", "contradicted"],
)
def test_single_unsupported_requirement(status):
    assessment = assess_question([
        make_result("req-001", status),
    ])

    assert assessment.total_requirements == 1
    assert assessment.supported_requirements == 0
    assert assessment.coverage == 0.0
    assert assessment.answerability == "abstain"
