
import pytest

from ragsmith.evidence.models import Evidence


def make_evidence(**overrides):
    data = {
        "evidence_id": "ev-001",
        "document_id": "doc-001",
        "document_version": "v1",
        "kind": "text",
        "content": "The company reported revenue growth.",
        "locator": "page:1",
        "page_number": 1,
    }
    data.update(overrides)
    return Evidence(**data)


def test_valid_evidence():
    evidence = make_evidence()
    assert evidence.evidence_id == "ev-001"


@pytest.mark.parametrize(
    "field,value",
    [
        ("evidence_id", ""),
        ("document_id", " "),
        ("document_version", ""),
        ("content", ""),
        ("locator", ""),
        ("kind", "unknown"),
        ("page_number", -1),
        ("page_number", 0),
        ("row_index", -1),
        ("metadata", "invalid"),
    ],
)
def test_invalid_evidence(field, value):
    with pytest.raises(ValueError):
        make_evidence(**{field: value})
