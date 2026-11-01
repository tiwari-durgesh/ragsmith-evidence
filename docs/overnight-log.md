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

## Item 4 — documentation

Completed: current root README with exact Windows setup/launch/API commands,
`docs/architecture.md` with Mermaid, `docs/project-status.md` separating built,
tested/unproven and every remaining research gate, one-page professor summary,
and updated sidebar/tabs demonstration script and app guides. Historical
research/roadmap documents remain preserved, not rewritten as current evidence.

Decisions: list calibration after authorized development selection and locked
labels because those are dependencies, not a new preregistration order. Explicitly
distinguish the runner's unset threshold from the older API's optional demo
constant. Preserve the 30–50 second-human gate and current all-30 evaluation
review requirement. Do not imply that a working UI establishes novelty, hybrid
retrieval effectiveness, risk guarantees or real-data compatibility.

Checks: full suite 720 passed, one existing Starlette/AnyIO warning; relative
links in current docs verified. No failures, cuts or modifications to protected
documents. Setup/install commands were documented, not executed; no registry or
external API access occurred in this session.

## Item 5 — final checks and screenshots

Completed. Ten PNGs in `docs/screenshots/` cover synthetic input/results, citation
focus, parse failure, projector mode and explanation pages. All are 1280x720
browser captures, 670,766 bytes total, checked as readable PNGs. No private primary
labels, new research questions or model outputs from external services appear.
The sidebar navigation label does not describe the pasted synthetic input.

Browser checks found and fixed numeric wrapping in projector mode and a tab reset
caused by conditional element insertion. Numeric data cells now scroll rather than
split values; display toggles preserve tab element order. No policy, prompt,
retrieval order, numeric source value or budget changed. Both themes were checked;
original system theme and display toggle restored. One browser checkbox locator
timed out; the visible native browser control worked and verified the setting.
No product failure was hidden or tuned away.

The final six-case UI smoke used only existing pilot inputs through the new shared
bridge: all six completed with zero inference calls, including the visible
controlled-conflict truncation warning (3,016 conservative input units, one omitted
unit). The earlier pilot has **18 independent source facts and 36 derived cases;
no statistical or performance claims are made from it**. Labels remain
**provisional, single-annotator** and question independence is not established.
The separate stub runner's incomplete candidates remain recorded failures.

Security/privacy checks: 208 tracked public text files scanned before screenshots;
no credential-pattern matches and no tracked model/.env/private-label filename
candidates. Three matching ignored local model/label filenames were inventoried
without reading their contents. Some old ignored third-party probe dependency
directories denied enumeration; the inventory is not a complete audit of all
ignored files. No attempt was made to read private annotations or new corpus
questions. No actual credentials or labels were printed. Protected-file byte hashes
matched the seven starting snapshots (preregistration/amendments/public manifest).
The frozen src tree and source diff were checked unchanged.

A prior demo process occupied localhost:8501. Only exact-identified Streamlit Python
processes were restarted. PowerShell Stop-Process returned an internal null-reference
error on the second restart; stopping the same verified PIDs through the standard
.NET process API released the port. No network/security settings were changed.
The final local demo was stopped to free RAM; no model server was started.

### Complete pytest record

| Queue item / run | Result | Duration | Warning |
|---|---|---|---|
| 1: redesign | 695 passed | 26.65s | Existing Starlette/AnyIO deprecation |
| 1: theme/header fixes | 695 passed | 24.62s | Same |
| 2: contracts/runner | 720 passed | 19.24s | Same |
| 2: failure handling | 720 passed | 17.58s | Same |
| 3: reviewer kit | 720 passed | 16.93s | Same |
| 4: documentation | 720 passed | 17.19s | Same |
| 5: initial final checks | 720 passed | 16.45s | Same |
| 5: projector/tab fixes | 720 passed | 17.49s | Same |

No pytest failures, removed ingestion tests or reverted items. Extra checks:
practice JSON/blinding/blank return, documentation links, all PNGs, shared-service
six-case UI smoke, schema equality and clean-diff whitespace checks passed.
AppTest's standalone ScriptRunContext notices are expected and not application
exceptions. No performance evaluation, inference or calibration was run.

### Commits and scope

- `bee46b3`: frontend redesign.
- `6395ae3`: explicit-input runner and shared transport contracts.
- `a0581c9`: synthetic reviewer kit.
- `4e723a7`: current documentation, architecture and professor summary.
- Final-check commit: screenshots, presentation fixes and this completed log.

No requested item was cut. The runner remains deliberately a skeleton with no
real-data loader, batch scoring or calibration implementation; this is its
requested scope, not evidence that research gates are complete. No PDF parser,
new model, external service, new corpus or unrequested diagnostics were added.
No preregistration/amendment/public-manifest changes, src changes, branch/tag
changes, push, money spent or external API calls. All commits are local on
`codex/public-progress`.

### Exact Windows launch command

The environment is already installed and prepared samples are local:

```powershell
Set-Location 'C:\Users\YOUR_USERNAME\Desktop\ragsmith-evidence'
.\.venv-api\Scripts\python.exe -m streamlit run app\frontend\streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Open http://127.0.0.1:8501. No API/model server is needed. Local model stays off.
Stop with Ctrl+C. No packages were downloaded during this overnight session.

Queue complete; stopping early as authorized, rather than starting additional
work to fill the time allowance. Final stopped timestamp and verification follow.

Finalization recorded 2026-11-01 20:16:24 UTC (November 2, 01:46:24 IST),
27 minutes 7 seconds after session start; queue finished well before the hard
stop. Remaining activity is only the final local commit and clean-status/source
verification. The current PROJECT_STATE also points to the new status/log so
historical validation counts are not mistaken for current readiness.
