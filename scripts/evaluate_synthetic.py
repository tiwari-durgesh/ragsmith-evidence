"""Run the frozen-evidence synthetic harness; this is not a benchmark claim."""

import argparse
import json
from pathlib import Path

from ragsmith.evaluation.harness import run_suite
from ragsmith.evaluation.uncertainty import BootstrapConfig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path,
                        default=Path("data/evaluation/fixtures"))
    parser.add_argument("--lineage", type=Path,
                        help="Source manifest (default: DIRECTORY/lineage.json)")
    parser.add_argument("--rankings", type=Path,
                        help="Frozen per-requirement ranking JSONL for Track B")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--bootstrap-replicates", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=1729)
    parser.add_argument("--profile-memory", action="store_true")
    args = parser.parse_args()
    try:
        report = run_suite(args.directory / "inputs.jsonl",
                           args.directory / "evidence.jsonl",
                           args.directory / "gold.jsonl", args.lineage,
                           rankings_path=args.rankings, retrieval_k=args.k,
                           bootstrap=BootstrapConfig(args.bootstrap_replicates,
                                                     args.bootstrap_seed),
                           profile_memory=args.profile_memory)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
