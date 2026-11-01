"""Validate provisional manual decisions and lossless source-cell transforms.

No dataset answer annotation is consulted and no evaluation gold is created.
"""

import re
from dataclasses import asdict

from ragsmith.evidence.models import Evidence
from ragsmith.evaluation.lineage import SourceManifest
from ragsmith.evaluation.records import (
    PROVISIONAL, evidence_fingerprint, require_keys, require_text, text_tuple,
)
from ragsmith.evaluation.tatqa_adapter import digest
from ragsmith.value_lookup import LookupQuestion


BINDING_KEYS = {"metric_cell_locator", "year_cell_locator", "unit_cell_locator", "value_cell_locator"}
DECISION_KEYS = {"question_id", "source_content_sha256", "question_sha256", "decision",
                 "reviewer_id", "notes", "rejection_reasons", "binding", "annotation_status"}


def question_digest(row: dict) -> str:
    return digest({key: row[key] for key in ("question_id", "context_id", "question")})


def decision_templates(screening: dict) -> list[dict]:
    sources = {row["context_id"]: row for row in screening["sources"]}
    return [{"question_id": row["question_id"],
             "source_content_sha256": sources[row["context_id"]]["source_content_sha256"],
             "question_sha256": question_digest(row), "decision": "pending", "reviewer_id": "",
             "notes": "", "rejection_reasons": [], "binding": None, "annotation_status": PROVISIONAL}
            for row in screening["screening_ledger"] if row["label_gate"] == "pass"]


def _safe_text(text: str, field: str) -> str:
    require_text(text, field)
    if any(char in text for char in (";", "\n", "\r")):
        raise ValueError(f"{field} contains unsupported canonical delimiters")
    return text.strip()


def resolve_binding(source: dict, raw_binding: object) -> dict:
    binding = require_keys(raw_binding, BINDING_KEYS, "cell binding")
    cells = {row["locator"]: row for row in source["table_cells"]}
    selected = {}
    for name, locator in binding.items():
        require_text(locator, name)
        if locator not in cells:
            raise ValueError("Binding references an unknown or cross-context cell")
        selected[name] = cells[locator]
    if len(set(binding.values())) != 4:
        raise ValueError("Metric, year, unit and value must bind distinct cells")
    metric, year, unit, value = (selected[name + "_cell_locator"] for name in ("metric", "year", "unit", "value"))
    if metric["row"] != value["row"] or metric["column"] >= value["column"]:
        raise ValueError("Metric must be a row label to the left of its value")
    if year["column"] != value["column"] or year["row"] >= value["row"]:
        raise ValueError("Year must be a column header above its value")
    if unit["row"] >= value["row"]:
        raise ValueError("Unit must be an explicit header above its value")
    year_text = _safe_text(year["text"], "year")
    if re.fullmatch(r"[1-9][0-9]{3}", year_text) is None:
        raise ValueError("Year cell must contain only a four-digit year")
    return {"metric": _safe_text(metric["text"], "metric"), "year": int(year_text),
            "unit": _safe_text(unit["text"], "unit"),
            "value": _safe_text(value["text"], "value"),
            "cell_locators": dict(binding), "value_row": value["row"]}


