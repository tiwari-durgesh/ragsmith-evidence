"""Synthetic-first evaluation with gold inaccessible until predictions exist."""

import copy
import hashlib
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ragsmith.evidence.models import Evidence
from ragsmith.lookup_config import LookupConfig
from ragsmith.lookup_pipeline import assess_lookup_question
from ragsmith.sufficiency.provenance import build_evidence_provenance
from ragsmith.value_lookup import LookupQuestion
from ragsmith.evaluation.lineage import SourceManifest
from ragsmith.evaluation.instrumentation import RunMeasurements, run_environment
from ragsmith.evaluation.retrieval_metrics import (
    RankingRecord, score_retrieval, summarize_retrieval, validate_cutoff,
)
from ragsmith.evaluation.uncertainty import (
    BootstrapConfig, PairedRate, paired_cluster_interval,
)
from ragsmith.evaluation.records import (
    PROVISIONAL, FrozenEvidenceRecord, GoldRecord, read_jsonl,
)


VARIANTS = ("extraction_only", "binary_sufficiency", "graded_sufficiency")
CLASSES = ("full", "partial", "abstain")


def _read_rows(path: Path) -> list[dict]:
    return read_jsonl(path)


def predict(request: LookupQuestion, evidence: list[Evidence]) -> list[dict]:
    """Freeze extraction/evidence and contrast policies without access to gold.

    Evidence list order is the frozen ranking for extraction-only selection.
    Binary and graded share the exact same production verifier judgments.
    No experimental policy modifies production code.
    """
    graded = assess_lookup_question(request, evidence, LookupConfig(True))
    raw_answers = []
    rank = {item.evidence_id: index for index, item in enumerate(evidence)}
    for requirement, discovery in zip(request.requirements, graded["discovery"]):
        if not discovery["candidates"]:
            continue
        candidate = min(discovery["candidates"], key=lambda item: min(
            rank[eid] for eid in item["evidence_ids"]
        ))
        ids = candidate["evidence_ids"]
        raw_answers.append({
            "requirement_id": requirement.requirement_id,
            "metric": requirement.metric, "year": requirement.year,
            "value": candidate["value"],
            "citations": build_evidence_provenance(
                {"requirements": [{"evidence_ids": ids}]}, evidence
            ),
        })
    answers = {
        "extraction_only": raw_answers,
        "binary_sufficiency": graded["answers"]
        if graded["assessment"]["answerability"] == "full" else [],
        "graded_sufficiency": graded["answers"],
    }
    labels = {
        "extraction_only": "full" if raw_answers else "abstain",
        "binary_sufficiency": "full"
        if graded["assessment"]["answerability"] == "full" else "abstain",
        "graded_sufficiency": graded["assessment"]["answerability"],
    }
    return [{"question_id": request.question_id, "variant": variant,
             "answerability": labels[variant], "answers": copy.deepcopy(answers[variant])}
            for variant in VARIANTS]


def _equal_value(actual: str, expected: str) -> bool:
    """Independent strict numeric equality, otherwise exact trimmed text.

    No implicit unit conversion, punctuation stripping, tolerance or gold label
    inference. This scorer deliberately does not call the production verifier.
    """
    try:
        a, b = Decimal(actual.strip()), Decimal(expected.strip())
        return a.is_finite() and b.is_finite() and a == b
    except InvalidOperation:
        return actual.strip() == expected.strip()


def validate_gold(row: dict, request: LookupQuestion) -> str:
    """Validate provisional labels without generating them from system output."""
    return GoldRecord.from_payload(row).validate_request(request)


