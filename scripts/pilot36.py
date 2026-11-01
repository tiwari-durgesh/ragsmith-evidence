"""Only the pilot's required lock, one-shot results and disagreement operations."""

import argparse
import hashlib
import json
import os
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ragsmith.evaluation.harness import predict
from ragsmith.evaluation.records import PROVISIONAL, strict_json
from ragsmith.retrieval import RetrievalConfig, retrieve_question_evidence
from ragsmith.value_lookup import LookupQuestion


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data/evaluation/pilot36"
LABELS = {"full", "partial", "abstain", "not_adjudicable"}


def read(path):
    return strict_json(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def verify_freeze(pilot):
    freeze = read(pilot / "freeze.json")
    if subprocess.check_output(["git", "rev-parse", freeze["pipeline_commit"] + ":src"], cwd=ROOT, text=True).strip() != freeze["src_tree"]:
        raise ValueError("Freeze commit does not match declared src tree")
    if subprocess.check_output(["git", "rev-parse", "HEAD:src"], cwd=ROOT, text=True).strip() != freeze["src_tree"]:
        raise ValueError("Committed src differs from frozen pipeline")
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all", "--", "src"], cwd=ROOT):
        raise ValueError("src contains changes since pipeline freeze")
    for name, expected in freeze["files"].items():
        if sha(pilot / name) != expected:
            raise ValueError("Frozen pilot artifact changed: " + name)
    for name, expected in freeze.get("helper_scripts", {}).items():
        if sha(ROOT / name) != expected:
            raise ValueError("Pilot helper changed after preparation: " + name)
    cases = read(pilot / "private/case-manifest.json")
    if len(cases) != 36 or len({row["case_id"] for row in cases}) != 36:
        raise ValueError("Expected exactly 36 unique derived cases")
    for case in cases:
        for kind in ("source", "database"):
            if sha(pilot / case[kind]) != case[kind + "_sha256"]:
                raise ValueError("Frozen case source/database changed")
    return freeze, cases


def validate_sheet(sheet, cases):
    if sheet["annotation_status"] != PROVISIONAL or not sheet.get("annotator_id", "").strip():
        raise ValueError("Need a named provisional, single-annotator sheet")
    rows = sheet["cases"]
    by_id = {row["case_id"]: row for row in rows}
    if len(rows) != len(by_id) or set(by_id) != {case["case_id"] for case in cases}:
        raise ValueError("Label sheet must contain exactly the 36 case IDs")
    for case in cases:
        row = by_id[case["case_id"]]
        if set(row) != {"case_id", "label_basis", "label", "notes"}:
            raise ValueError("Unexpected label fields")
        if row["label_basis"] != case["label_basis"] or row["label"] not in LABELS:
            raise ValueError("Missing or invalid label for " + case["case_id"])
        if case["label_basis"] == "determined_by_construction" and row["label"] != "abstain":
            raise ValueError("Do not overwrite construction labels; note a construction concern instead")
        if not isinstance(row["notes"], str):
            raise ValueError("Notes must be text")
    return by_id


def lock(pilot, source):
    freeze, cases = verify_freeze(pilot)
    sheet = read(source)
    validate_sheet(sheet, cases)
    target = pilot / "private/human-locked.json"
    receipt = pilot / "public/labels.lock.json"
    if target.exists() or receipt.exists():
        raise ValueError("Human labels already locked; no overwrite")
    create(target, sheet)
    os.chmod(target, stat.S_IREAD)
    create(receipt, {"locked_at_utc": datetime.now(timezone.utc).isoformat(),
                     "human_labels_sha256": sha(target), "public_packet_sha256": sha(pilot / "public/cases.json"),
                     "freeze_sha256": sha(pilot / "freeze.json"), "pipeline_commit": freeze["pipeline_commit"],
                     "src_tree": freeze["src_tree"], "annotation_status": PROVISIONAL})
    print("Human labels saved and hash-locked. The LLM stage reads only the public packet and this hash receipt.")


def locked_sheet(pilot, cases):
    receipt = read(pilot / "public/labels.lock.json")
    target = pilot / "private/human-locked.json"
    if sha(target) != receipt["human_labels_sha256"] or sha(pilot / "freeze.json") != receipt["freeze_sha256"]:
        raise ValueError("Locked labels or freeze changed")
    return validate_sheet(read(target), cases)


def run_once(pilot):
    freeze, cases = verify_freeze(pilot)
    labels = locked_sheet(pilot, cases)
    output = pilot / "results"
    output.mkdir(exist_ok=False)  # A failed/complete run cannot be silently repeated.
    create(output / "run-started.json", {"pipeline_commit": freeze["pipeline_commit"], "src_tree": freeze["src_tree"]})
    predictions, retrieval = [], []
    # Do not inspect labels inside inference. Baselines are imported from frozen src.
    for case in cases:
        request = LookupQuestion.from_payload({"question_id": case["case_id"], "question": case["question"], "requirements": case["requirements"]})
        result = retrieve_question_evidence(pilot / case["database"], request, RetrievalConfig(10))
        retrieval.append({"case_id": case["case_id"], **result.audit})
        predictions.extend(predict(request, list(result.evidence)))
    verify_freeze(pilot)
    locked_sheet(pilot, cases)
    create(output / "predictions.json", predictions)
    create(output / "retrieval.json", retrieval)
    failures, summaries = [], []
    for variant in ("extraction_only", "binary_sufficiency", "graded_sufficiency"):
        rows = [row for row in predictions if row["variant"] == variant]
        eligible = [row for row in rows if labels[row["question_id"]]["label"] != "not_adjudicable"]
        correct = sum(row["answerability"] == labels[row["question_id"]]["label"] for row in eligible)
        partial = [row for row in eligible if labels[row["question_id"]]["label"] == "partial"]
        returned = sum(bool(row["answers"]) for row in partial)
        summaries.append({"baseline": variant, "correct_case_labels": correct, "scored_cases": len(eligible),
                          "excluded_not_adjudicable": 36-len(eligible),
                          "partial_cases_with_values": returned, "human_partial_cases": len(partial),
                          "emitted_claims": sum(len(row["answers"]) for row in rows)})
        for row in eligible:
            if row["answerability"] != labels[row["question_id"]]["label"]:
                failures.append({"case_id": row["question_id"], "baseline": variant,
                                 "expected": labels[row["question_id"]]["label"], "predicted": row["answerability"],
                                 "label_basis": labels[row["question_id"]]["label_basis"],
                                 "answers": row["answers"], "human_notes": labels[row["question_id"]]["notes"]})
    create(output / "failure-cases.json", failures)
    create(output / "summary.json", {"notice": freeze["notice"], "annotation_status": PROVISIONAL,
                                     "pipeline_commit": freeze["pipeline_commit"], "summaries": summaries,
                                     "failure_count": len(failures), "dataset_reference_scores": "omitted"})
    table = ["# Minimal pilot results", "", freeze["notice"], "", "Labels: **provisional, single-annotator**. No dataset-derived reference scores. No tuning.", "",
             f"Frozen pipeline/baselines: `{freeze['pipeline_commit']}`.", "",
             "| Baseline | Correct case labels / scored | Partial cases returning values / partial | Emitted claims |",
             "| --- | ---: | ---: | ---: |"]
    table += [f"| {row['baseline']} | {row['correct_case_labels']} / {row['scored_cases']} | {row['partial_cases_with_values']} / {row['human_partial_cases']} | {row['emitted_claims']} |" for row in summaries]
    table += ["", f"{len(failures)} baseline/case label mismatches; see failure-cases.json. Not-adjudicable cases are excluded explicitly.", "",
              "Partial-case return counts are not factual correctness or citation precision. No timing, statistical intervals, generalization, superiority or novelty claims.", "",
              "Manual canonicalization and supplied decomposition precede native HTML ingestion and per-case SQLite FTS retrieval. These controlled scopes are not a full enterprise corpus or the planned hybrid retriever."]
    (output / "results.md").write_text("\n".join(table)+"\n", encoding="utf-8")
    print("One pilot pipeline run completed; source unchanged. See results/results.md and failure-cases.json.")


def compare(pilot, llm_path):
    freeze, cases = verify_freeze(pilot)
    human = locked_sheet(pilot, cases)
    receipt = read(pilot / "public/labels.lock.json")
    llm = read(llm_path)
    if llm["lock_receipt_sha256"] != sha(pilot / "public/labels.lock.json") or llm["packet_sha256"] != receipt["public_packet_sha256"]:
        raise ValueError("LLM output does not belong to locked pilot")
    rows = llm["cases"]
    by_id = {row["case_id"]: row for row in rows}
    if len(rows) != 36 or set(by_id) != set(human) or any(row["label"] not in LABELS for row in rows):
        raise ValueError("Invalid LLM case labels")
    disagreements = [{"case_id": qid, "human_or_construction_label": human[qid]["label"],
                       "label_basis": human[qid]["label_basis"], "llm_label": by_id[qid]["label"],
                       "llm_reason": by_id[qid].get("reason", ""), "review_decision": None, "notes": ""}
                      for qid in human if human[qid]["label"] != by_id[qid]["label"]]
    create(pilot / "disagreements.json", {"notice": freeze["notice"], "annotation_status": PROVISIONAL,
                    "interpretation": "Human/construction versus LLM comparison, NOT human inter-annotator agreement; no kappa.",
                    "model": llm["model"], "disagreements": disagreements})
    print(f"{len(disagreements)} disagreements saved; original human labels remain unchanged.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("lock", "run", "compare"))
    parser.add_argument("--pilot", type=Path, default=PILOT)
    parser.add_argument("--labels", type=Path)
    parser.add_argument("--llm", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "lock":
            lock(args.pilot, args.labels or args.pilot / "labels-to-fill.json")
        elif args.command == "run":
            run_once(args.pilot)
        else:
            if args.llm is None:
                parser.error("compare needs --llm")
            compare(args.pilot, args.llm)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
