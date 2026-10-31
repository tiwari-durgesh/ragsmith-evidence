
from collections.abc import Sequence

from ragsmith.evidence.models import Evidence
from .traceability import validate_evidence_traceability
from .structured_verifier import verify_metric_value
from .aggregator import aggregate_judgments
from .question_assessment import assess_question, QuestionAssessment
from .reporting import build_assessment_report

def assess_structured_requirement(
    requirement_id: str,
    metric: str,
    year: int,
    expected_value: str,
    evidence_items: Sequence[Evidence],
) -> QuestionAssessment:
    """Assess one structured requirement using supplied evidence."""

    judgments = [
        verify_metric_value(
            evidence=evidence,
            metric=metric,
            year=year,
            expected_value=expected_value,
            requirement_id=requirement_id,
        )
        for evidence in evidence_items
    ]

    result = aggregate_judgments(
        requirement_id=requirement_id,
        judgments=judgments,
    )

    return assess_question([result])

def assess_multiple_requirements(
    requirements: Sequence[tuple[str, str, int, str]],
    evidence_items: Sequence[Evidence],
) -> QuestionAssessment:
    """Assess multiple structured requirements together."""

    results = []

    for requirement_id, metric, year, expected_value in requirements:
        judgments = [
            verify_metric_value(
                evidence=evidence,
                metric=metric,
                year=year,
                expected_value=expected_value,
                requirement_id=requirement_id,
            )
            for evidence in evidence_items
        ]

        result = aggregate_judgments(
            requirement_id=requirement_id,
            judgments=judgments,
        )

        results.append(result)

    return assess_question(results)


def generate_structured_assessment_report(
    requirements: Sequence[tuple[str, str, int, str]],
    evidence_items: Sequence[Evidence],
) -> dict:
    """Generate a traceability-validated assessment report."""

    assessment = assess_multiple_requirements(
        requirements=requirements,
        evidence_items=evidence_items,
    )

    report = build_assessment_report(assessment)

    validate_evidence_traceability(
        report=report,
        evidence_items=evidence_items,
    )

    return report

