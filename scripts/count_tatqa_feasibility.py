"""Aggregate feasibility leads only: no evaluation selection, labels or scoring."""

import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from itertools import combinations
from pathlib import Path

from ragsmith.evaluation.tatqa_adapter import load_pinned_split


ROOT = Path(__file__).resolve().parents[1]


def norm(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def number(text):
    text = text.strip().replace(",", "").replace("$", "").replace("€", "").replace("£", "").replace("%", "")
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    try:
        result = Decimal(text.strip())
        return str(result.normalize()) if result.is_finite() else None
    except InvalidOperation:
        return None


def features(table):
    rows = {" | ".join(norm(cell) for cell in row) for row in table}
    tokens = re.findall(r"\w+", " ".join(" ".join(row) for row in table).casefold())
    shingles = {tuple(tokens[i:i+5]) for i in range(max(0,len(tokens)-4))}
    return rows, shingles, "\n".join(" | ".join(norm(cell) for cell in row) for row in table)


def main():
    contexts, source = load_pinned_split(ROOT / "data/evaluation/generated/tatqa-source", ROOT / "docs/tatqa-scope-audit.json")
    cards = json.loads((ROOT / "data/evaluation/pilot36/source-cards.json").read_text(encoding="utf-8"))["cards"]
    pilot_ids = {card["context_id"] for card in cards}
    pilot_features = [features(card["table"]) for card in cards]
    excluded = defaultdict(int)
    partial_leads, eligible_questions, remaining = 0, 0, 0
    conflict_contexts = []
    skeletons = defaultdict(list)
    for context in contexts:
        uid, table = context["table"]["uid"], context["table"]["table"]
        if uid in pilot_ids:
            excluded["pilot_context_uid"] += 1
            continue
        rows, shingles, exact = features(table)
        duplicate = False
        for old_rows, old_shingles, old_exact in pilot_features:
            jaccard = len(shingles & old_shingles)/len(shingles | old_shingles) if shingles | old_shingles else 0
            overlap = len(rows & old_rows)/min(len(rows),len(old_rows)) if rows and old_rows else 0
            if exact == old_exact or jaccard >= .8 or overlap >= .5:
                duplicate = True
                break
        if duplicate:
            excluded["pilot_table_duplicate_or_similarity_flag"] += 1
            continue
        remaining += 1
        eligible = [q for q in context["questions"] if q["answer_type"]=="span" and q["answer_from"]=="table" and not q["req_comparison"]]
        eligible_questions += len(eligible)
        year_cells = [(r,c,cell.strip()) for r,row in enumerate(table[:3]) for c,cell in enumerate(row)
                      if re.fullmatch(r"(?:19|20)\d{2}",cell.strip())]
        has_units = any(re.search(r"million|thousand|percent|\$m\b|dollars|usd|eur",cell,re.I)
                        for row in table[:3] for cell in row)
        years = {year for _,_,year in year_cells}
        if has_units and any(len(re.findall(r"\b(?:19|20)\d{2}\b",q["question"]))==1 and
                             re.findall(r"\b(?:19|20)\d{2}\b",q["question"])[0] in years for q in eligible):
            partial_leads += 1
        # Repeated row names/year values are only discrepancy leads: section,
        # entity and report priority are not established by this scan.
        values = defaultdict(list)
        for hr,col,year in year_cells:
            for r,row in enumerate(table[hr+1:],hr+1):
                if not row or len(row)<=col or col==0 or not row[0].strip():
                    continue
                value = number(row[col])
                if value is not None:
                    values[(norm(row[0]),year)].append((r,col,value))
        discrepancies = [{"metric":key[0],"year":key[1],"cells":items} for key,items in values.items()
                         if len({item[2] for item in items})>1]
        if discrepancies:
            conflict_contexts.append({"context_id":uid,"leads":discrepancies})
        paragraph_text = "\n".join(norm(row["text"]) for row in context["paragraphs"])
        skeleton = [["#NUM" if r>=3 and number(cell) is not None else norm(cell) for cell in row] for r,row in enumerate(table)]
        skeletons[(json.dumps(skeleton),paragraph_text)].append((uid,exact))
    cross_groups = [items for (skeleton,paragraphs),items in skeletons.items()
                    if paragraphs and len(items)>1 and len({exact for _,exact in items})>1]
    report = {"status":"feasibility_count_only_no_evaluation_selection",
              "source":source,"pilot_contexts":len(pilot_ids),"source_contexts":len(contexts),
              "excluded_contexts":dict(excluded),"remaining_contexts_unverified_report_identity":remaining,
              "remaining_noncomparison_table_span_questions":eligible_questions,
              "context_level_partial_leads":partial_leads,
              "within_context_discrepancy_lead_contexts":len(conflict_contexts),
              "within_context_discrepancy_keys":sum(len(row["leads"]) for row in conflict_contexts),
              "matching_layout_and_paragraphs_discrepant_table_groups":len(cross_groups),
              "verified_report_disjoint_partial_questions":0,
              "verified_report_disjoint_genuine_conflict_questions":0,
              "actual_report_disjoint_yield":"unknown; raw split has no report/entity/source URL fields and pilot report identities unresolved",
              "interpretation":"Partial leads are contexts with a labeled extraction fact and explicit year/unit, not verified absent facts. Discrepancies are not verified same-scope conflicts. No question authored, sampled, selected or scored."}
    output = ROOT / "data/evaluation/generated/feasibility-only"
    output.mkdir(exist_ok=False)
    (output/"counts.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    (output/"unverified-discrepancy-leads.json").write_text(json.dumps(conflict_contexts,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
    print("Unverified discrepancies (first 8 contexts; not evaluation selections):")
    print(json.dumps(conflict_contexts[:8],indent=2))


if __name__ == "__main__":
    main()
