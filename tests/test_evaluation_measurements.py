"""Analytical retrieval/uncertainty examples and profiling boundary tests."""

import json
import math
import tracemalloc
from pathlib import Path

import pytest

from ragsmith.evaluation.harness import run_suite
from ragsmith.evaluation.instrumentation import RunMeasurements, run_environment
from ragsmith.evaluation.records import FrozenEvidenceRecord, GoldRecord, read_jsonl
from ragsmith.evaluation.retrieval_metrics import (
    RankingRecord, score_retrieval, summarize_retrieval,
)
from ragsmith.evaluation.uncertainty import (
    BootstrapConfig, PairedRate, paired_cluster_interval,
)
from ragsmith.value_lookup import LookupQuestion


FIXTURES = Path(__file__).resolve().parents[1] / "data/evaluation/fixtures"


def load_case(index):
    request = LookupQuestion.from_payload(read_jsonl(FIXTURES / "inputs.jsonl")[index])
    universe = list(FrozenEvidenceRecord.from_payload(
        read_jsonl(FIXTURES / "evidence.jsonl")[index]
    ).evidence)
    gold = GoldRecord.from_payload(read_jsonl(FIXTURES / "gold.jsonl")[index])
    rankings = RankingRecord.from_payload(read_jsonl(FIXTURES / "rankings.jsonl")[index])
    return request, universe, gold, rankings


def run(track_b=False, k=10, **kwargs):
    return run_suite(FIXTURES / "inputs.jsonl", FIXTURES / "evidence.jsonl",
                     FIXTURES / "gold.jsonl",
                     rankings_path=FIXTURES / "rankings.jsonl" if track_b else None,
                     retrieval_k=k, **kwargs)


def test_recall_mrr_ndcg_have_hand_calculated_expected_values():
    request, universe, gold, ranking = load_case(0)
    scores = score_retrieval(ranking, gold, request, universe, k=2)
    by_id = {row["requirement_id"]: row for row in scores}
    assert by_id["revenue"]["recall"] == 1.0
    assert by_id["revenue"]["reciprocal_rank"] == 1.0
    assert by_id["profit"]["recall"] == 1.0
    assert by_id["profit"]["reciprocal_rank"] == 0.5
    assert by_id["profit"]["ndcg"] == pytest.approx(1 / math.log2(3))
    summary = summarize_retrieval(scores)
    assert summary["mrr"] == 0.75
    assert summary["ndcg"] == pytest.approx((1 + 1 / math.log2(3)) / 2)


def test_retrieval_miss_is_zero_not_excluded_or_relabelled():
    request, universe, gold, ranking = load_case(0)
    scores = score_retrieval(ranking, gold, request, universe, k=1)
    profit = next(row for row in scores if row["requirement_id"] == "profit")
    assert profit["recall"] == profit["reciprocal_rank"] == profit["ndcg"] == 0.0
    assert profit["excluded_reason"] is None
    assert gold.validate_request(request) == "full"


def test_conflict_recall_requires_both_gold_sources():
    request, universe, gold, ranking = load_case(3)
    scores = score_retrieval(ranking, gold, request, universe, k=1)
    assert scores[0]["gold_evidence_count"] == 2
    assert scores[0]["recall"] == 0.5
    assert summarize_retrieval(scores)["conflict_recall"] == 0.5


def test_no_gold_evidence_is_null_and_exclusion_is_counted():
    request, universe, gold, ranking = load_case(2)
    rows = score_retrieval(ranking, gold, request, universe, k=1)
    assert rows[0]["recall"] is None
    summary = summarize_retrieval(rows)
    assert summary["eligible_requirements"] == 0
    assert summary["excluded_no_gold"] == 1
    assert summary["mrr"] is None


def test_rankings_deduplicate_union_without_changing_per_requirement_k():
    request, universe, _, ranking = load_case(0)
    assert len(ranking.select(request, universe, 1)) == 1
    assert len(ranking.select(request, universe, 2)) == 2


@pytest.mark.parametrize("case", ["duplicate_id", "unknown_id", "duplicate_requirement",
                                  "unknown_requirement", "gold_field"])
def test_ranking_contract_rejects_ambiguous_or_leaking_logs(case):
    row = read_jsonl(FIXTURES / "rankings.jsonl")[0]
    if case == "duplicate_id":
        row["rankings"][0]["evidence_ids"] *= 2
    elif case == "unknown_id":
        row["rankings"][0]["evidence_ids"] = ["invented"]
    elif case == "duplicate_requirement":
        row["rankings"].append(row["rankings"][0])
    elif case == "unknown_requirement":
        row["rankings"][0]["requirement_id"] = "invented"
    else:
        row["rankings"][0]["gold_answer"] = "145"
    request, universe, _, _ = load_case(0)
    with pytest.raises(ValueError):
        RankingRecord.from_payload(row).select(request, universe, 2)


