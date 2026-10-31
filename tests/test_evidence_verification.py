
import pytest

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.verification import check_evidence_eligibility


def make_evidence(content="Revenue in 2025 was 145 million USD"):
    return Evidence(
        evidence_id="ev-001",
        document_id="doc-001",
        document_version="version-001",
        kind="text",
        content=content,
        locator="page:1",
    )


def test_valid_evidence_is_eligible():
    evidence = make_evidence()

    eligible, reason = check_evidence_eligibility(evidence)

    assert eligible is True
    assert reason == "Evidence has basic provenance information"


def test_invalid_object_is_ineligible():
    eligible, reason = check_evidence_eligibility(None)

    assert eligible is False
    assert reason == "Invalid evidence object"



def test_empty_content_is_ineligible():
    evidence = make_evidence()
    evidence.content = ""

    eligible, reason = check_evidence_eligibility(evidence)

    assert eligible is False
    assert reason == "Evidence content is empty"


def test_whitespace_content_is_ineligible():
    evidence = make_evidence()
    evidence.content = "   "

    eligible, reason = check_evidence_eligibility(evidence)

    assert eligible is False
    assert reason == "Evidence content is empty"

def test_missing_document_version_is_ineligible():
    evidence = make_evidence()
    evidence.document_version = ""

    eligible, reason = check_evidence_eligibility(evidence)

    assert eligible is False
    assert reason == "Document version is missing"


def test_missing_locator_is_ineligible():
    evidence = make_evidence()
    evidence.locator = ""

    eligible, reason = check_evidence_eligibility(evidence)

    assert eligible is False
    assert reason == "Evidence locator is missing"
