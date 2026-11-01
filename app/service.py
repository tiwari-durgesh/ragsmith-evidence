"""Thin orchestration of external ingestion and frozen QA/pilot policies."""

from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from ragsmith.evaluation.harness import predict
from ragsmith.lookup_config import LookupConfig
from ragsmith.lookup_pipeline import assess_lookup_question
from ragsmith.qa import MetricAssertion
from ragsmith.response import render_lookup_response
from ragsmith.retrieval import RetrievalConfig, retrieve_question_evidence
from ragsmith.supporting_citations import supporting_citations
from ragsmith.sufficiency.aggregator import aggregate_judgments
from ragsmith.sufficiency.question_assessment import assess_question
from ragsmith.sufficiency.reporting import build_assessment_report
from ragsmith.sufficiency.results import SufficiencyResult
from ragsmith.sufficiency.structured_verifier import verify_metric_value
from ragsmith.value_lookup import LookupQuestion, MetricLookup

from app.models import AskRequest
from app.runtime import LocalRuntime, conservative_token_count, pack
from scripts.tatqa_excerpt_ingestion import adapt_table, digest, write_database


def present(variant: str, decision: str, answers: list[dict], *, gaps: list[dict] | None = None) -> dict:
    citations, numbers, values = [], {}, []
    for answer in answers:
        refs = []
        for citation in answer.get("citations", []):
            eid = citation["evidence_id"]
            if eid not in numbers:
                numbers[eid] = len(citations) + 1
                citations.append({"citation_number": numbers[eid], **citation})
            refs.append(numbers[eid])
        values.append({k: v for k, v in answer.items() if k != "citations"} | {"citation_numbers": refs})
    return {"variant": variant, "decision": decision, "values": values,
            "citations": citations, "gaps": gaps or []}


def research_policies(request, evidence, candidates, threshold):
    """Same candidate cache for all policies; every graded claim uses frozen verification."""
    by_id = {c["requirement_id"]: c for c in candidates}
    evidence_by_id = {e.evidence_id: e for e in evidence}
    statuses, raw_answers, verified_answers = [], [], []
    for r in request.requirements:
        candidate = by_id[r.requirement_id]
        value = candidate["value"]
        if not value.strip():
            statuses.append(SufficiencyResult(r.requirement_id, "unverified", [],
                                              "No generated value; generation failure, not source absence"))
            continue
        source_citations = [{"evidence_id": e.evidence_id, "document_id": e.document_id,
                             "document_version": e.document_version, "locator": e.locator,
                             "unit": (e.metadata or {}).get("unit", "")}
                            for eid in candidate["citations"] for e in [evidence_by_id[eid]]]
        answer = {"requirement_id": r.requirement_id, "metric": r.metric, "year": r.year,
                  "value": value, "confidence": candidate["confidence"], "citations": source_citations}
        raw_answers.append(answer)
        result = aggregate_judgments(r.requirement_id, [
            verify_metric_value(e, r.metric, r.year, value, r.requirement_id) for e in r.scope(evidence)])
        support = supporting_citations(MetricAssertion(r.requirement_id, r.metric, r.year, value), r.scope(evidence))
        support = [c for c in support if c["evidence_id"] in candidate["citations"]]
        if result.status == "supported" and not support:
            result = SufficiencyResult(r.requirement_id, "unverified", candidate["citations"],
                                        "Generated citations do not support the candidate")
        statuses.append(result)
        if result.status == "supported":
            verified_answers.append({**answer, "citations": support})
    assessment = build_assessment_report(assess_question(statuses))
    if assessment["answerability"] == "abstain":
        verified_answers = []
    confident = [a for a in raw_answers if a["confidence"] >= threshold]

    def decision(answers):
        return "full" if len(answers) == len(request.requirements) else "partial" if answers else "abstain"

    gaps = [{"requirement_id": s.requirement_id, "status": s.status, "explanation": s.reason}
            for s in statuses if s.status != "supported"]
    policies = [present("never_abstain_retrieve_and_answer", decision(raw_answers), raw_answers),
                present("confidence_threshold_abstainer", decision(confident), confident),
                present("graded_sufficiency", assessment["answerability"], verified_answers, gaps=gaps)]
    for policy in policies:
        policy["candidate_cache_shared"] = True
        policy["confidence_calibrated"] = False
        policy["demo_threshold"] = threshold
        policy["citations_verified"] = policy["variant"] == "graded_sufficiency"
    return policies, assessment


