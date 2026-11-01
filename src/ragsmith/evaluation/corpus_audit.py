"""Reproducible label-only TAT-QA scope audit; no model or answer scoring."""

import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path


REVISION = "870accc41953dcde885aabeb963d94aabdc0fbc3"
FILES = {
    "train": "tatqa_dataset_train.json",
    "dev": "tatqa_dataset_dev.json",
    "test_gold": "tatqa_dataset_test_gold.json",
}


def fetch_sources(root: Path) -> None:
    """Explicitly fetch pinned public source files into caller-selected storage."""
    root.mkdir(parents=True, exist_ok=True)
    base = f"https://raw.githubusercontent.com/NExTplusplus/TAT-QA/{REVISION}/"
    records = []
    names = [f"dataset_raw/{name}" for name in FILES.values()]
    names += ["README.md", "LICENSE"]
    for name in names:
        url = base + name
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        target = root / Path(name).name
        target.write_bytes(data)
        records.append({"path": target.name, "url": url,
                        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    (root / "source_manifest.json").write_text(json.dumps(
        {"revision": REVISION, "files": records}, indent=2
    ), encoding="utf-8")


def count_questions(contexts: list) -> dict:
    """Count extraction labels and a conservative table-span eligibility screen.

    These counts do not assert compatibility with the metric/year verifier.
    Header/year, unit, source alignment and ambiguity require manual screening.
    """
    questions = [question for context in contexts for question in context["questions"]]
    ids = [question["uid"] for question in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source question IDs")
    types = Counter(question["answer_type"] for question in questions)
    origins = Counter(question["answer_from"] for question in questions)
    extraction = sum(question["answer_type"] in {"span", "multi-span"}
                     for question in questions)
    table_span = sum(question["answer_type"] == "span"
                     and question["answer_from"] == "table" for question in questions)
    return {
        "contexts": len(contexts), "questions": len(questions),
        "contexts_with_two_table_spans": sum(
            sum(q["answer_type"] == "span" and q["answer_from"] == "table"
                for q in context["questions"]) >= 2 for context in contexts
        ),
        "answer_types": dict(sorted(types.items())),
        "answer_sources": dict(sorted(origins.items())),
        "question_fields": sorted({key for question in questions for key in question}),
        "extraction_labels": extraction,
        "extraction_fraction": extraction / len(questions) if questions else None,
        "table_span_screen": table_span,
        "table_span_fraction": table_span / len(questions) if questions else None,
    }


def audit_sources(root: Path) -> dict:
    """Verify pinned file hashes, then produce aggregate counts without examples."""
    manifest = json.loads((root / "source_manifest.json").read_text(encoding="utf-8"))
    if manifest["revision"] != REVISION:
        raise ValueError("Unexpected TAT-QA revision")
    expected = {item["path"]: item for item in manifest["files"]}
    splits = {}
    combined = []
    for split, name in FILES.items():
        data = (root / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected[name]["sha256"]:
            raise ValueError(f"Source hash mismatch: {name}")
        contexts = json.loads(data)
        splits[split] = count_questions(contexts)
        combined.extend(contexts)
    return {
        "source_revision": REVISION,
        "source_manifest": manifest,
        "scope_definition": "answer_type=span AND answer_from=table; manual screen pending",
        "scope_status": "label-based eligibility upper bound, not verified engine compatibility",
        "splits": splits, "all_labelled": count_questions(combined),
    }
