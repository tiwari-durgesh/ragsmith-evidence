"""Discover untrusted metric values without changing the assertion verifier."""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from ragsmith.evidence.models import Evidence
from ragsmith.sufficiency.traceability import validate_evidence_traceability


@dataclass(frozen=True)
class MetricLookup:
    """A requested fact with no expected answer; scope is caller-controlled.

    Empty document_ids means all supplied evidence. This module cannot infer
    company identity, version precedence, units, or aliases from question text.
    """

    requirement_id: str
    metric: str
    year: int
    document_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("requirement_id", "metric"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if type(self.year) is not int or not 1000 <= self.year <= 9999:
            raise ValueError("year must be a four-digit integer")
        if not isinstance(self.document_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.document_ids
        ):
            raise ValueError("document_ids must be a tuple of non-empty strings")
        if len(self.document_ids) != len(set(self.document_ids)):
            raise ValueError("Duplicate document IDs are not allowed")

    def scope(self, evidence_items: Sequence[Evidence]) -> list[Evidence]:
        """Select only explicitly allowed documents, or all supplied evidence."""
        return [
            item for item in evidence_items
            if not self.document_ids or item.document_id in self.document_ids
        ]


@dataclass(frozen=True)
class LookupCandidate:
    """An extracted value and its origins, not a verified answer."""

    value: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class DiscoveryResult:
    """Candidates plus evidence whose format could not be interpreted."""

    candidates: tuple[LookupCandidate, ...]
    unverified_evidence_ids: tuple[str, ...]


def discover_values(
    requirement: MetricLookup,
    evidence_items: Sequence[Evidence],
) -> DiscoveryResult:
    """Read only canonical table rows; every candidate still needs verification.

    The grammar deliberately matches the existing verifier's limited format.
    Unsupported evidence is recorded, never parsed heuristically as an answer.
    Absence here concerns supplied evidence in scope, not the entire corpus.
    """
    if not isinstance(requirement, MetricLookup):
        raise ValueError("requirement must be a MetricLookup")
    validate_evidence_traceability({"requirements": []}, evidence_items)
    values: dict[str, list[str]] = {}
    unknown = []
    for item in requirement.scope(evidence_items):
        match = None
        if item.kind == "table_row":
            match = re.fullmatch(
                r"Metric:\s*(?P<metric>[^;]+);\s*"
                r"(?P<year>\d{4}):\s*(?P<value>[^;]+)",
                item.content.strip(),
            )
        if match is None or not match.group("value").strip():
            unknown.append(item.evidence_id)
            continue
        if (
            match.group("metric").strip().casefold()
            == requirement.metric.strip().casefold()
            and int(match.group("year")) == requirement.year
        ):
            values.setdefault(match.group("value").strip(), []).append(item.evidence_id)
    return DiscoveryResult(
        candidates=tuple(
            LookupCandidate(value, tuple(sorted(ids)))
            for value, ids in sorted(values.items())
        ),
        unverified_evidence_ids=tuple(sorted(unknown)),
    )


@dataclass(frozen=True)
class LookupQuestion:
    """Application-supplied decomposition; question text is display-only."""

    question_id: str
    question: str
    requirements: tuple[MetricLookup, ...]

    def __post_init__(self) -> None:
        for name in ("question_id", "question"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.requirements, tuple) or not self.requirements or any(
            not isinstance(item, MetricLookup) for item in self.requirements
        ):
            raise ValueError("requirements must be a non-empty tuple of MetricLookup")
        ids = [item.requirement_id for item in self.requirements]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate requirement IDs are not allowed")

    @classmethod
    def from_payload(cls, payload: Mapping[str, object]) -> "LookupQuestion":
        """Reject answer labels and coercion at the application boundary."""
        if not isinstance(payload, Mapping) or set(payload) != {
            "question_id", "question", "requirements"
        }:
            raise ValueError(
                "request must contain question_id, question, requirements only"
            )
        rows = payload["requirements"]
        if not isinstance(rows, list):
            raise ValueError("requirements must be a list")
        requirements = []
        for row in rows:
            required = {"requirement_id", "metric", "year"}
            if not isinstance(row, Mapping) or not required <= set(row) or (
                set(row) - required - {"document_ids"}
            ):
                raise ValueError(
                    "requirement accepts requirement_id, metric, year, "
                    "document_ids only"
                )
            documents = row.get("document_ids", [])
            if not isinstance(documents, list):
                raise ValueError("document_ids must be a list")
            requirements.append(MetricLookup(
                row["requirement_id"], row["metric"], row["year"], tuple(documents)
            ))
        return cls(payload["question_id"], payload["question"], tuple(requirements))
