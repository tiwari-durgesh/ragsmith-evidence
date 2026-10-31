
from collections.abc import Sequence

from ragsmith.evidence.models import Evidence

from .structured_verifier import verify_metric_value
from .aggregator import aggregate_judgments
from .question_assessment import assess_question, QuestionAssessment


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
