"""Value discovery is an extraction step, never an answerability judgment."""

import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.value_lookup import LookupQuestion, MetricLookup, discover_values


def row(eid="ev1", content="Metric: Revenue; 2025: 145", kind="table_row", doc="d1"):
    return Evidence(eid, doc, "v1", kind, content, "table:1/row:2")


def test_discovery_groups_exact_values_and_preserves_all_origins():
    result = discover_values(MetricLookup("r1", "Revenue", 2025), [
        row("b"), row("a"), row("c", "Metric: Revenue; 2025: 145.00"),
    ])
    assert [(item.value, item.evidence_ids) for item in result.candidates] == [
        ("145", ("a", "b")), ("145.00", ("c",)),
    ]
    assert result.unverified_evidence_ids == ()


def test_metric_year_and_units_are_not_inferred_or_converted():
    result = discover_values(MetricLookup("r1", "Revenue (million USD)", 2025), [
        row(content="Metric: Revenue (USD); 2025: 145000000"),
        row("old", "Metric: Revenue (million USD); 2024: 145"),
    ])
    assert result.candidates == ()
    assert result.unverified_evidence_ids == ()


def test_case_whitespace_and_document_scope():
    result = discover_values(MetricLookup("r1", " revenue ", 2025, ("d1",)), [
        row(content="  Metric: REVENUE ; 2025: 145  "),
        row("foreign", "Metric: Revenue; 2025: 999", doc="d2"),
    ])
    assert len(result.candidates) == 1
    assert result.candidates[0].value == "145"
    assert result.candidates[0].evidence_ids == ("ev1",)


@pytest.mark.parametrize("content,kind", [
    ("Revenue was 145 in 2025", "text"),
    ("Metric: Revenue; 2025: 145; 2024: 120", "table_row"),
    ("Metric: Revenue; 2025:   ", "table_row"),
    ("metric: Revenue; 2025: 145", "table_row"),
    ("Metric: Revenue; 2025: 145", "graph"),
])
def test_unsupported_formats_are_recorded(content, kind):
    result = discover_values(MetricLookup("r1", "Revenue", 2025), [row(content=content, kind=kind)])
    assert result.candidates == ()
    assert result.unverified_evidence_ids == ("ev1",)


def test_conflicting_candidates_are_both_retained():
    result = discover_values(MetricLookup("r1", "Revenue", 2025), [
        row(), row("conflict", "Metric: Revenue; 2025: 150"),
    ])
    assert {item.value for item in result.candidates} == {"145", "150"}


def test_discovery_never_takes_values_from_metadata():
    item = row(content="No supported row here")
    item.metadata = {"expected_value": "145", "cells": {"2025": "145"}}
    result = discover_values(MetricLookup("r1", "Revenue", 2025), [item])
    assert result.candidates == ()
    assert result.unverified_evidence_ids == ("ev1",)


def test_duplicate_ids_rejected_even_outside_scope():
    item = row(doc="other")
    with pytest.raises(ValueError, match="Duplicate evidence IDs"):
        discover_values(MetricLookup("r1", "Revenue", 2025, ("d1",)), [item, item])


@pytest.mark.parametrize("field,value", [
    ("requirement_id", " "), ("metric", 2), ("year", "2025"),
    ("year", True), ("year", 2025.0), ("year", 999), ("year", 10000),
    ("document_ids", ["d1"]), ("document_ids", ("",)),
    ("document_ids", ("d1", "d1")),
])
def test_invalid_lookup_requirement_rejected(field, value):
    args = {"requirement_id": "r1", "metric": "Revenue", "year": 2025}
    args[field] = value
    with pytest.raises(ValueError):
        MetricLookup(**args)


def test_payload_accepts_unknown_value_question_without_answer_label():
    request = LookupQuestion.from_payload({
        "question_id": "q1", "question": "What was revenue in 2025?",
        "requirements": [{"requirement_id": "r1", "metric": "Revenue", "year": 2025,
                          "document_ids": ["d1"]}],
    })
    assert request.requirements == (MetricLookup("r1", "Revenue", 2025, ("d1",)),)


@pytest.mark.parametrize("extra", ["expected_value", "gold_answer", "typo"])
def test_payload_rejects_answer_labels_and_unknown_fields(extra):
    with pytest.raises(ValueError, match="requirement accepts"):
        LookupQuestion.from_payload({
            "question_id": "q1", "question": "Revenue?",
            "requirements": [{"requirement_id": "r1", "metric": "Revenue", "year": 2025,
                              extra: "145"}],
        })


@pytest.mark.parametrize("requirements", [(), [], ("r1",)])
def test_question_rejects_missing_or_untyped_requirements(requirements):
    with pytest.raises(ValueError):
        LookupQuestion("q1", "Revenue?", requirements)


def test_question_rejects_duplicate_requirements():
    requirement = MetricLookup("r1", "Revenue", 2025)
    with pytest.raises(ValueError, match="Duplicate requirement IDs"):
        LookupQuestion("q1", "Revenue?", (requirement, requirement))
