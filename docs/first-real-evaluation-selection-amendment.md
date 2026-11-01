# Pre-selection amendment: report identity, Stage-1 sampling and reviewer packet

Recorded November 1, 2026. **Plan only: no implementation, candidate inspection,
new annotation, evaluation data selection or evaluation inference in this batch.**
The user accepted the runtime checks. This amendment specifies the next proposed
source/selection workflow; execution awaits approval. It preserves `prereg-v1`
at `6b1d04e`, the approved local 1.54B answerer, the existing verifier/schema/
contradiction policy, primary metric/risk gates and staged continuation criteria.

The completed pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from that pilot**. Facts share nine
contexts; statistical independence is not established. Labels remain
**provisional, single-annotator**. New questions remain provisional until their
own review; runtime acceptance does not resolve source identity or answerability.

## 1. Identity-recovery rule, decided before selection

Retain the existing **four-hour total identity/feasibility work budget**, with
start/stop and work-time entries. Do not restart the clock under another batch
name or move unresolved identity work into annotation time. This pass covers
pilot identity, prospective source-family identity/exclusions and source-only
quota feasibility, not model experiments. It may legitimately stop without a
single evaluation question being selected.

1. Start with the existing nine pilot context UIDs and their source cards.
   Check the pinned TAT-QA repository/release provenance material for an original
   document mapping. If no mapping is available, use distinctive paragraph
   phrases, table titles, fiscal dates, business/segment names and combinations
   of original numeric cells to locate the issuer's or regulator's original
   filing/report. Search results are leads, not identity evidence. Do not contact
   authors or other people without separate user authorization.
2. Require an inspected original source and an auditable match. Record issuer/
   legal entity and a stable identifier where available, fiscal-period end,
   report type, publication/filing date, version/restatement, official URL or
   accession, downloaded-document SHA-256, page/table/section locator, and the
   TAT-QA context UIDs matched to it. A verified upstream provenance mapping can
   assist this work but does not replace checking the actual source.
3. Confirm table title/row and column semantics, period, unit/sign and source
   values, plus an independent paragraph or other distinctive source feature.
   A generic financial row, company-name guess, number match, URL search snippet
   or table UID alone is insufficient. If there is no paragraph, require another
   distinctive table/section feature and explain the match. Record ambiguity,
   not a guessed identity, when independent corroboration is unavailable.
4. Give each original document a document ID. Give all versions, restatements
   and overlapping excerpts of an issuer/fiscal-period report family one family
   ID. Conservatively merge same-issuer/same-period boundaries when uncertain,
   as in v1. Resolve parent/subsidiary and segment scope explicitly; uncertainty
   is not a source of genuine conflicts or independent sampling units.
5. Map accepted candidate families in the same way. Scan the entire pinned
   split for additional excerpts/versions belonging to those families using the
   recovered provenance and table/paragraph fingerprints. A demonstrably complete
   upstream context-to-report mapping is preferable to manual inference. Include
   all available matched TAT-QA contexts for each accepted family; do not retain
   just the rows needed for a question. If potentially related unmapped excerpts
   leave family membership/completeness unresolved, that family is ineligible.

**Binding stop/exclude decisions:**

- If **any pilot context cannot be assigned confidently to its original report
  family**, block the whole TAT-QA evaluation selection. Excluding nine UIDs is
  not a substitute for excluding their reports.
- If a **candidate identity, family membership or possible pilot overlap remains
  unresolved**, exclude that candidate/family. Never treat an unidentified
  context as a new independent report. Unknown contexts cannot be distractors.
- At four hours, if all pilot identities and enough eligible families/strata
  cannot be certified, **stop and request a committed, user-approved corpus or
  scope amendment before any evaluation selection**. No automatic switch,
  synthetic-conflict backfill, quota reduction, context-only evaluation or
  extension of the recovery budget is authorized. This rule is fixed now.
- Stage 1 requires 10 eligible evaluation families with five questions each and
  the 20/15/8/7 mix; calibration uses four other families, five questions each,
  with mix 8/6/3/3. This instantiates v1's minimum of four development families.
  Aggregate case counts alone are insufficient
  if they cannot meet the family constraints simultaneously.
