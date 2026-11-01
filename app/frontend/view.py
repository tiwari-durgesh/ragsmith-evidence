"""Safe display helpers for source-cell citations; no grading or model inference."""

from __future__ import annotations

import copy
import html
import json
import re
from pathlib import Path

from pydantic import ValidationError

from app.models import AskRequest
from app.service import answer


ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "data/evaluation/generated/demo-api/samples.json"
BANNER = "Prototype. Provisional pilot only. No performance claims."
BASELINES = (("extraction_only", "Extraction-only", "E"),
             ("binary_sufficiency", "Binary", "B"),
             ("graded_sufficiency", "Graded", "G"))


def load_samples(path: Path = SAMPLES) -> dict:
    packet = json.loads(path.read_text(encoding="utf-8"))
    if len(packet["cases"]) != 6 or len({c["sample_id"] for c in packet["cases"]}) != 6:
        raise ValueError("The local packet must contain the six prepared pilot cases")
    for case in packet["cases"]:
        AskRequest.model_validate(case["request"])
    return packet


def run_lookup(payload: dict) -> dict:
    # No UI option, pasted field or prepared case can enable model inference.
    safe = copy.deepcopy(payload)
    safe["answerer"] = "lookup"
    return answer(AskRequest.model_validate(safe))


def parse_custom(question: str, facts_text: str, table_text: str, unit: str = "") -> dict:
    values = {}
    for name, text in (("requested facts", facts_text), ("table", table_text)):
        try:
            values[name] = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Cannot parse {name}: invalid JSON at line {exc.lineno}, column {exc.colno}. Header repair is unsupported.") from exc
    try:
        request = AskRequest.model_validate({"question": question,
            "requested_facts": values["requested facts"], "table": values["table"],
            "source_unit": unit, "source_reference": "User-pasted prototype table", "answerer": "lookup"})
    except ValidationError as exc:
        error = exc.errors()[0]
        location = ".".join(str(x) for x in error["loc"])
        raise ValueError(f"Cannot parse input ({location}): {error['msg']}. Header repair is unsupported.") from exc
    table = request.table
    if not table or len(table[0]) < 2 or any(len(row) != len(table[0]) for row in table):
        raise ValueError("Cannot parse table: rows must have the same number of cells as the header. Header repair is unsupported.")
    years = [cell.strip() for cell in table[0][1:] if re.fullmatch(r"(?:19|20)\d{2}", cell.strip())]
    if not years or len(years) != len(set(years)):
        raise ValueError("Cannot parse header: use explicit, unique YYYY columns in the first row. Header repair is unsupported.")
    return request.model_dump()


def citation_cell(citation: dict, table: list[list[str]]) -> tuple[int, int] | None:
    match = re.search(r"/row:(\d+)/column:(\d+)$", citation.get("locator", ""))
    if not match:
        return None
    row, column = map(int, match.groups())
    return (row, column) if row < len(table) and column < len(table[row]) else None


def cell_id(prefix: str, row: int, column: int) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", prefix):
        raise ValueError("Invalid table anchor prefix")
    return f"{prefix}-cell-r{row}-c{column}"


def highlights(result: dict | None, table: list[list[str]]) -> dict:
    marked = {}

    def add(citations, prefix, verified):
        for cite in citations:
            cell = citation_cell(cite, table)
            if cell is None:
                continue
            mark = marked.setdefault(cell, {"verified": False, "references": []})
            mark["verified"] = mark["verified"] or verified
            ref = prefix + str(cite["citation_number"])
            if ref not in mark["references"]:
                mark["references"].append(ref)

    if result:
        add(result.get("citations", []), "", True)
        by_name = {x["variant"]: x for x in result.get("baselines", [])}
        for variant, _, prefix in BASELINES:
            add(by_name.get(variant, {}).get("citations", []), prefix, variant == "graded_sufficiency")
    return marked


def table_html(table: list[list[str]], result: dict | None = None, *, prefix: str = "pilot") -> str:
    marked = highlights(result, table)
    rows = []
    for ri, row in enumerate(table):
        cells = [f'<th class="row-index" scope="row">{ri + 1}</th>']
        for ci, value in enumerate(row):
            mark = marked.get((ri, ci))
            css = "verified-cell" if mark and mark["verified"] else "baseline-cell" if mark else ""
            refs = '' if not mark else '<span class="cell-refs">' + ''.join(
                f'<a class="citation-chip" target="_self" href="#{cell_id(prefix, ri, ci)}" aria-label="Citation {html.escape(ref)}">{html.escape(ref)}</a>'
                for ref in mark["references"]) + '</span>'
            tag = "th" if ri == 0 or ci == 0 else "td"
            scope = ' scope="col"' if ri == 0 else ' scope="row"' if ci == 0 else ''
            cells.append(f'<{tag}{scope} id="{cell_id(prefix, ri, ci)}" class="{css}">{html.escape(value)}{refs}</{tag}>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return '<div class="source-scroll"><table class="source-table"><caption>Original submitted cells · row numbers include the header</caption>' + ''.join(rows) + '</table></div>'


def badge_html(decision: str, *, extraction_only: bool = False) -> str:
    labels = {"full": ("FULL", "All requested facts supported"),
              "partial": ("PARTIAL", "Only part of the question is supported"),
              "abstain": ("ABSTAIN", "Answer withheld")}
    if decision not in labels:
        raise ValueError("Unknown decision; cannot display a success badge")
    label, detail = labels[decision]
    if extraction_only and decision == "full":
        detail = "At least one value extracted; coverage not checked"
    icon = {"full": "✓", "partial": "◐", "abstain": "⊘"}[decision]
    return f'<div class="decision {decision}" role="status"><span class="decision-icon" aria-hidden="true">{icon}</span><strong>{label}</strong><span>{detail}</span></div>'


def value_html(value: dict, citations: list[dict], table: list[list[str]], *, prefix: str, ref_prefix: str = "") -> str:
    by_number = {c["citation_number"]: c for c in citations}
    refs = []
    for number in value.get("citation_numbers", []):
        cite = by_number.get(number)
        cell = citation_cell(cite, table) if cite else None
        label = html.escape(f"[{ref_prefix}{number}]")
        if cell:
            refs.append(f'<a target="_self" href="#{cell_id(prefix, *cell)}" aria-label="Source {ref_prefix}{number}, row {cell[0]+1}, column {cell[1]+1}">{label}</a>')
        else:
            refs.append(label + ' <small>(cell unavailable)</small>')
    return ('<div class="answer-value"><span class="fact-label">' + html.escape(str(value["metric"]))
            + ' · ' + html.escape(str(value["year"])) + '</span><br><strong>'
            + html.escape(str(value["value"])) + '</strong> ' + ' '.join(refs) + '</div>')


def plain_gap(gap: dict, payload: dict) -> str:
    facts = {x["requirement_id"]: x for x in payload["requested_facts"]}
    fact = facts.get(gap.get("requirement_id"), {})
    label = f"{fact.get('metric', 'This fact')} ({fact.get('year', 'period unspecified')})"
    status = gap.get("status")
    if status == "missing":
        return f"{label}: no matching value was found in the evidence used for this run."
    if status == "contradicted":
        return f"{label}: conflicting values prevent a reliable answer. The graded policy withholds the whole answer."
    if status == "unverified":
        return f"{label}: the pipeline could not verify this fact in the supported table format. Header repair is unsupported."
    return f"{label}: this fact remains unresolved."
