"""Discover candidates, verify them, and expose evidence-bounded fact answers."""

from collections.abc import Sequence
from dataclasses import asdict

from ragsmith.evidence.models import Evidence
from ragsmith.lookup_config import LookupConfig
from ragsmith.qa import MetricAssertion
from ragsmith.supporting_citations import supporting_citations
from ragsmith.sufficiency import structured_verifier
from ragsmith.sufficiency.aggregator import aggregate_judgments
from ragsmith.sufficiency.evidence_quality import build_evidence_quality_report
from ragsmith.sufficiency.provenance import build_evidence_provenance
from ragsmith.sufficiency.provenance_validation import validate_provenance_integrity
from ragsmith.sufficiency.quality_summary import build_quality_summary
from ragsmith.sufficiency.question_assessment import assess_question
from ragsmith.sufficiency.reporting import build_assessment_report
from ragsmith.sufficiency.requirement_quality import build_requirement_quality_report
from ragsmith.sufficiency.results import SufficiencyResult
from ragsmith.sufficiency.traceability import validate_evidence_traceability
from ragsmith.value_lookup import LookupQuestion, discover_values


def assess_lookup_question(
    request: LookupQuestion,
    evidence_items: Sequence[Evidence],
    config: LookupConfig = LookupConfig(),
) -> dict:
    """Assess explicit unknown-value requirements over supplied evidence.

    Every extracted candidate is checked against every scoped evidence item by
    the existing verifier, then the existing aggregator and decision policy are
    applied. No candidate is selected as truth before contradictory alternatives
    have been checked. The legacy assertion API and assessment schema are intact.
    """
    if not isinstance(request, LookupQuestion):
        raise ValueError("request must be a LookupQuestion")
    if not isinstance(config, LookupConfig):
        raise ValueError("config must be a LookupConfig")
    validate_evidence_traceability({"requirements": []}, evidence_items)
    results = []
    discoveries = []
    answer_candidates = []
    for requirement in request.requirements:
        scoped = requirement.scope(evidence_items)
        candidates = ()
        unknown = ()
        if config.value_lookup_enabled:
            discovery = discover_values(requirement, scoped)
            candidates = discovery.candidates
            unknown = discovery.unverified_evidence_ids
        judgments = []
        for candidate in candidates:
            judgments.extend(
                structured_verifier.verify_metric_value(
                    item, requirement.metric, requirement.year, candidate.value,
                    requirement.requirement_id,
                )
                for item in scoped
            )
        if candidates:
            result = aggregate_judgments(requirement.requirement_id, judgments)
        else:
            if not config.value_lookup_enabled:
                status, reason = "unverified", "Value lookup is disabled by config"
            elif unknown:
                status = "unverified"
                reason = "Supplied evidence includes unsupported formats"
            else:
                status = "missing"
                reason = (
                    "No matching value in supplied interpretable evidence in scope"
                )
            result = SufficiencyResult(
                requirement.requirement_id, status,
                [item.evidence_id for item in scoped], reason,
            )
        results.append(result)
        discoveries.append({
            "requirement_id": requirement.requirement_id,
            "candidates": [
                {"value": item.value, "evidence_ids": list(item.evidence_ids)}
                for item in candidates
            ],
            "unverified_evidence_ids": list(unknown),
        })
        if result.status == "supported":
            # All candidates passed through verification; disagreement would
            # have produced a contradiction. Sorting makes display reproducible.
            value = candidates[0].value
            assertion = MetricAssertion(
                requirement.requirement_id, requirement.metric, requirement.year, value
            )
            answer_candidates.append({
                "requirement_id": requirement.requirement_id,
                "metric": requirement.metric,
                "year": requirement.year,
                "value": value,
                "citations": supporting_citations(assertion, scoped),
            })

    report = build_assessment_report(assess_question(results))
    validate_evidence_traceability(report, evidence_items)
    report["evidence_provenance"] = build_evidence_provenance(report, evidence_items)
    validate_provenance_integrity(report, evidence_items)
    report["evidence_quality"] = build_evidence_quality_report(report, evidence_items)
    report["requirement_quality"] = build_requirement_quality_report(
        report, evidence_items
    )
    report["quality_summary"] = build_quality_summary(report)

    return {
        "schema_version": "1.0",
        "mode": "value_lookup",
        "config": asdict(config),
        "question_id": request.question_id,
        "question": request.question,
        "requirements": [
            {"requirement_id": item.requirement_id, "metric": item.metric,
             "year": item.year, "document_ids": list(item.document_ids)}
            for item in request.requirements
        ],
        "assessment": report,
        "discovery": discoveries,
        "answers": answer_candidates if report["answerability"] != "abstain" else [],
    }
