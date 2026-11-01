"""Run fresh/warmed process diagnostics without annotations or gold scoring."""

import argparse
import subprocess
from pathlib import Path

from ragsmith.evaluation.preparation import write_new_bundle
from ragsmith.evaluation.resource_trials import TrialConfig, run_resource_trials


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path("data/evaluation/fixtures"))
    parser.add_argument("--database", type=Path)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    args = parser.parse_args()
    try:
        report = run_resource_trials(args.directory, database=args.database,
                    config=TrialConfig(args.repeats, args.warmups, args.seed, args.top_k, args.timeout_seconds))
        write_new_bundle(args.output, {"resource-report.json": report})
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    print(f"Wrote diagnostics to {args.output.resolve()}; no research benchmark claim.")


if __name__ == "__main__":
    main()
