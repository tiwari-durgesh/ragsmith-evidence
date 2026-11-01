# Option C amendment: content-screened excerpt study

November 1, 2026. **Amendment for approval; plan only.** The user approved Option C
as a direction, conditional on reviewing this concrete amendment before data
selection. Writing and committing it does not authorize implementation, corpus
lock, candidate authoring, selection, calibration or evaluation. This document
supersedes the complete-original-report corpus and verified-report allocation
requirements only after that approval. Earlier tagged documents remain history.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Those facts share nine
contexts; statistical independence is not established. Pilot labels remain
**provisional, single-annotator**. The eight recovered pilot report families
remain excluded. No new dataset records or questions were inspected to prepare
this amendment.

## 1. Accepted limitation and permitted interpretation

**Unresolved report overlap is accepted under Option C.** Excerpts may originate
from the same report or related reports despite different context IDs, table
hashes and visible company names. **Hash deduplication and company-name
deduplication cannot establish report disjointness.** A company name can be absent,
abbreviated, refer to another entity or change over time. Different source content
can disclose the same fact. The rules below reduce known overlap; they do not
remove this limitation or prove that every pilot-related excerpt was excluded.

Allowed results are descriptive paired coverage, unsupported-claim risk, citation
correctness and failure counts on the exact declared excerpt scope, conditional
on the fixed local model, shared retrieval/candidates and manual decomposition.
The original partial-coverage metric and risk tolerances remain descriptive
targets. An observed difference is not a confirmatory decision or novelty proof.

The following claims are **not allowed**:

- Independence between questions, source facts, excerpt groups or partitions.
- Generalization to other documents, unseen reports, companies or enterprise
  question populations; report-disjoint or leakage-free evaluation.
- Effective sample sizes or report-family confidence intervals justified by
  content groups; tight comparable-risk guarantees or statistical superiority.
- Natural stratum prevalence, historical novelty, automatic decomposition,
  hybrid-retrieval superiority or model-size effects.

Do not replace missing report identities with invented family IDs or treat
components as independent sampling units. Report counts and denominators without
inferential confidence intervals/p-values. Public-source exposure during model
training remains unmeasured under both TAT-QA and filing alternatives.

## 2. Fixed source universe and pilot/company exclusions

