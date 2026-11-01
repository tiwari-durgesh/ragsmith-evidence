"""Versioned source declarations and evidence-link integrity for Track A."""

import re
from dataclasses import dataclass
from pathlib import Path

from ragsmith.evidence.models import Evidence
from ragsmith.evaluation.records import (
    GoldRecord, evidence_fingerprint, require_keys, require_text, strict_json,
    text_tuple,
)
from ragsmith.value_lookup import LookupQuestion


def _sha256(value: object, name: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    document_id: str
    document_version: str
    group_id: str
    source_uri: str
    source_sha256: str
    license: str
    parent_source_ids: tuple[str, ...]
    transformation: str

    def __post_init__(self) -> None:
        for name in ("source_id", "document_id", "document_version", "group_id",
                     "source_uri", "license", "transformation"):
            require_text(getattr(self, name), name)
        _sha256(self.source_sha256, "source_sha256")
        if not isinstance(self.parent_source_ids, tuple):
            raise ValueError("parent_source_ids must be a tuple")
        text_tuple(list(self.parent_source_ids), "parent_source_ids")
        if self.transformation not in {
            "original", "canonicalization", "masking", "synthetic_conflict"
        }:
            raise ValueError("Unknown source transformation")
        if (self.transformation == "original") != (not self.parent_source_ids):
            raise ValueError("Original sources have no parents; transformations need parents")
        if self.source_id in self.parent_source_ids:
            raise ValueError("A source cannot be its own parent")

    @classmethod
    def from_payload(cls, payload: object) -> "SourceRecord":
        row = require_keys(payload, {
            "source_id", "document_id", "document_version", "group_id", "source_uri",
            "source_sha256", "license", "parent_source_ids", "transformation",
        }, "source record")
        fields = dict(row)
        fields["parent_source_ids"] = text_tuple(row["parent_source_ids"], "parent_source_ids")
        return cls(**fields)


@dataclass(frozen=True)
class EvidenceLink:
    evidence_id: str
    source_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        require_text(self.evidence_id, "evidence_id")
        require_text(self.source_id, "source_id")
        _sha256(self.fingerprint, "fingerprint")

    @classmethod
    def from_payload(cls, payload: object) -> "EvidenceLink":
        row = require_keys(payload, {"evidence_id", "source_id", "fingerprint"},
                           "evidence link")
        return cls(**row)


@dataclass(frozen=True)
class SourceManifest:
    sources: tuple[SourceRecord, ...]
    evidence_links: tuple[EvidenceLink, ...]

    def __post_init__(self) -> None:
        for name, kind in (("sources", SourceRecord), ("evidence_links", EvidenceLink)):
            items = getattr(self, name)
            if not isinstance(items, tuple) or any(not isinstance(item, kind) for item in items):
                raise ValueError(f"{name} must contain typed immutable records")
        sources = {item.source_id: item for item in self.sources}
        if len(sources) != len(self.sources):
            raise ValueError("Duplicate source IDs")
        versions = {(item.document_id, item.document_version) for item in self.sources}
        if len(versions) != len(self.sources):
            raise ValueError("Duplicate document/version declarations")
        document_groups = {}
        for source in self.sources:
            if source.document_id in document_groups and (
                document_groups[source.document_id] != source.group_id
            ):
                raise ValueError("Versions of a document must share a family group")
            document_groups[source.document_id] = source.group_id
        links = {item.evidence_id: item for item in self.evidence_links}
        if len(links) != len(self.evidence_links):
            raise ValueError("Duplicate evidence lineage IDs")
        if any(item.source_id not in sources for item in self.evidence_links):
            raise ValueError("Evidence link references unknown source")
        for source in self.sources:
            for parent in source.parent_source_ids:
                if parent not in sources:
                    raise ValueError("Unknown parent source")
                if sources[parent].group_id != source.group_id:
                    raise ValueError("Derived sources must remain in the parent's group")
        remaining = set(sources)
        resolved = set()
        while remaining:
            ready = {key for key in remaining
                     if set(sources[key].parent_source_ids) <= resolved}
            if not ready:
                raise ValueError("Source lineage contains a cycle")
            resolved.update(ready)
            remaining.difference_update(ready)

    @classmethod
    def from_payload(cls, payload: object) -> "SourceManifest":
        row = require_keys(payload, {"schema_version", "sources", "evidence_links"},
                           "source manifest")
        if row["schema_version"] != "1.0":
            raise ValueError("Unsupported source manifest schema_version")
        if not isinstance(row["sources"], list) or not isinstance(row["evidence_links"], list):
            raise ValueError("Source manifest collections must be lists")
        return cls(tuple(SourceRecord.from_payload(item) for item in row["sources"]),
                   tuple(EvidenceLink.from_payload(item) for item in row["evidence_links"]))

    @classmethod
    def from_file(cls, path: Path) -> "SourceManifest":
        return cls.from_payload(strict_json(path.read_text(encoding="utf-8")))

    def validate_evidence(self, evidence: list[Evidence]) -> None:
        sources = {source.source_id: source for source in self.sources}
        links = {link.evidence_id: link for link in self.evidence_links}
        for item in evidence:
            link = links.get(item.evidence_id)
            if link is None:
                raise ValueError(f"Unregistered evidence ID: {item.evidence_id}")
            source = sources[link.source_id]
            if (item.document_id, item.document_version) != (
                source.document_id, source.document_version
            ) or evidence_fingerprint(item) != link.fingerprint:
                raise ValueError(f"Evidence fingerprint/source mismatch: {item.evidence_id}")

    def validate_request(self, request: LookupQuestion) -> None:
        documents = {source.document_id for source in self.sources}
        for requirement in request.requirements:
            if not set(requirement.document_ids) <= documents:
                raise ValueError("Requested document scope is absent from the source manifest")

    def validate_gold_links(
        self, gold: GoldRecord, request: LookupQuestion, evidence: list[Evidence]
    ) -> None:
        """Validate declared Track A scope, not factual entailment or authenticity."""
        items = {item.evidence_id: item for item in evidence}
        links = {item.evidence_id: item for item in self.evidence_links}
        sources = {item.source_id: item for item in self.sources}
        requirements = {item.requirement_id: item for item in request.requirements}
        if gold.group_id not in {item.group_id for item in self.sources}:
            raise ValueError("Source and gold family groups differ")
        for requirement in request.requirements:
            if any(source.group_id != gold.group_id for source in self.sources
                   if source.document_id in requirement.document_ids):
                raise ValueError("Requested scope and gold family groups differ")
        for item in evidence:
            source = sources[links[item.evidence_id].source_id]
            if source.group_id != gold.group_id:
                raise ValueError("Source and gold family groups differ")
            if not any(not req.document_ids or item.document_id in req.document_ids
                       for req in request.requirements):
                raise ValueError("Frozen evidence lies outside all requested document scopes")
        for fact in gold.requirements:
            allowed_documents = requirements[fact.requirement_id].document_ids
            for eid in fact.evidence_ids:
                if eid not in items:
                    raise ValueError("Gold link is absent from the frozen Track A evidence set")
                if allowed_documents and items[eid].document_id not in allowed_documents:
                    raise ValueError("Gold evidence lies outside its requirement document scope")
