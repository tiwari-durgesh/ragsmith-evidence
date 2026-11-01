"""Independent numerical checks and leakage/error cases for the pilot harness."""

import copy
import json
from pathlib import Path

import pytest

from ragsmith.evaluation.agreement import cohen_kappa, compare_annotation_files
from ragsmith.evaluation.corpus_audit import count_questions
from ragsmith.evaluation.harness import PROVISIONAL, run_suite


FIXTURES = Path(__file__).resolve().parents[1] / "data/evaluation/fixtures"


def suite(directory=FIXTURES):
    return run_suite(directory / "inputs.jsonl", directory / "evidence.jsonl",
                     directory / "gold.jsonl")


def copy_fixtures(tmp_path):
    for name in ("inputs", "evidence", "gold"):
        (tmp_path / f"{name}.jsonl").write_text(
            (FIXTURES / f"{name}.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
        )


def rewrite(path, transform):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    transform(rows)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_synthetic_expected_tradeoffs_are_measured_not_assumed():
    report = suite()
    assert report["annotation_status"] == PROVISIONAL
    assert report["research_evidence"] is False
    metrics = report["metrics"]
    assert metrics["graded_sufficiency"]["partial_answer_completeness"] == 1.0
    assert metrics["binary_sufficiency"]["partial_answer_completeness"] == 0.0
    assert metrics["graded_sufficiency"]["unsupported_claim_rate"] == 0.0
    assert metrics["extraction_only"]["unsupported_claim_rate"] > 0.0
    # Text is human-answerable but unsupported by production: do not relabel gold.
    assert metrics["graded_sufficiency"]["answerability_accuracy"] == 5 / 6
    assert json.loads(json.dumps(report, allow_nan=False)) == report


def test_gold_is_opened_only_after_all_inference(monkeypatch):
    import ragsmith.evaluation.harness as harness
    original_read = harness._read_rows
    original_predict = harness.predict
    events = []

    def track_read(path):
        events.append(path.name)
        return original_read(path)

    def track_predict(request, evidence):
        events.append("predict")
        return original_predict(request, evidence)

    monkeypatch.setattr(harness, "_read_rows", track_read)
    monkeypatch.setattr(harness, "predict", track_predict)
    suite()
    assert events.count("predict") == 6
    assert events.index("gold.jsonl") > max(i for i, event in enumerate(events)
                                           if event == "predict")


@pytest.mark.parametrize("field", ["expected_value", "gold_answer", "answerability"])
def test_gold_fields_rejected_in_system_inputs(tmp_path, field):
    copy_fixtures(tmp_path)
    rewrite(tmp_path / "inputs.jsonl", lambda rows: rows[0].update({field: "145"}))
    with pytest.raises(ValueError):
        suite(tmp_path)


@pytest.mark.parametrize("case", ["status", "duplicate_gold", "missing_gold", "group_leak",
                                  "mixed_origins", "missing_evidence", "mixed_partitions"])
def test_invalid_or_misleading_evaluation_records_rejected(tmp_path, case):
    copy_fixtures(tmp_path)

    def change(rows):
        if case == "status":
            rows[0]["annotation_status"] = "reviewed"
        elif case == "duplicate_gold":
            rows.append(copy.deepcopy(rows[0]))
        elif case == "missing_gold":
            rows.pop()
        elif case in {"group_leak", "mixed_partitions"}:
            rows[0]["partition"] = "held_out"
            if case == "mixed_partitions":
                rows[0]["group_id"] = "another-group"
        elif case == "mixed_origins":
            rows[0]["origin"] = "tatqa-derived"

    if case == "missing_evidence":
        rewrite(tmp_path / "evidence.jsonl", lambda rows: rows.pop())
    else:
        rewrite(tmp_path / "gold.jsonl", change)
    with pytest.raises(ValueError):
        suite(tmp_path)


def test_zero_claim_denominator_is_null_not_perfect_score(tmp_path):
    copy_fixtures(tmp_path)
    for name in ("inputs", "evidence", "gold"):
        rewrite(tmp_path / f"{name}.jsonl", lambda rows: rows.__setitem__(
            slice(None), [row for row in rows if row["question_id"] == "synthetic-missing"]
        ))
    metrics = suite(tmp_path)["metrics"]["graded_sufficiency"]
    assert metrics["unsupported_claim_rate"] is None
    assert metrics["citation_precision"] is None
    assert metrics["partial_answer_completeness"] is None
    assert metrics["counts"]["emitted_claims"] == 0
    assert metrics["counts"]["citation_links"] == 0


def test_altered_gold_cannot_change_predictions(tmp_path):
    original = suite()
    copy_fixtures(tmp_path)
    rewrite(tmp_path / "gold.jsonl", lambda rows: rows[0]["requirements"][0].update(
        {"acceptable_values": ["99999"]}
    ))
    altered = suite(tmp_path)
    assert altered["predictions"] == original["predictions"]
    assert altered["metrics"]["graded_sufficiency"]["supported_coverage_micro"] < (
        original["metrics"]["graded_sufficiency"]["supported_coverage_micro"]
    )


def test_all_nonadjudicable_cases_report_exclusions_and_null_accuracy(tmp_path):
    copy_fixtures(tmp_path)

    def change(rows):
        for row in rows:
            for fact in row["requirements"]:
                fact.update({"status": "not_adjudicable", "acceptable_values": []})

    rewrite(tmp_path / "gold.jsonl", change)
    metrics = suite(tmp_path)["metrics"]["graded_sufficiency"]
    assert metrics["answerability_accuracy"] is None
    assert metrics["answerability_macro_f1"] is None
    assert metrics["counts"]["excluded_not_adjudicable"] == 6


def test_kappa_known_positive_and_negative_examples():
    a = dict(zip("abcd", ["full", "full", "partial", "partial"]))
    b = dict(zip("abcd", ["full", "full", "full", "partial"]))
    report = cohen_kappa(a, b)
    assert report["observed_agreement"] == 0.75
    assert report["expected_agreement"] == 0.5
    assert report["kappa"] == 0.5
    assert report["disagreement_ids"] == ["c"]
    assert cohen_kappa({"a": "full", "b": "partial"},
                       {"b": "full", "a": "partial"})["kappa"] == -1.0


def test_kappa_degenerate_and_empty_cases_are_explicit():
    assert cohen_kappa({}, {})["kappa"] is None
    report = cohen_kappa({"a": "full"}, {"a": "full"})
    assert report["kappa"] is None
    assert report["observed_agreement"] == 1.0
    assert report["undefined_reason"] == "expected agreement is one"


def test_kappa_pairs_by_id_and_never_drops_unmatched_labels():
    with pytest.raises(ValueError, match="same item IDs"):
        cohen_kappa({"a": "full"}, {"b": "full"})
    assert cohen_kappa({"a": "full", "b": "partial"},
                       {"b": "partial", "a": "full"})["kappa"] == 1.0


@pytest.mark.parametrize("case", ["same_annotator", "duplicate", "unknown_label"])
def test_agreement_files_validate_independence_and_labels(tmp_path, case):
    left = tmp_path / "a.jsonl"
    right = tmp_path / "b.jsonl"
    first = {"item_id": "q1", "annotator_id": "A", "label": "full"}
    second = {**first, "annotator_id": "B"}
    if case == "same_annotator":
        second["annotator_id"] = "A"
    elif case == "unknown_label":
        second["label"] = "yes"
    left.write_text(json.dumps(first) + "\n", encoding="utf-8")
    if case == "duplicate":
        left.write_text((json.dumps(first) + "\n") * 2, encoding="utf-8")
    right.write_text(json.dumps(second) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        compare_annotation_files(left, right)


def test_scope_audit_counts_label_gate_without_claiming_compatibility():
    contexts = [{"questions": [
        {"uid": "a", "answer_type": "span", "answer_from": "table"},
        {"uid": "b", "answer_type": "multi-span", "answer_from": "text"},
        {"uid": "c", "answer_type": "arithmetic", "answer_from": "table"},
    ]}]
    result = count_questions(contexts)
    assert result["questions"] == 3
    assert result["extraction_labels"] == 2
    assert result["table_span_screen"] == 1
    assert result["extraction_fraction"] == 2 / 3


def test_citation_scoring_checks_provenance_and_does_not_call_the_verifier(monkeypatch):
    import ragsmith.evaluation.harness as harness
    from ragsmith.evidence.models import Evidence
    from ragsmith.sufficiency import structured_verifier
    from ragsmith.value_lookup import LookupQuestion

    request_row = json.loads((FIXTURES / "inputs.jsonl").read_text().splitlines()[0])
    evidence_row = json.loads((FIXTURES / "evidence.jsonl").read_text().splitlines()[0])
    gold_row = json.loads((FIXTURES / "gold.jsonl").read_text().splitlines()[0])
    request = LookupQuestion.from_payload(request_row)
    evidence = [Evidence(**row) for row in evidence_row["evidence"]]
    prediction = harness.predict(request, evidence)[2]
    prediction["answers"][0]["citations"][0]["locator"] = "invented"

    def forbidden(*args, **kwargs):
        pytest.fail("scoring must not use the production verifier as gold")

    monkeypatch.setattr(structured_verifier, "verify_metric_value", forbidden)
    qid = request.question_id
    metrics = harness.score_variant([prediction], {qid: gold_row}, {qid: request},
                                    {qid: evidence})
    assert metrics["citation_precision"] == 0.5
    assert metrics["supported_coverage_micro"] == 1.0
