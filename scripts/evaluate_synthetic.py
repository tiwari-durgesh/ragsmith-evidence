"""Run the frozen-evidence synthetic harness; this is not a benchmark claim."""

import argparse
import json
from pathlib import Path

from ragsmith.evaluation.harness import run_suite


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path,
                        default=Path("data/evaluation/fixtures"))
    args = parser.parse_args()
    try:
        report = run_suite(args.directory / "inputs.jsonl",
                           args.directory / "evidence.jsonl",
                           args.directory / "gold.jsonl")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