- Continuation still requires the cumulative 30 partial / 15 genuine-conflict
  opportunities and the already declared operational gates. Do not enlarge the
  initial run merely because the full 100 looks difficult to recruit.

The indexed collection remains the licensed pinned TAT-QA excerpts, with all
available contexts of accepted families and verified unrelated distractors.
Original reports retrieved for provenance are **identity aids**, not silently
added retrieval evidence. Gold absence means absent from the entire declared
indexed scope, not absent from the company's complete original report. Do not
hide an unresolved/missing excerpt to manufacture a negative. If completeness
cannot be established under this definition, stop rather than redefine it.

## 2. Pilot exclusion and duplicates before any draw

Exclude every recovered pilot family, including alternative versions and
overlapping excerpts. Apply the existing screens, preserving numbers, units,
signs and years during normalization:

- Exact SHA-256 equality of original document bytes and canonical text/tables.
- Unicode/whitespace/case-normalized table equality and normalized row hashes.
- Token 5-shingle Jaccard >=0.80, or row-hash overlap >=0.50 relative to the
  smaller table. Compare question text with all 18 pilot questions using exact
  normalized equality or token 3-shingle Jaccard >=0.80.
- Review issuer/period matches and every similarity flag against original
  sources. Record the pair, score, disposition and source-backed reason before
  model output. A demonstrable generic-header false positive may be cleared;
  unresolved flags exclude the candidate. Low similarity never overrides a
  known common report family.

Apply the same document/table/question checks between development and evaluation
and within the prospective pool. Put duplicate versions/overlapping sources in
one family or exclude them; do not distribute them across partitions. Treat the
same requested underlying fact as one opportunity, even if paired with different
second requirements. A repeatedly reused disputed cell cannot fill seven
conflict slots. Record unique supporting facts as well as report-family counts;
do not call 50 clustered questions 50 independent observations.

This is freshness relative to pilot/development sources, not proof that public
reports or TAT-QA were absent from the answerer's pretraining data.

## 3. Fixed source-only selection procedure

**Seed: 1729.** Use deterministic hash priorities, not operator choice of a
favorable random draw. Priority is SHA-256 of a canonical UTF-8 JSON array
containing the seed, stream name and stable family/case ID. Sort hash bytes
ascending, breaking any ties by the stable ID. Stream names are `source-screen`,
`development`, `stage1`, `reviewer`, and `reviewer-packet`. Record canonicalization
and input-pool hashes in the selection manifest. No implementation is added now.
Family IDs derive from verified issuer/period provenance; case IDs derive from
family, source-anchor IDs and canonical question/requirement content. Freeze
these IDs before ranking; never hand-pick or rename IDs to obtain another draw.

1. **Approve this amendment, then screen sources.** Use the identity/exclusion
   process above in `source-screen` priority order. Do not inspect answerer,
   retrieval, verifier, confidence, grading or policy-comparison outputs to
   create candidates or decide eligibility. Keep a source-only screening log,
   including failures and shortfalls; do not just log accepted cases.
2. **Declare the complete corpus and scope.** Freeze document/family membership,
   versions, all included TAT-QA contexts and distractors. Record entity and
   period scope and a source-backed precedence rule. Do not omit a resolving
   restatement to create a conflict. Development/evaluation families and any
   report-overlap groups must be disjoint from the pilot and each other.
3. **Build a source-only candidate inventory.** Use noncomparison table-span
   extraction anchors from the pinned corpus. Questions have exactly two atomic
   extraction requirements; no arithmetic, counting, comparison or ambiguous
   entity/year/unit. Preserve ordinary question wording, not aliases selected
   to suit the verifier. Question-only decomposition is identical for all three
   policies and contains no answer values or gold cell IDs.
   Human source screening/authorship fixes eligibility, question text and stratum;
   the experimental answerer does not propose, label or rank candidate questions.
   Full candidates pair two direct supported facts. Partial candidates pair one
   supported fact with one plausible absent fact; missing candidates request two
   plausible absent facts. For absent requests, use ordinary metrics from the
   predeclared catalogue: revenue, net income, operating income, total assets,
   total liabilities, cash and cash equivalents, capital expenditures, employee
   headcount. Use an applicable entity and a fiscal period actually represented
   in the collection; do not use implausible metrics or imaginary future years.
   If applicability is unclear, exclude rather than label missing. Check the
   entire declared scope, including aliases, headers, footnotes and prose; a
   failed retriever or literal string search is not an absence proof.
   Conflict candidates require at least one genuine inconsistent fact: same
   entity, metric, period and unit, equally applicable real sources, no resolving
   version/scope priority. Record both cell/span locators. Different concepts,
   regions, periods or clear restatements do not qualify. Never fabricate values,
   delete rows or ask the answerer to create the conflict candidates.
