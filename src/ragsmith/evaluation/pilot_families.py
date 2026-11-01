"""Provisional report grouping and four-condition controlled family drafts.

No independent identity verification, annotation gold or scoring is performed.
"""

import copy
from dataclasses import asdict
from decimal import Decimal, InvalidOperation

from ragsmith.evidence.models import Evidence
from ragsmith.evaluation.lineage import SourceManifest
from ragsmith.evaluation.records import (
    PROVISIONAL, FrozenEvidenceRecord, evidence_fingerprint, require_keys,
    require_text, text_tuple,
)
from ragsmith.evaluation.tatqa_adapter import digest
from ragsmith.sufficiency.numeric import values_equal
from ragsmith.value_lookup import LookupQuestion, discover_values


IDENTITY_KEYS = {"context_id", "source_content_sha256", "status", "report_group_id",
                 "organization", "period", "source_reference", "reviewer_id", "notes", "annotation_status"}
FAMILY_KEYS = {"context_id", "source_content_sha256", "status", "question_ids",
               "conflict_value", "reviewer_id", "notes", "annotation_status"}


def family_templates(screening: dict) -> dict:
    identities, families = [], []
    for row in screening["sampling_manifest"]["families"]:
        base = {"context_id": row["context_id"], "source_content_sha256": row["source_content_sha256"],
                "status": "pending", "reviewer_id": "", "notes": "", "annotation_status": PROVISIONAL}
        identities.append({**base, "report_group_id": "", "organization": "", "period": "", "source_reference": ""})
        families.append({**base, "question_ids": [], "conflict_value": ""})
    return {"identities": identities, "families": families}


def _declarations(rows, candidates, keys, ready_status):
    result = {}
    for raw in rows:
        row = require_keys(raw, keys, "pilot declaration")
        uid = row["context_id"]
        require_text(uid, "context_id")
        if uid in result or uid not in candidates:
            raise ValueError("Duplicate or unknown context declaration")
        if row["source_content_sha256"] != candidates[uid]["source_content_sha256"]:
            raise ValueError("Declaration source hash mismatch")
        if row["annotation_status"] != PROVISIONAL:
            raise ValueError("Declarations must remain provisional, single-annotator")
        if row["status"] not in {"pending", ready_status}:
            raise ValueError("Invalid declaration status")
        for key in ("notes", "reviewer_id"):
            if not isinstance(row[key], str):
                raise ValueError("Declaration notes and reviewer must be strings")
        if row["status"] == ready_status:
            require_text(row["reviewer_id"], "reviewer_id")
            require_text(row["notes"], "source-backed declaration notes")
        result[uid] = dict(row)
    return result


def group_contexts(screening: dict, identities: list[dict]) -> tuple[dict, dict]:
    """Union duplicate tables and declared report/version groups transitively."""
    candidates = {row["context_id"]: row for row in screening["sampling_manifest"]["families"]}
    declarations = _declarations(identities, candidates, IDENTITY_KEYS, "declared")
    parents = {uid: uid for uid in candidates}

    def root(uid):
        while parents[uid] != uid:
            parents[uid] = parents[parents[uid]]
            uid = parents[uid]
        return uid

    def join(a, b):
        a, b = root(a), root(b)
        parents[max(a, b)] = min(a, b)

    first_table, first_report = {}, {}
    for uid, candidate in sorted(candidates.items()):
        table = candidate["duplicate_table_group"]
        join(uid, first_table.setdefault(table, uid))
        declaration = declarations.get(uid)
        if declaration is not None:
            for name in ("report_group_id", "organization", "period", "source_reference"):
                if not isinstance(declaration[name], str):
                    raise ValueError("Identity fields must be strings")
                if declaration["status"] == "declared":
                    require_text(declaration[name], name)
                elif declaration[name]:
                    raise ValueError("Pending identity cannot contain asserted identity fields")
            if declaration["status"] == "declared":
                report = declaration["report_group_id"]
                join(uid, first_report.setdefault(report, uid))
    members = {}
    for uid in sorted(candidates):
        members.setdefault(root(uid), []).append(uid)
    groups, by_context = {}, {}
    for contexts in members.values():
        group_id = "report-cluster-" + digest(contexts)
        unresolved = [uid for uid in contexts if uid not in declarations or declarations[uid]["status"] != "declared"]
        groups[group_id] = {"context_ids": contexts, "unresolved_context_ids": unresolved,
                            "identity_status": "pending" if unresolved else "provisional_declared",
                            "report_group_ids": sorted({declarations[uid]["report_group_id"] for uid in contexts
                                                        if uid in declarations and declarations[uid]["status"] == "declared"})}
        by_context.update({uid: group_id for uid in contexts})
    return by_context, groups