@pytest.mark.parametrize("k", [0, 101, True, 2.5, "5"])
def test_retrieval_cutoff_is_strict(k):
    request, universe, _, ranking = load_case(0)
    with pytest.raises(ValueError, match="retrieval k"):
        ranking.select(request, universe, k)


def test_track_b_only_selected_evidence_reaches_inference(monkeypatch):
    import ragsmith.evaluation.harness as harness
    original = harness.predict
    observed = {}

    def track(request, evidence):
        observed[request.question_id] = [item.evidence_id for item in evidence]
        return original(request, evidence)

    monkeypatch.setattr(harness, "predict", track)
    report = run(track_b=True, k=1)
    assert observed["synthetic-full"] == ["ev-revenue"]
    graded = next(row for row in report["predictions"] if row["question_id"] == "synthetic-full"
                  and row["variant"] == "graded_sufficiency")
    assert graded["answerability"] == "partial"
    assert report["metrics"]["graded_sufficiency"]["counts"]["gold_supported_requirements"] == 4
    assert report["track"] == "B_frozen_rankings"
    assert "rankings" in report["file_hashes"]
    assert report["retrieval_metrics"]["evidence_union_sizes"]["synthetic-full"] == 1


def test_track_b_retains_conflicts_in_gold_when_top_k_hides_them():
    report = run(track_b=True, k=1)
    graded = report["metrics"]["graded_sufficiency"]
    assert graded["confusion"]["abstain"]["full"] == 1
    assert graded["unsupported_claim_rate"] > 0


def test_existing_track_a_metrics_and_single_cluster_guard_remain():
    report = run()
    assert report["metrics"]["graded_sufficiency"]["answerability_accuracy"] == 5 / 6
    assert report["retrieval_metrics"] is None
    for comparison in report["uncertainty"].values():
        assert comparison["clusters"] == 1
        assert comparison["interval"] is None
        assert comparison["undefined_reason"] == "fewer_than_two_clusters"


def test_bootstrap_constant_effect_and_row_order_invariance():
    rows = [PairedRate("q1", "g1", 1, 1, 0, 1),
            PairedRate("q2", "g1", 2, 2, 0, 2),
            PairedRate("q3", "g2", 1, 1, 0, 1)]
    config = BootstrapConfig(replicates=100)
    report = paired_cluster_interval(rows, estimand="paired_mean", config=config)
    assert report["point_difference"] == 1.0
    assert report["interval"] == [1.0, 1.0]
    assert report["clusters"] == 2
    assert report == paired_cluster_interval(list(reversed(rows)),
                                              estimand="paired_mean", config=config)


def test_bootstrap_resamples_whole_clusters_not_rows():
    rows = [PairedRate("a1", "A", 1, 1, 0, 1),
            PairedRate("a2", "A", 0, 1, 1, 1),
            PairedRate("b1", "B", 0, 1, 0, 1)]
    # Each source family has zero mean paired effect. Row-wise resampling
    # would produce nonzero intervals; whole-family sampling must not.
    report = paired_cluster_interval(rows, estimand="paired_mean",
                                     config=BootstrapConfig(replicates=100))
    assert report["interval"] == [0.0, 0.0]


def test_nonconstant_bootstrap_interval_covers_the_known_resampling_support():
    rows = [PairedRate("a", "A", 0, 1, 0, 1),
            PairedRate("b", "B", 1, 1, 0, 1)]
    report = paired_cluster_interval(rows, estimand="paired_mean",
                                     config=BootstrapConfig(replicates=1000))
    # Two whole-cluster draws can yield 0, 0.5 or 1 with probabilities
    # 1/4, 1/2 and 1/4. Both percentile endpoints are therefore known.
    assert report["point_difference"] == 0.5
    assert report["interval"] == [0.0, 1.0]
    assert report["replicates_valid"] == 1000


def test_invalid_ranking_tail_and_document_scope_are_checked_before_cutoff():
    request, universe, _, _ = load_case(0)
    row = read_jsonl(FIXTURES / "rankings.jsonl")[0]
    row["rankings"][0]["evidence_ids"] = ["ev-revenue", "invented-tail"]
    with pytest.raises(ValueError, match="absent from the source universe"):
        RankingRecord.from_payload(row).select(request, universe, 1)
    request_row = read_jsonl(FIXTURES / "inputs.jsonl")[0]
    request_row["requirements"][1]["document_ids"] = ["other-company"]
    scoped = LookupQuestion.from_payload(request_row)
    ranking = RankingRecord.from_payload(read_jsonl(FIXTURES / "rankings.jsonl")[0])
    with pytest.raises(ValueError, match="document scope"):
        ranking.select(scoped, universe, 1)