4. **Close and hash the pool before development inference.** Record each stable
   case ID, family, question, two requirements, intended source stratum and
   source-backed eligibility/absence/conflict rationale in a gold-only inventory.
   Keep model inputs separate. The stopping condition is the first source-screen
   pass establishing simultaneous development/Stage-1 feasibility within the
   four-hour budget; otherwise stop under section 1. After closure, do not add
   more favorable families/cases or change strata in response to any output.
5. **Select development first.** In `development` hash order, choose the
   lexicographically first feasible assignment of 20 cases from four families,
   five per family, satisfying 8 full / 6 partial / 3 missing / 3 conflict, while leaving
   a feasible 10-family Stage-1 assignment in the remaining pool. Check remaining
   capacity only; do not select or publish Stage-1 case IDs yet. Obtain and lock
   development gold; then calibrate the fixed confidence threshold using the
   already declared rule and commit it, its hashes and the runtime/prompt/
   interface manifest. No threshold choice influences subsequent selection.
   Order development assignments by their family-priority list then case-priority
   list, as for Stage 1. The selection process reads the frozen source-only pool,
   never the development model outputs or calibration scores.
6. **Draw Stage 1 after that freeze.** From the unchanged remaining source-only
   pool, select the lexicographically first feasible assignment under `stage1`
   priorities satisfying **10 families, exactly five questions per family,
   20 full / 15 partial / 8 missing / 7 conflict**, no duplicate requested facts
   and all exclusion rules. Compare assignments by their ordered family-priority
   list, then their ordered case-priority list. This is a quota-constrained draw;
   not uniform sampling from TAT-QA and not a prevalence estimate. No convenient
   fixed per-family stratum mix or extra requirement for seven conflict families
   is introduced. If no feasible assignment exists, stop; do not choose a new
   seed, relax a constraint or fill vacancies with another stratum.
7. **Annotate, review and lock before evaluation inference.** Audit the selected
   50 against the full source scope, keep uncertainty explicit, and commit the
   case/corpus/decomposition/gold hashes. Independent review may reveal errors:
   adjudicate from sources, retain both original labels and record any corrected
   composition. Do not replace a case merely because the reviewer disagrees.
   If pre-inference corrections invalidate the required mix/eligibility, stop
   for a sampling amendment, not silent backfilling. If an error is found after
   inference, retain the case and disclose the corrected gold/counts; do not
   rerun or resample to improve results.
8. **Run only after separate authorization.** Reuse one retrieved-evidence and
   candidate cache for the three policies. No test-set prompt/threshold tuning,
   repeat sampling or difficulty filtering using system results. Apply the
   existing >=45/50 adjudicability, >=95% generation completion, time and
   source-feasibility continuation criteria before viewing comparison scores.
   Stage 1 stays descriptive; no new hypothesis-testing decision at 50.

## 4. Annotation budget in sessions of about two hours

Budget **about 8–9 user hours**, excluding the separately capped **2–4 hours of
identity/feasibility work**. This is five sessions of at most about two hours,
not a promise of completing the study in a few hours. The following task ranges
sum to 6.5–9 hours; use the upper range for scheduling. They include development
gold and post-inference review so those costs are not hidden.

| Session | Work | User hours |
| --- | --- | ---: |
| 1 | Short invented-example practice; 20 development/calibration gold labels | 1.5–2 |
| 2 | Stage-1 source gold/decomposition: 20 full and 5 partial cases | 1.5–2 |
| 3 | Remaining 10 partial and 8 missing cases; documented absence checks | 1.5–2 |
| 4 | Seven genuine-conflict cases; final gold/scope checks and packet audit | 1–1.5 |
| 5, after the separately authorized run | Judge each unique cached claim/citation once; human adjudication | 1–1.5 |

