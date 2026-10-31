
from collections.abc import Sequence

from ragsmith.evidence.models import Evidence


def build_evidence_provenance(
    report: dict,
    evidence_items: Sequence[Evidence],
) -> list[dict]:
    """Build provenance records for evidence used in a report."""

    evidence_lookup = {
        evidence.evidence_id: evidence
        for evidence in evidence_items
    }

    referenced_ids = {
        evidence_id
        for requirement in report["requirements"]
        for evidence_id in requirement["evidence_ids"]
    }

    provenance = []

    for evidence_id in sorted(referenced_ids):
        if evidence_id not in evidence_lookup:
            raise ValueError(
                f"Unknown evidence ID: {evidence_id}"
            )

        evidence = evidence_lookup[evidence_id]

        provenance.append({
            "evidence_id": evidence.evidence_id,
            "document_id": evidence.document_id,
            "document_version": evidence.document_version,
            "kind": evidence.kind,
            "locator": evidence.locator,
            "page_number": evidence.page_number,
            "section_path": evidence.section_path,
            "table_id": evidence.table_id,
            "row_index": evidence.row_index,
            "extraction_method": evidence.extraction_method,
        })

    return provenance
