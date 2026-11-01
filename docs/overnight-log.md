# Overnight engineering log — November 2, 2026

Session started 2026-11-01 19:49:17 UTC (November 2, 01:19:17 IST).
Do not start a new item after 02:19:17 UTC; hard stop 02:49:17 UTC.
Finish earlier when the queue is done. Branch: `codex/public-progress`.
Initial commit: `c582a41`. Initial working tree clean.

## Constraints and autonomous decisions

- Frozen `src/` tree: `3261c6087757b9f3d9aed1166e264de45ac4f479`.
- No evaluation/development question access, sampling, labels or calibration.
- No preregistration, amendment or public manifest edits. No push or paid/external
  API calls. Browser checks use localhost only; no new package downloads.
- Use installed Streamlit and the direct service bridge. Keep the model off in
  the UI. Settings affect presentation only, never evidence/policies.
- New evaluation scaffolding will be import-only, explicit-input, with no corpus
  loader, calibration/search function or enabled real-data CLI.
- Keep reviewer worked examples separate from the blinded practice/return files.
  Examples explain labels; practice materials must not disclose conditions/keys.
- Log test results after each queue item; stop/revert an item if unresolved
  failures exceed 20 minutes. Commit only public code/docs/synthetic fixtures.

## Item 1 — frontend redesign

Completed. Sidebar case selection and display settings; source/result workspace;
accessible decision icons/colors; citation chips; comparison cards; explanatory
tabs. No policy or source changes.

Item 1 checks: full suite passed twice, 695 tests each run (26.65s and the
subsequent 24.62s run); one existing Starlette/AnyIO
deprecation warning. Browser inspected all five tabs, lookup results, citation
chips, light and manually selected dark theme. Fixed a clipped header and dark
panel contrast. No unresolved failures, reverts, tuning or scope cuts.
The previous demo process held port 8501; identified its exact Python command
and restarted only that local demo. No system/network settings changed.

## Item 2 — engineering finish

Completed in new `app/contracts.py`, `app/checked_service.py` and
`app/evaluation_runner.py` modules. Minimal wiring changes in existing `app/main.py`
and frontend `view.py` use the shared checked bridge. This is the recorded safe
interpretation of "new modules only": new logic lives in separate modules;
existing entry points need imports/decorators to actually share that logic.
`src/`, policy behavior, threshold calibration and research schemas are unchanged.

The runner explicitly requires an answerer; it has no file/corpus loader or CLI.
The confidence threshold defaults to None, with `not_run_uncalibrated` and no
confidence decision. No calibration routine was built. Synthetic numeric thresholds
are interface test values only. Preparation failures still raise; a future batch
executor must preserve their denominators. This is a skeleton, not research-ready.

Checks: full suite 720 passed (19.24s), then 720 passed after failure-handling
hardening; one existing Starlette/AnyIO warning. New tests cover schema parity,
broken references, malformed grids, request overflow, truncation logging, candidate
validation and shared generation. Six existing pilot sources were probed using a
deterministic lookup stub: 2 complete, 4 incomplete/generation-failed; the latter
remain failures, not successful abstentions. Fabricated zero stub confidence is
not a model result. No model execution, inference endpoint or threshold was used.
No unresolved failures, tuning, reverts or scope cuts.

## Item 3 — reviewer kit

Completed: 422-word one-page guide, engineering-student glossary, five worked
synthetic examples, two opaque-ID synthetic practice cases, blank JSON return
and return instructions. The missing-label procedure records keywords and a
complete row/paragraph scan; ambiguous content stays unverified.

Autonomous interpretation: worked examples necessarily explain their answers;
these are visibly separate training keys. The blinded practice source packet
and blank return contain no expected answers, assigned conditions, primary
labels, model outputs or confidence. No actual pilot/private label file was read.
Completed returns must stay private/uncommitted. Practice is not human agreement.

Checks: JSON parsed; case/requirement IDs match; practice keys are source-only;
all return labels/values/cells blank. Full suite: 720 passed in 16.93s, with one
existing Starlette/AnyIO warning. No failures, reverts or cuts.
