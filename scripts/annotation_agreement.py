"""Measure pre-adjudication agreement between two independent JSONL label files."""

import argparse
import json
from pathlib import Path

from ragsmith.evaluation.agreement import compare_annotation_files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotator_a", type=Path)
    parser.add_argument("annotator_b", type=Path)
    args = parser.parse_args()
    try:
        report = compare_annotation_files(args.annotator_a, args.annotator_b)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
