
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

def test_duplicate_requirement_ids_rejected():
    results = [
        make_result("req-001", "supported"),
        make_result("req-001", "supported"),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate requirement IDs",
    ):
        assess_question(results)


def test_conflicting_duplicate_requirements_rejected():
    results = [
        make_result("req-001", "supported"),
        make_result("req-001", "contradicted"),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate requirement IDs",
    ):
        assess_question(results)


def test_unique_requirement_ids_accepted():
    results = [
        make_result("req-001", "supported"),
        make_result("req-002", "unverified"),
        make_result("req-003", "missing"),
    ]

    assessment = assess_question(results)

    assert assessment.total_requirements == 3
    assert assessment.supported_requirements == 1
    assert assessment.coverage == pytest.approx(1 / 3)
    assert assessment.answerability == "partial"


def test_repeated_same_result_object_rejected():
    result = make_result("req-001", "supported")

    with pytest.raises(
        ValueError,
        match="Duplicate requirement IDs",
    ):
        assess_question([result, result])

def test_assessment_preserves_requirement_results():
    results = [
        SufficiencyResult(
            requirement_id="req-001",
            status="supported",
            evidence_ids=["ev-001"],
        ),
        SufficiencyResult(
            requirement_id="req-002",
            status="unverified",
            reason="Insufficient evidence",
        ),
    ]

    assessment = assess_question(results)

    assert assessment.requirement_results == results
    assert len(assessment.requirement_results) == 2


def test_assessment_preserves_evidence_and_reason():
    result = SufficiencyResult(
        requirement_id="req-001",
        status="contradicted",
        evidence_ids=["ev-002"],
        reason="Conflicting value",
    )

    assessment = assess_question([result])
    reported = assessment.requirement_results[0]

    assert reported.requirement_id == "req-001"
    assert reported.status == "contradicted"
    assert reported.evidence_ids == ["ev-002"]
    assert reported.reason == "Conflicting value"


def test_empty_assessment_has_empty_requirement_results():
    assessment = assess_question([])

    assert assessment.requirement_results == []
    assert assessment.total_requirements == 0
    assert assessment.answerability == "abstain"


def test_assessment_copies_requirement_results_list():
    results = [
        SufficiencyResult(
            requirement_id="req-001",
            status="supported",
        ),
    ]

    assessment = assess_question(results)

    results.clear()

    assert len(assessment.requirement_results) == 1
    assert assessment.requirement_results[0].requirement_id == "req-001"
