
from dataclasses import dataclass, field


@dataclass
class Requirement:
    requirement_id: str
    description: str
    status: str = "unverified"
    evidence_ids: list[str] = field(default_factory=list)
    reason: str = ""

    def __post_init__(self):
        if not isinstance(self.requirement_id, str) or not self.requirement_id.strip():
            raise ValueError("requirement_id must be a non-empty string")

        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string")

        allowed_statuses = {
            "unverified",
            "supported",
            "missing",
            "contradicted",
        }

        if self.status not in allowed_statuses:
            raise ValueError(f"Unsupported requirement status: {self.status}")

        if not isinstance(self.evidence_ids, list) or any(
            not isinstance(eid, str) or not eid.strip()
            for eid in self.evidence_ids
        ):
            raise ValueError("evidence_ids must be a list of non-empty strings")

        if not isinstance(self.reason, str):
            raise ValueError("reason must be a string")