Use the already pinned **TAT-QA raw training split**, revision
`870accc41953dcde885aabeb963d94aabdc0fbc3`, as the source-only screening universe.
Validate its existing trusted audit/hash before later use; do not switch splits,
revisions or add material after looking at system outputs. The [official pinned
README](https://github.com/NExTplusplus/TAT-QA/blob/870accc41953dcde885aabeb963d94aabdc0fbc3/README.md#license)
records CC BY 4.0. Use raw tables and paragraphs, not upstream answers, gold cell
mappings or heuristic `facts` preparations as evidence or authoring guidance.
The exact complete bounded excerpt corpus and context scopes will be declared
and locked only in a later authorized step, before question authoring. Include
whole contexts, not just requested cells or gold-selected two-row documents.

Apply exclusions before forming an eligible candidate pool:

1. Exclude all nine pilot context IDs and all eight known pilot report families,
   versions, copies and attributable overlapping excerpts recorded in the
   [ledger](report-identity-trial-exclusions.json). Retain its two unresolved
   table-overlap exclusions. An unresolved match is not silently cleared.
2. Exclude **every excerpt sharing a company name with a pilot company**, even
   if its period, values or table hash differ. Search the complete table-cell and
   paragraph source text, plus already source-verified identity metadata; do not
   read questions/answer labels to infer company names. Use this fixed initial
   list of legal names and distinctive core-name aliases:

   | Pilot issuer | Name strings to match |
   | --- | --- |
   | American Tower Corporation | American Tower Corporation; American Tower |
   | Carpenter Technology Corporation | Carpenter Technology Corporation; Carpenter Technology |
   | Mimecast Limited | Mimecast Limited; Mimecast |
   | Shopify Inc. | Shopify Inc; Shopify |
   | Teradyne, Inc. | Teradyne Inc; Teradyne |
   | Rogers Communications Inc. | Rogers Communications Inc; Rogers Communications; Rogers |
   | Cornerstone OnDemand, Inc. | Cornerstone OnDemand Inc; Cornerstone OnDemand |
   | Consolidated Communications Holdings, Inc. | Consolidated Communications Holdings Inc; Consolidated Communications Holdings; Consolidated Communications |

   Normalize source/name strings with Unicode NFKC, casefold, punctuation-to-space
   and whitespace collapse. Match contiguous whole-token sequences, not substrings
   inside a word. Do not remove numeric tokens, guess tickers, fuzzy-match unrelated
   companies or expand ambiguous acronyms automatically. A mention anywhere is
   sufficient for conservative exclusion, even if it names a counterparty. Company
   aliases learned later from sources extend the exclusion list and trigger a full
   rescreen **before selection**, with the extension logged and hash-locked; they
   cannot be used to clear exclusions or repair an unfavorable system result.
3. Exclude **every excerpt whose normalized table hash equals any of the nine
   pilot tables**, regardless of context ID or paragraph differences. Table hash
   is SHA-256 of the canonical nested list of cells after NFKC, casefold and
   whitespace collapse; preserve row/column boundaries, numbers, signs, years and
   units. Do not discard all numeric content to make a structural hash.
4. Retain earlier exact source equality and near-duplicate screens: normalized
   table/text equality, token 5-shingle Jaccard >=0.80, and normalized-row hash
   intersection >=0.50 relative to the smaller table's distinct nonempty row set.
   Preserve numbers/signs/units/years. A short nonempty token sequence with fewer
   than five tokens has only the equality screen; an empty token sequence is not
   evidence of a duplicate. For content similarity, normalize NFKC/case/whitespace
   without deleting signs or punctuation; serialize tables row-major for token
   comparison and retain nested cell boundaries for equality/row hashes. Tokenize
   into Unicode alphanumeric runs plus individual nonwhitespace punctuation tokens
   so numeric signs remain visible. Use sets of contiguous token n-grams and
   intersection/union Jaccard, not a bag or embedding score. Context-text equality
   uses the canonical normalized table plus source paragraphs in their original
   order, excluding UIDs and all question/answer fields. Apply the same conventions
   with n=3 for the later question screen. Log normalization and input hashes. Every
   unresolved pilot match is excluded. Company-name/table-hash matches in rules
   2–3 are mandatory exclusions, not generic-header false positives to waive.

Log every exclusion with context UID, matched pilot/name/hash, rule, score if
applicable, disposition and source-backed reason. Do not publish private labels
or raw source packets in that ledger. Unknown identity alone is accepted as the
explicit Option C limitation; ambiguous question entity/period/units still makes
a candidate not adjudicable. In the later authoring step, retain exact normalized
question equality / token 3-shingle Jaccard >=0.80 exclusions against all 18 pilot
questions before any draw. Their presence in a private duplicate screen does not
authorize use of pilot answers as gold or question-authoring guidance.

## 3. Candidate excerpt groups and deterministic allocation

These are **content/name-linked excerpt groups**, not report families. Before
partitioning, form an undirected graph over all source contexts in the declared
screening universe, using source content only. Add an edge for:

- Exact normalized table or complete context-text equality, or either retained
  table/text near-duplicate threshold above.
- A shared source-verified, explicitly named issuer, using the same name
  normalization and whole-token matching. Record the unambiguous issuer/core-name
  aliases from source metadata/prose; a generic "the Company" or an unverified
  inference from figures creates no identity claim or name edge. Record uncertainty.

Connected components are candidate excerpt groups. If any member meets a pilot
exclusion, quarantine the **whole connected component**, including linked members
without a direct pilot match. This transitive rule prevents splitting a cheap
known overlap across partitions. An unresolved similarity flag remains quarantined;
no clearance based on desired counts. Any source-backed nonmandatory false-positive
clearance must be logged before the graph/pool is frozen. No community clustering,
random graph cuts or post-run component changes are allowed.

Stable group ID: `excerpt-group-` plus SHA-256 of the canonical sorted member-UID
list. Hashing uses UTF-8 JSON, `ensure_ascii=False`, `sort_keys=True`, compact
separators `(',', ':')`, no NaN and no trailing newline. Use this same canonical
serialization for normalized-table hashes, priorities and later case IDs.

**Seed: 1729.** Priority is SHA-256 of canonical JSON `[1729, stream, stable_id]`;
sort digest bytes ascending, then stable ID. Retain stream names `source-screen`,
`development`, `stage1`, `reviewer` and `reviewer-packet`. Visit source groups in
`source-screen` order. Later case IDs derive from group ID, original context/cell
anchor IDs, final question and question-only requirements, excluding gold values.
Freeze the exact inputs and resulting source-only pool before any study system run.

**At most five questions total per candidate excerpt group**, across development
and evaluation combined. Keep groups wholly in one partition; a component cannot
contribute five to development and another five to evaluation. Retain the proposed
six evaluation groups and four other development groups, five questions each,
so this design uses the cap exactly when feasible:

| Partition | Questions | Full | Partial | Missing | Genuine conflict |
| --- | ---: | ---: | ---: | ---: | ---: |
| Evaluation, six groups | 30 | 12 | 9 | 5 | 4 |
| Development, four other groups | 20 | 8 | 6 | 3 | 3 |

Do not require a convenient fixed stratum mix per group; satisfy the aggregate
mix with no duplicated requested fact across cases. A question whose evidence
spans multiple contexts must stay within its assigned group; two equally
applicable sources must be available for a genuine conflict. Group membership
must be determined before authoring to prevent case-specific grouping.

After source-only feasibility and the full pool/requirements freeze, enumerate
joint feasible development/evaluation assignments satisfying these constraints.
Choose lexicographically first by the development group-priority list, development
case-priority list, evaluation group-priority list, then evaluation case-priority
list (each sorted within its own stream). A source-only coordinator may certify
joint capacity without exposing/committing selected evaluation IDs before the
calibration freeze. Development selection reads no system output. Lock development
gold, calibrate using the already fixed rule, then commit the threshold/runtime
manifest. Only then materialize the reserved first-feasible evaluation assignment
from the unchanged source-only pool. Do not resample based on calibration scores.
No candidate pool or assignment is created by writing this plan.

## 4. Labels, genuine-quota stop rule and retained controls

Retain the [source-only templates, accountable human authorship/manual question-
only decomposition and independent absence-verification procedure](thirty-question-reduced-scope-amendment.md).
Apply the exhaustive keyword/table/narrative scan to **all excerpts in the declared
question scope**, not to retrieved hits alone. Scope must be fixed from the source
inventory before authoring, shared across policies, and never narrowed to turn a
supported fact into a negative. Missing means absent from that excerpt scope,
not absent from the original report or company disclosures. Unsupported extraction
or verifier format is never gold `missing`.

Genuine conflict still requires the same entity, metric, fiscal period and units,
equally applicable real source statements, and no resolving version/definition
priority. Different figures with unknown issuer/context are not genuine conflicts.
No fabrication, source deletion, synthetic backfill or reuse of the constructed
pilot to meet quotas. Reviewer uncertainty stays `not_adjudicable`.

**If fewer than nine genuine partial or four genuine conflict evaluation
opportunities exist, STOP for another explicit amendment.** Likewise stop if the
development 6 partial / 3 genuine conflict targets, six/four group allocation,
five-question cap or any required mix cannot be met simultaneously. Do not proceed
automatically with actual counts, change seed, replace strata or weaken labels.
Actual eligible yields remain unknown. Pre-inference adjudication that invalidates
feasibility triggers the same stop rule. Preserve original labels and exclusions.

Retain the metrics, risk definitions/tolerances, fixed Qwen2.5-1.5B-Instruct Q4_K_M
and runtime, seed, shared eight-chunk/3,200-token retrieval-input target, 384-token
generation cap, never-abstain retrieve-and-answer baseline, per-requirement
confidence-threshold abstainer and graded sufficiency policy. Keep the existing
development-only confidence grid/tie breaks and identical source scope,
decomposition, packed evidence and cached candidates for all policies. No prompt,
alias, threshold or policy tuning on evaluation data. Full prompt/packing and
candidate-log-probability compatibility still need a pre-selection engineering
pass; a compact source format alone is not that pass.

Labels/results remain provisional and single-annotator until independent human
review. A second human must label all 30 evaluation questions before paper results;
hide primary labels/system outputs during source-gold review, lock both originals,
report agreement before adjudication, and preserve disagreements. No LLM substitute.
Even after review, the prohibited independence/generalization claims remain
prohibited. Plan 5–7 hours per person for all 50 questions with usable excerpt
packets, potentially 8–10 if scope/absence checks are difficult. This is an estimate,
not a measured saving; keep the <=9h user cap and stop if it cannot be respected
without weakening the procedure. No inference or annotation is authorized here.

## 5. Hour-by-hour engineering plan — before building

**6–10 additional engineering hours, conditional on approval to proceed under this
amendment.** This is separate from the four-hour active-work
identity/feasibility cap, which does not reset. Do not spend remaining search time
on unapproved infrastructure. No PDF parser, general HTML parser, new diagnostics
framework, partition service or reporting subsystem is proposed.

Any new ingestion/canonicalization code belongs in a **separate module outside
the frozen `src/` tree** (proposed `scripts/tatqa_excerpt_ingestion.py`), with its
own focused tests. Existing `src/` verifier, contradiction policy and assessment
schema remain unchanged, as does the full source tree
`3261c6087757b9f3d9aed1166e264de45ac4f479`. Separate runtime glue must call the
existing APIs; it may not replace or bypass verification.

| Hour | Bounded work and deliverable | Gate |
| --- | --- | --- |
| 1 | Read source contracts; specify the external module's source-only input/output and exclusion/grouping normalization using synthetic fixtures and already-excluded pilot examples | No fresh candidate selection; no question/answer label fields accepted by ingestion |
| 2 | Implement the minimal source-cell adapter: complete context/headers/prose, original row/column locators, byte hashes and unambiguous metric/year/unit/sign bindings | Interpret all source facts by fixed rules; never just gold/requested cells; ambiguous bindings remain unsupported and visible |
| 3 | Focused tests for multirow headers, duplicate years/units, missing cells, spans and lineage; exercise name/table exclusion and transitive-group invariants on synthetic examples | No guessed aliases, lost conflicting facts or source-shaping based on expected answers |
| 4 | Connect canonical evidence plus preserved unsupported source material to existing read-only retrieval; implement the single shared deterministic eight-chunk/3,200-token packing contract with full prompt accounting | Log truncation; preserve required headers/units/locators; failure is not missing gold |
| 5 | Minimal local answerer/citation/value-token-span bridge and shared cache using existing runtime components | Fixed model/settings; candidate citations resolve to preserved evidence; existing verifier receives candidates unchanged |
| 6 | Synthetic-only end-to-end checks of all three policies and calibration fallback; commit module/runtime/interface hashes and report engineering readiness | Meaningful checks pass; no study data, score tuning, model substitution or src edits |
| 7, if needed | Fix source-adapter defects found in synthetic/excluded examples | Same contracts; no scope expansion |
| 8, if needed | Resolve packing/citation boundary defects and rerun only affected checks | No per-policy evidence differences or silent token clipping |
| 9, if needed | Resolve value-token/log-probability transport defects | No confidence-feature substitution or evaluation data access |
| 10, if needed | Final focused verification and documentation of remaining blockers | Hard stop at 10h; report rather than build more infrastructure or select data |

Hours 7–10 are a bounded contingency, not automatic extra scope. At a failed gate,
stop and report the concrete defect; do not use the next task to conceal it. Six
hours is the optimistic complete path, not a promise. All new code/tests would be
committed separately from this planning amendment. Runtime/source/interface freeze
must precede corpus lock and question authoring; preserve `src/` throughout.
Engineering approval does not by itself authorize later corpus selection or a run.

## 6. Approval and integrity record

Current action is documentation only. Append this amendment's **exact Git-blob
SHA-256** to `docs/preregistration-public-manifest.json`; retain older hash entries
and public/local tags unchanged. This record is local pending a future explicit
push; do not imply it is already published on GitHub.

Next required action is user approval of this amendment. **No data selection until
that approval.** Follow the engineering plan only when authorized to proceed;
report any engineering or genuine-quota gate failure before dependent work.
No corpus lock, candidate screening/authoring, new labels, calibration or evaluation
is performed by this commit. Commit locally on `codex/public-progress`; do not push.
