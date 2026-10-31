
from dataclasses import dataclass
from collections.abc import Sequence

from .results import SufficiencyResult
from .coverage import calculate_coverage
from .decision import decide_answerability


@dataclass
class QuestionAssessment:
    total_requirements: int
    supported_requirements: int
    coverage: float
    answerability: str


def assess_question(
    results: Sequence[SufficiencyResult],
) -> QuestionAssessment:
    """Summarize requirement-level sufficiency for a question."""

    total = len(results)

    supported = sum(
        result.status == "supported"
        for result in results
    )

    return QuestionAssessment(
        total_requirements=total,
        supported_requirements=supported,
        coverage=calculate_coverage(results),
        answerability=decide_answerability(results),
    )
