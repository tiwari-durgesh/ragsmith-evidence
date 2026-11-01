"""Synthetic-only adapter contract tests: no corpus or gold-file reads."""

import hashlib
import sqlite3

import pytest

from scripts.tatqa_excerpt_ingestion import (
    adapt_table, canonical, excerpt_groups, matching_pilot_names, numeric_value,
    table_hash, validate_allocations, write_database, similarity,
)
from ragsmith.core import verify_source_integrity
from ragsmith.retrieval import retrieve_question_evidence
from ragsmith.value_lookup import LookupQuestion, MetricLookup


def test_all_year_cells_not_only_requested_fact_are_adapted():
    source = [["Metric", "2025", "2024"], ["Revenue", "$1,200", "(200)"], ["Cash", "0", "12.5"]]
    c = adapt_table("synthetic", source, unit="USD millions")
    assert len(c.evidence) == 4
    assert [e.content for e in c.evidence] == [
        "Metric: Revenue; 2025: 1200", "Metric: Revenue; 2024: -200",
        "Metric: Cash; 2025: 0", "Metric: Cash; 2024: 12.5"]
    assert c.evidence[0].metadata["original_row"] == source[1]
    assert c.evidence[0].locator.endswith("row:1/column:1")
    assert c.evidence[0].metadata["unit"] == "USD millions"
    assert hashlib.sha256(canonical(c.source_payload)).hexdigest() == c.source_version


@pytest.mark.parametrize("raw,expected", [
    ("0", "0"), ("1,234.50", "1234.50"), ("($1,200)", "-1200"),
    ("−2.5", "-2.5"), ("12%", "12"), ("—", None), ("N/A", None),
    ("", None), ("1,2", None), ("NaN", None), ("(-1)", None),
    ("(20", None), ("20)", None), ("1; 2024: 5", None),
])
def test_exact_financial_normalization(raw, expected):
    assert numeric_value(raw) == expected


@pytest.mark.parametrize("table", [
    [["Metric", "2025", "2025"], ["Revenue", "1", "2"]],
    [["", "Domestic", "International"], ["", "2025", "2024"], ["Revenue", "1", "2"]],
    [["Metric", "2025", "2024"], ["Revenue", "1"]],
    [["Metric", "2025"], ["Revenue; injected", "1"]],
    [["Metric", "FY2025"], ["Revenue", "1"]],
])
def test_ambiguous_headers_and_ragged_grids_remain_visible_unsupported(table):
    c = adapt_table("bad-header", table)
    assert not any(e.kind == "table_row" for e in c.evidence)
    assert c.evidence


def test_multiline_date_heading_and_blank_marker_not_zero():
    c = adapt_table("x", [["", "Years ended June 30,", ""], ["", "2025", "2024"],
                          ["Cost", "5", "—"]])
    assert sum(e.kind == "table_row" for e in c.evidence) == 1
    assert any(e.kind == "table" and "—" in e.content for e in c.evidence)


def test_empty_data_cell_is_unsupported_not_silently_removed():
    c = adapt_table("x", [["Metric", "2025"], ["Cash", ""]])
    assert len(c.evidence) == 1 and c.evidence[0].kind == "table"
    assert c.evidence[0].metadata["raw_value"] == ""


def test_source_unit_rows_and_full_header_lineage_preserved():
    c = adapt_table("x", [["Metric", "2025"], ["(In millions)", ""], ["Revenue", "10"]])
    assert c.evidence[0].metadata["unit"] == "(In millions)"
    assert c.evidence[0].metadata["header_rows"] == [["Metric", "2025"], ["(In millions)", ""]]


def test_qualifier_below_year_header_is_not_silently_bound():
    c = adapt_table("x", [["Metric", "2025", "2024"], ["", "Domestic", "International"],
                          ["Revenue", "10", "20"]])
    assert not any(e.kind == "table_row" for e in c.evidence)


def test_caller_unit_cannot_override_an_explicit_source_unit():
    c = adapt_table("x", [["Metric", "2025"], ["(In millions)", ""], ["Revenue", "10"]], unit="in thousands")
    assert not any(e.kind == "table_row" for e in c.evidence)


def test_duplicate_rows_preserve_real_disagreement_without_edits():
    c = adapt_table("x", [["Metric", "2025"], ["Revenue", "10"], ["Revenue", "20"]])
    assert [e.content for e in c.evidence] == ["Metric: Revenue; 2025: 10", "Metric: Revenue; 2025: 20"]
    assert len({e.evidence_id for e in c.evidence}) == 2