def canonicalize_decisions(screening: dict, decisions: list[dict]) -> dict:
    """Compile only explicitly accepted, hash-bound decisions.

    Missing decisions remain pending. Hash/geometry checks cannot establish
    semantic correctness, explicit unit meaning or original report identity.
    """
    sources = {row["context_id"]: row for row in screening["sources"]}
    questions = {row["question_id"]: row for row in screening["screening_ledger"]}
    if len(questions) != len(screening["screening_ledger"]) or len(sources) != len(screening["sources"]):
        raise ValueError("Duplicate screening source/question")
    for source in sources.values():
        core = {key: source[key] for key in ("context_id", "table_cells", "table_shape", "paragraphs")}
        if digest(core) != source["source_content_sha256"]:
            raise ValueError("Source content hash mismatch")
        shape = source["table_shape"]
        expected = {(r, c) for r, width in enumerate(shape) for c in range(width)}
        actual = {(cell["row"], cell["column"]) for cell in source["table_cells"]}
        if len(actual) != len(source["table_cells"]) or actual != expected:
            raise ValueError("Invalid cell coordinates")
        for cell in source["table_cells"]:
            if cell["locator"] != f"table:{source['context_id']}/row:{cell['row']}/column:{cell['column']}":
                raise ValueError("Invalid cell locator")
    accepted, dispositions, seen = {}, [], set()
    for raw in decisions:
        row = require_keys(raw, DECISION_KEYS, "manual decision")
        qid = row["question_id"]
        require_text(qid, "question_id")
        if qid in seen or qid not in questions:
            raise ValueError("Duplicate or unknown decision question ID")
        seen.add(qid)
        question = questions[qid]
        source = sources[question["context_id"]]
        if question["label_gate"] != "pass":
            raise ValueError("Manual decisions cannot override the approved label gate")
        if row["source_content_sha256"] != source["source_content_sha256"] or row["question_sha256"] != question_digest(question):
            raise ValueError("Decision source/question hash mismatch")
        if row["annotation_status"] != PROVISIONAL:
            raise ValueError("Manual screening must remain provisional, single-annotator")
        if row["decision"] not in {"pending", "accept", "reject"}:
            raise ValueError("Unknown screening decision")
        if not isinstance(row["notes"], str) or not isinstance(row["reviewer_id"], str):
            raise ValueError("Reviewer and notes must be strings")
        reasons = text_tuple(row["rejection_reasons"], "rejection_reasons")
        if row["decision"] != "pending":
            require_text(row["reviewer_id"], "reviewer_id")
            require_text(row["notes"], "source-backed decision notes")
        if (row["decision"] == "reject") != bool(reasons):
            raise ValueError("Only rejected decisions must have rejection reasons")
        if row["decision"] == "accept":
            accepted[qid] = resolve_binding(source, row["binding"])
        elif row["binding"] is not None:
            raise ValueError("Only accepted decisions may contain a cell binding")
        dispositions.append({"question_id": qid, "decision": row["decision"],
                             "reviewer_id": row["reviewer_id"], "notes": row["notes"],
                             "rejection_reasons": list(reasons)})
    # Units are not verified by the production engine: ambiguous same-key units
    # must fail here rather than collapse into an apparently supported row.
    units = {}
    for qid, fact in accepted.items():
        key = (questions[qid]["context_id"], fact["metric"].casefold(), fact["year"])
        if key in units and units[key] != fact["unit"]:
            raise ValueError("Same metric/year has inconsistent bound units")
        units[key] = fact["unit"]
    declarations, links, evidence_rows, requests, transforms = [], [], [], [], []
    by_context = {}
    for qid in sorted(accepted):
        by_context.setdefault(questions[qid]["context_id"], []).append(qid)
    for uid, qids in sorted(by_context.items()):
        source = sources[uid]
        unique = {digest(accepted[qid]): accepted[qid] for qid in qids}
        canonical_version = digest({"source_content_sha256": source["source_content_sha256"],
                                    "bindings": [unique[key] for key in sorted(unique)]})
        parent_id, canonical_id = f"original:{uid}", f"canonical:{uid}"
        doc_id = f"tatqa:{uid}:canonical"
        group = f"context-pending:{uid}"
        for source_id, document_id, version, parents, transformation in (
            (parent_id, f"tatqa:{uid}:original", source["source_content_sha256"], [], "original"),
            (canonical_id, doc_id, canonical_version, [parent_id], "canonicalization"),
        ):
            declarations.append({"source_id": source_id, "document_id": document_id,
                                 "document_version": version, "group_id": group,
                                 "source_uri": screening["summary"]["source"]["url"] + f"#table={uid}",
                                 "source_sha256": version, "license": "CC BY 4.0",
                                 "parent_source_ids": parents, "transformation": transformation})
        items, fact_ids = [], {}
        for key, fact in sorted(unique.items()):
            eid = "cell-" + digest({"context": uid, "version": canonical_version, "binding": fact})
            item = Evidence(eid, doc_id, canonical_version, "table_row",
                            f"Metric: {fact['metric']}; {fact['year']}: {fact['value']}",
                            fact["cell_locators"]["value_cell_locator"], row_index=fact["value_row"],
                            table_id=uid, extraction_method="manual_cell_binding_v1",
                            metadata={"unit": fact["unit"], "cell_locators": fact["cell_locators"],
                                      "dataset_file_sha256": source["dataset_file_sha256"],
                                      "parent_content_sha256": source["source_content_sha256"]})
            items.append(item)
            fact_ids[key] = eid
            links.append({"evidence_id": eid, "source_id": canonical_id,
                          "fingerprint": evidence_fingerprint(item)})
        for qid in qids:
            fact = accepted[qid]
            request = {"question_id": qid, "question": questions[qid]["question"], "requirements": [
                {"requirement_id": "fact-1", "metric": fact["metric"], "year": fact["year"], "document_ids": [doc_id]}]}
            LookupQuestion.from_payload(request)
            requests.append(request)
            evidence_rows.append({"question_id": qid, "evidence": [asdict(item) for item in items]})
            transforms.append({"question_id": qid, "evidence_id": fact_ids[digest(fact)],
                               "source_content_sha256": source["source_content_sha256"],
                               "binding": fact["cell_locators"], "trimmed_cell_edges_only": True})
    lineage = {"schema_version": "1.0", "sources": declarations, "evidence_links": links}
    manifest = SourceManifest.from_payload(lineage)
    for row in evidence_rows:
        manifest.validate_evidence([Evidence(**item) for item in row["evidence"]])
    accepted_count, rejected_count = len(accepted), sum(row["decision"] == "reject" for row in dispositions)
    gate_count = sum(row["label_gate"] == "pass" for row in questions.values())
    return {"inputs": requests, "evidence": evidence_rows, "lineage": lineage,
            "transformations": transforms, "decision_log": dispositions,
            "summary": {"schema_version": "1.0", "annotation_status": PROVISIONAL,
                        "accepted_questions": accepted_count, "rejected_questions": rejected_count,
                        "pending_questions": gate_count - accepted_count - rejected_count,
                        "source_contexts_with_accepted_bindings": len(by_context),
                        "evidence_scope": "accepted_bound_cells_only_not_complete_corpus",
                        "report_identity_status": "unresolved_context_groups_only",
                        "pilot_selected": False, "gold_generated": False, "research_evidence": False}}
