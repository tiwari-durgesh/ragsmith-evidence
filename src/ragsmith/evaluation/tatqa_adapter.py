"""Pinned TAT-QA source adaptation and provisional, label-only screening.

No inference, semantic eligibility decision, canonical row or pilot gold is
produced here. Upstream annotations are confined to coordinator-only records.
"""

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from ragsmith.evaluation.corpus_audit import FILES, REVISION
from ragsmith.evaluation.records import PROVISIONAL, require_text, strict_json


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def load_pinned_split(source_dir: Path, audit_path: Path, split: str = "train") -> tuple[list, dict]:
    """Anchor bytes to the committed audit, not a mutable adjacent manifest."""
    if split not in FILES:
        raise ValueError("Unknown TAT-QA split")
    audit_bytes = audit_path.read_bytes()
    audit = strict_json(audit_bytes.decode("utf-8"))
    if audit.get("source_revision") != REVISION:
        raise ValueError("Unexpected source revision in trusted audit")
    manifest = audit["source_manifest"]
    if manifest["revision"] != REVISION:
        raise ValueError("Unexpected manifest revision")
    entries = [item for item in manifest["files"] if item["path"] == FILES[split]]
    if len(entries) != 1:
        raise ValueError("Trusted audit must identify exactly one split file")
    entry = entries[0]
    expected_url = f"https://raw.githubusercontent.com/NExTplusplus/TAT-QA/{REVISION}/dataset_raw/{FILES[split]}"
    if entry["url"] != expected_url:
        raise ValueError("Unexpected pinned source URL")
    data = (source_dir / FILES[split]).read_bytes()
    actual_hash = hashlib.sha256(data).hexdigest()
    if actual_hash != entry["sha256"] or len(data) != entry["bytes"]:
        raise ValueError("Source bytes do not match trusted audit")
    contexts = strict_json(data.decode("utf-8"))
    if not isinstance(contexts, list) or not contexts:
        raise ValueError("Source split must be a nonempty context list")
    return contexts, {"revision": REVISION, "split": split, "file": FILES[split],
                      "sha256": actual_hash, "url": entry["url"],
                      "trusted_audit_sha256": hashlib.sha256(audit_bytes).hexdigest()}


