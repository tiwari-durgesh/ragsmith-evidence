"""Import-only research runner skeleton. No file loading, selection or calibration.

The caller must explicitly supply a source snapshot and an answerer. The default
threshold is None: the confidence policy has no decision until separately fixed.
No score calculation or paper-result export is implemented here.
"""

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol
from subprocess import SubprocessError

from pydantic import BaseModel, ConfigDict, Field

from app.checked_service import validate_table
from app.contracts import AskRequest
from app.runtime import INPUT_BUDGET, Packed, pack
from app.service import present
from ragsmith.evidence.models import Evidence
from ragsmith.qa import MetricAssertion
from ragsmith.retrieval import RetrievalConfig, retrieve_question_evidence
from ragsmith.supporting_citations import supporting_citations
from ragsmith.sufficiency.aggregator import aggregate_judgments
from ragsmith.sufficiency.question_assessment import assess_question
from ragsmith.sufficiency.reporting import build_assessment_report
from ragsmith.sufficiency.results import SufficiencyResult
from ragsmith.sufficiency.structured_verifier import verify_metric_value
from ragsmith.value_lookup import LookupQuestion, MetricLookup
from scripts.tatqa_excerpt_ingestion import adapt_table, digest, write_database


class Answerer(Protocol):
    """LocalRuntime satisfies this interface; no implicit runtime is constructed."""
    def count(self, prompt: str) -> int: ...
    def generate(self, request: LookupQuestion, packed: Packed) -> tuple[list[dict], dict]: ...


class Candidate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    requirement_id: str
    value: str
    citations: list[str]
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    value_byte_span: list[int] | None = None
    value_token_count: int | None = None
    generation_failure: bool = False


@dataclass(frozen=True)
class Prepared:
    request: LookupQuestion
    packed: Packed
    retrieval: dict


def prepare(payload: AskRequest, answerer: Answerer) -> Prepared:
    validate_table(payload)
    identity = "request-" + digest([payload.source_reference, payload.table])[:16]
    adapted = adapt_table(identity, payload.table, paragraphs=payload.paragraphs,
                          source_reference=payload.source_reference, unit=payload.source_unit)
    request = LookupQuestion("runner-" + digest(payload.model_dump())[:16], payload.question, tuple(
        MetricLookup(f.requirement_id, f.metric, f.year, (adapted.document_id,)) for f in payload.requested_facts))
    with TemporaryDirectory(prefix="ragsmith-runner-") as folder:
        root = Path(folder)
        write_database(adapted, root / "source.sqlite", root / "source.json")
        retrieved = retrieve_question_evidence(root / "source.sqlite", request, RetrievalConfig(8))
    ranked = sorted(retrieved.evidence, key=lambda e: (
        min(h["rank"] for q in retrieved.audit["queries"] for h in q["hits"] if h["evidence_id"] == e.evidence_id),
        e.evidence_id))
    def count(text):
        number = answerer.count(text)
        if type(number) is not int or number < 0:
            raise ValueError("Tokenizer must return a nonnegative integer")
        return number
    packed = pack(request, ranked, count, budget=INPUT_BUDGET)
    return Prepared(request, packed, {"method": retrieved.audit["method"],
                                     "retrieved_units": len(ranked)})


