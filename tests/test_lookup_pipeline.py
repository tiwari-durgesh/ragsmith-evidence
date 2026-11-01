"""Integration of discovery, unchanged verification, and support-only answers."""

import json

import pytest

import ragsmith.lookup_pipeline as pipeline
from ragsmith.evidence.models import Evidence
from ragsmith.lookup_config import LookupConfig
from ragsmith.qa import MetricAssertion
from ragsmith.sufficiency.pipeline import generate_structured_assessment_report
from ragsmith.supporting_citations import supporting_citations
from ragsmith.value_lookup import (
    DiscoveryResult, LookupCandidate, LookupQuestion, MetricLookup,
)


ENABLED = LookupConfig(value_lookup_enabled=True)


def row(eid="ev1", metric="Revenue", value="145", kind="table_row", doc="d1"):
    return Evidence(eid, doc, "v1", kind, f"Metric: {metric}; 2025: {value}",
                    "table:1/row:2", table_id="table:1", row_index=2)


def question(*metrics):
    return LookupQuestion("q1", "What were the requested facts in 2025?", tuple(
        MetricLookup(f"r{i}", metric, 2025) for i, metric in enumerate(metrics or ("Revenue",))
    ))


def test_full_answer_uses_discovered_values_and_support_only_citations():
    items = [row(), row("profit", "Profit", "30", doc="d2"), row("other", "Assets", "500")]
    result = pipeline.assess_lookup_question(question("Revenue", "Profit"), items, ENABLED)
    assert result["assessment"]["answerability"] == "full"
    assert [(item["metric"], item["value"]) for item in result["answers"]] == [
        ("Revenue", "145"), ("Profit", "30"),
    ]
    assert [[cite["evidence_id"] for cite in answer["citations"]]
            for answer in result["answers"]] == [["ev1"], ["profit"]]
    assert {cite["evidence_id"] for cite in result["assessment"]["evidence_provenance"]} == {
        "ev1", "profit", "other",
    }
    assert result["answers"][1]["citations"][0]["document_id"] == "d2"
    assert json.loads(json.dumps(result)) == result


def test_partial_answer_marks_missing_and_omits_unsupported_fact():
    result = pipeline.assess_lookup_question(question("Revenue", "Employees"), [row()], ENABLED)
    assert result["assessment"]["answerability"] == "partial"
    assert result["assessment"]["coverage"] == 0.5
    assert [item["status"] for item in result["assessment"]["requirements"]] == [
        "supported", "missing",
    ]
    assert len(result["answers"]) == 1
    assert result["answers"][0]["metric"] == "Revenue"


@pytest.mark.parametrize("items,status", [
    ([], "missing"), ([row(metric="Assets")], "missing"),
    ([row(kind="text")], "unverified"),
    ([row(metric="Assets"), row("text", kind="text")], "unverified"),
])
def test_missing_distinguished_from_uninterpretable_evidence(items, status):
    result = pipeline.assess_lookup_question(question(), items, ENABLED)
    assert result["assessment"]["requirements"][0]["status"] == status
    assert result["assessment"]["answerability"] == "abstain"
    assert result["answers"] == []


def test_conflict_anywhere_suppresses_all_answer_claims():
    result = pipeline.assess_lookup_question(question("Revenue", "Profit"), [
        row(), row("conflict", value="150", doc="d2"), row("profit", "Profit", "30"),
    ], ENABLED)
    assert result["assessment"]["answerability"] == "abstain"
    assert [item["status"] for item in result["assessment"]["requirements"]] == [
        "contradicted", "supported",
    ]
    assert result["answers"] == []
    assert len(result["discovery"][0]["candidates"]) == 2
    assert len(result["assessment"]["evidence_provenance"]) == 3


def test_equivalent_numeric_candidates_are_not_conflicts():
    result = pipeline.assess_lookup_question(question(), [row(), row("equal", value="145.00")], ENABLED)
    assert result["assessment"]["answerability"] == "full"
    assert len(result["answers"]) == 1
    assert {item["evidence_id"] for item in result["answers"][0]["citations"]} == {"ev1", "equal"}


def test_every_discovered_candidate_is_verified_against_every_scoped_item(monkeypatch):
    original = pipeline.structured_verifier.verify_metric_value
    calls = []

    def track(item, metric, year, expected, requirement_id):
        calls.append((expected, item.evidence_id))
        return original(item, metric, year, expected, requirement_id)

    monkeypatch.setattr(pipeline.structured_verifier, "verify_metric_value", track)
    pipeline.assess_lookup_question(question(), [row(), row("conflict", value="150")], ENABLED)
    assert set(calls) == {("145", "ev1"), ("145", "conflict"),
                          ("150", "ev1"), ("150", "conflict")}


