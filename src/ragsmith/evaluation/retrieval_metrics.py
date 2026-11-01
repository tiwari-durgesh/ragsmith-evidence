"""Ranking evaluation against full-scope gold; retrieval misses remain misses."""

import math
from dataclasses import dataclass

from ragsmith.evidence.models import Evidence
from ragsmith.evaluation.records import GoldRecord, require_keys, require_text, text_tuple
from ragsmith.value_lookup import LookupQuestion


def validate_cutoff(k: int) -> None:
    if type(k) is not int or not 1 <= k <= 100:
        raise ValueError("retrieval k must be an integer from 1 to 100")


@dataclass(frozen=True)
class RequirementRanking:
    requirement_id: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        require_text(self.requirement_id, "requirement_id")
        if not isinstance(self.evidence_ids, tuple):
            raise ValueError("Ranked evidence IDs must be an immutable tuple")
        text_tuple(list(self.evidence_ids), "ranked evidence IDs")


@dataclass(frozen=True)
class RankingRecord:
    question_id: str
    rankings: tuple[RequirementRanking, ...]

    def __post_init__(self) -> None:
        require_text(self.question_id, "question_id")
        if not isinstance(self.rankings, tuple) or any(
            not isinstance(item, RequirementRanking) for item in self.rankings
        ):
            raise ValueError("Rankings must be typed immutable records")
        ids = [item.requirement_id for item in self.rankings]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate ranked requirement IDs")

    @classmethod
    def from_payload(cls, payload: object) -> "RankingRecord":
        row = require_keys(payload, {"question_id", "rankings"}, "ranking record")
        if not isinstance(row["rankings"], list):
            raise ValueError("rankings must be a list")
        rankings = []
        for item in row["rankings"]:
            item = require_keys(item, {"requirement_id", "evidence_ids"}, "requirement ranking")
            rankings.append(RequirementRanking(
                item["requirement_id"], text_tuple(item["evidence_ids"], "ranked evidence IDs")
            ))
        return cls(row["question_id"], tuple(rankings))

    def select(
        self, request: LookupQuestion, universe: list[Evidence], k: int
    ) -> list[Evidence]:
        """Validate ranking IDs/scope, then form a stable deduplicated top-k union."""
        validate_cutoff(k)
        if self.question_id != request.question_id or {
            row.requirement_id for row in self.rankings
        } != {row.requirement_id for row in request.requirements}:
            raise ValueError("Ranking question/requirement IDs must match the input")
        sources = {item.evidence_id: item for item in universe}
        if len(sources) != len(universe):
            raise ValueError("Duplicate evidence IDs in ranking universe")
        requirements = {item.requirement_id: item for item in request.requirements}
        ranked = {item.requirement_id: item for item in self.rankings}
        for row in self.rankings:
            allowed = requirements[row.requirement_id].document_ids
            for eid in row.evidence_ids:
                if eid not in sources:
                    raise ValueError("Ranked evidence ID is absent from the source universe")
                if allowed and sources[eid].document_id not in allowed:
                    raise ValueError("Ranked evidence lies outside requirement document scope")
        selected = {}
        for requirement in request.requirements:
            for eid in ranked[requirement.requirement_id].evidence_ids[:k]:
                selected.setdefault(eid, sources[eid])
        return list(selected.values())


def score_retrieval(
    ranking: RankingRecord, gold: GoldRecord, request: LookupQuestion,
    universe: list[Evidence], k: int,
) -> list[dict]:
    """Binary relevance is decisive support/conflict evidence, not topical overlap."""
    ranking.select(request, universe, k)
    gold.validate_request(request)
    facts = {fact.requirement_id: fact for fact in gold.requirements}
    known = {item.evidence_id for item in universe}
    scored = []
    for row in ranking.rankings:
        fact = facts[row.requirement_id]
        relevant = set(fact.evidence_ids) if fact.status in {"supported", "conflicted"} else set()
        if not relevant <= known:
            raise ValueError("Gold evidence ID is absent from the full source universe")
        retained = row.evidence_ids[:k]
        ranks = [rank for rank, eid in enumerate(retained, 1) if eid in relevant]
        reason = "not_adjudicable" if fact.status == "not_adjudicable" else (
            "no_gold_decisive_evidence" if not relevant else None
        )
        dcg = sum(1 / math.log2(rank + 1) for rank in ranks)
        ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(k, len(relevant)) + 1))
        scored.append({
            "question_id": request.question_id, "requirement_id": row.requirement_id,
            "gold_status": fact.status, "k": k,
            "gold_evidence_count": len(relevant), "retrieved_relevant_count": len(ranks),
            "ranked_count": len(row.evidence_ids), "retained_count": len(retained),
            "cutoff_truncated": len(row.evidence_ids) > k,
            "recall": len(ranks) / len(relevant) if reason is None else None,
            "reciprocal_rank": (1 / ranks[0] if ranks else 0.0) if reason is None else None,
            "ndcg": dcg / ideal if reason is None else None,
            "excluded_reason": reason,
        })
    return scored


def summarize_retrieval(rows: list[dict]) -> dict:
    eligible = [row for row in rows if row["excluded_reason"] is None]

    def average(records, key):
        return sum(row[key] for row in records) / len(records) if records else None

    return {
        "aggregation": "macro over eligible requirements; k is per requirement",
        "requirements": len(rows), "eligible_requirements": len(eligible),
        "excluded_no_gold": sum(row["excluded_reason"] == "no_gold_decisive_evidence"
                                for row in rows),
        "excluded_not_adjudicable": sum(row["excluded_reason"] == "not_adjudicable"
                                        for row in rows),
        "recall": average(eligible, "recall"),
        "mrr": average(eligible, "reciprocal_rank"),
        "ndcg": average(eligible, "ndcg"),
        "support_recall": average([r for r in eligible if r["gold_status"] == "supported"], "recall"),
        "conflict_recall": average([r for r in eligible if r["gold_status"] == "conflicted"], "recall"),
    }
