"""Fetch optionally, then audit pinned official TAT-QA labels."""

import argparse
import json
from pathlib import Path

from ragsmith.evaluation.corpus_audit import audit_sources, fetch_sources


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path,
                        default=Path("data/evaluation/generated/tatqa-source"))
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.fetch:
        fetch_sources(args.source_dir)
    report = audit_sources(args.source_dir)
    output = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
