
from collections.abc import Sequence

from ragsmith.evidence.models import Evidence
from .evidence_quality import score_evidence_quality


def build_requirement_quality_report(
    report: dict,
    evidence_items: Sequence[Evidence],
) -> list[dict]:
    """Summarize metadata completeness for each requirement."""

    evidence_lookup = {
        evidence.evidence_id: evidence
        for evidence in evidence_items
    }

    results = []

    for requirement in report["requirements"]:
        evidence_ids = list(dict.fromkeys(
            requirement["evidence_ids"]
        ))

        scores = []

        for evidence_id in evidence_ids:
            if evidence_id not in evidence_lookup:
                raise ValueError(
                    f"Unknown evidence ID: {evidence_id}"
                )

            scores.append(
                score_evidence_quality(
                    evidence_lookup[evidence_id]
                )["completeness_score"]
            )

        if scores:
            average_score = round(
                sum(scores) / len(scores), 2
            )
            lowest_score = min(scores)
            weakest_ids = [
                evidence_id
                for evidence_id, score in zip(evidence_ids, scores)
                if score == lowest_score
            ]
        else:
            average_score = None
            lowest_score = None
            weakest_ids = []

        results.append({
            "requirement_id": requirement["requirement_id"],
            "evidence_count": len(evidence_ids),
            "average_completeness": average_score,
            "lowest_completeness": lowest_score,
            "weakest_evidence_ids": weakest_ids,
        })

    return results
