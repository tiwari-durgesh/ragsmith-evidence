
from collections.abc import Sequence

from ragsmith.evidence.models import Evidence


def validate_evidence_traceability(
    report: dict,
    evidence_items: Sequence[Evidence],
) -> None:
    """Reject report evidence IDs absent from supplied evidence."""

    evidence_ids = [
        evidence.evidence_id
        for evidence in evidence_items
    ]

    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError(
            "Duplicate evidence IDs are not allowed"
        )

    available_ids = {
        evidence.evidence_id
        for evidence in evidence_items
    }

    for requirement in report["requirements"]:
        for evidence_id in requirement["evidence_ids"]:
            if evidence_id not in available_ids:
                raise ValueError(
                    f"Unknown evidence ID: {evidence_id}"
                )
