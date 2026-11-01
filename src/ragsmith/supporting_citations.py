"""Build answer citations using verifier support rather than examined IDs."""

from collections.abc import Sequence

from ragsmith.evidence.models import Evidence
from ragsmith.qa import MetricAssertion
from ragsmith.sufficiency import structured_verifier
from ragsmith.sufficiency.provenance import build_evidence_provenance
from ragsmith.sufficiency.traceability import validate_evidence_traceability


def supporting_citations(
    assertion: MetricAssertion,
    evidence_items: Sequence[Evidence],
) -> list[dict]:
    """Return support-only provenance, or no citations for a conflicting claim.

    Callers must also suppress answer claims when the overall question abstains.
    Contradictions and unverified evidence remain available in assessment audit
    records; they are never presented here as support for a factual answer.
    """
    if not isinstance(assertion, MetricAssertion):
        raise ValueError("assertion must be a MetricAssertion")
    validate_evidence_traceability({"requirements": []}, evidence_items)
    judgments = [
        structured_verifier.verify_metric_value(
            item, assertion.metric, assertion.year, assertion.expected_value,
            assertion.requirement_id,
        )
        for item in evidence_items
    ]
    if any(item.verdict == "contradicts" for item in judgments):
        return []
    ids = [item.evidence_id for item in judgments if item.verdict == "supports"]
    return build_evidence_provenance(
        {"requirements": [{"evidence_ids": ids}]}, evidence_items
    )
