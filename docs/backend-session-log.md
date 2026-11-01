# Backend session — November 2, 2026

Started 2026-11-01 20:32:03 UTC (November 2, 02:02:03 IST), at `84bbdff` on
`codex/public-progress`, clean. No new item after 02:02:03 UTC; stop 02:32:03 UTC.
Finish earlier when the queue is complete.

## Standing decisions

- Keep every `src/` byte frozen. Keep all preregistration, amendment and public
  manifest bytes unchanged; seven protected files snapshotted locally.
- No network/API/model execution, spending, push, branch/tag deletion or force.
- No real pool access before the LAST source-only feasibility count. No real
  development/evaluation question access, selection, labeling or calibration.
- Build reusable modules under `app/research/`; test synthetic fixtures and the
  existing pilot only. Threshold remains None outside synthetic unit checks.
- Preserve fixed source scopes, requirements and candidates across policies.
  Log failures without retries or silently dropping denominator entries.
- Source-only feasibility will not access upstream question/answer fields. Counts
  must distinguish machine leads from source-certified genuine opportunities.
  Unknown eligibility cannot be called successful quota feasibility.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Labels remain
**provisional, single-annotator**; independence is not established.

## Item 1 — corpus runner

Completed. One excerpt corpus, immutable snapshot/database verification, fixed
scope before lexical retrieval, shared decomposition/packing/candidates and
unchanged verification. Threshold remains None. Minimal outer-runner refactoring
exposes run_prepared; new logic is in app/research/corpus_runner.py.

Decisions: programmatic explicit-input interface, no default real-data CLI;
explicit answerer identity; content-addressed terminal success/failure cache;
exclusive generation claims; interrupted/corrupt cache fails closed, no retries;
operational cache counts outside logical result hashes; preparation failures stay
in denominators. No model determinism claim from synthetic tests.

Checks: full suite 729 passed in 14.73s, one existing Starlette/AnyIO warning.
Synthetic checks cover scope/distractors, two-source conflict, cache reuse/failure,
corruption/interruption, changed source/runtime, stable ordering and denominators.
Six existing pilot source inputs passed a deterministic lookup-stub compatibility
probe; repeated output hash identical and six cache hits. Stub scores are not model
confidence. No real pool access, inference, failed tests, reversions or scope cuts.

## Item 2 — selection tooling

Completed and tested only on invented candidates. Fixed seed 1729 and registered
stream names; source-only table/context/row/5-shingle and verified-name graph;
eight-family/name/pilot-table/retained-UID exclusions and transitive quarantine.
A sparse connectivity proof records links/rules/scores for exclusion auditing;
skipping already-connected pairs preserves the exact connected components and
reduces work without clearing flags. Tests compare components with the existing
pairwise implementation.

Exact lazy enumeration orders development group tuple, development case tuple,
evaluation group tuple then evaluation case tuple. It enforces 4/6 separate groups,
exactly five cases per group, 8/6/3/3 and 12/9/5/4 aggregate mixes, certified source
eligibility and no reused underlying facts. Case IDs derive from frozen anchors,
question-only requirements and final question. Pool hashes bind metadata as well
as IDs and the frozen source inventory. Pilot 3-shingle question screens accept
explicit input only; no actual pilot/new candidate questions were loaded for
selection tests. Real-pool selection was not run.

Decisions: a deterministic search-node cap fails as uncertified, never returns an
approximate draw or relaxes quotas. Reservation contains evaluation IDs privately
in memory; its development export omits them. Evaluation materialization requires
a matching locked development threshold, with None still unset. Source-certified
names must be explicitly supplied; generic names cannot create issuer edges.

Checks: full suite 738 passed in 13.98s, 738 passed in 13.90s after strict pool/lock
checks, and 738 passed after connectivity-proof audit changes. One existing
Starlette/AnyIO warning. Exact-order oracle and cap/uniqueness/quarantine/lock/
infeasibility tests passed. No real source pool access or selected IDs, no test
failures, reversions or scope cuts.

