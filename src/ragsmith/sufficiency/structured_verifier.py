
import re

from ragsmith.evidence.models import Evidence
from .judgments import SupportJudgment


def verify_metric_value(
    evidence: Evidence,
    metric: str,
    year: int,
    expected_value: str,
) -> SupportJudgment:
    """Verify an exact metric-year-value assertion in a table row."""

    verdict = "unverified"
    reason = "Evidence does not match the supported table-row format"

    pattern = (
        r"^Metric:\s*(?P<metric>[^;]+);\s*"
        r"(?P<year>\d{4}):\s*(?P<value>[^;]+)$"
    )

    if evidence.kind == "table_row":
        match = re.fullmatch(pattern, evidence.content.strip())

        if match:
            actual_metric = match.group("metric").strip()
            actual_year = int(match.group("year"))
            actual_value = match.group("value").strip()

            if (
                actual_metric.casefold() == metric.strip().casefold()
                and actual_year == year
            ):
                if actual_value == expected_value.strip():
                    verdict = "supports"
                    reason = "Exact metric, year, and value match"
                else:
                    verdict = "contradicts"
                    reason = "Metric and year match, but value differs"
            else:
                reason = "Metric or year does not match the requirement"

    return SupportJudgment(
        requirement_id=f"{metric.strip()}-{year}",
        evidence_id=evidence.evidence_id,
        verdict=verdict,
        reason=reason,
    )