def test_discovery_cannot_bypass_verifier(monkeypatch):
    monkeypatch.setattr(pipeline, "discover_values", lambda *_: DiscoveryResult(
        (LookupCandidate("invented", ("ev1",)),), (),
    ))
    result = pipeline.assess_lookup_question(question(), [row()], ENABLED)
    assert result["assessment"]["requirements"][0]["status"] == "contradicted"
    assert result["answers"] == []


def test_disabled_switch_skips_discovery_and_verifier_without_oracle_fallback(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("disabled lookup must not discover or verify values")

    monkeypatch.setattr(pipeline, "discover_values", forbidden)
    monkeypatch.setattr(pipeline.structured_verifier, "verify_metric_value", forbidden)
    result = pipeline.assess_lookup_question(question(), [row()])
    assert result["config"] == {"value_lookup_enabled": False}
    assert result["assessment"]["requirements"][0]["status"] == "unverified"
    assert result["assessment"]["answerability"] == "abstain"
    assert result["discovery"][0]["candidates"] == []
    assert result["answers"] == []


def test_same_inputs_enable_disable_ablation(tmp_path):
    path = tmp_path / "lookup.json"
    outcomes = []
    for enabled in (True, False):
        path.write_text(json.dumps({"value_lookup_enabled": enabled}), encoding="utf-8")
        config = LookupConfig.from_file(path)
        result = pipeline.assess_lookup_question(question(), [row()], config)
        outcomes.append(result["assessment"]["answerability"])
    assert outcomes == ["full", "abstain"]


def test_explicit_document_scope_excludes_other_companies_or_versions():
    request = LookupQuestion("q1", "Revenue?", (MetricLookup("r1", "Revenue", 2025, ("d1",)),))
    result = pipeline.assess_lookup_question(request, [
        row(), row("foreign", value="999", doc="d2"),
    ], ENABLED)
    assert result["assessment"]["answerability"] == "full"
    assert [item["evidence_id"] for item in result["answers"][0]["citations"]] == ["ev1"]


@pytest.mark.parametrize("config", [LookupConfig(), ENABLED])
def test_duplicate_evidence_is_rejected_with_either_switch(config):
    item = row()
    with pytest.raises(ValueError, match="Duplicate evidence IDs"):
        pipeline.assess_lookup_question(question(), [item, item], config)


def test_assessment_schema_and_legacy_semantics_remain_compatible():
    items = [row()]
    legacy = generate_structured_assessment_report([("r0", "Revenue", 2025, "145")], items)
    lookup = pipeline.assess_lookup_question(question(), items, ENABLED)
    assert lookup["assessment"] == legacy
    original_missing = generate_structured_assessment_report([("r0", "Revenue", 2025, "145")], [])
    assert original_missing["requirements"][0]["status"] == "unverified"
    assert set(original_missing) == set(lookup["assessment"])


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_candidate_does_not_bypass_existing_numeric_rules(value):
    result = pipeline.assess_lookup_question(question(), [row(value=value)], ENABLED)
    assert result["assessment"]["answerability"] == "abstain"
    assert result["answers"] == []


def test_supporting_citation_filter_rechecks_support_and_preserves_locator():
    assertion = MetricAssertion("r1", "Revenue", 2025, "145")
    items = [row(), row("other", "Assets"), row("text", kind="text")]
    citations = supporting_citations(assertion, items)
    assert [item["evidence_id"] for item in citations] == ["ev1"]
    assert citations[0]["locator"] == "table:1/row:2"
    assert citations[0]["document_version"] == "v1"
    assert supporting_citations(assertion, []) == []
    assert supporting_citations(assertion, [row(), row("conflict", value="150")]) == []


@pytest.mark.parametrize("value", ["true", "false", 1, 0, None])
def test_config_boolean_is_strict(value):
    with pytest.raises(ValueError, match="boolean"):
        LookupConfig(value)


@pytest.mark.parametrize("payload", [{}, {"enabled": True}, [],
                                      {"value_lookup_enabled": True, "typo": False}])
def test_unknown_config_keys_rejected(tmp_path, payload):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="config must contain"):
        LookupConfig.from_file(path)