## Item 3 — labeling, locking, agreement and calibration tooling

Completed. Versioned source-only sheets contain question/requirements/context
snapshots, no assigned strata, system outputs or other annotator labels. Validators
check schema/allowed values/no nulls, unchanged inputs, raw cited cells/units,
provisional status and exhaustive absence-scan declarations. They validate format
and provenance, not semantic correctness of a human label. Locks refuse overwrite
and bind content/template/input/selection hashes; they are receipts, not signatures
or proof of independent annotation. Old pilot labels and reviewer-practice formats
were not rewritten or imported.

New explicit-file CLI supports validate/lock/agreement. Agreement reports raw
agreement and categorical Cohen's kappa before adjudication; degenerate kappa is
undefined, not a perfect-score claim. Synthetic annotators are never called human
IAA; independence is declared and must be established outside software.

The development-only routine requires 20 locked, non-pilot development cases and
matching selection hash; rejects unresolved source gold, missing cases, bad scores
and hidden generation failures. Fixed grid 0,0.1,...,1 plus always-abstain fallback;
<=1 unsafe question; maximize macro supported-requirement coverage, then fewer
unsafe questions, then higher threshold. Correctness requires reviewed value and
supporting cell/version/unit. Fractions implement exact coverage tie comparisons.
Generation failures stay in the 20-question denominator. No evaluation or pilot
calibration, global threshold setting or real threshold artifact was run/written.

Decision: macro per-question supported coverage follows the registered coverage
metric; uncertainty blocks calibration, rather than dropping cases. Added the
registered always-abstain sentinel to the outer runner so a future fallback can
be represented without infinity/NaN or changing the frozen policies. Default None
is still unset. All calibration calls in tests use fabricated twenty-case inputs;
no threshold chosen there applies to the project.

Checks: full suite 755 passed in 14.79s, then 756 passed in 14.91s including fallback
integration, then 756 passed after public interface type annotations. One existing
Starlette/AnyIO warning. No failed tests, reversions, real labels or scope cuts.

## Item 4 — freeze checklist

Completed docs/backend-freeze-checklist.md with exact committed-blob SHA-256 for
155 code/config/dependency/test/specification files, fixed model/server/tokenizer
pins, required private artifact inventory and pre-run checks. Checklist byte SHA-256
at this item: `601c8caf75cd58f0962b3f5e89e9215f508127544806fb1e3f12a75784828a82`. No existing public manifest changed.

Decisions: preserve two existing freezes (code/source pool before development
selection; threshold/runtime parents after locked development labels and calibration,
before evaluation materialization). Actual study source scopes, source-certified
question pool, labels and threshold are not created or falsely marked locked.
The final source-only feasibility tool has not yet been built; its code hash must
be appended as the final item before any future selection. Inventory uses Git blob
bytes and requires deployed-file hashes separately, avoiding CRLF ambiguity.
Historical demo runtime metadata is not upgraded to a research lock.

Checks: full suite 756 passed, one existing Starlette/AnyIO warning. No failures,
reversions, real pool access or scope cuts. The next and LAST queue item is the
source-only feasibility count; no later selection, calibration or model run follows.

## Item 5 — LAST: source-only feasibility count

Completed one pinned-training source-only count. Selective parser never decoded
upstream question/answer values. No official dev/test file, real question, upstream
gold, completed private label, selection function, model or calibration was used.
Before opening the training source, all synthetic parser tests and full suite
passed: 763 tests, 14.88s, one existing Starlette/AnyIO warning. Staged count-tool
and test blob hashes were appended to the engineering checklist before execution.

Count: 2,201 source contexts, 1,992 components, 124 contexts/42 components excluded,
2,077 contexts/1,950 groups surviving. Fixed name matches affected 41 contexts;
75 contexts were quarantined transitively only. Rule counts overlap.
Mechanical leads: 550 groups with at least two canonical fact leads; 202 with two
explicit-unit-bound fact leads; 15 within-context discrepancy groups, 16 groupwide
(overlapping). No exclusions were cleared, no case was authored or chosen.

