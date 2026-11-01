# Reduced-scope amendment: authoring, absence checks and engineering gate

Recorded November 1, 2026, before new evaluation-data selection. The user approved
the [30-question direction](thirty-question-reduced-scope-proposal.md) in principle,
subject to the conditions implemented here. This amendment supersedes that
proposal's pending-authority wording for the specified planning/probe work. It
does not authorize selection through a failed feasibility or engineering gate.
Earlier tagged snapshots and historical reports are retained unchanged.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. The facts share nine
contexts, and statistical independence is not established. Labels remain
**provisional, single-annotator**; they are not new-study evidence.

## 1. Pilot identities and exclusions

The remaining four lookups took **2.83 minutes total**, inside the 15-minute cap.
All nine pilot contexts now map to **eight** issuer/report-period families; two
Carpenter contexts share a report. See the [identity record](report-identity-remaining-four.json)
and [exclusion ledger](report-identity-trial-exclusions.json).
Archive follow-up remained within the same 15-minute wall-clock window (9.26
minutes at its checkpoint). Teradyne and Cornerstone mirrors were hashed and
their local table fingerprints corroborated; Rogers' mirror was also verified.
Consolidated's mirror returned HTTP503 on both attempted transports, so its
official HTML is the inspected identity authority and its byte archive remains
pending. No further retry was made. This does not weaken the family exclusion
or certify complete archival provenance for a future corpus lock.

