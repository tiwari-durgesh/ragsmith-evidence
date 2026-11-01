"""Synthetic API tests; never load local pilot/evaluation/development labels."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def request(table=None):
    return {"question": "Give Revenue and Cash in 2025.", "requested_facts": [
        {"requirement_id": "r", "metric": "Revenue", "year": 2025},
        {"requirement_id": "c", "metric": "Cash", "year": 2025}],
        "table": table or [["Metric", "2025"], ["Revenue", "10"], ["Cash", "4"]]}


def test_full_api_has_three_frozen_policies_and_numbered_cell_citations():
    response = client.post("/ask", json=request())
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["decision"] == "full"
    assert len(result["baselines"]) == 3
    assert {v["value"] for v in result["values"]} == {"10", "4"}
    assert [c["citation_number"] for c in result["citations"]] == [1, 2]
    assert all("/column:1" in c["locator"] for c in result["citations"])
    assert result["generation"]["inference_requests"] == 0
    assert result["baseline_family"] == "frozen_pilot_baselines"
    assert result["packing"]["input_tokens"] <= 3200


def test_partial_does_not_cite_or_invent_missing_value():
    result = client.post("/ask", json=request([["Metric", "2025"], ["Revenue", "10"]])).json()
    assert result["decision"] == "partial"
    assert [x["metric"] for x in result["values"]] == ["Revenue"]
    assert result["gap_explanation"][0]["status"] == "missing"
    assert len(result["citations"]) == 1
    binary = next(x for x in result["baselines"] if x["variant"] == "binary_sufficiency")
    assert binary["decision"] == "abstain"


def test_conflict_preserves_frozen_question_wide_abstention():
    result = client.post("/ask", json=request([["Metric", "2025"], ["Revenue", "10"],
                                             ["Revenue", "20"], ["Cash", "4"]])).json()
    assert result["decision"] == "abstain"
    assert not result["values"] and not result["citations"]
    assert any(x["status"] == "contradicted" for x in result["gap_explanation"])


def test_empty_source_scope_abstains():
    result = client.post("/ask", json=request([["Metric", "2025"]])).json()
    assert result["decision"] == "abstain"
    assert result["values"] == []


def test_unsupported_dash_does_not_become_missing_or_zero():
    result = client.post("/ask", json=request([["Metric", "2025"], ["Revenue", "—"]])).json()
    assert result["decision"] == "abstain"
    assert {r["status"] for r in result["assessment"]["requirements"]} == {"unverified"}


@pytest.mark.parametrize("change", [
    {"expected_answer": "secret gold"}, {"table": [[1]]},
    {"requested_facts": [{"requirement_id": "r", "metric": "Revenue", "year": "2025"}]},
    {"requested_facts": [{"requirement_id": "r", "metric": "Revenue", "year": 2025}] * 2},
    {"demo_confidence_threshold": 1.1}, {"answerer": "remote_api"},
])
def test_invalid_requests_rejected(change):
    payload = request() | change
    assert client.post("/ask", json=payload).status_code == 422


def test_health_and_openapi_are_available():
    assert client.get("/health").json()["demo_only"]
    assert "/ask" in client.get("/openapi.json").json()["paths"]
