
from collections.abc import Sequence

from .results import SufficiencyResult


def calculate_coverage(
    results: Sequence[SufficiencyResult],
) -> float:
    """Calculate the fraction of supported requirements."""

    if not results:
        return 0.0

    supported = sum(
        result.status == "supported"
        for result in results
    )

    return supported / len(results)
