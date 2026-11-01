"""Export native retrieval rankings or gold-free reviewer calibration packets."""

import argparse
import sqlite3
from pathlib import Path

from ragsmith.evaluation.preparation import (
    calibration_packets, export_rankings, write_new_bundle,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("rankings", "calibration"))
    parser.add_argument("--directory", type=Path, default=Path("data/evaluation/fixtures"))
    parser.add_argument("--output", type=Path, required=True, help="A new output directory")
    parser.add_argument("--database", type=Path)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--annotators", nargs=2, default=("reviewer-a", "reviewer-b"))
    parser.add_argument("--seed", type=int, default=1729)
    args = parser.parse_args()
    paths = (args.directory / "inputs.jsonl", args.directory / "evidence.jsonl",
             args.directory / "lineage.json")
    try:
        if args.mode == "rankings":
            if args.database is None:
                parser.error("rankings requires --database")
            result = export_rankings(args.database, *paths, limit=args.limit)
            rows = result.pop("rankings")
            files = {"rankings.jsonl": rows, "retrieval-audit.json": result}
        else:
            result = calibration_packets(*paths, annotators=tuple(args.annotators), seed=args.seed)
            files = {"reviewer-packet.json": result["packet"],
                     "COORDINATOR-ONLY.json": result["coordinator_only"]}
            for index, (author, template) in enumerate(result["templates"].items(), 1):
                files[f"reviewer-{index}-labels.jsonl"] = template
            files["requirement-worksheet.json"] = [
                {"item_id": item["item_id"], "requirements": [
                    {"requirement_id": req["requirement_id"], "status": "",
                     "acceptable_values": [], "evidence_ids": [], "notes": ""}
                    for req in item["requirements"]]} for item in result["packet"]["items"]]
        write_new_bundle(args.output, files)
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(files)} files to {args.output.resolve()}")


if __name__ == "__main__":
    main()