Decision: do not turn leads into genuine question counts. No fixed partial absence
question/scope or genuine-conflict entity/period/unit/version adjudication was
performed under this count-only instruction. Thus zero opportunities are certified,
not proof that no opportunities exist. 9/4 evaluation and 6/3 development genuine
quotas, unique facts and joint allocation remain unverified: STOP, no selection.
If genuine shortage is later established, another amendment is required. See
backend-feasibility-count.md for counts and hashes. Its limitation is recorded,
not hidden by calling numeric discrepancies genuine conflicts.

No engineering queue item was cut. Genuine question-level yield certification
remains unresolved under the source-only count; it is not falsely marked complete.
No research work follows this count: only the mandated final regression, source/
protected-file checks, privacy scan, local commit and log finalization remain.

## End checks and disposition

No work continued past feasibility except mandated tests, privacy/source checks,
report/log finalization and the final local commit. No source/tool code changed
after the count. The real data was opened only by the source-only projection;
source bytes were checksum-verified, not loaded through the old gold/question
adapter. The numeric/group leads are not genuine-question labels. No additional
non-pilot issuer identities were certified, so later verified-name edges could
merge groups or expand quarantine. Current graph IDs are not a selection lock.

Full pytest record (every queue item checked):

| Item/run | Passed | Seconds |
|---|---:|---:|
| 1 corpus runner | 729 | 14.73 |
| 2 allocation | 738 | 13.98 |
| 2 strict metadata/lock | 738 | 13.90 |
| 2 connectivity audit | 738 | 14.06 |
| 3 label/calibration tools | 755 | 14.79 |
| 3 always-abstain integration | 756 | 14.91 |
| 3 interface types | 756 | 14.93 |
| 4 freeze checklist | 756 | 14.89 |
| 5 synthetic source-projection tests | 763 | 14.88 |
| 5 final regression after actual count | 763 | 14.92 |

Every run has the same one pre-existing Starlette/AnyIO deprecation warning.
No failed tests, test deletions or item reversions. Source diff from 1b0df45 is
empty; current src tree remains 3261c6087757b9f3d9aed1166e264de45ac4f479. All seven
protected document hashes still match. No original public manifest or amendments
were changed. The separate engineering checklist now includes the two final tool
files; its final byte SHA-256 is `d62f12bf24223e3fffc8a3a41dfe397fc9f2f620d9dd68c2a459caf140b29f70`.

Privacy scan: 222 tracked public text files, no credential-pattern
matches and no tracked private-label/model/.env file candidates. Three matching
local sensitive filenames remain ignored; contents were not opened. Old ignored
third-party dependency directories denied enumeration, so the ignored-file
inventory is explicitly incomplete; no permission bypass was attempted to inspect
those files. Raw source, corpus/cache snapshots, generated labels and the private
exclusion ledger remain uncommitted under ignored local storage. A final staged
filename/credential recheck follows before the local commit.

Local item commits: b854d8b (runner), 470900c (selection tools), 5d4c1a6
(label/calibration tools), 6fc6242 (freeze checklist), followed by the final count/
checks commit. Branch remains codex/public-progress; no push, force, ref deletion,
money, external API, model startup or project threshold write occurred.

Finished: all engineering tools and checklist, plus a mechanical source-only
feasibility inventory. Cut/unfinished: genuine question-level yield is **not
certified**; no claim that 9/4 or 6/3 exist or do not exist. The current research
feasibility gate remains blocked, and the session stops rather than selecting
questions, treating discrepancy leads as conflicts or changing the plan.

Final checks recorded at 2026-11-01 21:03:53 UTC (November 2, 02:33:53 IST),
31m50s after start; final bookkeeping/commit only thereafter, well within the
six-hour cap. Queue finished early; no new tasks or retries are started.