def test_ratio_of_sums_is_not_a_mean_of_question_rates():
    rows = [PairedRate("a", "A", 1, 1, 0, 1),
            PairedRate("b", "B", 0, 9, 0, 9)]
    pooled = paired_cluster_interval(rows, estimand="ratio_of_sums",
                                     config=BootstrapConfig(replicates=100))
    mean = paired_cluster_interval(rows, estimand="paired_mean",
                                   config=BootstrapConfig(replicates=100))
    assert pooled["point_difference"] == 0.1
    assert mean["point_difference"] == 0.5


def test_undefined_resamples_are_not_silently_dropped():
    rows = [PairedRate("a", "A", 1, 1, 0, 1),
            PairedRate("b", "B", 0, 0, 0, 0)]
    report = paired_cluster_interval(rows, estimand="ratio_of_sums",
                                     config=BootstrapConfig(replicates=100))
    assert report["point_difference"] == 1
    assert report["replicates_undefined"] > 0
    assert report["interval"] is None
    assert report["undefined_reason"] == "undefined_metric_in_resamples"


def test_undefined_point_and_pair_exclusions_are_reported():
    rows = [PairedRate("a", "A", 0, 0, 0, 1)]
    report = paired_cluster_interval(rows, estimand="paired_mean")
    assert report["excluded_undefined_pairs"] == 1
    assert report["point_difference"] is None
    assert report["interval"] is None
    assert report["undefined_reason"] == "undefined_point_metric"


@pytest.mark.parametrize("field,value", [
    ("replicates", 0), ("replicates", True), ("replicates", 100001),
    ("seed", "1729"), ("seed", False), ("confidence", 1),
    ("confidence", float("nan")), ("confidence", True),
])
def test_bootstrap_configuration_rejects_invalid_types(field, value):
    with pytest.raises(ValueError):
        BootstrapConfig(**{field: value})


def test_rate_validation_duplicate_ids_and_estimator_errors():
    with pytest.raises(ValueError):
        PairedRate("q", "g", 2, 1, 0, 1)
    with pytest.raises(ValueError):
        PairedRate("q", "g", float("inf"), 1, 0, 1)
    row = PairedRate("q", "g", 1, 1, 0, 1)
    with pytest.raises(ValueError, match="Duplicate"):
        paired_cluster_interval([row, row], estimand="paired_mean")
    with pytest.raises(ValueError, match="Unknown"):
        paired_cluster_interval([row], estimand="not_an_estimand")


def test_measurement_stages_are_nonnegative_and_not_fake_rss():
    with RunMeasurements() as measurements:
        with measurements.stage("work"):
            _ = sum(range(100))
    report = measurements.report()
    assert report["seconds"]["total"] >= report["seconds"]["work"] >= 0
    assert report["memory"]["python_peak_bytes"] is None
    assert report["memory"]["process_peak_rss_bytes"] is None
    assert report["live_retrieval_seconds"] is None


def test_memory_profiler_releases_owned_session_on_error():
    if tracemalloc.is_tracing():
        pytest.skip("An external profiler owns the process session")
    with pytest.raises(RuntimeError):
        with RunMeasurements(True) as measurements:
            _ = bytearray(10000)
            raise RuntimeError("synthetic failure")
    assert not tracemalloc.is_tracing()
    assert measurements.report()["memory"]["python_peak_bytes"] >= 10000


def test_memory_profiler_does_not_reset_or_stop_existing_session():
    owned = not tracemalloc.is_tracing()
    if owned:
        tracemalloc.start()
    try:
        with RunMeasurements(True) as measurements:
            pass
        assert tracemalloc.is_tracing()
        assert measurements.report()["memory"]["method"] == "unavailable_existing_tracemalloc_session"
    finally:
        if owned:
            tracemalloc.stop()


def test_environment_metadata_failure_is_explicit(tmp_path):
    report = run_environment(tmp_path)
    assert report["git_metadata_status"] == "unavailable"
    assert report["git_commit"] is None
    assert report["python"]


def test_profiled_suite_remains_serializable_and_records_shared_timing():
    report = run(profile_memory=True)
    assert "inference_all_variants" in report["measurements"]["seconds"]
    assert "uncertainty" in report["measurements"]["seconds"]
    assert report["environment"]["git_commit"]
    assert report["research_evidence"] is False
    assert report["annotation_status"] == "provisional, single-annotator"
    assert json.loads(json.dumps(report, allow_nan=False)) == report
