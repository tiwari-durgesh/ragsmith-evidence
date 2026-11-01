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
