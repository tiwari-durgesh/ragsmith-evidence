
from collections.abc import Sequence

from .judgments import SupportJudgment
from .results import SufficiencyResult


def aggregate_judgments(
    requirement_id: str,
    judgments: Sequence[SupportJudgment],
) -> SufficiencyResult:
    """Combine evidence judgments into one requirement result."""

    if not isinstance(requirement_id, str) or not requirement_id.strip():
        raise ValueError("requirement_id must be non-empty")

    relevant = [
        judgment
        for judgment in judgments
        if judgment.requirement_id == requirement_id
    ]

    evidence_ids = list(
        dict.fromkeys(judgment.evidence_id for judgment in relevant)
    )

    verdicts = {judgment.verdict for judgment in relevant}

    if "contradicts" in verdicts:
        status = "contradicted"
        reason = "At least one evidence judgment contradicts the requirement"

    elif "supports" in verdicts:
        status = "supported"
        reason = "At least one evidence judgment supports the requirement"

    else:
        status = "unverified"
        reason = "No supporting or contradicting judgment is available"

    return SufficiencyResult(
        requirement_id=requirement_id,
        status=status,
        evidence_ids=evidence_ids,
        reason=reason,
    )
