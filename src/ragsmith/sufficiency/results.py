
from dataclasses import dataclass, field


@dataclass
class SufficiencyResult:
    requirement_id: str
    status: str = "unverified"
    evidence_ids: list[str] = field(default_factory=list)
    reason: str = ""

    def __post_init__(self):
        if not isinstance(self.requirement_id, str) or not self.requirement_id.strip():
            raise ValueError("requirement_id must be a non-empty string")

        allowed_statuses = {
            "unverified",
            "supported",
            "missing",
            "contradicted",
        }

        if self.status not in allowed_statuses:
            raise ValueError(f"Unsupported sufficiency status: {self.status}")

        if not isinstance(self.evidence_ids, list) or any(
            not isinstance(eid, str) or not eid.strip()
            for eid in self.evidence_ids
        ):
            raise ValueError("evidence_ids must be a list of non-empty strings")

        if not isinstance(self.reason, str):
            raise ValueError("reason must be a string")
