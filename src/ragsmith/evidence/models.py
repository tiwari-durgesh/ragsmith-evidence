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


    def __post_init__(self):
        required = {
            "evidence_id": self.evidence_id,
            "document_id": self.document_id,
            "document_version": self.document_version,
            "content": self.content,
            "locator": self.locator,
        }

        for name, value in required.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        allowed_kinds = {"text", "table_row", "table", "graph"}

        if self.kind not in allowed_kinds:
            raise ValueError(f"Unsupported evidence kind: {self.kind}")

        if self.page_number is not None:
            if type(self.page_number) is not int or self.page_number < 1:
                raise ValueError("page_number must be a positive integer")

        if self.row_index is not None:
            if type(self.row_index) is not int or self.row_index < 0:
                raise ValueError("row_index must be a non-negative integer")

        if self.metadata is not None and not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary or None")
