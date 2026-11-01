"""Source-only, conservative TAT-QA/table adapter outside frozen src/.

No dataset loader, question fields, gold labels, sampling or alias matching.
Canonical rows preserve literal metric labels; unsupported cells stay visible.
"""

from __future__ import annotations

import hashlib
import copy
import json
import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ragsmith.core import connect
from ragsmith.evidence.models import Evidence


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def name_tokens(text: str) -> list[str]:
    return re.findall(r"[^\W_]+", normalize(text), re.UNICODE)


PILOT_NAMES = (
    "American Tower", "Carpenter Technology", "Mimecast", "Shopify", "Teradyne",
    "Rogers", "Cornerstone OnDemand", "Consolidated Communications",
)


def matching_pilot_names(table: list[list[str]], paragraphs: list[str]) -> list[str]:
    # Match each source cell/paragraph independently: never invent a company name
    # by joining unrelated rows or adjacent cells.
    sequences = [name_tokens(x) for row in table for x in row] + [name_tokens(x) for x in paragraphs]
    matches = []
    for name in PILOT_NAMES:
        target = name_tokens(name)
        if any(any(tokens[i:i + len(target)] == target
                   for i in range(len(tokens) - len(target) + 1)) for tokens in sequences):
            matches.append(name)
    return matches


def table_hash(table: list[list[str]]) -> str:
    return digest([[normalize(cell) for cell in row] for row in table])


def similarity(left: dict, right: dict) -> dict:
    """Fixed content-only screens, preserving cell boundaries/signs and numbers."""
    def normalized(context):
        return {"table": [[normalize(cell) for cell in row] for row in context["table"]],
                "paragraphs": [normalize(p) for p in context.get("paragraphs", [])]}

    def shingles(value):
        tokens = re.findall(r"[^\W_]+|_|[^\w\s]", canonical(value).decode("utf-8"), re.UNICODE)
        return {tuple(tokens[i:i+5]) for i in range(len(tokens)-4)}

    a, b = normalized(left), normalized(right)
    sa, sb = shingles(a), shingles(b)
    ta, tb = shingles(a["table"]), shingles(b["table"])
    ra = {digest(row) for row in a["table"] if any(row)}
    rb = {digest(row) for row in b["table"] if any(row)}
    return {"table_equal": a["table"] == b["table"], "context_equal": a == b,
            "context_jaccard": len(sa & sb)/len(sa | sb) if sa and sb else 0,
            "table_jaccard": len(ta & tb)/len(ta | tb) if ta and tb else 0,
            "row_overlap": len(ra & rb)/min(len(ra), len(rb)) if ra and rb else 0}


def excerpt_groups(contexts: list[dict], *, pilot_hashes: set[str] = frozenset()) -> list[dict]:
    """Small source-only graph helper. Never load/split a research dataset here.

    Names must already be source-verified by a caller. Fixed content screens and
    additional source-only flagged links conservatively stay joined.
    """
    ids = [x["context_id"] for x in contexts]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate context IDs")
    parent = {uid: uid for uid in ids}

    def find(uid):
        while parent[uid] != uid:
            uid = parent[uid]
        return uid

    def union(a, b):
        if b not in parent:
            raise ValueError("Unknown near-duplicate link")
        parent[find(b)] = find(a)

    hashes, names = {}, {}
    excluded = set()
    for index, left in enumerate(contexts):
        for right in contexts[index+1:]:
            score = similarity(left, right)
            if (score["table_equal"] or score["context_equal"] or score["table_jaccard"] >= .8
                    or score["context_jaccard"] >= .8 or score["row_overlap"] >= .5):
                union(left["context_id"], right["context_id"])
    for ctx in contexts:
        uid = ctx["context_id"]
        h = table_hash(ctx["table"])
        if h in hashes:
            union(uid, hashes[h])
        hashes[h] = uid
        if (h in pilot_hashes or ctx.get("known_pilot_family", False)
                or matching_pilot_names(ctx["table"], ctx.get("paragraphs", []))):
            excluded.add(uid)
        for name in ctx.get("verified_company_names", []):
            key = tuple(name_tokens(name))
            if not key or key in {("company",), ("the", "company")}:
                raise ValueError("Verified company name must identify an issuer")
            if key in names:
                union(uid, names[key])
            names[key] = uid
        for other in ctx.get("near_duplicate_links", []):
            union(uid, other)
    groups = {}
    for uid in ids:
        groups.setdefault(find(uid), []).append(uid)
    return sorted([{"group_id": "excerpt-group-" + digest(sorted(members)),
                    "members": sorted(members), "excluded": bool(set(members) & excluded),
                    "independence_established": False}
                   for members in groups.values()], key=lambda x: x["group_id"])


