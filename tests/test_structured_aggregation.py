
from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.structured_verifier import verify_metric_value
from ragsmith.sufficiency.aggregator import aggregate_judgments


def make_evidence(evidence_id, value):
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-001",
        document_version="version-001",
        kind="table_row",
        content=f"Metric: Revenue (million USD); 2025: {value}",
        locator="table:1/row:2",
    )


def test_structured_support_aggregation():
    evidence = make_evidence("ev-001", "145")

    judgment = verify_metric_value(
        evidence,
        "Revenue (million USD)",
        2025,
        "145.0",
        requirement_id="req-001",
    )

    result = aggregate_judgments("req-001", [judgment])

    assert judgment.requirement_id == "req-001"
    assert judgment.verdict == "supports"
    assert result.status == "supported"
    assert result.evidence_ids == ["ev-001"]


def test_structured_contradiction_aggregation():
    evidence = make_evidence("ev-001", "150")

    judgment = verify_metric_value(
        evidence,
        "Revenue (million USD)",
        2025,
        "145",
        requirement_id="req-001",
    )

    result = aggregate_judgments("req-001", [judgment])

    assert judgment.verdict == "contradicts"
    assert result.status == "contradicted"


def test_mixed_structured_evidence():
    evidence_1 = make_evidence("ev-001", "145")
    evidence_2 = make_evidence("ev-002", "150")

    judgments = [
        verify_metric_value(
            evidence,
            "Revenue (million USD)",
            2025,
            "145",
            requirement_id="req-001",
        )
        for evidence in [evidence_1, evidence_2]
    ]

    result = aggregate_judgments("req-001", judgments)

    assert result.status == "contradicted"
    assert result.evidence_ids == ["ev-001", "ev-002"]


def test_unrelated_requirement_ignored():
    evidence = make_evidence("ev-001", "145")

    judgment = verify_metric_value(
        evidence,
        "Revenue (million USD)",
        2025,
        "145",
        requirement_id="req-002",
    )

    result = aggregate_judgments("req-001", [judgment])

    assert result.status == "unverified"
    assert result.evidence_ids == []


def test_default_requirement_id_preserved():
    evidence = make_evidence("ev-001", "145")

    judgment = verify_metric_value(
        evidence,
        "Revenue (million USD)",
        2025,
        "145",
    )

    assert judgment.requirement_id == "Revenue (million USD)-2025"
