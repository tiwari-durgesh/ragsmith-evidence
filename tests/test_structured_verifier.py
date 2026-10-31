
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.structured_verifier import verify_metric_value


def make_evidence(
    content="Metric: Revenue (million USD); 2025: 145",
    kind="table_row",
):
    return Evidence(
        evidence_id="ev-001",
        document_id="doc-001",
        document_version="version-001",
        kind=kind,
        content=content,
        locator="table:1/row:2",
    )


def test_exact_metric_year_value_supports():
    evidence = make_evidence()

    result = verify_metric_value(
        evidence, "Revenue (million USD)", 2025, "145"
    )

    assert result.verdict == "supports"
    assert result.evidence_id == "ev-001"


def test_different_value_contradicts():
    evidence = make_evidence()

    result = verify_metric_value(
        evidence, "Revenue (million USD)", 2025, "150"
    )

    assert result.verdict == "contradicts"


def test_different_year_unverified():
    evidence = make_evidence()

    result = verify_metric_value(
        evidence, "Revenue (million USD)", 2024, "145"
    )

    assert result.verdict == "unverified"


def test_different_metric_unverified():
    evidence = make_evidence()

    result = verify_metric_value(
        evidence, "Profit (million USD)", 2025, "145"
    )

    assert result.verdict == "unverified"


def test_unsupported_format_unverified():
    evidence = make_evidence(
        content="Revenue for 2025 was 145 million USD",
        kind="text",
    )

    result = verify_metric_value(
        evidence, "Revenue (million USD)", 2025, "145"
    )

    assert result.verdict == "unverified"


def test_non_table_row_unverified():
    evidence = make_evidence(kind="text")

    result = verify_metric_value(
        evidence, "Revenue (million USD)", 2025, "145"
    )

    assert result.verdict == "unverified"


def test_metric_case_insensitive():
    evidence = make_evidence()

    result = verify_metric_value(
        evidence, "REVENUE (MILLION USD)", 2025, "145"
    )

    assert result.verdict == "supports"



def test_numeric_format_is_normalized():
    evidence = make_evidence()

    result = verify_metric_value(
        evidence, "Revenue (million USD)", 2025, "145.0"
    )

    assert result.verdict == "supports"

