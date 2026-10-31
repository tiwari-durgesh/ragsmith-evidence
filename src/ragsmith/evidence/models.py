from dataclasses import dataclass


@dataclass
class Evidence:
    evidence_id: str
    document_id: str
    document_version: str
    kind: str
    content: str
    locator: str
    page_number: int | None = None
    section_path: str | None = None
    table_id: str | None = None
    row_index: int | None = None
    extraction_method: str = ""
    metadata: dict | None = None