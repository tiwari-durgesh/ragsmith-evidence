"""Read-only SQLite FTS retrieval with complete evidence and source metadata."""

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from ragsmith.evidence.models import Evidence
from ragsmith.lookup_config import LookupConfig
from ragsmith.lookup_pipeline import assess_lookup_question
from ragsmith.response import render_lookup_response
from ragsmith.value_lookup import LookupQuestion


@dataclass(frozen=True)
class RetrievalConfig:
    """Bound the candidate budget per explicit question requirement."""

    per_requirement_limit: int = 10

    def __post_init__(self) -> None:
        if (
            type(self.per_requirement_limit) is not int
            or not 1 <= self.per_requirement_limit <= 100
        ):
            raise ValueError("per_requirement_limit must be an integer from 1 to 100")


@dataclass(frozen=True)
class RetrievalResult:
    """A deduplicated evidence union and per-requirement retrieval audit."""

    evidence: tuple[Evidence, ...]
    audit: dict


def retrieve_question_evidence(
    db_path: Path,
    request: LookupQuestion,
    config: RetrievalConfig = RetrievalConfig(),
) -> RetrievalResult:
    """Retrieve scoped FTS candidates from one read snapshot, without writing.

    This preserves the legacy search's tokenized OR matching and FTS5 BM25
    ordering. Evidence IDs break score ties deterministically. Document scope
    is applied in SQL before top-k. The extra row detects truncation; it cannot
    establish whether the retained evidence is sufficient for the whole corpus.
    """
    if not isinstance(request, LookupQuestion):
        raise ValueError("request must be a LookupQuestion")
    if not isinstance(config, RetrievalConfig):
        raise ValueError("config must be a RetrievalConfig")
    path = db_path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Evidence database does not exist: {path}")
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    unique: dict[str, Evidence] = {}
    queries = []
    try:
        db.execute("PRAGMA query_only = ON")
        db.execute("BEGIN")
        for requirement in request.requirements:
            query = f"{requirement.metric} {requirement.year}"
            tokens = re.findall(r"[^\W_]+", query, flags=re.UNICODE)[:20]
            expression = " OR ".join('"' + token + '"' for token in tokens)
            scope_sql = ""
            parameters: list = [expression]
            if requirement.document_ids:
                placeholders = ",".join("?" for _ in requirement.document_ids)
                scope_sql = f" AND e.document_id IN ({placeholders})"
                parameters.extend(requirement.document_ids)
            parameters.append(config.per_requirement_limit + 1)
            rows = db.execute(
                """
                SELECT e.*, d.source_path, d.sha256 AS source_version,
                       bm25(evidence_fts) AS score
                FROM evidence_fts
                JOIN evidence e ON e.evidence_id = evidence_fts.evidence_id
                LEFT JOIN documents d ON d.document_id = e.document_id
                WHERE evidence_fts MATCH ?
                """ + scope_sql + """
                ORDER BY bm25(evidence_fts), e.evidence_id
                LIMIT ?
                """,
                parameters,
            ).fetchall()
            hits = []
            for rank, row in enumerate(rows[:config.per_requirement_limit], 1):
                if (
                    not isinstance(row["source_path"], str)
                    or not row["source_path"].strip()
                    or row["source_version"] != row["document_version"]
                ):
                    raise ValueError(
                        f"Inconsistent stored source provenance: {row['evidence_id']}"
                    )
                try:
                    metadata = json.loads(row["metadata_json"])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Invalid evidence metadata JSON: {row['evidence_id']}"
                    ) from exc
                item = Evidence(
                    evidence_id=row["evidence_id"],
                    document_id=row["document_id"],
                    document_version=row["document_version"],
                    kind=row["kind"],
                    content=row["content"],
                    locator=row["locator"],
                    page_number=row["page_number"],
                    section_path=row["section_path"],
                    table_id=row["table_id"],
                    row_index=row["row_index"],
                    extraction_method=row["extraction_method"],
                    metadata=metadata,
                )
                unique.setdefault(item.evidence_id, item)
                hits.append({
                    "rank": rank,
                    "evidence_id": item.evidence_id,
                    "document_id": item.document_id,
                    "document_version": item.document_version,
                    "source_path": row["source_path"],
                    "score": row["score"],
                })
            queries.append({
                "requirement_id": requirement.requirement_id,
                "query": query,
                "match_expression": expression,
                "document_ids": list(requirement.document_ids),
                "truncated": len(rows) > config.per_requirement_limit,
                "hits": hits,
            })
    finally:
        db.close()
    return RetrievalResult(tuple(unique.values()), {
        "method": "sqlite_fts5_bm25",
        "per_requirement_limit": config.per_requirement_limit,
        "unique_evidence_count": len(unique),
        "queries": queries,
    })


def answer_from_database(
    db_path: Path,
    request: LookupQuestion,
    lookup_config: LookupConfig = LookupConfig(),
    retrieval_config: RetrievalConfig = RetrievalConfig(),
) -> dict:
    """Connect ingestion's stored evidence to unchanged lookup assessment.

    The result concerns the deduplicated union of retrieved evidence, not all
    database rows. Retrieval audit is outside the existing assessment schema.
    No text/table reshaping, model inference, or source-file rehashing occurs.
    """
    if not isinstance(lookup_config, LookupConfig):
        raise ValueError("lookup_config must be a LookupConfig")
    retrieved = retrieve_question_evidence(db_path, request, retrieval_config)
    result = assess_lookup_question(request, retrieved.evidence, lookup_config)
    result["retrieval"] = retrieved.audit
    result["response"] = render_lookup_response(result)
    return result
