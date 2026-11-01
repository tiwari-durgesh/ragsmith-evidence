"""Synthetic view/parser checks; no evaluation, development or human-label reads."""

import json

import pytest

from app.frontend.view import (
    badge_html, citation_cell, highlights, parse_custom, plain_gap, run_lookup,
    table_html, value_html,
)


def payload():
    return {"question": "Give synthetic Revenue and Cash in 2025.", "requested_facts": [
        {"requirement_id": "r", "metric": "Revenue", "year": 2025},
        {"requirement_id": "c", "metric": "Cash", "year": 2025}],
        "table": [["Metric", "2025"], ["Revenue", "10"], ["Cash", "4"]]}


def test_primary_and_baseline_citations_link_exact_raw_cells():
    request = payload()
    result = run_lookup(request)
    marked = highlights(result, request["table"])
    assert set(marked) == {(1, 1), (2, 1)}
    assert all(v["verified"] for v in marked.values())
    table = table_html(request["table"], result)
    assert 'id="pilot-cell-r1-c1" class="verified-cell"' in table
    assert 'id="pilot-cell-r2-c1" class="verified-cell"' in table
    for value in result["values"]:
        rendered = value_html(value, result["citations"], request["table"], prefix="pilot")
        assert 'target="_self" href="#pilot-cell-' in rendered


def test_baseline_only_conflict_citations_are_amber_not_verified():
    request = payload()
    request["table"].append(["Revenue", "20"])
    result = run_lookup(request)
    assert result["decision"] == "abstain" and not result["citations"]
    marked = highlights(result, request["table"])
    assert marked and not any(m["verified"] for m in marked.values())
    assert 'class="baseline-cell"' in table_html(request["table"], result)


def test_source_and_answer_html_are_escaped():
    table = [["Metric", "2025"], ['<img src="http://example.invalid" onerror="bad()">', "<script>bad()</script>"]]
    rendered = table_html(table)
    assert "<img" not in rendered and "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    rendered = value_html({"metric": "<script>", "year": 2025, "value": "<img>", "citation_numbers": []}, [], table, prefix="custom")
    assert "<img>" not in rendered and "&lt;img&gt;" in rendered


@pytest.mark.parametrize("locator", ["text:body", "table:x/row:99/column:1", "table:x/row:1/column:99", "table:x/row:-1/column:1"])
def test_unresolvable_citation_is_not_linked_to_an_invented_cell(locator):
    assert citation_cell({"locator": locator}, payload()["table"]) is None


def test_models_cannot_be_enabled_by_a_frontend_payload(monkeypatch):
    from app.runtime import LocalRuntime
    def forbidden(*a, **k):
        raise AssertionError("Model must stay off")
    monkeypatch.setattr(LocalRuntime, "generate", forbidden)
    monkeypatch.setattr(LocalRuntime, "count", forbidden)
    request = payload() | {"answerer": "local_llm"}
    assert run_lookup(request)["generation"]["inference_requests"] == 0


def test_valid_paste_preserves_explicit_facts_and_table():
    request = payload()
    parsed = parse_custom(request["question"], json.dumps(request["requested_facts"]), json.dumps(request["table"]))
    assert parsed["table"] == request["table"] and parsed["answerer"] == "lookup"


@pytest.mark.parametrize("table", ["not json", '[["Metric", "2025"], ["Revenue"]]',
                                  '[["Metric", "FY25"], ["Revenue", "10"]]',
                                  '[["Metric", "2025", "2025"], ["Revenue", "10", "20"]]',
                                  '[["Metric", 2025], ["Revenue", "10"]]'])
def test_bad_input_explains_header_repair_is_unsupported(table):
    with pytest.raises(ValueError, match="Header repair is unsupported"):
        parse_custom("Revenue?", json.dumps(payload()["requested_facts"]), table)


def test_missing_badges_and_gaps_do_not_claim_real_world_absence():
    request = payload()
    text = plain_gap({"requirement_id": "c", "status": "missing"}, request)
    assert "evidence used for this run" in text and "Cash" in text
    assert "ABSTAIN" in badge_html("abstain")
    assert "coverage not checked" in badge_html("full", extraction_only=True)
    assert "All requested facts supported" not in badge_html("full", extraction_only=True)
    with pytest.raises(ValueError):
        badge_html("unknown")