def build_family_drafts(screening: dict, canonical: dict, identities: list[dict],
                        family_decisions: list[dict]) -> dict:
    """Create deterministic grouped drafts, never reviewed gold or model scores."""
    candidates = {row["context_id"]: row for row in screening["sampling_manifest"]["families"]}
    decisions = _declarations(family_decisions, candidates, FAMILY_KEYS, "ready")
    by_context, groups = group_contexts(screening, identities)
    manifest = SourceManifest.from_payload(canonical["lineage"])
    requests = {row["question_id"]: LookupQuestion.from_payload(row) for row in canonical["inputs"]}
    frozen = {row["question_id"]: FrozenEvidenceRecord.from_payload(row) for row in canonical["evidence"]}
    transforms = {row["question_id"]: row for row in canonical["transformations"]}
    if any(len(rows) != len(mapping) for rows, mapping in (
        (canonical["inputs"], requests), (canonical["evidence"], frozen),
        (canonical["transformations"], transforms),
    )):
        raise ValueError("Duplicate canonical question records")
    if set(requests) != set(frozen) or set(requests) != set(transforms):
        raise ValueError("Canonical input/evidence/transformation question mismatch")
    for record in frozen.values():
        manifest.validate_evidence(list(record.evidence))
    eligible, selection_log = [], []
    for uid, candidate in sorted(candidates.items(), key=lambda pair: pair[1]["screening_order"]):
        row = decisions.get(uid)
        if row is None or row["status"] == "pending":
            if row is not None and (row["question_ids"] != [] or row["conflict_value"] != ""):
                raise ValueError("Pending family cannot contain selected facts or conflict value")
            selection_log.append({"context_id": uid, "status": "pending_family_decision"})
            continue
        qids = text_tuple(row["question_ids"], "family question IDs")
        if len(qids) != 2 or not set(qids) <= set(candidate["candidate_question_ids"]) or not set(qids) <= set(requests):
            raise ValueError("A family needs two distinct accepted questions from its context")
        facts = []
        for qid in qids:
            if transforms[qid]["source_content_sha256"] != candidate["source_content_sha256"]:
                raise ValueError("Canonical transformation source hash mismatch")
            req = requests[qid].requirements
            if len(req) != 1:
                raise ValueError("Family facts must have one supplied canonical requirement")
            item = next((item for item in frozen[qid].evidence if item.evidence_id == transforms[qid]["evidence_id"]), None)
            if item is None or item.table_id != uid:
                raise ValueError("Family transformation references missing or wrong-context evidence")
            facts.append((req[0], item))
        if (facts[0][0].metric.casefold(), facts[0][0].year) == (facts[1][0].metric.casefold(), facts[1][0].year):
            raise ValueError("Two family requirements must request distinct metric/year facts")
        if facts[0][1].locator == facts[1][1].locator:
            raise ValueError("Two family facts must bind distinct source value cells")
        for requirement, item in facts:
            if len(discover_values(requirement, [item]).candidates) != 1:
                raise ValueError("Bound family evidence does not match its requirement")
        conflict = row["conflict_value"]
        require_text(conflict, "explicit synthetic conflict value")
        if any(char in conflict for char in (";", "\n", "\r")):
            raise ValueError("Conflict value contains unsupported delimiters")
        discovered = discover_values(facts[0][0], [facts[0][1]]).candidates
        if len(discovered) != 1:
            raise ValueError("Bound family evidence does not match its requirement")
        original_value = discovered[0].value
        try:
            if not Decimal(conflict).is_finite():
                raise ValueError("Synthetic conflict cannot be nonfinite")
        except InvalidOperation:
            pass
        if values_equal(original_value, conflict):
            raise ValueError("Synthetic conflict value must differ from the source value")
        group = by_context[uid]
        if groups[group]["unresolved_context_ids"]:
            selection_log.append({"context_id": uid, "status": "pending_report_identity", "group_id": group})
            continue
        eligible.append((uid, facts, conflict.strip(), group))
    plan = screening["sampling_manifest"]
    selected = eligible[:plan["target_families"]]
    partitions, development_count = {}, 0
    for uid, _, _, group in selected:
        if group not in partitions:
            partitions[group] = "development" if development_count < plan["target_development_families"] else "held_out"
            if partitions[group] == "development":
                development_count += sum(candidate[3] == group for candidate in selected)
    out_inputs, out_evidence, declarations, links, changes, families = [], [], [], [], [], []
    for uid, facts, conflict, group in selected:
        parent_ids = set()
        for _, item in facts:
            parent_ids.add(next(link.source_id for link in manifest.evidence_links if link.evidence_id == item.evidence_id))
        family_id, doc_id = f"family:{uid}", f"pilot:{uid}"
        question = "Provide these source facts: " + "; ".join(f"{req.metric} ({req.year})" for req, _ in facts) + "."
        requirements = [{"requirement_id": f"fact-{i}", "metric": req.metric, "year": req.year,
                         "document_ids": [doc_id]} for i, (req, _) in enumerate(facts, 1)]
        families.append({"family_id": family_id, "context_id": uid, "group_id": group,
                         "partition": partitions[group], "question_ids": list(decisions[uid]["question_ids"]),
                         "status": "provisional_draft", "annotation_status": PROVISIONAL})
        for condition in ("full", "partial", "missing", "conflict"):
            source_rows = list(facts) if condition in {"full", "conflict"} else list(facts[:1]) if condition == "partial" else []
            artifact = [{"parent_evidence_id": item.evidence_id, "content": item.content} for _, item in source_rows]
            if condition == "conflict":
                artifact.append({"parent_evidence_id": facts[0][1].evidence_id,
                                 "content": f"Metric: {facts[0][0].metric}; {facts[0][0].year}: {conflict}"})
            version = digest({"family": family_id, "condition": condition, "rows": artifact})
            source_id = f"{family_id}:{condition}"
            declarations.append({"source_id": source_id, "document_id": doc_id, "document_version": version,
                                 "group_id": group, "source_uri": f"controlled://{uid}/{condition}",
                                 "source_sha256": version, "license": "CC BY 4.0; controlled adaptation",
                                 "parent_source_ids": sorted(parent_ids),
                                 "transformation": "synthetic_conflict" if condition == "conflict" else
                                 "masking" if condition in {"partial", "missing"} else "canonicalization"})
            items = []
            for index, row in enumerate(artifact):
                parent = next(item for _, item in facts if item.evidence_id == row["parent_evidence_id"])
                payload = asdict(parent)
                payload.update(evidence_id="pilot-" + digest({"version": version, "index": index}),
                               document_id=doc_id, document_version=version, content=row["content"])
                payload["metadata"] = {**(parent.metadata or {}), "parent_evidence_id": parent.evidence_id}
                item = Evidence(**payload)
                items.append(asdict(item))
                links.append({"evidence_id": item.evidence_id, "source_id": source_id,
                              "fingerprint": evidence_fingerprint(item)})
            qid = f"{family_id}/{condition}"
            out_inputs.append({"question_id": qid, "question": question, "requirements": copy.deepcopy(requirements)})
            out_evidence.append({"question_id": qid, "evidence": items})
            changes.append({"question_id": qid, "group_id": group, "partition": partitions[group],
                            "condition": condition, "parent_evidence_ids": [item.evidence_id for _, item in facts],
                            "removed_evidence_ids": [item.evidence_id for _, item in facts if
                                                     item.evidence_id not in {row['parent_evidence_id'] for row in artifact}],
                            "changed_fields": [{"field": "content", "parent_evidence_id": facts[0][1].evidence_id,
                                                "before": facts[0][1].content, "after": artifact[-1]["content"]}]
                            if condition == "conflict" else []})
    # Include only selected sources' ancestors, remapping all versions to their
    # declared report cluster. Never retain unresolved sources in the draft graph.
    needed = {parent for source in declarations for parent in source["parent_source_ids"]}
    old_sources = {source["source_id"]: source for source in canonical["lineage"]["sources"]}
    while True:
        expanded = needed | {parent for key in needed for parent in old_sources[key]["parent_source_ids"]}
        if expanded == needed:
            break
        needed = expanded
    for key in sorted(needed):
        source = copy.deepcopy(old_sources[key])
        uid = next(uid for uid in candidates if source["group_id"] == f"context-pending:{uid}")
        source["group_id"] = by_context[uid]
        declarations.append(source)
    lineage = {"schema_version": "1.0", "sources": declarations, "evidence_links": links}
    final_manifest = SourceManifest.from_payload(lineage)
    for request, evidence in zip(out_inputs, out_evidence):
        final_manifest.validate_request(LookupQuestion.from_payload(request))
        final_manifest.validate_evidence(list(FrozenEvidenceRecord.from_payload(evidence).evidence))
    selection_log.extend({"context_id": uid, "status": "draft_selected" if index < len(selected) else "outside_target",
                          "group_id": group} for index, (uid, _, _, group) in enumerate(eligible))
    return {"inputs": out_inputs, "evidence": out_evidence, "lineage": lineage,
            "changes": changes, "families": families, "selection_log": selection_log,
            "coordinator_declarations": {"identities": sorted(copy.deepcopy(identities), key=lambda row: row["context_id"]),
                                         "families": [decisions[uid] for uid in sorted(decisions)]},
            "groups": groups, "summary": {"annotation_status": PROVISIONAL, "research_evidence": False,
                "status": "provisional_draft_not_final_pilot", "gold_generated": False,
                "draft_families": len(selected), "draft_cases": len(out_inputs),
                "target_shortfall": max(0, plan["target_families"] - len(selected)),
                "development_families": sum(row["partition"] == "development" for row in families),
                "held_out_families": sum(row["partition"] == "held_out" for row in families),
                "selected_report_clusters": len(partitions),
                "identity_status": "manual_declarations_not_independently_verified",
                "evidence_scope": "two_bound_facts_per_family_controlled_conditions_not_complete_corpus"}}
