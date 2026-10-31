from dataclasses import dataclass, field
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
    requirement_results: list[SufficiencyResult] = field(
        default_factory=list
    )


def assess_question(
    results: Sequence[SufficiencyResult],
) -> QuestionAssessment:
    """Summarize requirement-level sufficiency for a question."""
    
    requirement_ids = [
        result.requirement_id
        for result in results
    ]

    if len(requirement_ids) != len(set(requirement_ids)):
        raise ValueError(
            "Duplicate requirement IDs are not allowed"
        )

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
        requirement_results=list(results),
    )

