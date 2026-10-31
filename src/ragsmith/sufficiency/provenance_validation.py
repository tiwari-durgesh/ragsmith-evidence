
from collections.abc import Sequence

from ragsmith.evidence.models import Evidence


PROVENANCE_FIELDS = (
    "evidence_id",
    "document_id",
    "document_version",
    "kind",
    "locator",
    "page_number",
    "section_path",
    "table_id",
    "row_index",
    "extraction_method",
)


def validate_provenance_integrity(
    report: dict,
    evidence_items: Sequence[Evidence],
) -> None:
    """Validate report provenance against original evidence."""

    evidence_lookup = {
        evidence.evidence_id: evidence
        for evidence in evidence_items
    }

    referenced_ids = {
        evidence_id
        for requirement in report["requirements"]
        for evidence_id in requirement["evidence_ids"]
    }

    records = report["evidence_provenance"]
    provenance_ids = [
        record["evidence_id"]
        for record in records
    ]

    if len(provenance_ids) != len(set(provenance_ids)):
        raise ValueError("Duplicate provenance records")

    if set(provenance_ids) != referenced_ids:
        raise ValueError(
            "Provenance records do not match referenced evidence"
        )

    for record in records:
        evidence_id = record["evidence_id"]

        if evidence_id not in evidence_lookup:
            raise ValueError(
                f"Unknown provenance evidence ID: {evidence_id}"
            )

        evidence = evidence_lookup[evidence_id]

        for field in PROVENANCE_FIELDS:
            if field not in record:
                raise ValueError(
                    f"Missing provenance field: {field}"
                )

            if record[field] != getattr(evidence, field):
                raise ValueError(
                    f"Provenance mismatch for {field}: {evidence_id}"
                )