def validate_allocations(groups: list[dict], allocations: list[dict]) -> None:
    """Enforce the five-total cap and no component split, without selecting IDs."""
    by_id = {x["group_id"]: x for x in groups}
    partitions, counts, cases = {}, {}, set()
    for row in allocations:
        gid, partition, case = row["group_id"], row["partition"], row["case_id"]
        if gid not in by_id or by_id[gid]["excluded"] or partition not in {"development", "evaluation"}:
            raise ValueError("Unknown/excluded group or invalid partition")
        if case in cases:
            raise ValueError("Duplicate case ID")
        cases.add(case)
        if gid in partitions and partitions[gid] != partition:
            raise ValueError("Cannot split an excerpt group")
        partitions[gid] = partition
        counts[gid] = counts.get(gid, 0) + 1
        if counts[gid] > 5:
            raise ValueError("At most five questions total per excerpt group")


def numeric_value(text: str) -> str | None:
    """Normalize financial punctuation without rounding or inventing zeroes."""
    value = text.strip()
    if not re.fullmatch(r"\(?[+\-−]?[£€$]?\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?\)?", value):
        return None
    if value.startswith("(") != value.endswith(")"):
        return None
    negative = value.startswith("(")
    value = value.strip("()").replace("−", "-")
    value = re.sub(r"[£€$,\s%]", "", value)
    if negative:
        if value.startswith(("-", "+")):
            return None
        value = "-" + value
    try:
        return value if Decimal(value).is_finite() else None
    except InvalidOperation:
        return None


@dataclass(frozen=True)
class AdaptedContext:
    document_id: str
    source_version: str
    source_payload: dict
    evidence: tuple[Evidence, ...]
    audit: tuple[dict, ...]