def score_variant(
    predictions: list[dict], gold: dict, requests: dict, evidence_sets: dict
) -> dict:
    """Score only after inference; retain denominators and excluded counts."""
    confusion = {a: {b: 0 for b in CLASSES} for a in CLASSES}
    counts = Counter()
    coverages = []
    partial_coverages = []
    seen = set()
    for prediction in predictions:
        qid = prediction["question_id"]
        if qid in seen or qid not in gold:
            raise ValueError("Duplicate or unknown prediction question ID")
        seen.add(qid)
        request = requests[qid]
        row = gold[qid]
        record = row if isinstance(row, GoldRecord) else GoldRecord.from_payload(row)
        label = record.validate_request(request)
        if label == "not_adjudicable":
            counts["excluded_not_adjudicable"] += 1
            continue
        predicted = prediction["answerability"]
        if predicted not in CLASSES:
            raise ValueError("Unknown predicted answerability")
        confusion[label][predicted] += 1
        counts["scored_questions"] += 1
        counts["correct_labels"] += label == predicted
        counts["predicted_abstentions"] += predicted == "abstain"
        counts["correct_abstentions"] += label == predicted == "abstain"
        counts["answerable_questions"] += label != "abstain"
        counts["over_abstentions"] += predicted == "abstain" and label != "abstain"
        facts = {item.requirement_id: item for item in record.requirements}
        sources = {item.evidence_id: item for item in evidence_sets[qid]}
        requirements = {item.requirement_id: item for item in request.requirements}
        correct_ids = set()
        answer_ids = set()
        for answer in prediction["answers"]:
            rid = answer["requirement_id"]
            if rid in answer_ids or rid not in facts:
                raise ValueError("Duplicate or unknown answered requirement")
            answer_ids.add(rid)
            fact = facts[rid]
            requirement = requirements[rid]
            correct = (
                fact.status == "supported"
                and answer["metric"] == requirement.metric
                and answer["year"] == requirement.year
                and any(_equal_value(answer["value"], value)
                        for value in fact.acceptable_values)
            )
            if correct:
                correct_ids.add(rid)
            counts["emitted_claims"] += 1
            counts["unsupported_claims"] += not correct
            counts["uncited_claims"] += not answer["citations"]
            for citation in answer["citations"]:
                counts["citation_links"] += 1
                source = sources.get(citation["evidence_id"])
                consistent = source is not None and all(
                    citation.get(name) == getattr(source, name)
                    for name in ("document_id", "document_version", "locator")
                )
                counts["supported_citation_links"] += (
                    correct and consistent
                    and citation["evidence_id"] in fact.evidence_ids
                )
        denominator = sum(fact.status == "supported" for fact in facts.values())
        counts["gold_supported_requirements"] += denominator
        counts["correct_supported_requirements"] += len(correct_ids)
        if denominator:
            coverages.append(len(correct_ids) / denominator)
            if label == "partial":
                partial_coverages.append(len(correct_ids) / denominator)
    if seen != set(gold):
        raise ValueError("Missing predictions cannot be silently excluded")
    f1s = []
    for label in CLASSES:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in CLASSES if other != label)
        fn = sum(confusion[label][other] for other in CLASSES if other != label)
        f1s.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)

    def ratio(numerator: str, denominator: str) -> float | None:
        return counts[numerator] / counts[denominator] if counts[denominator] else None

    for name in (
        "scored_questions", "excluded_not_adjudicable", "correct_labels",
        "predicted_abstentions", "correct_abstentions", "answerable_questions",
        "over_abstentions", "emitted_claims", "unsupported_claims", "uncited_claims",
        "citation_links", "supported_citation_links", "gold_supported_requirements",
        "correct_supported_requirements",
    ):
        counts.setdefault(name, 0)
    return {
        "counts": dict(counts), "confusion": confusion,
        "answerability_accuracy": ratio("correct_labels", "scored_questions"),
        "answerability_macro_f1": sum(f1s) / len(f1s)
        if counts["scored_questions"] else None,
        "supported_coverage_micro": ratio("correct_supported_requirements", "gold_supported_requirements"),
        "supported_coverage_macro": sum(coverages) / len(coverages) if coverages else None,
        "partial_answer_completeness": sum(partial_coverages) / len(partial_coverages)
        if partial_coverages else None,
        "unsupported_claim_rate": ratio("unsupported_claims", "emitted_claims"),
        "citation_precision": ratio("supported_citation_links", "citation_links"),
        "abstention_precision": ratio("correct_abstentions", "predicted_abstentions"),
        "over_abstention_rate": ratio("over_abstentions", "answerable_questions"),
    }


