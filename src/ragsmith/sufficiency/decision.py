
from collections.abc import Sequence

from .results import SufficiencyResult
from .coverage import calculate_coverage


def decide_answerability(
    results: Sequence[SufficiencyResult],
) -> str:
    """Decide whether to answer fully, partially, or abstain."""

    if not results:
        return "abstain"

    if any(result.status == "contradicted" for result in results):
        return "abstain"

    coverage = calculate_coverage(results)

    if coverage == 1.0:
        return "full"

    if coverage > 0.0:
        return "partial"

    return "abstain"