def adapt_table(context_id: str, table: list[list[str]], *, paragraphs: list[str] | None = None,
                source_reference: str = "user-supplied table", unit: str = "") -> AdaptedContext:
    """Adapt every interpretable source cell, never a question-selected subset.

    Only explicit, unique year columns and numeric data cells are supported.
    Multirow headers with qualifiers, ragged grids and percent/change columns
    remain unsupported rather than guessing a binding. Repeated identical
    metric/year rows are preserved so the frozen contradiction policy sees them.
    """
    if not isinstance(context_id, str) or not context_id.strip():
        raise ValueError("context_id is required")
    if (not isinstance(table, list) or not table or len(table) > 200
            or any(not isinstance(row, list) or not row or len(row) > 30
                   or any(not isinstance(cell, str) or len(cell) > 4000 for cell in row) for row in table)):
        raise ValueError("table must contain 1..200 rows of 1..30 bounded string cells")
    paragraphs = [] if paragraphs is None else paragraphs
    if (not isinstance(paragraphs, list) or len(paragraphs) > 100
            or any(not isinstance(x, str) or len(x) > 12000 for x in paragraphs)):
        raise ValueError("paragraphs must contain bounded strings")
    if not isinstance(unit, str) or len(unit) > 200 or not isinstance(source_reference, str):
        raise ValueError("Invalid source unit/reference")
    payload = {"context_id": context_id, "table": table, "paragraphs": paragraphs,
               "source_reference": source_reference, "unit": unit}
    payload = copy.deepcopy(payload)
    table, paragraphs = payload["table"], payload["paragraphs"]
    version = digest(payload)
    doc = "excerpt-" + digest([context_id, source_reference])[:24]
    evidence, audit = [], []
    headers: dict[int, int] = {}
    header_rows = []
    structural_rows = []
    source_units = []
    header_width = None
    ambiguous_qualifiers = False
    section = ""

    def emit(kind, content, locator, row_index, metadata):
        evidence.append(Evidence(digest([doc, version, locator, content]), doc, version,
                                 kind, content, locator, table_id="table:" + context_id,
                                 row_index=row_index, extraction_method="source-cell-adapter-v1",
                                 metadata={"source_reference": source_reference, "unit": unit, **metadata}))

    for ri, row in enumerate(table):
        for cell in row:
            if re.search(r"\bin\s+(?:thousands|millions|billions)\b", cell, re.I) and cell not in source_units:
                source_units.append(cell)
        years = {ci: int(cell.strip()) for ci, cell in enumerate(row) if ci > 0 and re.fullmatch(r"(?:19|20)\d{2}", cell.strip())}
        # Year rows are structural only if column zero is blank or a known header.
        is_header = bool(years) and (not row[0].strip() or normalize(row[0]) in {"metric", "year", "(in millions)", "($ in millions)", "(in thousands)"})
        if is_header:
            repeated = len(set(years.values())) != len(years)
            headers = {} if repeated else years
            header_width = len(row)
            # Distinct region/product/segment headers require semantic binding
            # beyond this adapter. Ordinary fiscal/date/unit headings do not.
            qualifiers = [cell for prior in table[:ri] for cell in prior[1:]
                          if cell.strip() and not re.search(
                              r"year|ended|fiscal|as of|in (?:thousands|millions|billions)|dollars", cell, re.I)]
            ambiguous_qualifiers = bool(qualifiers)
            header_rows.append(ri)
            structural_rows.append(ri)
            audit.append({"row": ri, "status": "unsupported_header" if repeated else "year_header",
                          "reason": "duplicate years" if repeated else "explicit year columns"})
            if repeated:
                emit("table", json.dumps(row), f"table:{context_id}/row:{ri}", ri,
                     {"original_row": row, "reason": "duplicate year header", "header_rows": header_rows[:]})
            continue
        if not any(x.strip() for x in row):
            audit.append({"row": ri, "status": "blank"})
            continue
        if all(not x.strip() for x in row[1:]) and (
                row[0].strip().endswith(":") or row[0].strip().startswith("(")
                or not headers):
            # A section can change metric semantics, so do not drop it from lineage.
            section = row[0].strip()
            structural_rows.append(ri)
            audit.append({"row": ri, "status": "structural", "section": section})
            continue
        metric = row[0].strip()
        if headers and not metric and any(
                cell.strip() and numeric_value(cell) is None
                and not re.search(r"year|ended|fiscal|as of|in (?:thousands|millions|billions)|dollars", cell, re.I)
                for cell in row[1:]):
            ambiguous_qualifiers = True
            structural_rows.append(ri)
        for ci in range(1, len(row)):
            raw = row[ci]
            value = numeric_value(raw)
            year = headers.get(ci)
            reason = None
            if not metric or ";" in metric:
                reason = "metric label not representable"
            elif ambiguous_qualifiers:
                reason = "multirow qualifiers need explicit source binding"
            elif header_width is not None and len(row) != header_width:
                reason = "ragged row does not match year header width"
            elif year is None:
                reason = "no unambiguous explicit year for column"
            elif value is None:
                reason = "non-numeric/blank-marker cell; not assumed zero or absent"
            elif len(source_units) > 1:
                reason = "multiple source unit declarations need explicit source binding"
            elif unit and source_units and normalize(unit) != normalize(source_units[0]):
                reason = "caller unit and source unit differ; no unit alias or conversion inferred"
            # Reject a column if a preceding header qualifier denotes a percentage/change.
            if year and any(re.search(r"change|percent|%", table[hr][ci], re.I)
                            for hr in header_rows if ci < len(table[hr])):
                reason = "ambiguous change/percentage column"
            locator = f"table:{context_id}/row:{ri}/column:{ci}"
            currency = next((x for x in ("$", "£", "€") if x in raw), "")
            resolved_unit = unit or (source_units[0] if len(source_units) == 1 else "")
            metadata = {"original_row": row, "raw_value": raw, "column_index": ci,
                        "header_rows": [table[h] for h in structural_rows], "section": section,
                        "year": year, "currency_marker": currency,
                        "unit": "%" if raw.strip().endswith("%") else resolved_unit}
            if reason:
                emit("table", f"Source row {ri}, column {ci}: {metric} | {raw}", locator, ri,
                     {**metadata, "reason": reason})
                audit.append({"row": ri, "column": ci, "status": "unsupported", "reason": reason})
            else:
                emit("table_row", f"Metric: {metric}; {year}: {value}", locator, ri, metadata)
                audit.append({"row": ri, "column": ci, "status": "canonical"})
    # Same row label under different sections/units is not a genuine conflict.
    # Preserve it as unsupported instead of renaming a label into an oracle alias.
    contexts = {}
    for e in evidence:
        if e.kind == "table_row":
            key = (e.metadata["original_row"][0].strip().casefold(), e.metadata["year"])
            contexts.setdefault(key, set()).add((e.metadata["section"], e.metadata["unit"], e.metadata["currency_marker"]))
    for e in evidence:
        if e.kind == "table_row":
            key = (e.metadata["original_row"][0].strip().casefold(), e.metadata["year"])
            if len(contexts[key]) > 1:
                e.kind = "table"
                e.metadata["reason"] = "same label/year has different section or unit scope"
                audit.append({"row": e.row_index, "column": e.metadata["column_index"],
                              "status": "unsupported", "reason": e.metadata["reason"]})
    for pi, text in enumerate(paragraphs):
        if text.strip():
            emit("text", text, f"paragraph:{pi}", None, {"paragraph_index": pi})
    return AdaptedContext(doc, version, payload, tuple(evidence), tuple(audit))


def write_database(context: AdaptedContext, database: Path, source_file: Path) -> None:
    """Store external evidence with a real source hash; use existing SQLite schema."""
    if database.exists() or source_file.exists():
        raise ValueError("Refuse to overwrite a source/database snapshot")
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_bytes(canonical(context.source_payload))
    if hashlib.sha256(source_file.read_bytes()).hexdigest() != context.source_version:
        raise ValueError("Source hash mismatch")
    db = connect(database)
    try:
        with db:
            db.execute('INSERT INTO documents VALUES (?,?,?,?)',
                       (context.document_id, str(source_file.resolve()), context.source_version, "external-source-snapshot"))
            for e in context.evidence:
                db.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                           (e.evidence_id, e.document_id, e.document_version, e.kind, e.content,
                            e.locator, e.page_number, e.section_path, e.table_id, e.row_index,
                            e.extraction_method, json.dumps(e.metadata)))
                db.execute('INSERT INTO evidence_fts VALUES (?,?)', (e.evidence_id, e.content))
    finally:
        db.close()
