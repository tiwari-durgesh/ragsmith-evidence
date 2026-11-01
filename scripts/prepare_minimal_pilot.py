"""One fixed 36-case pilot; no inference, labels from dataset answers or tuning."""

import hashlib
import html
import json
import subprocess
from pathlib import Path

from ragsmith.core import ingest
from ragsmith.evaluation.records import PROVISIONAL
from ragsmith.evaluation.tatqa_adapter import load_pinned_split


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data/evaluation/pilot36"
FREEZE = "1b0df45c5e5fe443c5dd8be463ccf26dd9463de3"
SRC_TREE = "3261c6087757b9f3d9aed1166e264de45ac4f479"
NOTICE = "18 independent source facts and 36 derived cases; no statistical or performance claims are made from this pilot. Facts share nine contexts and are not asserted statistically independent."
# context, question IDs, value cells, year-header row, unit cell.
# Selected from a seeded source-only review before any predictions. All rows are
# table-only single-span labels; original answer annotations are never consulted.
SELECTION = [
    ("ed8b53ea-a594-4380-bafd-5fa8d9ee3c0a", ["ca4e8419-3be1-4660-9d50-edbbbc4c99b2", "3fd2e090-f51a-45cb-8f09-350cad639ad4"], [(5,5),(8,1)], 1, (2,0)),
    ("e3462c1a-1e69-4a4a-b9e1-b65898926335", ["9695cfc3-08a4-41b8-a282-383eb9ca9146", "ccac6448-f54d-4750-ba70-d524a0617749"], [(3,1),(4,1)], 1, (1,0)),
    ("a5283e18-51a8-4d2a-a6be-cba392b1f375", ["ef1ddca8-fe3a-486b-9453-16dfaf21ecdf", "346a81b6-0808-471c-acc7-921ccb540386"], [(3,3),(5,1)], 1, (2,2)),
    ("71649e80-12e2-4c60-8177-2825f9b4e375", ["38f715b1-61bc-4b28-8855-506887b393f2", "34c4efc8-5c91-440b-9888-b624ac268988"], [(4,1),(5,1)], 0, (1,2)),
    ("59ee6792-ddc9-4963-a2bd-cd15e6a13703", ["53c246db-09fa-4131-a673-5bc39f5be3dc", "23d3c339-21bb-42fa-adf6-00481d06dcbc"], [(3,1),(6,2)], 1, (1,0)),
    ("12550948-0d8e-40bb-b643-da2d8e2ab6f0", ["66d2343a-29b3-47ea-ade5-cf2d54682363", "85e595ae-e3b8-46cd-b133-2572adbd836d"], [(16,1),(16,2)], 1, (2,3)),
    ("0763f40c-4de1-417b-b3b0-7080ce64ba5b", ["90977b20-58d0-4a27-a9da-5cc4777156a5", "199cf79b-206b-426f-a605-49f014953ee2"], [(4,1),(5,2)], 1, (1,0)),
    ("0ff0244d-7a27-4650-94ab-9cd26268e656", ["a5492bae-1d14-4fe6-a31d-65867b1c392b", "9d5901f3-2b8f-47bb-b254-cf0352a897dc"], [(3,1),(3,2)], 1, (2,1)),
    ("b79cd05c-76c5-41ae-9bf9-3bf399507b46", ["1dfcd630-6db5-4bdf-bcc0-b0486befcc60", "be6e2106-d242-4782-aee2-4cff6f2f2efc"], [(2,1),(5,1)], 1, (0,0)),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def review_html(cards, packet, sheet):
    parts = ["<!doctype html><meta charset='utf-8'><title>Pilot review</title><style>body{font:16px system-ui;max-width:1100px;margin:30px auto}table{border-collapse:collapse;font-size:14px}td,th{border:1px solid #bbb;padding:7px}section{margin-bottom:45px}mark{background:#fff0a5}</style>",
             "<h1>Minimal pilot review</h1><p>" + html.escape(NOTICE) + "</p><p>All labels: provisional, single-annotator. Fill only the 18 null labels in labels-to-fill.json. No statistical or performance claims.</p>"]
    for index, card in enumerate(cards):
        parts.append("<section><h2>" + card["family"] + "</h2><p>Dataset table UID: " + card["context_id"] + "</p><table>")
        selected = {tuple(fact["value_cell"]) for fact in card["facts"]}
        for r, row in enumerate(card["table"]):
            parts.append("<tr>" + "".join("<td>" + ("<mark>" if (r,c) in selected else "") + html.escape(text) + ("</mark>" if (r,c) in selected else "") + "</td>" for c,text in enumerate(row)) + "</tr>")
        parts.append("</table><p>Source fact bindings:</p><ul>")
        for fact in card["facts"]:
            parts.append("<li>" + html.escape(fact["question"]) + " → " + html.escape(fact["metric"]) + " / " + str(fact["year"]) + " / " + html.escape(fact["value"]) + " / " + html.escape(fact["unit"]) + ". Value cell " + str(fact["value_cell"]) + " (zero-based).</li>")
        parts.append("</ul>")
        for case, label in zip(packet[index*4:index*4+4], sheet[index*4:index*4+4]):
            parts.append("<h3>" + case["case_id"] + " — " + label["label_basis"].replace("_", " ") + "</h3><p>" + html.escape(case["question"]) + "</p><pre>" + html.escape(json.dumps(case["evidence"], ensure_ascii=False, indent=2)) + "</pre>")
        parts.append("</section>")
    return "\n".join(parts)


def main():
    if subprocess.check_output(["git", "rev-parse", "HEAD:src"], cwd=ROOT, text=True).strip() != SRC_TREE:
        raise ValueError("Frozen src tree differs")
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all", "--", "src"], cwd=ROOT):
        raise ValueError("src must remain unchanged")
    contexts, provenance = load_pinned_split(ROOT / "data/evaluation/generated/tatqa-source", ROOT / "docs/tatqa-scope-audit.json")
    contexts = {row["table"]["uid"]: row for row in contexts}
    PILOT.mkdir(exist_ok=False)
    for name in ("public", "private", "sources", "databases"):
        (PILOT / name).mkdir()
    cards, packet, manifest, sheet = [], [], [], []
    for family_number, (uid, qids, coordinates, year_row, unit_cell) in enumerate(SELECTION, 1):
        context = contexts[uid]
        table = context["table"]["table"]
        questions = {q["uid"]: q for q in context["questions"]}
        facts = []
        for qid, (r,c) in zip(qids, coordinates):
            q = questions[qid]
            if (q["answer_type"], q["answer_from"], q["req_comparison"]) != ("span", "table", False):
                raise ValueError("Selected question outside direct extraction label gate")
            metric, year, value = table[r][0].strip(), int(table[year_row][c].strip()), table[r][c].strip()
            unit = table[unit_cell[0]][unit_cell[1]].strip()
            facts.append({"question_id": qid, "question": q["question"], "metric": metric,
                          "year": year, "value": value, "unit": unit,
                          "metric_cell": [r,0], "year_cell": [year_row,c], "value_cell": [r,c], "unit_cell": list(unit_cell)})
        cards.append({"family": f"F{family_number:02d}", "context_id": uid, "table": table,
                      "facts": facts, "source_url": provenance["url"] + f"#table={uid}"})
        for offset, condition in enumerate(("full", "partial", "missing", "conflict")):
            case_id = f"Q{(family_number-1)*4+offset+1:02d}"
            scoped = facts[:] if condition in {"full", "conflict"} else facts[:1] if condition == "partial" else []
            # A changed source value is synthetic, never claimed to be in TAT-QA.
            if condition == "conflict":
                scoped = scoped + [{**facts[0], "value": "999999999", "synthetic": True}]
            source = PILOT / "sources" / f"{case_id}.html"
            body = "".join("<table><tr><th>Metric</th><th>" + str(fact["year"]) + "</th></tr><tr><td>" +
                           html.escape(fact["metric"]) + "</td><td>" + html.escape(fact["value"]) + "</td></tr></table>" for fact in scoped)
            source.write_text("<!doctype html><meta charset='utf-8'>" + (body or "<p>No factual source rows supplied in this scope.</p>"), encoding="utf-8")
            db = PILOT / "databases" / f"{case_id}.sqlite"
            ingest(source, db)
            question = "Answer both questions using only the supplied evidence: " + " ".join(fact["question"] for fact in facts)
            requirements = [{"requirement_id": f"fact-{i}", "metric": fact["metric"], "year": fact["year"]} for i,fact in enumerate(facts,1)]
            visible = {"case_id": case_id, "question": question,
                       "requirements": [{"requirement_id": f"fact-{i}", "metric": fact["metric"], "year": fact["year"], "unit": fact["unit"]} for i,fact in enumerate(facts,1)],
                       "evidence": [{"metric": fact["metric"], "year": fact["year"], "value": fact["value"], "unit": fact["unit"]} for fact in scoped]}
            packet.append(visible)
            basis = "determined_by_construction" if condition in {"missing", "conflict"} else "needs_your_judgment"
            sheet.append({"case_id": case_id, "label_basis": basis,
                          "label": "abstain" if basis == "determined_by_construction" else None, "notes": ""})
            manifest.append({"case_id": case_id, "family": f"F{family_number:02d}", "condition": condition,
                             "label_basis": basis, "question": question, "requirements": requirements,
                             "database": f"databases/{case_id}.sqlite", "database_sha256": sha(db),
                             "source": f"sources/{case_id}.html", "source_sha256": sha(source)})
    dump(PILOT / "public/cases.json", {"notice": NOTICE, "cases": packet})
    dump(PILOT / "source-cards.json", {"notice": NOTICE, "cards": cards})
    dump(PILOT / "labels-to-fill.json", {"notice": NOTICE, "annotation_status": PROVISIONAL, "annotator_id": "Durgesh", "cases": sheet})
    dump(PILOT / "private/case-manifest.json", manifest)
    (PILOT / "review.html").write_text(review_html(cards, packet, sheet), encoding="utf-8")
    freeze = {"pipeline_commit": FREEZE, "src_tree": SRC_TREE, "notice": NOTICE,
              "annotation_status": PROVISIONAL, "source": provenance,
              "source_format": {"context": ["table", "paragraphs", "questions"], "table": ["uid", "table"],
                                "question_fields": sorted(questions[qids[0]])},
              "source_facts": 18, "derived_cases": 36, "manual_labels": 18, "construction_labels": 18,
              "license": "CC BY 4.0", "license_source": "https://github.com/NExTplusplus/TAT-QA/blob/870accc41953dcde885aabeb963d94aabdc0fbc3/README.md#license",
              "selection": "Source-only seeded candidate review; 9 explicit contexts; no model output consulted. Ambiguous repeated row names excluded. No original report identity or statistical independence established.",
              "scope": "Manual source-cell extraction to canonical HTML, native ingestion, per-case SQLite FTS BM25 top-k 10, then frozen three-baseline pipeline. Not full hybrid RAG.",
              "helper_scripts": {name: sha(ROOT / name) for name in ("scripts/prepare_minimal_pilot.py", "scripts/pilot36.py", "scripts/label_pilot36_llm.py")},
              "files": {name: sha(PILOT / name) for name in ("public/cases.json", "source-cards.json", "private/case-manifest.json", "review.html")}}
    dump(PILOT / "freeze.json", freeze)
    print(f"Prepared {PILOT}; no pilot inference run. {NOTICE}")


if __name__ == "__main__":
    main()
