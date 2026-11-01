"""Gold-free retrieval exports and masked reviewer calibration materials."""

import hashlib
import json
import random
import sqlite3
import tempfile
from pathlib import Path

from ragsmith.evaluation.lineage import SourceManifest
from ragsmith.evaluation.records import (
    FrozenEvidenceRecord, evidence_fingerprint, read_jsonl, require_text,
)
from ragsmith.evaluation.retrieval_metrics import RankingRecord
from ragsmith.retrieval import RetrievalConfig, retrieve_question_evidence
from ragsmith.value_lookup import LookupQuestion


def load_bundle(inputs: Path, evidence: Path, lineage: Path):
    """Read only system inputs and registered source evidence; never labels."""
    paths = {"inputs": inputs, "evidence": evidence, "lineage": lineage}
    contents = {name: path.read_bytes() for name, path in paths.items()}
    manifest = SourceManifest.from_file(lineage)
    requests, universe = {}, {}
    for row in read_jsonl(inputs):
        request = LookupQuestion.from_payload(row)
        if request.question_id in requests:
            raise ValueError("Duplicate input question ID")
        manifest.validate_request(request)
        requests[request.question_id] = request
    for row in read_jsonl(evidence):
        record = FrozenEvidenceRecord.from_payload(row)
        if record.question_id in universe:
            raise ValueError("Duplicate evidence question ID")
        manifest.validate_evidence(list(record.evidence))
        universe[record.question_id] = list(record.evidence)
    if not requests or set(requests) != set(universe):
        raise ValueError("Evidence must cover exactly the nonempty input questions")
    for qid, request in requests.items():
        if any(not any(not req.document_ids or item.document_id in req.document_ids
                       for req in request.requirements) for item in universe[qid]):
            raise ValueError("Evidence outside declared question scope")
    if any(path.read_bytes() != contents[name] for name, path in paths.items()):
        raise ValueError("Bundle changed during loading")
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in contents.items()}
    return requests, universe, manifest, hashes


def export_rankings(db_path: Path, inputs: Path, evidence: Path, lineage: Path,
                    *, limit: int = 100) -> dict:
    """Freeze one SQLite online-backup snapshot for all questions and log top-k.

    Returned hits must match the supplied universe exactly. This does not prove
    that the registered universe exhausts the corpus or authenticate live files.
    """
    config = RetrievalConfig(limit)
    requests, universe, manifest, hashes = load_bundle(inputs, evidence, lineage)
    rows, audits = [], []
    with tempfile.TemporaryDirectory(prefix="ragsmith-eval-") as folder:
        snapshot = Path(folder) / "snapshot.sqlite"
        source = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
        target = sqlite3.connect(snapshot)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        snapshot_hash = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        for qid, request in requests.items():
            result = retrieve_question_evidence(snapshot, request, config)
            manifest.validate_evidence(list(result.evidence))
            registered = {item.evidence_id: evidence_fingerprint(item) for item in universe[qid]}
            if any(registered.get(item.evidence_id) != evidence_fingerprint(item)
                   for item in result.evidence):
                raise ValueError("Retrieved evidence is absent or changed in the declared universe")
            row = {"question_id": qid, "rankings": [
                {"requirement_id": query["requirement_id"],
                 "evidence_ids": [hit["evidence_id"] for hit in query["hits"]]}
                for query in result.audit["queries"]]}
            RankingRecord.from_payload(row).select(request, universe[qid], limit)
            rows.append(row)
            audits.append({"question_id": qid, **result.audit})
    return {"schema_version": "1.0", "rankings": rows, "audit": audits,
            "file_hashes": hashes, "database_snapshot_sha256": snapshot_hash,
            "snapshot_method": "sqlite_online_backup", "limit_per_requirement": limit,
            "gold_read": False, "research_evidence": False}


def calibration_packets(inputs: Path, evidence: Path, lineage: Path, *,
                        annotators: tuple[str, str] = ("reviewer-a", "reviewer-b"),
                        seed: int = 1729) -> dict:
    """Mask identifiers and omit model outputs, annotations and transformations.

    The coordinator mapping must not be shared with reviewers. Content remains
    visible and can itself reveal interventions; this is label/model blinding,
    not guaranteed blinding to experimental condition.
    """
    if len(annotators) != 2:
        raise ValueError("Exactly two annotator IDs are required")
    for author in annotators:
        require_text(author, "annotator_id")
    if annotators[0] == annotators[1]:
        raise ValueError("Annotator IDs must differ")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    requests, universe, _, hashes = load_bundle(inputs, evidence, lineage)
    order = sorted(requests)
    random.Random(seed).shuffle(order)
    items, mapping = [], []
    for number, qid in enumerate(order, 1):
        request = requests[qid]
        item_id = f"item-{number:04d}"
        document_ids = sorted({item.document_id for item in universe[qid]} |
                              {doc for req in request.requirements for doc in req.document_ids})
        documents = {doc: f"source-{i:03d}" for i, doc in enumerate(document_ids, 1)}
        # Shuffle independently of input/retrieval order and mask all evidence IDs.
        sources = sorted(universe[qid], key=lambda item: item.evidence_id)
        random.Random(seed + number).shuffle(sources)
        evidence_ids = {item.evidence_id: f"evidence-{i:03d}" for i, item in enumerate(sources, 1)}
        requirements = {req.requirement_id: f"requirement-{i:02d}"
                        for i, req in enumerate(request.requirements, 1)}
        items.append({"item_id": item_id, "question": request.question,
                      "requirements": [{"requirement_id": requirements[req.requirement_id],
                                        "metric": req.metric, "year": req.year,
                                        "source_scope": [documents[doc] for doc in req.document_ids]}
                                       for req in request.requirements],
                      "evidence": [{"evidence_id": evidence_ids[item.evidence_id],
                                    "source_id": documents[item.document_id],
                                    "document_version": item.document_version,
                                    "kind": item.kind, "content": item.content,
                                    "locator": item.locator, "page_number": item.page_number,
                                    "section_path": item.section_path, "table_id": item.table_id,
                                    "row_index": item.row_index,
                                    "extraction_method": item.extraction_method} for item in sources]})
        mapping.append({"item_id": item_id, "question_id": qid,
                        "requirements": requirements, "documents": documents,
                        "evidence_ids": evidence_ids})
    return {"packet": {"schema_version": "1.0", "purpose": "synthetic calibration or provisional annotation",
                       "items": items},
            "templates": {author: [{"item_id": item["item_id"], "annotator_id": author,
                                     "label": ""} for item in items] for author in annotators},
            "coordinator_only": {"file_hashes": hashes, "seed": seed, "mapping": mapping,
                                 "source_manifest": str(lineage.resolve()),
                                 "gold_read": False, "research_evidence": False}}


def write_new_bundle(output: Path, files: dict[str, object]) -> None:
    """Require a fresh directory, protecting previously completed annotations."""
    if any(Path(name).name != name for name in files):
        raise ValueError("Output names must be plain filenames")
    serialized = {name: ("\n".join(json.dumps(row, ensure_ascii=False, allow_nan=False)
                                   for row in value) + "\n") if name.endswith(".jsonl")
                  else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
                  for name, value in files.items()}
    output.mkdir(parents=True, exist_ok=False)
    for name, content in serialized.items():
        (output / name).write_text(content, encoding="utf-8")
