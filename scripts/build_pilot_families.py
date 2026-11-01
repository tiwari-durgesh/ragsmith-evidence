"""Prepare report/family declarations or compile provisional controlled family drafts."""

import argparse
import hashlib
from pathlib import Path

from ragsmith.evaluation.cell_bindings import canonicalize_decisions
from ragsmith.evaluation.pilot_families import build_family_drafts, family_templates
from ragsmith.evaluation.preparation import write_new_bundle
from ragsmith.evaluation.records import read_jsonl
from ragsmith.evaluation.tatqa_adapter import load_pinned_split, prepare_screening


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("template", "compile"))
    parser.add_argument("--source-dir", type=Path, default=Path("data/evaluation/generated/tatqa-source"))
    parser.add_argument("--audit", type=Path, default=Path("docs/tatqa-scope-audit.json"))
    parser.add_argument("--bindings", type=Path)
    parser.add_argument("--identities", type=Path)
    parser.add_argument("--families", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        contexts, provenance = load_pinned_split(args.source_dir, args.audit)
        screening = prepare_screening(contexts, provenance)
        if args.mode == "template":
            templates = family_templates(screening)
            files = {"report-identities.jsonl": templates["identities"],
                     "family-decisions.jsonl": templates["families"], "source-provenance.json": provenance}
        else:
            if any(path is None for path in (args.bindings, args.identities, args.families)):
                parser.error("compile requires --bindings, --identities and --families")
            paths = {"bindings": args.bindings, "identities": args.identities, "families": args.families}
            initial = {name: path.read_bytes() for name, path in paths.items()}
            canonical = canonicalize_decisions(screening, read_jsonl(args.bindings))
            result = build_family_drafts(screening, canonical, read_jsonl(args.identities), read_jsonl(args.families))
            if any(path.read_bytes() != initial[name] for name, path in paths.items()):
                raise ValueError("Declaration files changed during compilation")
            result["summary"]["file_hashes"] = {name: hashlib.sha256(value).hexdigest() for name, value in initial.items()}
            result["summary"]["source"] = provenance
            files = {"inputs.jsonl": result["inputs"], "evidence.jsonl": result["evidence"],
                     "lineage.json": result["lineage"], "COORDINATOR-condition-log.jsonl": result["changes"],
                     "COORDINATOR-family-manifest.json": result["families"],
                     "COORDINATOR-selection-log.jsonl": result["selection_log"],
                     "COORDINATOR-report-groups.json": result["groups"], "summary.json": result["summary"]}
            files["COORDINATOR-declarations.json"] = result["coordinator_declarations"]
        write_new_bundle(args.output, files)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(files)} files to {args.output.resolve()}; no gold or model scoring performed.")


if __name__ == "__main__":
    main()