def answer(payload: AskRequest, runtime: LocalRuntime | None = None) -> dict:
    context_id = "request-" + digest([payload.source_reference, payload.table])[:16]
    adapted = adapt_table(context_id, payload.table, paragraphs=payload.paragraphs,
                          source_reference=payload.source_reference, unit=payload.source_unit)
    request = LookupQuestion("demo-" + digest(payload.model_dump())[:16], payload.question, tuple(
        MetricLookup(f.requirement_id, f.metric, f.year, (adapted.document_id,)) for f in payload.requested_facts))
    with TemporaryDirectory(prefix="ragsmith-api-") as folder:
        folder = Path(folder)
        db = folder / "source.sqlite"
        write_database(adapted, db, folder / "source.json")
        retrieved = retrieve_question_evidence(db, request, RetrievalConfig(8))
    ranked = sorted(retrieved.evidence, key=lambda e: (
        min(h["rank"] for q in retrieved.audit["queries"] for h in q["hits"] if h["evidence_id"] == e.evidence_id),
        e.evidence_id))
    counter = conservative_token_count
    if payload.answerer == "local_llm":
        runtime = runtime or LocalRuntime()
        counter = runtime.count
    packed = pack(request, ranked, counter)
    evidence = list(packed.evidence)
    result = assess_lookup_question(request, evidence, LookupConfig(True))
    # QA assessment retains its frozen schema. Transport-only audit sits outside it.
    rendered = render_lookup_response(result)
    main = present("graded_sufficiency", result["assessment"]["answerability"], result["answers"],
                   gaps=rendered["unsupported_requirements"])
    legacy = [present(p["variant"], p["answerability"], p["answers"])
              for p in predict(request, evidence)]
    generation = {"inference_requests": 0, "mode": "frozen deterministic lookup"}
    policies = legacy
    baseline_family = "frozen_pilot_baselines"
    if payload.answerer == "local_llm":
        candidates, generation = runtime.generate(request, packed)
        policies, candidate_assessment = research_policies(request, evidence, candidates, payload.demo_confidence_threshold)
        main = policies[-1]
        main["candidate_assessment"] = candidate_assessment
        baseline_family = "research_policies_demo_uncalibrated"
    # Source/cell coordinates are always available for front-end inspection; no
    # claim that a user-submitted table is an authenticated issuer document.
    return {"question_id": request.question_id, "decision": main["decision"],
            "values": main["values"], "citations": main["citations"],
            "gap_explanation": main["gaps"] or [
                {"requirement_id": r["requirement_id"], "status": r["status"], "explanation": r["reason"]}
                for r in result["assessment"]["requirements"] if r["status"] != "supported"],
            "baseline_family": baseline_family, "baselines": policies,
            "assessment": result["assessment"], "assessment_scope": "frozen source-lookup assessment",
            "lookup_response": rendered,
            "candidate_assessment": main.get("candidate_assessment"),
            "retrieval": {"method": retrieved.audit["method"], "retrieved_units": len(ranked),
                          "per_requirement_limit": 8, "queries": [
                              {k: v for k, v in q.items() if k != "hits"} for q in retrieved.audit["queries"]]},
            "packing": {**packed.audit, "token_count_method": "fixed Qwen tokenizer" if payload.answerer == "local_llm" else "conservative UTF-8-byte upper bound"},
            "generation": generation, "source": {"document_id": adapted.document_id,
                "sha256": adapted.source_version, "reference": payload.source_reference, "unit": payload.source_unit,
                "provenance_scope": "submitted source snapshot, not authenticated issuer bytes",
                "canonical_cells": sum(e.kind == "table_row" for e in adapted.evidence),
                "unsupported_units": sum(e.kind != "table_row" for e in adapted.evidence)},
            "source_audit": list(adapted.audit),
            "notices": ["Demo only; no research scores, tuning or calibration.",
                        "Lookup mode shows the frozen pilot's three policies; local_llm uses the research policies with an uncalibrated demo threshold.",
                        "Decisions concern the packed evidence; truncation can omit support or conflicts."]}