def _run_suite(
    inputs_path: Path, evidence_path: Path, gold_path: Path,
    lineage_path: Path | None, rankings_path: Path | None, retrieval_k: int,
    bootstrap: BootstrapConfig, measurements: RunMeasurements,
) -> dict:
    """Load labels only after all inference; no model or real pilot is run here.

    Data files contain explicit frozen evidence sets (Track A). Retrieval
    metrics and source-derived annotation collection are later batches.
    """
    lineage_path = lineage_path or evidence_path.parent / "lineage.json"
    validate_cutoff(retrieval_k)
    manifest = SourceManifest.from_file(lineage_path)
    initial_hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for name, path in [("inputs", inputs_path),
                                         ("evidence", evidence_path),
                                         ("lineage", lineage_path)]}
    if rankings_path is not None:
        initial_hashes["rankings"] = hashlib.sha256(rankings_path.read_bytes()).hexdigest()
    requests = {}
    for row in _read_rows(inputs_path):
        request = LookupQuestion.from_payload(row)
        manifest.validate_request(request)
        if request.question_id in requests:
            raise ValueError("Duplicate input question ID")
        requests[request.question_id] = request
    if not requests:
        raise ValueError("No evaluation inputs")
    evidence = {}
    for row in _read_rows(evidence_path):
        frozen = FrozenEvidenceRecord.from_payload(row)
        if frozen.question_id in evidence:
            raise ValueError("Invalid or duplicate frozen evidence record")
        evidence[frozen.question_id] = list(frozen.evidence)
        manifest.validate_evidence(evidence[frozen.question_id])
    if set(requests) != set(evidence):
        raise ValueError("Frozen evidence must cover exactly the input questions")
    rankings = {}
    selected_evidence = evidence
    if rankings_path is not None:
        for row in _read_rows(rankings_path):
            ranking = RankingRecord.from_payload(row)
            if ranking.question_id in rankings or ranking.question_id not in requests:
                raise ValueError("Duplicate or unknown ranking question ID")
            rankings[ranking.question_id] = ranking
        if set(rankings) != set(requests):
            raise ValueError("Rankings must cover exactly the input questions")
        selected_evidence = {
            qid: rankings[qid].select(request, evidence[qid], retrieval_k)
            for qid, request in requests.items()
        }
    measurements.checkpoint("load_inputs_validate_lineage_and_rankings")
    predictions = [prediction for qid, request in requests.items()
                   for prediction in predict(request, selected_evidence[qid])]
    measurements.checkpoint("inference_all_variants")
    for items in evidence.values():
        manifest.validate_evidence(items)
    immutable_files = [("inputs", inputs_path), ("evidence", evidence_path),
                       ("lineage", lineage_path)]
    if rankings_path is not None:
        immutable_files.append(("rankings", rankings_path))
    for name, path in immutable_files:
        if hashlib.sha256(path.read_bytes()).hexdigest() != initial_hashes[name]:
            raise ValueError("Evaluation input files changed during inference")
    # Intentionally do not open gold_path until every prediction exists.
    gold = {}
    groups = {}
    for row in _read_rows(gold_path):
        record = GoldRecord.from_payload(row)
        qid = record.question_id
        if qid in gold or qid not in requests:
            raise ValueError("Duplicate or unknown gold question ID")
        record.validate_request(requests[qid])
        manifest.validate_gold_links(record, requests[qid], evidence[qid])
        group = record.group_id
        if group in groups and groups[group] != record.partition:
            raise ValueError("Source family leaks across partitions")
        groups[group] = record.partition
        gold[qid] = record
    if set(gold) != set(requests):
        raise ValueError("Gold must cover exactly the input questions")
    origins = sorted({row.origin for row in gold.values()})
    if len(origins) != 1:
        raise ValueError("Synthetic and source-derived cases must be scored separately")
    partitions = sorted({row.partition for row in gold.values()})
    if len(partitions) != 1:
        raise ValueError("Development and held-out results must be reported separately")
    measurements.checkpoint("validate_after_inference_and_load_gold")
    metrics = {variant: score_variant(
        [row for row in predictions if row["variant"] == variant], gold, requests, evidence,
    ) for variant in VARIANTS}
    retrieval_rows = [row for qid, ranking in rankings.items()
                      for row in score_retrieval(ranking, gold[qid], requests[qid],
                                                 evidence[qid], retrieval_k)]
    measurements.checkpoint("scoring")
    paired_partial, paired_risk = [], []
    by_question = {(row["question_id"], row["variant"]): row for row in predictions}
    for qid, record in gold.items():
        label = record.validate_request(requests[qid])
        if label == "not_adjudicable":
            continue
        counts = {variant: score_variant(
            [by_question[qid, variant]], {qid: record}, {qid: requests[qid]},
            {qid: evidence[qid]},
        )["counts"] for variant in VARIANTS}
        graded, binary, raw = (counts[name] for name in (
            "graded_sufficiency", "binary_sufficiency", "extraction_only"
        ))
        if label == "partial":
            paired_partial.append(PairedRate(
                qid, record.group_id, graded["correct_supported_requirements"],
                graded["gold_supported_requirements"], binary["correct_supported_requirements"],
                binary["gold_supported_requirements"],
            ))
        paired_risk.append(PairedRate(
            qid, record.group_id, graded["unsupported_claims"], graded["emitted_claims"],
            raw["unsupported_claims"], raw["emitted_claims"],
        ))
    uncertainty = {
        "partial_coverage_graded_minus_binary": paired_cluster_interval(
            paired_partial, estimand="paired_mean", config=bootstrap,
        ),
        "unsupported_rate_graded_minus_extraction": paired_cluster_interval(
            paired_risk, estimand="ratio_of_sums", config=bootstrap,
        ),
    }
    measurements.checkpoint("uncertainty")
    return {
        "evaluation_version": "0.3", "annotation_status": PROVISIONAL,
        "track": "B_frozen_rankings" if rankings else "A_fixed_evidence",
        "origin": origins[0], "partition": partitions[0],
        "research_evidence": False,
        "lineage_status": "validated_internal_consistency",
        "file_hashes": {**initial_hashes,
                        "gold": hashlib.sha256(gold_path.read_bytes()).hexdigest()},
        "predictions": predictions,
        "metrics": metrics, "uncertainty": uncertainty,
        "retrieval_metrics": {
            "k_per_requirement": retrieval_k, "per_requirement": retrieval_rows,
            "summary": summarize_retrieval(retrieval_rows),
            "evidence_union_sizes": {qid: len(items) for qid, items in selected_evidence.items()},
        } if rankings else None,
    }


def run_suite(
    inputs_path: Path, evidence_path: Path, gold_path: Path,
    lineage_path: Path | None = None, *, rankings_path: Path | None = None,
    retrieval_k: int = 10, bootstrap: BootstrapConfig = BootstrapConfig(),
    profile_memory: bool = False,
) -> dict:
    """Run fixed-evidence or frozen-ranking evaluation, retaining full-scope gold.

    Profiling records this in-process diagnostic run, not benchmark performance.
    In Track B the evidence file is the full annotated universe; only top-k
    ranked evidence reaches inference. No source label is opened beforehand.
    """
    if not isinstance(bootstrap, BootstrapConfig):
        raise ValueError("bootstrap must be a BootstrapConfig")
    with RunMeasurements(profile_memory) as measurements:
        report = _run_suite(inputs_path, evidence_path, gold_path, lineage_path,
                            rankings_path, retrieval_k, bootstrap, measurements)
        report["environment"] = run_environment(Path(__file__).resolve().parents[3])
        measurements.checkpoint("environment_metadata")
    report["measurements"] = measurements.report()
    return report
