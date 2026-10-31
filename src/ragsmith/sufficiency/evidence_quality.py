
from collections.abc import Sequence

from ragsmith.evidence.models import Evidence



FIELDS_BY_KIND = {
    "text": (
        "page_number",
        "section_path",
        "extraction_method",
    ),
    "table_row": (
        "page_number",
        "table_id",
        "row_index",
        "extraction_method",
    ),
    "table": (
        "page_number",
        "table_id",
        "extraction_method",
    ),
    "graph": (
        "page_number",
        "section_path",
        "extraction_method",
    ),
}


def score_evidence_quality(evidence: Evidence) -> dict:
    """Score source metadata completeness by evidence type."""

    fields = FIELDS_BY_KIND[evidence.kind]

    present_fields = [
        field
        for field in fields
        if getattr(evidence, field) is not None
        and getattr(evidence, field) != ""
    ]

    missing_fields = [
        field
        for field in fields
        if field not in present_fields
    ]

    score = round(len(present_fields) / len(fields), 2)

    if score >= 0.8:
        level = "high"
    elif score >= 0.4:
        level = "medium"
    else:
        level = "low"

    return {
        "evidence_id": evidence.evidence_id,
        "evidence_kind": evidence.kind,
        "completeness_score": score,
        "completeness_level": level,
        "present_fields": len(present_fields),
        "total_fields": len(fields),
        "missing_fields": missing_fields,
    }



def build_evidence_quality_report(
    report: dict,
    evidence_items: Sequence[Evidence],
) -> list[dict]:
    """Score referenced evidence without including unused items."""

    evidence_lookup = {
        evidence.evidence_id: evidence
        for evidence in evidence_items
    }

    referenced_ids = {
        evidence_id
        for requirement in report["requirements"]
        for evidence_id in requirement["evidence_ids"]
    }

    quality_records = []

    for evidence_id in sorted(referenced_ids):
        if evidence_id not in evidence_lookup:
            raise ValueError(
                f"Unknown evidence ID: {evidence_id}"
            )

        quality_records.append(
            score_evidence_quality(evidence_lookup[evidence_id])
        )

    return quality_records
