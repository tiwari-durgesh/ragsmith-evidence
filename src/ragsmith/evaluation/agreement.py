"""Unweighted Cohen's kappa for aligned, independent categorical annotations."""

import json
from collections import Counter
from pathlib import Path


LABELS = ("full", "partial", "abstain", "not_adjudicable")


def load_annotations(path: Path) -> tuple[str, dict[str, str]]:
    """Read JSONL labels; reject duplicates, unknown labels and mixed annotators."""
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    annotations = {}
    authors = set()
    for row in rows:
        if set(row) != {"item_id", "annotator_id", "label"}:
            raise ValueError("annotation needs item_id, annotator_id, label only")
        if any(not isinstance(row[key], str) or not row[key].strip() for key in row):
            raise ValueError("annotation fields must be nonempty strings")
        if row["item_id"] in annotations:
            raise ValueError("Duplicate annotation item ID")
        if row["label"] not in LABELS:
            raise ValueError("Unknown annotation label")
        authors.add(row["annotator_id"])
        annotations[row["item_id"]] = row["label"]
    if len(authors) != 1:
        raise ValueError("Each annotation file must contain one nonempty annotator")
    return authors.pop(), annotations


def cohen_kappa(first: dict[str, str], second: dict[str, str]) -> dict:
    """Pair by ID, never row order; no silent intersection or category weighting.

    Kappa = (observed agreement - expected agreement) / (1 - expected).
    Empty pairs or degenerate expected agreement return null with a reason.
    """
    if set(first) != set(second):
        raise ValueError("Annotators must label exactly the same item IDs")
    if any(label not in LABELS for label in [*first.values(), *second.values()]):
        raise ValueError("Unknown annotation label")
    n = len(first)
    confusion = {a: {b: 0 for b in LABELS} for a in LABELS}
    for item_id in first:
        confusion[first[item_id]][second[item_id]] += 1
    left, right = Counter(first.values()), Counter(second.values())
    observed = sum(first[key] == second[key] for key in first) / n if n else None
    expected = sum(left[label] * right[label] for label in LABELS) / n**2 if n else None
    undefined = "no paired annotations" if not n else (
        "expected agreement is one" if expected == 1.0 else None
    )
    return {
        "paired_items": n, "labels": list(LABELS), "confusion": confusion,
        "observed_agreement": observed, "expected_agreement": expected,
        "kappa": (observed - expected) / (1 - expected) if undefined is None else None,
        "undefined_reason": undefined,
        "disagreement_ids": sorted(key for key in first if first[key] != second[key]),
    }


def compare_annotation_files(first: Path, second: Path) -> dict:
    """Compare independent files before adjudication, including ambiguity labels."""
    left_id, left = load_annotations(first)
    right_id, right = load_annotations(second)
    if left_id == right_id:
        raise ValueError("Two different annotator IDs are required")
    result = cohen_kappa(left, right)
    result["annotator_ids"] = [left_id, right_id]
    result["stage"] = "pre-adjudication"
    return result
