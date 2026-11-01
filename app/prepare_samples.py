"""Export six existing pilot-only demo inputs; never read private human labels.

The old controlled conflict already contains an artificial alternative value.
It is copied unchanged, explicitly disclosed, and is not a genuine-conflict example.
"""

import hashlib
import json
from pathlib import Path

from app.models import AskRequest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/evaluation/pilot36/public/cases.json"
OUTPUT = ROOT / "data/evaluation/generated/demo-api/samples.json"
# Fixed before any new pipeline/demo output. These are pilot IDs, not evaluation IDs.
CHOICES = (("Q01", "full"), ("Q05", "full"), ("Q02", "partial"),
           ("Q06", "partial"), ("Q04", "controlled_conflict"), ("Q03", "abstain"))


def prepare(source: Path = SOURCE, output: Path = OUTPUT):
    data = source.read_bytes()
    packet = json.loads(data)
    by_id = {x["case_id"]: x for x in packet["cases"]}
    cases = []
    for case_id, category in CHOICES:
        case = by_id[case_id]
        years = sorted({r["year"] for r in case["requirements"]} | {e["year"] for e in case["evidence"]})
        table = [["Metric"] + [str(y) for y in years]]
        for e in case["evidence"]:
            table.append([e["metric"]] + [e["value"] if y == e["year"] else "" for y in years])
        payload = {"question": case["question"], "requested_facts": [
            {k: r[k] for k in ("requirement_id", "metric", "year")} for r in case["requirements"]],
            "table": table, "source_reference": "Existing controlled pilot table " + case_id,
            "source_unit": case["requirements"][0]["unit"], "answerer": "lookup"}
        AskRequest.model_validate(payload)
        cases.append({"sample_id": case_id, "demo_category": category,
                      "source": "existing pilot public source packet; no human labels read",
                      "construction_notice": (
                          "Existing pilot artificial conflicting value copied unchanged; not a genuine report conflict."
                          if category == "controlled_conflict" else
                          "Existing controlled pilot scope; not a new study case or corpus-wide absence claim."),
                      "request": payload})
    result = {"notice": packet["notice"], "usage": "demo only; no research scores or new labels",
              "source_packet_sha256": hashlib.sha256(data).hexdigest(), "cases": cases}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return result


if __name__ == "__main__":
    if OUTPUT.exists():
        print("Local samples already exist; no overwrite. Use GET /samples.")
    else:
        prepare()
        print("Prepared six local pilot-only samples; no human labels read, no inference.")