def prepare_screening(contexts: list, provenance: dict, *, seed: int = 1729,
                      target_families: int = 60, development_families: int = 12) -> dict:
    """Enumerate label gates and draft a context-grouped review queue.

    Identical normalized tables are conservatively linked. These links do not
    recover report identity; partitions remain pending and no family is accepted.
    """
    if provenance.get("revision") != REVISION or provenance.get("split") != "train":
        raise ValueError("Custom pilot screening is restricted to pinned training data")
    if type(seed) is not int or type(target_families) is not int or target_families < 1:
        raise ValueError("Seed and positive target must be integers")
    if type(development_families) is not int or not 0 < development_families < target_families:
        raise ValueError("Development target must be between zero and total target")
    sources, ledger, context_ledger, annotation_aids, candidates = [], [], [], [], []
    seen_contexts, seen_questions = set(), set()
    for context in contexts:
        table = context["table"]
        uid = table["uid"]
        require_text(uid, "table uid")
        if uid in seen_contexts:
            raise ValueError("Duplicate context/table UID")
        seen_contexts.add(uid)
        cells = table["table"]
        if (not isinstance(cells, list) or not cells or
                any(not isinstance(row, list) or not row or
                    any(not isinstance(cell, str) for cell in row) for row in cells)):
            raise ValueError("Table must contain nonempty rows of string cells")
        paragraphs = context["paragraphs"]
        if not isinstance(paragraphs, list):
            raise ValueError("Paragraphs must be a list")
        paragraph_rows, paragraph_ids = [], set()
        for paragraph in paragraphs:
            require_text(paragraph["uid"], "paragraph uid")
            if paragraph["uid"] in paragraph_ids or not isinstance(paragraph["text"], str):
                raise ValueError("Invalid or duplicate paragraph")
            paragraph_ids.add(paragraph["uid"])
            paragraph_rows.append({"uid": paragraph["uid"], "order": paragraph["order"],
                                   "text": paragraph["text"],
                                   "locator": f"table:{uid}/paragraph:{paragraph['uid']}"})
        source = {"context_id": uid, "table_cells": [
            {"row": r, "column": c, "text": cell,
             "locator": f"table:{uid}/row:{r}/column:{c}"}
            for r, row in enumerate(cells) for c, cell in enumerate(row)],
                  "table_shape": [len(row) for row in cells], "paragraphs": paragraph_rows}
        source_hash = digest(source)
        table_hash = digest([[" ".join(cell.split()).casefold() for cell in row] for row in cells])
        sources.append({**source, "source_content_sha256": source_hash,
                        "dataset_file_sha256": provenance["sha256"]})
        candidate_ids = []
        if not isinstance(context["questions"], list):
            raise ValueError("Questions must be a list")
        for question in context["questions"]:
            qid = question["uid"]
            require_text(qid, "question uid")
            require_text(question["question"], "question")
            if qid in seen_questions:
                raise ValueError("Duplicate question UID")
            seen_questions.add(qid)
            if question["answer_type"] not in {"span", "multi-span", "arithmetic", "count"}:
                raise ValueError("Unknown upstream answer type")
            if question["answer_from"] not in {"table", "text", "table-text"}:
                raise ValueError("Unknown upstream answer source")
            gate = question["answer_type"] == "span" and question["answer_from"] == "table"
            reasons = ([] if gate else ["outside_table_single_span_label_gate"])
            if gate:
                candidate_ids.append(qid)
            ledger.append({"question_id": qid, "context_id": uid,
                           "question": question["question"], "label_gate": "pass" if gate else "exclude",
                           "gate_reasons": reasons, "semantic_eligibility": "pending" if gate else "not_screened",
                           "manual_rejection_reasons": [], "reviewer_id": "", "notes": "",
                           "binding": {"metric": "", "year": None, "unit": "",
                                       "value_cell_locator": "", "header_cell_locators": []},
                           "annotation_status": PROVISIONAL})
            # Annotation aids are never placed in source rows or inference inputs.
            annotation_aids.append({"question_id": qid, "context_id": uid,
                                    "upstream_answer_type": question["answer_type"],
                                    "upstream_answer_from": question["answer_from"],
                                    "upstream_answer": question["answer"],
                                    "upstream_scale": question["scale"],
                                    "upstream_comparison_flag": question["req_comparison"]})
        context_ledger.append({"context_id": uid, "table_span_questions": len(candidate_ids),
                               "family_label_gate": "pass" if len(candidate_ids) >= 2 else "exclude",
                               "reasons": [] if len(candidate_ids) >= 2 else ["fewer_than_two_table_single_spans"],
                               "semantic_eligibility": "pending" if len(candidate_ids) >= 2 else "not_screened"})
        if len(candidate_ids) >= 2:
            candidates.append({"context_id": uid, "candidate_question_ids": sorted(candidate_ids),
                               "duplicate_table_group": "table-" + table_hash,
                               "source_content_sha256": source_hash,
                               "report_identity": {"report_group_id": "", "organization": "",
                                                   "period": "", "source_reference": "",
                                                   "reviewer_id": "", "notes": ""},
                               "eligibility": "pending_manual_review", "partition": "pending"})
    # Shuffle sorted duplicate groups, then contexts; identical tables remain together.
    groups = {}
    for candidate in candidates:
        groups.setdefault(candidate["duplicate_table_group"], []).append(candidate)
    group_ids = sorted(groups)
    random.Random(seed).shuffle(group_ids)
    ordered = [candidate for group in group_ids
               for candidate in sorted(groups[group], key=lambda row: row["context_id"])]
    for rank, candidate in enumerate(ordered, 1):
        candidate["screening_order"] = rank
    counts = Counter(row["label_gate"] for row in ledger)
    summary = {"schema_version": "1.0", "source": provenance,
               "attribution": {"dataset": "TAT-QA", "creators": "NExTplusplus/TAT-QA contributors",
                               "license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
                               "changes": "Cell locators, source hashes, screening templates and draft duplicate groups added; no canonicalization"},
               "contexts": len(sources), "questions": len(ledger),
               "label_gate_pass": counts["pass"], "label_gate_excluded": counts["exclude"],
               "label_gate_fraction": counts["pass"] / len(ledger) if ledger else None,
               "candidate_contexts_with_two_spans": len(candidates),
               "duplicate_table_groups": len(groups), "semantic_accepted": None,
               "semantic_accepted_fraction": None, "report_identities_verified": 0,
               "annotation_status": PROVISIONAL, "research_evidence": False}
    manifest = {"schema_version": "1.0", "status": "draft_screening_queue_not_selected_pilot",
                "seed": seed, "target_families": target_families,
                "target_development_families": development_families,
                "target_held_out_families": target_families - development_families,
                "target_conditions_per_family": 4, "accepted_families": 0,
                "remaining_target": target_families, "selected_shortfall": None,
                "screening_queue_below_target": len(candidates) < target_families,
                "partition_status": "blocked_on_semantic_screen_and_report_identity",
                "families": ordered}
    return {"sources": sources, "screening_ledger": ledger, "context_screening_ledger": context_ledger,
            "coordinator_annotation_aids": annotation_aids,
            "sampling_manifest": manifest, "summary": summary}
