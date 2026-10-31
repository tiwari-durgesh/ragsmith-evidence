
from dataclasses import dataclass


@dataclass
class SupportJudgment:
    requirement_id: str
    evidence_id: str
    verdict: str
    reason: str = ""

    def __post_init__(self):
        for name in ("requirement_id", "evidence_id"):
            value = getattr(self, name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        allowed_verdicts = {
            "supports",
            "insufficient",
            "contradicts",
            "unverified",
        }

        if self.verdict not in allowed_verdicts:
            raise ValueError(f"Unsupported support verdict: {self.verdict}")

        if not isinstance(self.reason, str):
            raise ValueError("reason must be a string")