def verify_candidates(request: LookupQuestion, evidence: list[Evidence], candidates: list[Candidate]):
    """Delegate each judgment and aggregation to frozen functions, without repair."""
    judgments, verified, gaps = [], [], []
    for requirement, candidate in zip(request.requirements, candidates):
        if not candidate.value.strip():
            result = SufficiencyResult(requirement.requirement_id, "unverified", [], "Generation failed to return a value")
        else:
            scope = requirement.scope(evidence)
            result = aggregate_judgments(requirement.requirement_id, [verify_metric_value(
                e, requirement.metric, requirement.year, candidate.value, requirement.requirement_id) for e in scope])
            support = supporting_citations(MetricAssertion(requirement.requirement_id, requirement.metric,
                                                           requirement.year, candidate.value), scope)
            support = [c for c in support if c["evidence_id"] in candidate.citations]
            if result.status == "supported" and not support:
                result = SufficiencyResult(requirement.requirement_id, "unverified", candidate.citations,
                                           "Generated citations do not support the candidate")
            if result.status == "supported":
                verified.append({"requirement_id": requirement.requirement_id, "metric": requirement.metric,
                                 "year": requirement.year, "value": candidate.value, "citations": support})
        judgments.append(result)
        if result.status != "supported":
            gaps.append({"requirement_id": requirement.requirement_id, "status": result.status, "explanation": result.reason})
    assessment = build_assessment_report(assess_question(judgments))
    if assessment["answerability"] == "abstain":
        verified = []
    return present("graded_sufficiency", assessment["answerability"], verified, gaps=gaps), assessment


def run_case(payload: AskRequest, answerer: Answerer, *, threshold: float | None = None) -> dict:
    if threshold is not None and (type(threshold) not in (int, float) or not 0 <= threshold <= 1):
        raise ValueError("Threshold must be None or a finite value in [0, 1]")
    prepared = prepare(payload, answerer)
    request, packed = prepared.request, prepared.packed
    common = {"question_id": request.question_id, "research_ready": False,
              "confidence_threshold": threshold, "confidence_calibrated": False,
              "included_in_denominator": True, "packing": packed.audit, "retrieval": prepared.retrieval}
    try:
        raw, generation = answerer.generate(request, packed)
        candidates = [Candidate.model_validate(c) for c in raw]
        if [c.requirement_id for c in candidates] != [r.requirement_id for r in request.requirements]:
            raise ValueError("One candidate per requirement, in original order, is required")
        known = {e.evidence_id: e for e in packed.evidence}
        if any(eid not in known for c in candidates for eid in c.citations):
            raise ValueError("Unknown generated citation")
        if any(c.generation_failure and c.value.strip() for c in candidates):
            raise ValueError("Inconsistent generation-failure flag")
    except (ValueError, TypeError, KeyError, OSError, RuntimeError, TimeoutError, SubprocessError) as exc:
        return {**common, "status": "generation_failed", "failure_type": type(exc).__name__,
                "policies": [], "notices": ["No repair, retry or model substitution. Failure remains in denominators."]}
    raw_answers = []
    failures = []
    for requirement, candidate in zip(request.requirements, candidates):
        if not candidate.value.strip():
            failures.append(requirement.requirement_id)
            continue
        citations = [{"evidence_id": e.evidence_id, "document_id": e.document_id,
                      "document_version": e.document_version, "locator": e.locator}
                     for eid in candidate.citations for e in [known[eid]]]
        raw_answers.append({"requirement_id": requirement.requirement_id, "metric": requirement.metric,
                            "year": requirement.year, "value": candidate.value,
                            "confidence": candidate.confidence, "citations": citations})
    def decision(answers):
        return "full" if len(answers) == len(request.requirements) else "partial" if answers else "abstain"
    never = present("never_abstain_retrieve_and_answer", decision(raw_answers), raw_answers)
    never.update(citations_verified=False, generation_failures=failures)
    if threshold is None:
        confident = {"variant": "confidence_threshold_abstainer", "status": "not_run_uncalibrated",
                     "decision": None, "values": [], "citations": [], "gaps": []}
    else:
        kept = [a for a in raw_answers if a["confidence"] >= threshold]
        confident = present("confidence_threshold_abstainer", decision(kept), kept)
        confident.update(status="synthetic_threshold_only", citations_verified=False)
    graded, assessment = verify_candidates(request, list(packed.evidence), candidates)
    graded["citations_verified"] = True
    return {**common, "status": "generation_failed" if failures else "completed",
            "generation_failures": failures, "generation": generation,
            "policies": [never, confident, graded], "assessment": assessment,
            "notices": ["Engineering skeleton, not an evaluation run. No calibration or performance claims."]}
