"""Application-level assertion requests for the structured assessment pipeline.

This interface verifies caller-supplied claims. It does not extract requirements
from natural language or discover an unknown answer. Question text is retained
for display; callers are responsible for supplying all intended requirements.
"""

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.pipeline import generate_structured_assessment_report


def _require_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_keys(payload: Mapping, expected: set[str], name: str) -> None:
    if set(payload) != expected:
        raise ValueError(f"{name} must contain exactly: {', '.join(sorted(expected))}")


@dataclass(frozen=True)
class MetricAssertion:
    """One metric/year/value claim, distinct from a verification result."""

    requirement_id: str
    metric: str
    year: int
    expected_value: str

    def __post_init__(self) -> None:
        for name in ("requirement_id", "metric", "expected_value"):
            _require_text(name, getattr(self, name))
        if type(self.year) is not int or not 1000 <= self.year <= 9999:
            raise ValueError("year must be a four-digit integer")

    def as_requirement(self) -> tuple[str, str, int, str]:
        """Adapt to the unchanged Phase 3 pipeline contract."""
        return self.requirement_id, self.metric, self.year, self.expected_value


@dataclass(frozen=True)
class QuestionRequest:
    """A question and an explicit, caller-controlled decomposition into claims."""

    question_id: str
    question: str
    requirements: tuple[MetricAssertion, ...]

    def __post_init__(self) -> None:
        _require_text("question_id", self.question_id)
        _require_text("question", self.question)
        if (
            not isinstance(self.requirements, tuple)
            or not self.requirements
            or any(not isinstance(item, MetricAssertion) for item in self.requirements)
        ):
            raise ValueError("requirements must be a non-empty tuple of MetricAssertion")
        ids = [item.requirement_id for item in self.requirements]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate requirement IDs are not allowed")

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "QuestionRequest":
        """Read a JSON-compatible request without guessing or coercing fields.

        Unknown fields are rejected so misspelled requirements and accidental
        inclusion of gold labels cannot silently affect application behavior.
        """
        if not isinstance(payload, Mapping):
            raise ValueError("question request must be an object")
        _require_keys(payload, {"question_id", "question", "requirements"}, "request")
        rows = payload["requirements"]
        if not isinstance(rows, list):
            raise ValueError("requirements must be a list")
        requirements = []
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError("each requirement must be an object")
            _require_keys(
                row,
                {"requirement_id", "metric", "year", "expected_value"},
                "requirement",
            )
            requirements.append(MetricAssertion(**row))
        return cls(
            question_id=payload["question_id"],
            question=payload["question"],
            requirements=tuple(requirements),
        )


def assess_question_request(
    request: QuestionRequest,
    evidence_items: Sequence[Evidence],
) -> dict:
    """Assess supplied evidence and retain the existing report in an envelope.

    ``full`` means all supplied assertions are supported by this verifier. It
    does not establish that the caller's decomposition covers the question.
    No expected value is inferred from evidence or from the question text.
    Existing contradiction, provenance, quality, and evidence-reference rules
    are delegated unchanged to the Phase 3 pipeline.
    """
    if not isinstance(request, QuestionRequest):
        raise ValueError("request must be a QuestionRequest")
    report = generate_structured_assessment_report(
        requirements=[item.as_requirement() for item in request.requirements],
        evidence_items=evidence_items,
    )
    return {
        "schema_version": "1.0",
        "mode": "assertion_verification",
        "question_id": request.question_id,
        "question": request.question,
        "requirements": [asdict(item) for item in request.requirements],
        "assessment": report,
    }