| Remaining pilot context | Recovered issuer / FY end | Official identity evidence |
| --- | --- | --- |
| 71649e80-12e2-4c60-8177-2825f9b4e375 | Teradyne / 2019-12-31 | [Issuer-hosted filed 10-K](https://investors.teradyne.com/sec-filings/all-sec-filings/content/0001193125-20-058676/d860886d10k.htm), postretirement expense table and named-issuer prose, printed p.91 |
| b79cd05c-76c5-41ae-9bf9-3bf399507b46 | Rogers Communications / 2019-12-31 | [Filed MD&A](https://www.sec.gov/Archives/edgar/data/733099/000119312520063454/d822661dex991.htm), depreciation table and IFRS16 explanation, annual report p.44 |
| a5283e18-51a8-4d2a-a6be-cba392b1f375 | Cornerstone OnDemand / 2019-12-31 | [Filed 10-K](https://www.sec.gov/Archives/edgar/data/1401680/000140168020000004/a10-k20191231q4.htm), Other Income (Expense) table and independent note-repayment/FX explanation |
| e3462c1a-1e69-4a4a-b9e1-b65898926335 | Consolidated Communications Holdings / 2019-12-31 | [Filed 10-K](https://www.sec.gov/Archives/edgar/data/1304421/000155837020001763/cnsl-20191231x10k829a6e.htm), funding prose p.43 and three-year cash-flow table p.44 |

Every pilot family, version, overlapping excerpt and verified near-duplicate
remains excluded from both development and evaluation. The two conservative
table-overlap flags remain excluded pending source-backed clearance. Recovering
these identities does not certify full TAT-QA split membership, clear those flags,
or establish partial/conflict yield. Nine contexts were not nine distinct reports.
Exact extractor filing copies are not always uniquely inferable; exclusion covers
all matched family copies rather than guessing priority. No new source was chosen
for evaluation in this batch.

Retain the prior equality/hash and similarity thresholds, including table
5-shingle Jaccard >=0.80, smaller-table row overlap >=0.50, and question exact
equality / 3-shingle Jaccard >=0.80 against the pilot. New-corpus membership and
every flag's disposition must be logged before selection. Do not clear an issuer,
period or version ambiguity based on similarity scores alone.

## 2. Fixed source-only authorship before any study system run

Target **30 evaluation questions across six new families**, five per family,
with 12 full / 9 partial / 5 missing / 4 genuine conflict. Development remains
20 questions across four other families, five per family, with 8/6/3/3. These
are **50 total questions**, with aggregate mix 20/15/8/7; not 50 evaluation cases.
The complete bounded original-report corpus, source versions and external family
mapping must pass the engineering gate and be locked before question authoring.
Never remove resolving reports, pages, rows or facts to obtain a stratum.

Use these neutral two-requirement templates, with no stratum hints in the wording:

- T1: "What were [metric A] and [metric B] for [entity] in [fiscal period]?"
- T2: "What was [metric] for [entity] in [period A] and in [period B]?"
- T3: "For [entity], give [metric A] in [period A] and [metric B] in [period B]."

Explicitly specify report scope and units only when part of the intended request.
Exactly two direct extraction requirements; no arithmetic, counting, comparison,
invented entities or ambiguous periods. A conflict candidate uses the same neutral
templates; it does not instruct the answerer to find or resolve a contradiction.
Absent facts must be plausible requests for the real entity/period, rather than
nonsense metrics. Log template ID, author, source-only rationale, proposed scope,
and source screening evidence for rejected as well as accepted candidates.

**Who writes:** Codex does the source lookups and prepares blank templates,
source inventories and mechanical slot substitutions from that inventory. The
user is the accountable human author: verifies/finalizes each instantiated request
from the source packet and records the manual question-only decomposition. This
does not introduce free-form model authorship or automatic decomposition. If a
draft is unsuitable, record its rejection before inference, without system-based
rewriting. The independent reviewer labels sources, rather than co-authoring from
the user's labels. Authoring effort is included in the estimates below.

Finish and hash-lock the **entire source-only candidate pool**, question wording,
template assignments and decompositions before any development/calibration or
evaluation retrieval, answerer, verifier, confidence or policy run. Later draws
read that unchanged pool. The experimental answerer never proposes or ranks
questions. Neither Codex nor the human authors may use experimental retrieval,
generated answers, verifier verdicts, confidence or comparison results to choose,
rewrite or classify candidates. The excluded-report engineering probe below is
not a study run and supplies no candidate questions or labels.

Keep seed **1729** and the existing canonical-JSON SHA-256 priority procedure and
stream names (`source-screen`, `development`, `stage1`, `reviewer`,
`reviewer-packet`), with stable IDs and tie breaks. Use the existing first-feasible
assignment procedure with only the amended counts/family counts. No reseeding or
convenient substitution. All three policies receive the identical hash-locked
manual decomposition, retrieved packed evidence and shared candidate generation.

## 3. Reproducible corpus absence verification

Apply this procedure separately to every putatively absent atomic requirement,
including the unavailable part of a partial question. It concerns the complete
declared corpus in the question's entity/report scope, not the retrieved top-k.

1. **Record scope and coverage first.** List every in-scope file/family/version
   and SHA-256, expected/actual page counts, text-extraction status and table
   inventory. Include notes, appendices and resolving versions under the fixed
   source-priority rule. A missing/unreadable page, unavailable referenced table
   or unresolved scope makes absence `not_adjudicable`, not `missing`.
2. **Freeze the search vocabulary before labeling.** Record the exact metric
   phrase, meaningful individual terms, ordinary financial synonyms/abbreviations,
   entity names, period variants and unit variants. Derive these from the question,
   corpus glossary and ordinary source terminology, never system results. Search
   the metric phrase and each synonym individually, without requiring a year match;
   then search period/unit variants independently to catch split headers. Normalize
   Unicode, case, whitespace and line-break hyphenation; preserve numbers/signs.
   Log every literal query, files searched, hit count and hit page/section IDs.
3. **Inspect all hits against the original layout.** Read the complete table,
   header, continuation, adjacent prose and relevant footnotes. Check entity,
   period, unit, consolidation/segment scope and definition. Record each apparent
   match's disposition and locator. Search near-matching concepts rather than
   assuming a renamed item is absent. Do not rely on the study retriever.
4. **Scan tables independently of keyword success.** Use the TOC/note index and
   full page inventory to enumerate every in-scope table; visually scan each
   table title, all row labels, all column headers and continuations. Inspect
   plausible tables' cells and footnotes. Also scan relevant narrative sections
   and cross-references. Record scanned table/page ranges, including no-hit files.
   Searching extracted text alone is insufficient for a PDF table negative.
5. **Decide and preserve the audit.** A found direct fact is supported; two equally
   applicable incompatible facts require conflict review. An explicit zero is a
   fact. A dash/blank/"not applicable" needs source interpretation and is not
   automatically absent. Permit `missing` only after complete keyword and table/
   narrative checks find no direct answer within scope. Extraction/verification
   failure is not corpus absence. Record residual uncertainty as
   `not_adjudicable`; no silent negative label.
6. **Reviewer reproduces independently.** Supply full original sources, a blank
   scope/query/table-scan form and these rules. Hide the primary labels, stratum,
   primary hit/disposition log and highlighted answers. The reviewer independently
   chooses/logs synonyms and performs the same exhaustive procedure, then locks
   their original labels. Only afterward compare logs and adjudicate from sources.
   Archive both original logs and label hashes. Absence logs/candidate gold remain
   private. Report pre-adjudication human agreement; this is not an LLM cross-check.

This establishes absence only within the named bounded collection. It does not
claim that the company never disclosed the fact elsewhere. If the fixed scans
cannot be finished within the feasibility/annotation caps, stop; do not weaken
the negative-label standard to meet a count or time target.

## 4. Quota shortfall rule decided before data selection

**Stop for another explicit, committed amendment** if fewer than **9 genuine
partial or 4 genuine conflict evaluation opportunities** can be certified, or
fewer than 6 partial / 3 genuine conflict development opportunities exist in
disjoint eligible families under the fixed per-family limits. Apply the same
rule if independent pre-inference adjudication invalidates feasibility. Do not
proceed automatically with actual counts, backfill full cases, manufacture
conflicts, relabel version/scope differences, or extend the search budget.
Current eligible yields remain unknown; this batch makes no feasibility pass.

Even with all targets met, results are descriptive. The original 15-family
partial gate cannot be met by six evaluation families. Retain the existing
primary metric, risk definition/tolerance, baselines, confidence signal and
development-only threshold rule as descriptive targets, without a confirmatory
decision or superiority claim. Retain >=27/30 source-adjudicable evaluation
cases, >=48/50 completed shared generations and <=9 user annotation/review hours;
retain failures/uncertainty in denominators. Do not automatically extend to 50
or 100 evaluation cases based on observed scores.

## 5. One excluded-report ingestion probe: engineering gate failed

The [probe record](one-report-ingestion-probe.json) uses the already-excluded
Carpenter FY2019 report, SHA-256
`07a8b90b17e6a79fd46a0a87a094d02b67fe88cfde79d89ad0b8b93fbf301d3d`.
No fresh evaluation source or question was selected, and no model inference,
policy scoring or answer-quality measurement ran.

- Bundled Python 3.12.14 was used; the old `.venv` points to an unavailable
  Python 3.11 installation. Python **3.11 remains unverified**.
- Installed the already pinned PyMuPDF 1.26.5 into an ignored probe-only directory;
  no dependency declaration, global environment or `src/` was changed. The first
  sandboxed attempt could not access that installed module correctly; the
  authorized probe then ran with access to it. No source workaround was used.
- Frozen `core.ingest` accepted the complete 100-page PDF, emitted **98 text
  evidence units**, and source-integrity verification passed. The two pages with
  no extracted text require layout inspection before any completeness claim.
- Two technical metric/year transport queries, scoped to that excluded document,
  used frozen FTS retrieval with eight hits per requirement and returned a
  **14-unit union**. Evidence JSON round-trip retained identity/version/locators.
  These technical strings are not authored evaluation questions or source-gold
  labels. No verifier verdict was scored.
- A temporary transport-only eight-unit packing prototype ordered by best
  per-requirement rank then evidence ID measured **7,194 tokens**, using the
  fixed Qwen tokenizer executable. This exceeds **3,200 input tokens**, even
  before a final answerer prompt/chat-template envelope. It is not a new locked
  packing policy. No tokens were clipped to make a favorable result.
- The native PDF parser emits page text and **zero canonical table rows**.
  Existing discovery returned zero candidates and marked all 14 retrieved units
  unsupported for each technical requirement. This is an interface-format
  blocker, not evidence that source facts are absent or a performance result.
  Frozen discovery/verifier expects canonical metric/year/value rows. Plain
  PDF pages do not satisfy that contract.
- Existing document IDs depend on absolute file paths. An external immutable
  family/version-to-document mapping is necessary for a portable source lock.

Successful probe execution took **2.41 seconds**, excluding setup. Human/agent
engineering preparation was approximately **3–5 minutes** (not separately timed);
identity lookup time above is separate. This is not evaluation throughput.
Remaining engineering is provisionally **8–16 hours**: a provenance-preserving
full-report table/continuation extraction and packing adapter (4–8h), fixed
answerer-candidate/citation/token-span interface integration (2–4h), and meaningful
synthetic/excluded-report compatibility checks plus lock documentation (2–4h).
These are uncertain planning estimates, not measured implementation times or
authorization to build infrastructure. Poor PDF layouts/OCR can exceed them.

**Do not lock the corpus or select study questions yet.** Frozen ingestion,
retrieval transport and Evidence construction work, but end-to-end table/packing/
answerer-verifier compatibility has not passed. No adapter is implemented here;
no verifier, contradiction policy, assessment schema, retrieval baseline or model
is modified. Any proposed adapter must be reviewed/authorized before coding and
locked before authoring/inference; it must not create oracle evidence from gold
or silently bypass the frozen verifier. The engineering work does not fit inside
the four-hour identity/feasibility budget and cannot be charged as completed
feasibility. Record blockers rather than spend that budget on infrastructure.

## 6. Annotation and independent review effort for all 50 questions

Conditional on a readable, source-complete, engineering-compatible corpus and
usable source-only packets, plan **7–9 user hours** and **7–9 reviewer hours** for
20 development plus 30 evaluation questions. These are estimates, not an observed
timing result. Without reusable source inventories and good layouts, either
person could need **10–12 hours**; the user <=9h gate then requires stopping for
an amendment rather than skipping scans. Researcher/agent source discovery and
the 8–16h engineering estimate above are additional, not hidden annotation time.

| Activity | User hours | Reviewer hours |
| --- | ---: | ---: |
| Practice; question finalization / manual decomposition (user); protocol familiarization (reviewer) | 0.75–1 | 0.5–0.75 |
| Independent source gold for 20 full, 15 partial, 8 missing, 7 conflict cases, including absence scans | 4.5–5.5 | 4.75–5.75 |
| After the separately authorized run: unique cached candidate value/citation judgments, reused across policies | 1–1.5 | 1–1.5 |
| After original labels lock: disagreement review and source adjudication | 0.5–1 | 0.5–1 |
| Rounded planning total | **7–9** | **7–9** |

Schedule four sessions of roughly two hours, with up to one extra hour for
adjudication. For the reviewer, all-50 review includes development labels before
threshold calibration; source-gold review is blinded to user labels and system
outputs. A minimum of all 30 evaluation questions must receive independent human
review before any paper results, retaining the earlier 30–50 subset requirement.
If the reviewer is unavailable, labels/results stay provisional/internal.

Codex can reduce time by locating sources, preparing unmarked complete-report
packets, blank template/forms, indexed tables and a neutral glossary, batching
work by family, and deduplicating identical post-run candidate claims. Reuse a
person's exhaustive metric/family scan only when the scope/version/search log is
identical. Never share primary scan conclusions with the independent reviewer or
use system hits to shortcut gold absence checks. If only the mandatory 30-case
review subset is feasible, estimate about 4.5–6.5 reviewer hours, record the actual
subset, and do not claim agreement on unreviewed development cases.

## 7. Immutable settings, budget and current status

Seed 1729, metrics, never-abstain retrieve-and-answer baseline, per-requirement
confidence-threshold abstainer, graded sufficiency policy, development threshold
grid/tie breaks, fixed Qwen2.5-1.5B-Instruct Q4_K_M/runtime settings, shared-cache
design, verifier and assessment schema remain unchanged. Production source tree:
`3261c6087757b9f3d9aed1166e264de45ac4f479`.

The four-hour cap counts active work; time waiting for user approval is paused,
not budget consumed. Prior recorded work was about 21.15 minutes. This turn's
work resumes at 17:08:39 UTC; its checkpoint is recorded separately in the probe
record. There is no budget reset. The original 15/60/90/20-minute allocation is
not expanded by this amendment; the 15-minute pilot-identity task passed, while
new-source feasibility has not begun. No engineering implementation is funded
by unused search time. Record this amendment's exact Git-blob SHA-256 in the
public manifest, without moving or reinterpreting the historical public tag.

Current state: identities recovered; no new evaluation selection, source lock,
labels, calibration or evaluation run. Stop at the demonstrated engineering
gate and report it. Commit documentation locally on `codex/public-progress`;
do not push, alter `src/`, or publish private labels, raw reports or probe caches.
