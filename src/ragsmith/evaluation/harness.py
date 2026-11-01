"""Synthetic-first evaluation with gold inaccessible until predictions exist."""

import copy
import hashlib
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ragsmith.evidence.models import Evidence
from ragsmith.lookup_config import LookupConfig
from ragsmith.lookup_pipeline import assess_lookup_question
from ragsmith.sufficiency.provenance import build_evidence_provenance
from ragsmith.value_lookup import LookupQuestion


PROVISIONAL = "provisional, single-annotator"
VARIANTS = ("extraction_only", "binary_sufficiency", "graded_sufficiency")
CLASSES = ("full", "partial", "abstain")


def _read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


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
    if set(row) != {"question_id", "group_id", "partition", "origin",
                    "annotation_status", "annotator_id", "requirements"}:
        raise ValueError("Invalid gold fields")
    if row["annotation_status"] != PROVISIONAL:
        raise ValueError("Pilot labels must remain provisional, single-annotator")
    for name in ("group_id", "annotator_id"):
        if not isinstance(row[name], str) or not row[name].strip():
            raise ValueError(f"Gold {name} must be nonempty")
    if row["origin"] not in {"synthetic", "tatqa-derived"}:
        raise ValueError("Unknown label origin")
    if row["partition"] not in {"diagnostic", "development", "held_out"}:
        raise ValueError("Unknown partition")
    facts = row["requirements"]
    if not isinstance(facts, list) or not facts:
        raise ValueError("Gold requirements must be a nonempty list")
    ids = [fact["requirement_id"] for fact in facts]
    if len(ids) != len(set(ids)) or set(ids) != {
        item.requirement_id for item in request.requirements
    }:
        raise ValueError("Gold requirement IDs must match the system input")
    for fact in facts:
        if set(fact) != {"requirement_id", "status", "acceptable_values", "evidence_ids"}:
            raise ValueError("Invalid gold requirement fields")
        if fact["status"] not in {"supported", "missing", "conflicted", "not_adjudicable"}:
            raise ValueError("Unknown gold requirement status")
        for name in ("acceptable_values", "evidence_ids"):
            values = fact[name]
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value.strip() for value in values
            ) or len(values) != len(set(values)):
                raise ValueError(f"Invalid gold {name}")
        if fact["status"] == "supported":
            if not fact["acceptable_values"] or not fact["evidence_ids"]:
                raise ValueError("Supported gold facts need values and source evidence IDs")
        elif fact["acceptable_values"]:
            raise ValueError("Only unambiguous supported facts have acceptable values")
    states = [fact["status"] for fact in facts]
    if "not_adjudicable" in states:
        return "not_adjudicable"
    if "conflicted" in states or "supported" not in states:
        return "abstain"
    return "full" if all(state == "supported" for state in states) else "partial"


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
        label = validate_gold(row, request)
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
        facts = {item["requirement_id"]: item for item in row["requirements"]}
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
                fact["status"] == "supported"
                and answer["metric"] == requirement.metric
                and answer["year"] == requirement.year
                and any(_equal_value(answer["value"], value)
                        for value in fact["acceptable_values"])
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
                    and citation["evidence_id"] in fact["evidence_ids"]
                )
        denominator = sum(fact["status"] == "supported" for fact in facts.values())
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


def run_suite(inputs_path: Path, evidence_path: Path, gold_path: Path) -> dict:
    """Load labels only after all inference; no model or real pilot is run here.

    Data files contain explicit frozen evidence sets (Track A). Retrieval
    metrics and source-derived annotation collection are later batches.
    """
    requests = {}
    for row in _read_rows(inputs_path):
        request = LookupQuestion.from_payload(row)
        if request.question_id in requests:
            raise ValueError("Duplicate input question ID")
        requests[request.question_id] = request
    if not requests:
        raise ValueError("No evaluation inputs")
    evidence = {}
    for row in _read_rows(evidence_path):
        if set(row) != {"question_id", "evidence"} or row["question_id"] in evidence:
            raise ValueError("Invalid or duplicate frozen evidence record")
        evidence[row["question_id"]] = [Evidence(**item) for item in row["evidence"]]
    if set(requests) != set(evidence):
        raise ValueError("Frozen evidence must cover exactly the input questions")
    predictions = [prediction for qid, request in requests.items()
                   for prediction in predict(request, evidence[qid])]
    # Intentionally do not open gold_path until every prediction exists.
    gold = {}
    groups = {}
    for row in _read_rows(gold_path):
        qid = row["question_id"]
        if qid in gold or qid not in requests:
            raise ValueError("Duplicate or unknown gold question ID")
        validate_gold(row, requests[qid])
        group = row["group_id"]
        if group in groups and groups[group] != row["partition"]:
            raise ValueError("Source family leaks across partitions")
        groups[group] = row["partition"]
        gold[qid] = row
    if set(gold) != set(requests):
        raise ValueError("Gold must cover exactly the input questions")
    origins = sorted({row["origin"] for row in gold.values()})
    if len(origins) != 1:
        raise ValueError("Synthetic and source-derived cases must be scored separately")
    partitions = sorted({row["partition"] for row in gold.values()})
    if len(partitions) != 1:
        raise ValueError("Development and held-out results must be reported separately")
    return {
        "evaluation_version": "0.1", "annotation_status": PROVISIONAL,
        "origin": origins[0], "partition": partitions[0],
        "research_evidence": False,
        "file_hashes": {name: hashlib.sha256(path.read_bytes()).hexdigest()
                        for name, path in [("inputs", inputs_path),
                                           ("evidence", evidence_path), ("gold", gold_path)]},
        "predictions": predictions,
        "metrics": {variant: score_variant(
            [row for row in predictions if row["variant"] == variant], gold, requests,
            evidence,
        ) for variant in VARIANTS},
    }