def test_section_and_currency_mismatch_not_promoted_to_conflict():
    c = adapt_table("x", [["Metric", "2025"], ["Assets:", ""], ["Other", "$10"],
                          ["Liabilities:", ""], ["Other", "€20"]])
    assert all(e.kind != "table_row" for e in c.evidence)
    assert {e.metadata["section"] for e in c.evidence} == {"Assets:", "Liabilities:"}


def test_prose_survives_and_input_mutation_does_not_change_emitted_content():
    table = [["Metric", "2025"], ["A", "1"]]
    c = adapt_table("x", table, paragraphs=["Scope unclear."])
    table[1][1] = "changed"
    assert c.evidence[-1].content == "Scope unclear."
    assert c.evidence[-1].kind == "text"
    assert c.source_payload["table"][1][1] == "1"
    assert c.evidence[0].metadata["original_row"][1] == "1"


def test_hash_stable_and_sensitive_to_sign_period_and_grid():
    assert table_hash([[" A ", "2025"], [" X", "1"]]) == table_hash([["a", "2025"], ["x", "1"]])
    assert table_hash([["A", "2025"], ["X", "1"]]) != table_hash([["A", "2024"], ["X", "-1"]])
    assert table_hash([["a b"]]) != table_hash([["a", "b"]])


@pytest.mark.parametrize("name", ["AMERICAN TOWER CORPORATION", "Shopify, Inc.", "Teradyne’s", "Rogers Communications Inc."])
def test_pilot_name_exclusion(name):
    assert matching_pilot_names([[name]], [])


def test_names_do_not_match_inside_words_or_across_unrelated_cells():
    assert not matching_pilot_names([["Shopifyish", "American"], ["Tower", "1"]], [])


def test_transitive_component_quarantine_and_stable_groups():
    contexts = [
        {"context_id": "a", "table": [["Shopify", "1"]], "near_duplicate_links": ["b"]},
        {"context_id": "b", "table": [["Other", "2"]], "near_duplicate_links": ["c"]},
        {"context_id": "c", "table": [["Other", "3"]]},
    ]
    groups = excerpt_groups(contexts)
    assert len(groups) == 1 and groups[0]["excluded"]
    assert groups == excerpt_groups(list(reversed(contexts)))
    assert not groups[0]["independence_established"]


def test_verified_names_and_exact_pilot_table_hash_join_and_quarantine():
    contexts = [{"context_id": str(i), "table": [["Metric", "2025"], ["X", str(i)]],
                 "verified_company_names": ["Synthetic Aurora Inc"]} for i in range(2)]
    assert excerpt_groups(contexts, pilot_hashes={table_hash(contexts[0]["table"])})[0]["excluded"]


def test_near_duplicate_row_threshold_and_numeric_preservation():
    left = {"context_id": "l", "table": [["Metric", "2025"], ["X", "10"], ["Y", "20"]]}
    right = {"context_id": "r", "table": [["Metric", "2025"], ["X", "10"], ["Y", "-20"]]}
    score = similarity(left, right)
    assert not score["table_equal"]
    assert score["row_overlap"] == pytest.approx(2/3)
    assert len(excerpt_groups([left, right])) == 1


def test_no_group_partition_split_or_sixth_question():
    groups = [{"group_id": "g", "excluded": False}]
    rows = [{"group_id": "g", "partition": "development", "case_id": str(i)} for i in range(5)]
    validate_allocations(groups, rows)
    with pytest.raises(ValueError, match="five"):
        validate_allocations(groups, rows + [{"group_id": "g", "partition": "development", "case_id": "six"}])
    with pytest.raises(ValueError, match="split"):
        validate_allocations(groups, rows[:1] + [{"group_id": "g", "partition": "evaluation", "case_id": "other"}])


def test_real_source_snapshot_retrieval_and_no_overwrite(tmp_path):
    c = adapt_table("x", [["Metric", "2025"], ["Revenue", "17"], ["Cost", "8"]])
    db, source = tmp_path / "e.sqlite", tmp_path / "source.json"
    write_database(c, db, source)
    assert verify_source_integrity(db, c.document_id)["status"] == "valid"
    r = LookupQuestion("synthetic", "Revenue?", (MetricLookup("r", "Revenue", 2025),))
    evidence = retrieve_question_evidence(db, r).evidence
    assert any(e.content == "Metric: Revenue; 2025: 17" for e in evidence)
    assert evidence[0].metadata["header_rows"]
    with pytest.raises(ValueError, match="overwrite"):
        write_database(c, db, source)


@pytest.mark.parametrize("table", [[], [[]], [[1]], [["x"]] * 201])
def test_invalid_tables_rejected(table):
    with pytest.raises(ValueError):
        adapt_table("x", table)
