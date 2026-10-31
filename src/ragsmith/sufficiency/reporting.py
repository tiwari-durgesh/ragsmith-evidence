
from .question_assessment import QuestionAssessment


def build_assessment_report(
    assessment: QuestionAssessment,
) -> dict:
    """Convert an assessment into a JSON-compatible report."""

    return {
        "total_requirements": assessment.total_requirements,
        "supported_requirements": assessment.supported_requirements,
        "coverage": assessment.coverage,
        "answerability": assessment.answerability,
        "requirements": [
            {
                "requirement_id": result.requirement_id,
                "status": result.status,
                "evidence_ids": list(result.evidence_ids),
                "reason": result.reason,
            }
            for result in assessment.requirement_results
        ],
    }
