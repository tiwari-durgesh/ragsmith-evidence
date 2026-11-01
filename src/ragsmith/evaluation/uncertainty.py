"""Paired percentile bootstrap of source clusters for bounded-rate differences."""

import math
import random
from dataclasses import dataclass

from ragsmith.evaluation.records import require_text


@dataclass(frozen=True)
class BootstrapConfig:
    replicates: int = 2000
    seed: int = 1729
    confidence: float = 0.95

    def __post_init__(self) -> None:
        if type(self.replicates) is not int or not 1 <= self.replicates <= 100000:
            raise ValueError("replicates must be an integer from 1 to 100000")
        if type(self.seed) is not int:
            raise ValueError("seed must be an integer")
        if type(self.confidence) not in {int, float} or not 0 < self.confidence < 1:
            raise ValueError("confidence must lie strictly between zero and one")


@dataclass(frozen=True)
class PairedRate:
    question_id: str
    group_id: str
    numerator_a: float
    denominator_a: float
    numerator_b: float
    denominator_b: float

    def __post_init__(self) -> None:
        require_text(self.question_id, "question_id")
        require_text(self.group_id, "group_id")
        for name in ("numerator_a", "denominator_a", "numerator_b", "denominator_b"):
            value = getattr(self, name)
            if type(value) not in {int, float} or not math.isfinite(value) or value < 0:
                raise ValueError("Rate counts must be finite nonnegative numbers")
        if self.numerator_a > self.denominator_a or self.numerator_b > self.denominator_b:
            raise ValueError("Rate numerator cannot exceed its denominator")


def _difference(rows: list[PairedRate], estimand: str) -> float | None:
    if not rows:
        return None
    if estimand == "paired_mean":
        return sum(row.numerator_a / row.denominator_a
                   - row.numerator_b / row.denominator_b for row in rows) / len(rows)
    a, b = sum(row.denominator_a for row in rows), sum(row.denominator_b for row in rows)
    if not a or not b:
        return None
    return sum(row.numerator_a for row in rows) / a - sum(row.numerator_b for row in rows) / b


def _quantile(sorted_values: list[float], probability: float) -> float:
    position = (len(sorted_values) - 1) * probability
    left, right = math.floor(position), math.ceil(position)
    return sorted_values[left] + (sorted_values[right] - sorted_values[left]) * (position - left)


def paired_cluster_interval(
    rows: list[PairedRate], *, estimand: str,
    config: BootstrapConfig = BootstrapConfig(),
) -> dict:
    """Resample whole families with replacement, retaining both policy outcomes.

    For paired means, undefined per-question pairs are excluded and counted.
    Ratios pool counts before division, retaining zero-claim questions. Any
    undefined resample prevents an interval rather than conditioning it away.
    One cluster never produces an inferential interval.
    """
    if estimand not in {"paired_mean", "ratio_of_sums"}:
        raise ValueError("Unknown bootstrap estimand")
    if not isinstance(config, BootstrapConfig) or any(not isinstance(row, PairedRate) for row in rows):
        raise ValueError("Bootstrap needs typed rows and config")
    ids = [row.question_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate paired question IDs")
    eligible = [row for row in rows if estimand == "ratio_of_sums"
                or (row.denominator_a > 0 and row.denominator_b > 0)]
    clusters = {}
    for row in sorted(eligible, key=lambda item: item.question_id):
        clusters.setdefault(row.group_id, []).append(row)
    names = sorted(clusters)
    point = _difference(eligible, estimand)
    report = {
        "difference_direction": "A minus B", "estimand": estimand,
        "input_questions": len(rows), "eligible_questions": len(eligible),
        "excluded_undefined_pairs": len(rows) - len(eligible), "clusters": len(names),
        "replicates_requested": config.replicates, "replicates_valid": 0,
        "replicates_undefined": 0, "seed": config.seed, "confidence": config.confidence,
        "point_difference": point, "interval": None, "undefined_reason": None,
        "method": "paired source-cluster percentile bootstrap",
    }
    if point is None or len(names) < 2:
        report["undefined_reason"] = "undefined_point_metric" if point is None else "fewer_than_two_clusters"
        return report
    rng = random.Random(config.seed)
    values = []
    for _ in range(config.replicates):
        sample = [row for name in rng.choices(names, k=len(names)) for row in clusters[name]]
        value = _difference(sample, estimand)
        if value is None:
            report["replicates_undefined"] += 1
        else:
            values.append(value)
    report["replicates_valid"] = len(values)
    if report["replicates_undefined"]:
        report["undefined_reason"] = "undefined_metric_in_resamples"
    else:
        values.sort()
        tail = (1 - config.confidence) / 2
        report["interval"] = [_quantile(values, tail), _quantile(values, 1 - tail)]
    return report
