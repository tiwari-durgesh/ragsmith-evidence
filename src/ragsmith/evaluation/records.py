"""Strict typed boundaries for provisional evaluation records, not inference."""

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ragsmith.evidence.models import Evidence
from ragsmith.value_lookup import LookupQuestion


PROVISIONAL = "provisional, single-annotator"


def require_keys(row: object, keys: set[str], name: str) -> Mapping:
    """Reject nonobjects and unknown/missing fields rather than coerce them."""
    if not isinstance(row, Mapping) or set(row) != keys:
        raise ValueError(f"Invalid {name} fields; expected {', '.join(sorted(keys))}")
    return row


def require_text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


def text_tuple(values: object, name: str) -> tuple[str, ...]:
    if not isinstance(values, list):
        raise ValueError(f"{name} must be a list")
    for value in values:
        require_text(value, name)
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {name}")
    return tuple(values)


def strict_json(text: str) -> object:
    """Reject duplicate keys and nonfinite constants before field validation."""
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"Nonfinite JSON constant: {value}")

    return json.loads(text, object_pairs_hook=object_pairs,
                      parse_constant=invalid_constant)


def _reject_gold_metadata(value: object) -> None:
    """Reject reserved annotation fields, not the factual values of source cells."""
    if isinstance(value, Mapping):
        if set(value) & {"gold_answer", "expected_value", "acceptable_values",
                         "annotation_status", "gold_evidence_ids", "answerability"}:
            raise ValueError("Gold annotation fields are forbidden in evidence metadata")
        for nested in value.values():
            _reject_gold_metadata(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_gold_metadata(nested)


def read_jsonl(path: Path) -> list[dict]:
    """Produce contextual errors for malformed JSONL without dumping content."""
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = strict_json(line)
            if not isinstance(row, dict):
                raise ValueError("JSONL record must be an object")
        except ValueError as exc:
            raise ValueError(f"{path.name}:{number}: {exc}") from exc
        rows.append(row)
    return rows


@dataclass(frozen=True)
class GoldFact:
    requirement_id: str
    status: str
    acceptable_values: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        require_text(self.requirement_id, "requirement_id")
        require_text(self.status, "status")
        if self.status not in {"supported", "missing", "conflicted", "not_adjudicable"}:
            raise ValueError("Unknown gold requirement status")
        for name in ("acceptable_values", "evidence_ids"):
            values = getattr(self, name)
            if not isinstance(values, tuple):
                raise ValueError(f"{name} must be an immutable tuple")
            text_tuple(list(values), name)
        if self.status == "supported":
            if not self.acceptable_values or not self.evidence_ids:
                raise ValueError("Supported gold facts need values and source evidence IDs")
        elif self.acceptable_values:
            raise ValueError("Only unambiguous supported facts have acceptable values")
        if self.status == "missing" and self.evidence_ids:
            raise ValueError("Missing facts cannot declare supporting evidence IDs")
        if self.status == "conflicted" and len(self.evidence_ids) < 2:
            raise ValueError("Conflicted facts need at least two distinct evidence IDs")
        for value in self.acceptable_values:
            try:
                number = Decimal(value)
            except InvalidOperation:
                continue
            if not number.is_finite():
                raise ValueError("Nonfinite numeric gold value")

    @classmethod
    def from_payload(cls, payload: object) -> "GoldFact":
        row = require_keys(payload, {"requirement_id", "status", "acceptable_values",
                                     "evidence_ids"}, "gold requirement")
        return cls(row["requirement_id"], row["status"],
                   text_tuple(row["acceptable_values"], "acceptable_values"),
                   text_tuple(row["evidence_ids"], "evidence_ids"))


@dataclass(frozen=True)
class GoldRecord:
    question_id: str
    group_id: str
    partition: str
    origin: str
    annotation_status: str
    annotator_id: str
    requirements: tuple[GoldFact, ...]

    def __post_init__(self) -> None:
        for name in ("question_id", "group_id", "annotator_id", "origin",
                     "partition", "annotation_status"):
            require_text(getattr(self, name), name)
        if self.annotation_status != PROVISIONAL:
            raise ValueError("Pilot labels must remain provisional, single-annotator")
        if self.origin not in {"synthetic", "tatqa-derived"}:
            raise ValueError("Unknown label origin")
        if self.partition not in {"diagnostic", "development", "held_out"}:
            raise ValueError("Unknown partition")
        if not isinstance(self.requirements, tuple) or not self.requirements or any(
            not isinstance(fact, GoldFact) for fact in self.requirements
        ):
            raise ValueError("Gold requirements must be a nonempty tuple of GoldFact")
        ids = [fact.requirement_id for fact in self.requirements]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate gold requirement IDs")

    @classmethod
    def from_payload(cls, payload: object) -> "GoldRecord":
        row = require_keys(payload, {"question_id", "group_id", "partition", "origin",
                                     "annotation_status", "annotator_id", "requirements"},
                           "gold")
        if not isinstance(row["requirements"], list):
            raise ValueError("Gold requirements must be a list")
        return cls(row["question_id"], row["group_id"], row["partition"], row["origin"],
                   row["annotation_status"], row["annotator_id"],
                   tuple(GoldFact.from_payload(item) for item in row["requirements"]))

    def validate_request(self, request: LookupQuestion) -> str:
        if self.question_id != request.question_id or {
            fact.requirement_id for fact in self.requirements
        } != {item.requirement_id for item in request.requirements}:
            raise ValueError("Gold question/requirement IDs must match the system input")
        states = {fact.status for fact in self.requirements}
        if "not_adjudicable" in states:
            return "not_adjudicable"
        if "conflicted" in states or "supported" not in states:
            return "abstain"
        return "full" if states == {"supported"} else "partial"


@dataclass(frozen=True)
class FrozenEvidenceRecord:
    """Typed container; the existing Evidence class itself remains mutable."""

    question_id: str
    evidence: tuple[Evidence, ...]

    def __post_init__(self) -> None:
        require_text(self.question_id, "question_id")
        if not isinstance(self.evidence, tuple) or any(
            not isinstance(item, Evidence) for item in self.evidence
        ):
            raise ValueError("evidence must be a tuple of Evidence")
        ids = [item.evidence_id for item in self.evidence]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate frozen evidence IDs")

    @classmethod
    def from_payload(cls, payload: object) -> "FrozenEvidenceRecord":
        row = require_keys(payload, {"question_id", "evidence"}, "frozen evidence")
        if not isinstance(row["evidence"], list):
            raise ValueError("evidence must be a list")
        items = []
        for raw in row["evidence"]:
            if not isinstance(raw, Mapping):
                raise ValueError("Evidence record must be an object")
            _reject_gold_metadata(raw.get("metadata"))
            try:
                items.append(Evidence(**raw))
            except TypeError as exc:
                raise ValueError("Invalid evidence fields") from exc
        return cls(row["question_id"], tuple(items))


def evidence_fingerprint(item: Evidence) -> str:
    """Hash full canonical evidence, including metadata, provenance and content."""
    import hashlib

    canonical = json.dumps(asdict(item), sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
