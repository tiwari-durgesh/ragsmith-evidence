"""Prepare a pinned training-source adapter and provisional screening queue offline."""

import argparse
from pathlib import Path

from ragsmith.evaluation.preparation import write_new_bundle
from ragsmith.evaluation.tatqa_adapter import load_pinned_split, prepare_screening


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path("data/evaluation/generated/tatqa-source"))
    parser.add_argument("--audit", type=Path, default=Path("docs/tatqa-scope-audit.json"))
    parser.add_argument("--output", type=Path, required=True, help="New local directory; contains upstream content")
    parser.add_argument("--seed", type=int, default=1729)
    args = parser.parse_args()
    try:
        contexts, provenance = load_pinned_split(args.source_dir, args.audit)
        result = prepare_screening(contexts, provenance, seed=args.seed)
        write_new_bundle(args.output, {
            "sources.jsonl": result["sources"], "screening-ledger.jsonl": result["screening_ledger"],
            "context-screening-ledger.jsonl": result["context_screening_ledger"],
            "COORDINATOR-annotation-aids.jsonl": result["coordinator_annotation_aids"],
            "sampling-manifest.json": result["sampling_manifest"], "summary.json": result["summary"]})
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(f"Wrote screening materials to {args.output.resolve()}")
    print(f"Label gate: {result['summary']['label_gate_pass']} questions; "
          f"{result['summary']['candidate_contexts_with_two_spans']} candidate contexts. "
          "Semantic eligibility and report identity remain pending.")


if __name__ == "__main__":
    main()
