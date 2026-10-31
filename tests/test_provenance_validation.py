
import copy

import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.provenance import (
    build_evidence_provenance,
)
from ragsmith.sufficiency.provenance_validation import (
    validate_provenance_integrity,
)
from ragsmith.sufficiency.pipeline import (
    generate_structured_assessment_report,
)


def make_evidence(evidence_id="ev-001"):
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-001",
        document_version="v1",
        kind="table_row",
        content="Metric: Revenue (million USD); 2025: 145",
        locator="table:1/row:1",
        page_number=3,
        table_id="table-1",
        row_index=1,
        extraction_method="pdfplumber",
    )


def make_report(evidence):
    report = {
        "requirements": [
            {"evidence_ids": [evidence.evidence_id]},
        ],
    }
    report["evidence_provenance"] = (
        build_evidence_provenance(report, [evidence])
    )
    return report


def test_valid_provenance_accepted():
    evidence = make_evidence()
    report = make_report(evidence)

    assert validate_provenance_integrity(
        report, [evidence]
    ) is None


def test_duplicate_provenance_rejected():
    evidence = make_evidence()
    report = make_report(evidence)
    report["evidence_provenance"].append(
        copy.deepcopy(report["evidence_provenance"][0])
    )

    with pytest.raises(
        ValueError, match="Duplicate provenance"
    ):
        validate_provenance_integrity(report, [evidence])


def test_missing_provenance_rejected():
    evidence = make_evidence()
    report = make_report(evidence)
    report["evidence_provenance"] = []

    with pytest.raises(
        ValueError, match="do not match referenced"
    ):
        validate_provenance_integrity(report, [evidence])


def test_unreferenced_provenance_rejected():
    evidence = make_evidence()
    report = make_report(evidence)
    report["requirements"][0]["evidence_ids"] = []

    with pytest.raises(
        ValueError, match="do not match referenced"
    ):
        validate_provenance_integrity(report, [evidence])


def test_incorrect_document_id_rejected():
    evidence = make_evidence()
    report = make_report(evidence)
    report["evidence_provenance"][0]["document_id"] = "wrong-doc"

    with pytest.raises(
        ValueError, match="Provenance mismatch"
    ):
        validate_provenance_integrity(report, [evidence])


def test_incorrect_locator_rejected():
    evidence = make_evidence()
    report = make_report(evidence)
    report["evidence_provenance"][0]["locator"] = "wrong-location"

    with pytest.raises(
        ValueError, match="Provenance mismatch"
    ):
        validate_provenance_integrity(report, [evidence])


def test_missing_field_rejected():
    evidence = make_evidence()
    report = make_report(evidence)
    del report["evidence_provenance"][0]["document_version"]

    with pytest.raises(
        ValueError, match="Missing provenance field"
    ):
        validate_provenance_integrity(report, [evidence])


def test_pipeline_generates_valid_provenance():
    evidence = make_evidence()

    report = generate_structured_assessment_report(
        requirements=[
            ("req-001", "Revenue (million USD)", 2025, "145"),
        ],
        evidence_items=[evidence],
    )

    assert validate_provenance_integrity(
        report, [evidence]
    ) is None
