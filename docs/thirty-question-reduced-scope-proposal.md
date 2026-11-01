# Proposed 30-question reduced-scope amendment — not approved or implemented

November 1, 2026. Prepared only because the [five-context identity trial](report-identity-five-context-trial.md)
puts the full manual split-reconciliation scenario above the four-hour cap.
**Stop and wait for approval. No new reports/questions are selected here.**
The user has authorized neither implementation nor evaluation-data selection
under this proposal. Existing tagged preregistration snapshots remain unchanged.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Facts share nine contexts;
statistical independence is not established. Labels remain **provisional,
single-annotator**. Its report families remain excluded from any new study.

## Proposed changes requiring explicit approval

1. Reduce the evaluation stage from 50 questions/10 families to **30 questions
   across six new report families, five questions each**. Proposed mix:

   | Full | Partial | Missing | Genuine conflict | Total |
   | ---: | ---: | ---: | ---: | ---: |
   | 12 | 9 | 5 | 4 | 30 |

2. Keep **20 development questions across four other families**, five each,
   with the existing 8/6/3/3 mix and unchanged confidence-threshold calibration
   rule. This proposal has 50 total development/evaluation generations, cached
   once across all three policies, not 150 generations.
3. A question-count reduction alone cannot remove the requirement to reconcile
   unidentified TAT-QA excerpts. Therefore propose a **provenance-first bounded
   original-report corpus**, rather than claiming the full pinned TAT-QA excerpt
   collection has been reconciled. Candidate sources would be complete archived
   official issuer/regulator reports with explicit entity/period/version IDs;
   verified mirrors may archive the same report with their origin made explicit.
   TAT-QA may supply identity leads only. Newly authored questions must be direct
   extraction-answerable requests against this declared collection; they would
   not be reported as a native held-out TAT-QA benchmark.
4. This changes the corpus boundary: original reports would now be retrieval
   evidence, whereas the current approved plan uses them only as identity aids.
   It changes what can legitimately be labeled absent. It requires a new locked
   source manifest, gold scope, retrieval-packing/interface compatibility check
   and user approval before selection. No PDF ingestion or other implementation
   change is authorized by writing this proposal; `src/` remains frozen.

## Gates retained

- Recover the remaining four pilot context identities before selecting anything;
  conservatively exclude all nine pilot contexts' original report families,
  versions and near-duplicates. A smaller sample does not waive this gate.
- Freeze a named, complete source collection before constructing negatives.
  Do not delete rows/pages or omit resolving versions to create partial,
  missing or conflict cases. Scope ambiguity is not a genuine conflict.
- Require the 9 partial / 4 genuine-conflict opportunities for evaluation plus
  6 partial / 3 genuine conflicts for development, in disjoint eligible families.
  **No such yield has been established.** Whole reports may make absence harder
  to establish; genuine conflicts may still be unavailable. If the real-data
  quotas cannot be met, stop for another explicit amendment, not synthetic fill.
- Preserve seed 1729, source-only hash priorities, no system-output-based
  selection, shared question-only decomposition, identical retrieval/candidates,
  the approved 1.54B local model, verifier, contradiction policy and assessment
  schema. Calibrate on development data only, then freeze before evaluation
  selection. A new source format must not silently change the implementation.
- Preserve the original metric and risk definitions/tolerances as descriptive
  targets. With nine intended partial questions across at most six evaluation
  families, the original minimum of 15 partial-contributing families cannot be
  met. **No confirmatory hypothesis decision or tight comparable-risk claim is
  permitted.** Publish descriptive coverage/risk/failure counts and the sample
  limitations, not a claim of superiority or general enterprise performance.
- Proposed operational gates are **>=27/30 source-adjudicable cases**, **>=48/50
  scheduled development/evaluation generations completed** (the >=95% rule
  rounded up), and the unchanged **<=9 user annotation/review hours**. Retain
  unresolved cases and generation failures in reporting; no retries, convenient
  replacements or tuning. Any pre-inference loss of eligibility/quotas requires
  an amendment. No automatic extension back to 50/100 or score-based continuation
  is authorized. The old >=45/50 gate is replaced only if this proposal is approved;
  no run is approved merely by writing this document.
- A human second annotator must independently label **all 30 evaluation cases**
  before any paper results. This meets the retained 30–50-case requirement; hide
  primary labels and system outputs during source-gold review. If no reviewer is
  available, results remain internal/provisional. Report actual human agreement
  before adjudication; an LLM is not a substitute.

## Budget and interpretation

The existing four-hour identity/feasibility clock **does not restart**. Before
additional work, approve this corpus/scope change and the following bounded
identity/feasibility allocation: up to 15 minutes for four remaining pilot
identities, 60 minutes for ten new source-family provenance/archives, 90 minutes
for source-only quota feasibility, and 20 minutes for exclusion reconciliation
and reporting. This is **at most 185 additional work minutes**, further limited
by whatever remains on the original four-hour clock. Stop earlier when a gate
cannot be established; do not shift unused budgets to bypass a failed gate.
These are stopping budgets, not promises that the tasks will succeed. The
five-context trial measured report lookup only; it did not measure
complete-report curation, negative searches or genuine-conflict validation.
**Thirty questions are not yet proven to fit the remaining cap.** Stop if the
bounded corpus cannot be established within the approved remaining time.

The lower workload is 50 rather than 70 development/evaluation questions, about
29% fewer shared generations and primary question labels. This is a count-based
saving, not a measured annotation-hour or runtime guarantee. Full-report search
and absence judgments may offset it; do not promise a proportional reduction
from the previous 8–9 user hours. The agent performs provenance lookups; the user
approves scope and verifies genuinely ambiguous identities/labels when needed.

Interpret the eventual study as a small, deliberately stratified **bounded-
corpus extraction/abstention feasibility study conditional on the fixed local
answerer**. It would no longer evaluate the same TAT-QA-excerpt corpus as the
50-question preregistration. It cannot establish historical novelty, model-size
effects, population prevalence or reliable transfer to other document sets.
Changes in corpus completeness can change both answerability and retrieval
difficulty; comparisons with the constructed pilot or a future different corpus
must not be presented as controlled performance gains.

No data selection, label creation, source change, model run or push is performed
by this proposal. Approval is requested before any dependent work continues.
