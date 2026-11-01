"""Fixed Option C source screens and exact first-feasible allocation.

No file loader or command line. Never run against a real pool without separate
authorization. No system output is accepted in source/candidate records.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from itertools import combinations
import re

from scripts.tatqa_excerpt_ingestion import canonical, digest, matching_pilot_names, normalize, name_tokens, table_hash

SEED = 1729
DEVELOPMENT = {"full": 8, "partial": 6, "missing": 3, "conflict": 3}
EVALUATION = {"full": 12, "partial": 9, "missing": 5, "conflict": 4}
STREAMS = {"source-screen", "development", "stage1", "reviewer", "reviewer-packet"}


def priority(stream: str, stable_id: str):
    if stream not in STREAMS:
        raise ValueError("Unknown registered stream")
    return (bytes.fromhex(digest([SEED, stream, stable_id])), stable_id)


def tokens(value):
    return re.findall(r"[^\W_]+|_|[^\w\s]", value, re.UNICODE)


def shingles(sequence, n):
    return {tuple(sequence[i:i+n]) for i in range(len(sequence)-n+1)}


def _signature(context):
    table = [[normalize(c) for c in row] for row in context["table"]]
    source = {"table": table, "paragraphs": [normalize(p) for p in context.get("paragraphs", [])]}
    return (digest(table), digest(source), shingles(tokens(canonical(table).decode()),5),
            shingles(tokens(canonical(source).decode()),5), {digest(row) for row in table if any(row)})


def source_groups(contexts: list[dict], pilot_contexts: list[dict], *, family_ids: set[str],
                  excluded_context_ids: set[str]) -> tuple[list[dict], list[dict]]:
    """Precomputed equivalent of fixed pairwise screens, transitive quarantine.

    The eight family IDs and pilot contexts must be explicitly supplied. Source
    fields only. Unknown identity alone is accepted; it never proves disjointness.
    """
    if len(family_ids) != 8:
        raise ValueError("All eight pilot family IDs required")
    allowed = {"context_id","table","paragraphs","verified_company_names","report_family","near_duplicate_links"}
    if any(set(c)-allowed for c in contexts+pilot_contexts):
        raise ValueError("Source records contain non-source fields")
    by_id = {c["context_id"]:c for c in contexts}
    if len(by_id)!=len(contexts):
        raise ValueError("Duplicate context IDs")
    # A pilot is also part of the full source universe when its UID is present.
    for p in pilot_contexts:
        if p["context_id"] in by_id and digest(by_id[p["context_id"]]["table"])!=digest(p["table"]):
            raise ValueError("Pilot UID source mismatch")
        by_id.setdefault(p["context_id"],p)
    ids=sorted(by_id)
    parent={u:u for u in ids}
    edges=defaultdict(list)
    def find(u):
        while parent[u]!=u:
            parent[u]=parent[parent[u]]
            u=parent[u]
        return u
    def union(a,b,rule="source_flagged_link",score=None):
        if b not in parent:
            raise ValueError("Unknown source-only duplicate link")
        left,right=a,b
        a,b=find(a),find(b)
        if a!=b:
            parent[max(a,b)]=min(a,b)
            edges[left].append({"other_context":right,"rule":rule,"score":score})
            edges[right].append({"other_context":left,"rule":rule,"score":score})
    sig={u:_signature(by_id[u]) for u in ids}
    def jac(a,b):
        if not a or not b or min(len(a),len(b))/max(len(a),len(b))<.8:return False
        overlap=len(a&b)
        return overlap/(len(a)+len(b)-overlap)>=.8
    for i,a in enumerate(ids):
        sa=sig[a]
        for b in ids[i+1:]:
            if find(a)==find(b):continue  # Connectivity already certified; no rule is weakened.
            sb=sig[b]
            if sa[0]==sb[0]:union(a,b,"normalized_table_equality",1.0)
            elif sa[1]==sb[1]:union(a,b,"normalized_context_equality",1.0)
            elif sa[4] and sb[4] and len(sa[4]&sb[4])/min(len(sa[4]),len(sb[4]))>=.5:
                union(a,b,"row_overlap",len(sa[4]&sb[4])/min(len(sa[4]),len(sb[4])))
            elif jac(sa[2],sb[2]):union(a,b,"table_5shingle_jaccard",len(sa[2]&sb[2])/len(sa[2]|sb[2]))
            elif jac(sa[3],sb[3]):union(a,b,"context_5shingle_jaccard",len(sa[3]&sb[3])/len(sa[3]|sb[3]))
    names={}
    pilot_ids={p["context_id"] for p in pilot_contexts}
    pilot_hashes={table_hash(p["table"]) for p in pilot_contexts}
    direct={}
    for uid in ids:
        c=by_id[uid];reasons=[]
        if uid in pilot_ids:reasons.append("pilot_context_uid")
        if uid in excluded_context_ids:reasons.append("retained_exclusion_ledger")
        if c.get("report_family") in family_ids:reasons.append("pilot_report_family")
        if table_hash(c["table"]) in pilot_hashes:reasons.append("pilot_table_hash")
        matches=matching_pilot_names(c["table"],c.get("paragraphs",[])+c.get("verified_company_names",[]))
        if matches:reasons.append("pilot_company_name:"+"|".join(matches))
        for name in c.get("verified_company_names",[]):
            key=tuple(name_tokens(name))
            if not key or key in {("company",),("the","company")}:
                raise ValueError("Unverified/generic issuer name cannot establish a source edge")
            if key in names:union(uid,names[key],"source_verified_shared_issuer",1.0)
            names[key]=uid
        for other in c.get("near_duplicate_links",[]):union(uid,other)
        if reasons:direct[uid]=reasons
    members=defaultdict(list)
    for uid in ids:members[find(uid)].append(uid)
    groups=[];ledger=[]
    for values in members.values():
        values.sort();gid="excerpt-group-"+digest(values)
        causes=sorted(u for u in values if u in direct)
        group={"group_id":gid,"members":values,"excluded":bool(causes),"independence_established":False}
        groups.append(group)
        if causes:
            for uid in values:
                ledger.append({"context_id":uid,"group_id":gid,"rules":direct.get(uid,["transitive_quarantine"]),
                               "matched_contexts":causes,"disposition":"exclude",
                               "connectivity_proof_edges":edges[uid]})
    return sorted(groups,key=lambda g:priority("source-screen",g["group_id"])),sorted(ledger,key=lambda r:r["context_id"])


@dataclass(frozen=True)
class CaseSpec:
    group_id: str
    context_ids: tuple[str,...]
    anchors: tuple[str,...]
    question: str
    requirements: tuple[tuple[str,str,int],...]
    fact_ids: tuple[str,...]
    stratum: str
    source_certified: bool

    @property
    def case_id(self):
        return "case-"+digest([self.group_id,list(self.anchors),self.question,[list(r) for r in self.requirements]])


class NotFeasible(ValueError):pass
class SearchNotCertified(RuntimeError):pass


@dataclass(frozen=True)
class Reservation:
    development: tuple[CaseSpec,...]
    _evaluation: tuple[CaseSpec,...]
    pool_sha256: str

    @property
    def development_sha256(self):return digest([c.case_id for c in self.development])
    @property
    def sha256(self):return digest([self.pool_sha256,self.development_sha256,[c.case_id for c in self._evaluation]])
    def development_packet(self):
        return {"case_ids":[c.case_id for c in self.development],"selection_sha256":self.development_sha256,
                "reservation_sha256":self.sha256,"seed":SEED}
    def materialize_evaluation(self, threshold_lock: dict):
        threshold=threshold_lock.get("threshold")
        valid=(threshold=="always_abstain" or type(threshold) in (int,float) and 0<=threshold<=1)
        if (threshold_lock.get("locked") is not True or threshold_lock.get("threshold") is None or
            not valid or threshold_lock.get("development_selection_sha256")!=self.development_sha256):
            raise ValueError("Matching development calibration/threshold lock required")
        return tuple(self._evaluation)


def question_is_duplicate(question, pilot_questions):
    value=normalize(question);s=shingles(tokens(value),3)
    for other in pilot_questions:
        other=normalize(other);t=shingles(tokens(other),3)
        if value==other or s and t and len(s&t)/len(s|t)>=.8:return True
    return False


def reserve_joint(groups: list[dict], cases: list[CaseSpec], *, pilot_questions: tuple[str,...], source_pool_sha256: str,
                  max_nodes: int = 1_000_000) -> Reservation:
    """Exact registered lexicographic order; resource limits stop, never relax rules."""
    if not re.fullmatch(r"[0-9a-f]{64}",source_pool_sha256):raise ValueError("Frozen source inventory SHA-256 required")
    bygroup={g["group_id"]:g for g in groups}
    if len(bygroup)!=len(groups):raise ValueError("Duplicate groups")
    members=[u for g in groups for u in g["members"]]
    if len(members)!=len(set(members)) or any(not g["members"] or g["group_id"]!="excerpt-group-"+digest(sorted(g["members"])) for g in groups):
        raise ValueError("Source components/IDs must be frozen canonical connected groups")
    if len({c.case_id for c in cases})!=len(cases):raise ValueError("Duplicate case IDs")
    usable=[]
    for c in cases:
        if c.group_id not in bygroup or not set(c.context_ids)<=set(bygroup[c.group_id]["members"]):
            raise ValueError("Case crosses or references unknown source groups")
        if (c.stratum not in DEVELOPMENT or not c.fact_ids or len(set(c.fact_ids))!=len(c.fact_ids)
            or len(c.fact_ids)!=len(c.requirements) or not c.anchors or type(c.source_certified) is not bool):
            raise ValueError("Invalid stratum or underlying fact identifiers")
        if c.source_certified and not bygroup[c.group_id]["excluded"] and not question_is_duplicate(c.question,pilot_questions):
            usable.append(c)
    pool_hash=digest({"source_pool_sha256":source_pool_sha256,"groups":sorted(groups,key=lambda g:g["group_id"]),
                      "cases":[asdict(c) for c in sorted(usable,key=lambda c:c.case_id)],
                      "pilot_question_screen_sha256":digest([normalize(p) for p in pilot_questions])})
    group_cases=defaultdict(list)
    for c in usable:group_cases[c.group_id].append(c)
    eligible={g for g,v in group_cases.items() if len(v)>=5}
    nodes=0
    def tick():
        nonlocal nodes
        nodes+=1
        if nodes>max_nodes:raise SearchNotCertified("Exact search limit reached; no feasible assignment certified")
    def assignments(gids,target,stream,used):
        ordered=sorted([c for g in gids for c in group_cases[g]],key=lambda c:priority(stream,c.case_id))
        need=sum(target.values())
        def walk(start,chosen,counts,pergroup,facts):
            tick()
            remaining=need-len(chosen)
            if len(ordered)-start<remaining:return
            if any(counts[s]>target[s] for s in target):return
            rest=ordered[start:]
            if any(sum(c.stratum==s for c in rest)<target[s]-counts[s] for s in target):return
            if any(sum(c.group_id==g for c in rest)<5-pergroup[g] for g in gids):return
            if not remaining:
                if all(pergroup[g]==5 for g in gids) and dict(counts)==target:yield tuple(chosen)
                return
            for i in range(start,len(ordered)):
                c=ordered[i]
                if counts[c.stratum]>=target[c.stratum] or pergroup[c.group_id]>=5 or set(c.fact_ids)&facts:continue
                counts[c.stratum]+=1;pergroup[c.group_id]+=1
                yield from walk(i+1,chosen+[c],counts,pergroup,facts|set(c.fact_ids))
                counts[c.stratum]-=1;pergroup[c.group_id]-=1
        yield from walk(0,[],Counter({s:0 for s in target}),Counter(),set(used))
    dev_order=sorted(eligible,key=lambda g:priority("development",g))
    for dg in combinations(dev_order,4):
        for dev in assignments(dg,DEVELOPMENT,"development",set()):
            facts={f for c in dev for f in c.fact_ids}
            eval_order=sorted(eligible-set(dg),key=lambda g:priority("stage1",g))
            for eg in combinations(eval_order,6):
                for evaluation in assignments(eg,EVALUATION,"stage1",facts):
                    return Reservation(dev,evaluation,pool_hash)
    raise NotFeasible("Joint 20/30 mix, four/six groups, five-case cap and unique facts cannot all be certified")
