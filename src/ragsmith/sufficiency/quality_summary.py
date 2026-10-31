
from collections import Counter


def build_quality_summary(report: dict) -> dict:
    """Summarize evidence metadata completeness."""

    records = report["evidence_quality"]

    if not records:
        return {
            "total_evidence": 0,
            "average_completeness": None,
            "quality_distribution": {
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "incomplete_evidence_ids": [],
        }

    ids = [record["evidence_id"] for record in records]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate evidence quality records")

    distribution = Counter(
        record["completeness_level"]
        for record in records
    )

    average = round(
        sum(
            record["completeness_score"]
            for record in records
        ) / len(records),
        2,
    )

    incomplete_ids = [
        record["evidence_id"]
        for record in records
        if record["completeness_score"] < 1.0
    ]

    return {
        "total_evidence": len(records),
        "average_completeness": average,
        "quality_distribution": {
            "high": distribution["high"],
            "medium": distribution["medium"],
            "low": distribution["low"],
        },
        "incomplete_evidence_ids": incomplete_ids,
    }
