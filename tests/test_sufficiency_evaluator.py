
from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.models import Requirement
from ragsmith.sufficiency.evaluator import evaluate_requirement


def make_evidence(evidence_id="ev-001"):
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-001",
        document_version="version-001",
        kind="text",
        content="Revenue in 2025 was 145 million USD",
        locator="page:1",
    )


def test_no_evidence():
    requirement = Requirement("req-1", "Find revenue for 2025")

    result = evaluate_requirement(requirement, [])

    assert result.status == "unverified"
    assert result.evidence_ids == []
    assert result.reason == "No eligible candidate evidence available"


def test_eligible_evidence():
    requirement = Requirement("req-1", "Find revenue for 2025")
    evidence = make_evidence()

    result = evaluate_requirement(requirement, [evidence])

    assert result.status == "unverified"
    assert result.evidence_ids == ["ev-001"]
    assert result.reason == (
        "Eligible evidence found; semantic support not yet verified"
    )


def test_ineligible_evidence():
    requirement = Requirement("req-1", "Find revenue for 2025")
    evidence = make_evidence()
    evidence.content = ""

    result = evaluate_requirement(requirement, [evidence])

    assert result.status == "unverified"
    assert result.evidence_ids == []


def test_duplicate_evidence():
    requirement = Requirement("req-1", "Find revenue for 2025")
    evidence = make_evidence()

    result = evaluate_requirement(requirement, [evidence, evidence])

    assert result.evidence_ids == ["ev-001"]


def test_multiple_eligible_evidence():
    requirement = Requirement("req-1", "Find revenue for 2025")

    first = make_evidence("ev-001")
    second = make_evidence("ev-002")

    result = evaluate_requirement(requirement, [first, second])

    assert result.status == "unverified"
    assert result.evidence_ids == ["ev-001", "ev-002"]


def test_irrelevant_evidence_not_marked_supported():
    requirement = Requirement("req-1", "Find revenue for 2025")
    evidence = make_evidence()
    evidence.content = "Revenue in 2024 was 120 million USD"

    result = evaluate_requirement(requirement, [evidence])

    assert result.status == "unverified"
    assert result.evidence_ids == ["ev-001"]
