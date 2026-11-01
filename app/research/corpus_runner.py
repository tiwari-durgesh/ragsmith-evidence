"""Scoped Option C excerpt retrieval and deterministic, cached batch execution.

No dataset downloader, question authoring, selection or calibration. Callers supply
an explicitly authorized source corpus and requests. No implicit answerer startup.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from subprocess import SubprocessError

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.evaluation_runner import Answerer, Candidate, Prepared, run_prepared
from app.models import RequestedFact
from app.runtime import pack
from ragsmith.core import connect
from ragsmith.retrieval import RetrievalConfig, retrieve_question_evidence
from ragsmith.value_lookup import LookupQuestion, MetricLookup
from scripts.tatqa_excerpt_ingestion import adapt_table, canonical, digest

LOG = logging.getLogger("ragsmith.study")
FAILURES = (ValueError, TypeError, KeyError, OSError, RuntimeError, TimeoutError, SubprocessError)


class Excerpt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    context_id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    table: list[list[str]]
    paragraphs: list[str] = Field(default_factory=list)
    source_reference: str = "supplied excerpt"
    unit: str = ""


class StudyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    case_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=4000)
    group_id: str = Field(min_length=1)
    context_ids: list[str] = Field(min_length=1)
    requested_facts: list[RequestedFact] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def unique(self):
        if not self.question.strip() or any(not r.metric.strip() or not r.requirement_id.strip() for r in self.requested_facts):
            raise ValueError("Blank question or requirement")
        if len(self.context_ids) != len(set(self.context_ids)):
            raise ValueError("Duplicate context scope")
        ids = [r.requirement_id for r in self.requested_facts]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate requirement IDs")
        return self


@dataclass(frozen=True)
class Corpus:
    database: Path
    sha256: str
    database_sha256: str
    contexts: dict

    def verify(self):
        if hashlib.sha256(self.database.read_bytes()).hexdigest() != self.database_sha256:
            raise ValueError("Corpus database changed after construction")
        for entry in self.contexts.values():
            if hashlib.sha256(Path(entry["source_path"]).read_bytes()).hexdigest() != entry["version"]:
                raise ValueError("Source snapshot changed after construction")


def build_corpus(excerpts: list[Excerpt], output: Path) -> Corpus:
    """Index every supplied excerpt/cell, including unrelated distractors."""
    if not excerpts or len({x.context_id for x in excerpts}) != len(excerpts):
        raise ValueError("Nonempty corpus with unique context IDs required")
    if output.exists():
        raise ValueError("Refuse to overwrite corpus directory")
    # Validate all adapter inputs before creating a partially usable corpus.
    ordered = sorted(excerpts, key=lambda x: x.context_id)
    adapted = [(x, adapt_table(x.context_id, x.table, paragraphs=x.paragraphs,
               source_reference=x.source_reference, unit=x.unit)) for x in ordered]
    output.mkdir(parents=True)
    database = output / "evidence.sqlite"
    db = connect(database)
    contexts = {}
    try:
        with db:
            for source, context in adapted:
                path = output / (digest(source.context_id) + ".json")
                path.write_bytes(canonical(context.source_payload))
                contexts[source.context_id] = {"group_id": source.group_id, "document_id": context.document_id,
                    "version": context.source_version, "source_path": str(path.resolve())}
                db.execute('INSERT INTO documents VALUES (?,?,?,?)',
                           (context.document_id, str(path.resolve()), context.source_version, "option-c-snapshot"))
                for e in context.evidence:
                    db.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                        (e.evidence_id, e.document_id, e.document_version, e.kind, e.content, e.locator,
                         e.page_number, e.section_path, e.table_id, e.row_index, e.extraction_method, json.dumps(e.metadata)))
                    db.execute('INSERT INTO evidence_fts VALUES (?,?)', (e.evidence_id, e.content))
    finally:
        db.close()
    logical = [{"context_id": x.context_id, "group_id": x.group_id, "source_version": c.source_version}
               for x, c in adapted]
    result = Corpus(database, digest(logical), hashlib.sha256(database.read_bytes()).hexdigest(), contexts)
    result.verify()
    return result


def prepare_corpus(corpus: Corpus, payload: StudyRequest, answerer: Answerer) -> Prepared:
    corpus.verify()
    scope = []
    for uid in payload.context_ids:
        entry = corpus.contexts.get(uid)
        if not entry or entry["group_id"] != payload.group_id:
            raise ValueError("Unknown context or scope crosses excerpt groups")
        scope.append(entry["document_id"])
    request = LookupQuestion(payload.case_id, payload.question, tuple(
        MetricLookup(r.requirement_id, r.metric, r.year, tuple(sorted(scope))) for r in payload.requested_facts))
    retrieved = retrieve_question_evidence(corpus.database, request, RetrievalConfig(8))
    ranks = {}
    for query in retrieved.audit["queries"]:
        for hit in query["hits"]:
            ranks[hit["evidence_id"]] = min(ranks.get(hit["evidence_id"], 10**9), hit["rank"])
    ranked = sorted(retrieved.evidence, key=lambda e: (ranks[e.evidence_id], e.evidence_id))
    def counter(text):
        count = answerer.count(text)
        if type(count) is not int or count < 0:
            raise ValueError("Tokenizer returned an invalid count")
        return count
    packed = pack(request, ranked, counter, budget=3200)
    return Prepared(request, packed, {"method": retrieved.audit["method"], "retrieved_units": len(ranked),
                    "corpus_sha256": corpus.sha256, "scope_context_ids": sorted(payload.context_ids),
                    "decomposition_sha256": digest([r.model_dump() for r in payload.requested_facts])})


class CachedFailure(RuntimeError):
    pass


class GenerationCache:
    """Immutable content-addressed successes AND terminal failures; no retries.

    Cache is private local storage. Identity must include the frozen model/runtime
    and prompt/interface version. Operational hit counts are separate from results.
    """
    def __init__(self, root: Path, identity: dict):
        if not identity:
            raise ValueError("Explicit frozen answerer identity required")
        self.root, self.identity = root, json.loads(canonical(identity))
        root.mkdir(parents=True, exist_ok=True)
        self.hits = self.misses = 0

    def key(self, corpus: Corpus, prepared: Prepared):
        return digest(["generation-cache-v1", self.identity, corpus.sha256, prepared.packed.audit,
                       [{"id": r.requirement_id, "metric": r.metric, "year": r.year,
                         "documents": list(r.document_ids)} for r in prepared.request.requirements]])

    def generate(self, corpus, prepared, answerer):
        key = self.key(corpus, prepared)
        path = self.root / (key + ".json")
        if path.exists():
            self.hits += 1
            envelope = json.loads(path.read_text(encoding="utf-8"))
            record = envelope["record"]
            if envelope.get("sha256") != digest(record) or record.get("key") != key:
                raise CachedFailure("Cache integrity failure; no retry")
        else:
            try:
                with (self.root / (key + ".claim")).open("xb") as claim:
                    claim.write(canonical({"key": key, "rule": "no retry after interrupted generation"}))
            except FileExistsError as exc:
                raise CachedFailure("Generation already claimed or interrupted; no retry") from exc
            self.misses += 1
            try:
                raw, audit = answerer.generate(prepared.request, prepared.packed)
                candidates = [Candidate.model_validate(x) for x in raw]
                if [x.requirement_id for x in candidates] != [r.requirement_id for r in prepared.request.requirements]:
                    raise ValueError("Candidate requirement order mismatch")
                evidence_ids = {e.evidence_id for e in prepared.packed.evidence}
                if any(e not in evidence_ids for c in candidates for e in c.citations):
                    raise ValueError("Unknown candidate citation")
                if any(c.generation_failure and c.value.strip() for c in candidates):
                    raise ValueError("Invalid candidate failure flag")
                record = {"key": key, "status": "success", "candidates": raw, "audit": audit}
                canonical(record)  # Reject NaN/nonserializable runtime audit before writing.
            except FAILURES as exc:
                record = {"key": key, "status": "failure", "failure_type": type(exc).__name__}
            with path.open("xb") as stream:
                stream.write(canonical({"record": record, "sha256": digest(record)}))
        if record["status"] == "failure":
            LOG.warning("generation_failed code=%s", record["failure_type"])
            raise CachedFailure("Cached terminal generation failure; no retry")
        return record["candidates"], record["audit"]


def run_batch(corpus: Corpus, requests: list[StudyRequest], answerer: Answerer,
              cache: GenerationCache, *, threshold: float | None = None) -> dict:
    """Stable case order; every preparation/generation failure stays in results."""
    if len({r.case_id for r in requests}) != len(requests):
        raise ValueError("Duplicate case IDs")
    if threshold is not None and (type(threshold) not in (int, float) or not 0 <= threshold <= 1):
        raise ValueError("Invalid threshold")
    before = (cache.hits, cache.misses)
    results = []
    for payload in sorted(requests, key=lambda r: r.case_id):
        try:
            prepared = prepare_corpus(corpus, payload, answerer)
            class Shared:
                def generate(self, request, packed):
                    return cache.generate(corpus, prepared, answerer)
            result = run_prepared(prepared, Shared(), threshold=threshold)
        except FAILURES as exc:
            LOG.warning("preparation_failed code=%s", type(exc).__name__)
            result = {"question_id": payload.case_id, "status": "preparation_failed",
                      "failure_type": type(exc).__name__, "included_in_denominator": True,
                      "confidence_threshold": threshold, "confidence_calibrated": False,
                      "research_ready": False, "policies": []}
        results.append(result)
    return {"corpus_sha256": corpus.sha256, "results": results,
            "results_sha256": digest(results), "requested_cases": len(requests),
            "execution": {"generation_cache_hits": cache.hits-before[0],
                          "generation_cache_misses": cache.misses-before[1]},
            "confidence_threshold": threshold, "confidence_calibrated": False,
            "notice": "No research/performance claims. Threshold unset unless explicitly supplied; no calibration here."}
