
from dataclasses import replace

from .models import Requirement


def record_assessment(
    requirement: Requirement,
    status: str,
    evidence_ids: list[str],
    reason: str,
) -> Requirement:
    """Record an externally determined assessment decision."""
    return replace(
        requirement,
        status=status,
        evidence_ids=evidence_ids.copy(),
        reason=reason,
    )
