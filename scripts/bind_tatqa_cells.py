"""Create provisional screening templates or compile manually accepted cell bindings."""

import argparse
import hashlib
from pathlib import Path

from ragsmith.evaluation.cell_bindings import canonicalize_decisions, decision_templates
from ragsmith.evaluation.preparation import write_new_bundle
from ragsmith.evaluation.records import read_jsonl
from ragsmith.evaluation.tatqa_adapter import load_pinned_split, prepare_screening


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("template", "compile"))
    parser.add_argument("--source-dir", type=Path, default=Path("data/evaluation/generated/tatqa-source"))
    parser.add_argument("--audit", type=Path, default=Path("docs/tatqa-scope-audit.json"))
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    args = parser.parse_args()
    try:
        contexts, provenance = load_pinned_split(args.source_dir, args.audit)
        screening = prepare_screening(contexts, provenance)
        if args.mode == "template":
            files = {"manual-decisions.jsonl": decision_templates(screening),
                     "source-provenance.json": provenance}
        else:
            if args.decisions is None:
                parser.error("compile requires --decisions")
            initial = args.decisions.read_bytes()
            result = canonicalize_decisions(screening, read_jsonl(args.decisions))
            if args.decisions.read_bytes() != initial:
                raise ValueError("Decision file changed during compilation")
            result["summary"]["decision_file_sha256"] = hashlib.sha256(initial).hexdigest()
            result["summary"]["source"] = provenance
            files = {"inputs.jsonl": result["inputs"], "evidence.jsonl": result["evidence"],
                     "lineage.json": result["lineage"], "transformations.jsonl": result["transformations"],
                     "COORDINATOR-decision-log.jsonl": result["decision_log"], "summary.json": result["summary"]}
        write_new_bundle(args.output, files)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(files)} files to {args.output.resolve()}; no gold or final pilot created.")


if __name__ == "__main__":
    main()
