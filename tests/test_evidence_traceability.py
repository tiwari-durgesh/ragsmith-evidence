
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.traceability import (
    validate_evidence_traceability,
)


def make_evidence(evidence_id):
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-001",
        document_version="version-001",
        kind="table_row",
        content="Metric: Revenue (million USD); 2025: 145",
        locator="table:1/row:2",
    )


def make_report(requirements):
    return {"requirements": requirements}


def test_valid_evidence_reference():
    report = make_report([
        {"evidence_ids": ["ev-001"]},
    ])

    assert validate_evidence_traceability(
        report,
        [make_evidence("ev-001")],
    ) is None


def test_unknown_evidence_reference_rejected():
    report = make_report([
        {"evidence_ids": ["ev-999"]},
    ])

    with pytest.raises(ValueError, match="Unknown evidence ID: ev-999"):
        validate_evidence_traceability(
            report,
            [make_evidence("ev-001")],
        )


def test_empty_evidence_references_accepted():
    report = make_report([
        {"evidence_ids": []},
    ])

    assert validate_evidence_traceability(report, []) is None


def test_multiple_requirements_valid():
    report = make_report([
        {"evidence_ids": ["ev-001"]},
        {"evidence_ids": ["ev-002"]},
    ])

    assert validate_evidence_traceability(
        report,
        [make_evidence("ev-001"), make_evidence("ev-002")],
    ) is None


def test_unknown_reference_in_second_requirement_rejected():
    report = make_report([
        {"evidence_ids": ["ev-001"]},
        {"evidence_ids": ["ev-999"]},
    ])

    with pytest.raises(ValueError, match="Unknown evidence ID: ev-999"):
        validate_evidence_traceability(
            report,
            [make_evidence("ev-001")],
        )


def test_empty_requirements_accepted():
    report = make_report([])

    assert validate_evidence_traceability(report, []) is None
