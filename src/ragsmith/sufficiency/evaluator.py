
from collections.abc import Sequence

from ragsmith.evidence.models import Evidence

from .models import Requirement
from .results import SufficiencyResult
from .verification import check_evidence_eligibility


def evaluate_requirement(
    requirement: Requirement,
    evidence_items: Sequence[Evidence],
) -> SufficiencyResult:
    """Check candidate evidence without claiming semantic support."""

    eligible_ids = []

    for evidence in evidence_items:
        eligible, _ = check_evidence_eligibility(evidence)

        if eligible and evidence.evidence_id not in eligible_ids:
            eligible_ids.append(evidence.evidence_id)

    if not eligible_ids:
        return SufficiencyResult(
            requirement_id=requirement.requirement_id,
            status="unverified",
            evidence_ids=[],
            reason="No eligible candidate evidence available",
        )

    return SufficiencyResult(
        requirement_id=requirement.requirement_id,
        status="unverified",
        evidence_ids=eligible_ids,
        reason="Eligible evidence found; semantic support not yet verified",
    )