The 50-question source-gold work is approximately **4–5.5 hours** in sessions
2–4. A second human's independent 30-case gold/citation review and later
adjudication remains about **4–7 hours**, typically two or three two-hour
sessions plus a short resolution session. Neither estimate assumes an LLM can
replace the reviewer. If the user's measured study annotation/review time
exceeds nine hours, preserve the existing stop/continuation rule; do not rush
labels or silently increase the commitment. Record actual time per task.

Shorten the work by recovering provenance in advance, grouping views by report,
providing clean full tables with headers/units and stable locators, drafting
neutral question-only decompositions for human checking, and searching the full
scope once per metric/family with a reusable search log. Reuse judgments for
identical cached claims across policies; ask the user to inspect unique claims
once. Keep forms short with requirement states, value/units, source locator and
brief reason only when needed. These are workflow savings, not permission to
skip negative searches, hard conflicts, independent review or changed labels.

## 5. Blinded second-annotator packet plan

Select **30 of the 50 cases**, using `reviewer` priorities within the fixed source
strata: **12 full / 9 partial / 5 missing / 4 conflict**. Select before any
evaluation output and commit the selected-ID manifest privately. Within a
stratum, visit families in `reviewer` priority order and take their next case in
round-robin order until its quota is met, maximizing spread without changing
the mix. The reviewer does not receive the stratum labels or target counts.
Reclassification does not cause replacement of the reviewed cases. Preserve
the existing plan to add 4/3/1/2 cases if extending to a 40-case review at 100.

Prepare an **allowlisted export**, never an archive of the working evaluation
directory. The future packet contains:

- A short cover note, protocol version/hash, instructions for uncertainty and
  the source-priority rule. Include five invented worked examples covering full,
  partial, missing, genuine unresolved conflict, and a scope/version mismatch
  that must not be called a conflict. Do not reuse pilot/evaluation facts or the
  legacy guide's controlled-removal examples as real-data instructions.
- Random-looking opaque IDs, question text and exactly the shared question-only
  requirements; no IDs/filenames containing `full`, `partial`, `missing`,
  `conflict`, expected values or source-gold annotation IDs. Order cases with
  `reviewer-packet` priorities. Keep the private ID crosswalk out of the export.
- The complete declared source scope, verified source snapshots with intact
  headers/units/versions, neutral navigation/search index and locators. No
  highlighted answer cells, primary-annotator search notes, answer inventory,
  expected values, upstream answer labels, proposed verdicts or uncertainty flags.
- A blank independent form for requirement state (`supported`, `missing`,
  `conflicted`, `not_adjudicable`), value/unit and locator or conflicting pair,
  plus the question policy label (`full`, `partial`, `abstain`,
  `not_adjudicable`). Brief absence/ambiguity/conflict reasons are required.

The reviewer labels corpus gold **before seeing model outputs**, submits a
separate original file and locks its hash before either annotator sees the
other's labels. Then, after the authorized run, provide a second neutral sheet
of unique cached candidate value/citation claims for those cases, in shuffled
order, without policy names, confidence, verifier verdicts or the user's claim
judgments. Judge those claims once and reuse them across policies. Keep source
gold and retrieved-evidence sufficiency as different annotation targets.

Before delivery, inspect every exported field/file against the allowlist and
search for primary gold values/labels, notes, policy names and hidden metadata.
Some source values will naturally be present in the source snapshots; the audit
must distinguish those from leaked answer annotations. Seal the packet hash.
The user arranges delivery; this planning batch sends nothing to another person.
The private working repository and primary-label area are not part of delivery;
give the reviewer only the allowlisted packet until independent labels are locked.

Measure raw human agreement and Cohen's kappa on the independently labeled
requirement states and question-policy labels **before adjudication**, retaining
`not_adjudicable` and reporting counts/undefined kappa where applicable. Preserve
both original files and source-backed adjudication notes. This is human agreement;
no LLM agreement is claimed. Cases outside the reviewed subset remain explicitly
single-annotator. If a second human is unavailable, keep the study internal and
provisional: **a human second annotator for 30–50 questions is required before
any paper results**, unchanged.

Production `src/` remains frozen at tree
`3261c6087757b9f3d9aed1166e264de45ac4f479`. No code, corpus/label files or
evaluation-selection artifacts are created by this amendment. No push is authorized.
