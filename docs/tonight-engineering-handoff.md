# Local engineering handoff for the next frontend session

November 2, 2026 IST (November 1 UTC). Work uses synthetic or already constructed
pilot material only. No evaluation/development questions were selected, inspected
or labeled, and no research corpus was locked. No verifier, contradiction-policy
or assessment-schema changes were made. Python 3.11 remains unverified; the new
ignored `.venv-api` uses bundled Python 3.12.14.

## Step 0 completed before building

Started clean on `codex/public-progress` at `b5ffc6f`, not local private `main`.
Verified the exact Option C amendment Git-blob SHA-256 and manifest value:

`78eca0bab6ce0f21c4310dc44508b2f4f09cada0a48778ce17260ad79c56c3d2`

The outgoing range was exactly these four commits:

| Commit | Files changed, all under `docs/` |
| --- | --- |
| 297d260 | roadmap.md; report-identity-five-context-trial.json/.md; report-identity-trial-exclusions.json; thirty-question-reduced-scope-proposal.md |
| 79d66f2 | roadmap.md; preregistration-public-manifest.json; report-identity-remaining-four.json; report-identity-trial-exclusions.json; one-report-ingestion-probe.json; thirty-question-reduced-scope-amendment.md |
| ed76304 | roadmap.md; corpus-options-after-html-probe.md; sec-html-ingestion-probe.json |
| b5ffc6f | roadmap.md; option-c-excerpt-corpus-amendment.md; preregistration-public-manifest.json |

Scanned 17 document versions across 12 distinct paths, including JSON field
checks, populated-secret/private-path patterns and private-annotation ancestry.
The JSONs contain source provenance/exclusions or aggregate probe diagnostics,
not question-level gold/answers. No suspicious labels, annotations, datasets,
model binaries, keys, `.env` or local config found. The pre-push hook was read
and left unchanged; the actual push executed it normally.

The first sandboxed `ls-remote` could not connect. The single authorized push
with network permission succeeded using:

```powershell
git -c push.followTags=false push origin b5ffc6fdbb7b444148887f714e7fec7a8d6ae442:refs/heads/main
```

It fast-forwarded origin/main from `8fd4cea` to
**`b5ffc6fdbb7b444148887f714e7fec7a8d6ae442`**. Verified with `git ls-remote`
and fetched both public files at that exact commit, recomputing the amendment
hash against the fetched manifest. No force push, private branch, tag push,
hook edit/bypass or building commit was included. No new tag was created.

## Implemented locally

- Separate `scripts/tatqa_excerpt_ingestion.py`: conservative source-cell
  canonicalization, stable snapshot/cell lineage, full source headers/units,
  financial signs, visible unsupported/blank cells, name/hash/near-duplicate
  helpers, transitive quarantine and five-total-per-group validation. No source
  alias inference or gold-selected extraction. All helper checks used synthetic
  fixtures, not a dataset screening run.
- `app/`: strict FastAPI transport with `/health`, `/samples`, `/ask` and OpenAPI
  `/docs`. Accepts question, requested facts and table; returns decision, values,
  numbered cell citations, gap explanations, source/packing audit and three
  explicitly named baselines. The outer API schema is new; frozen assessment
  output is retained inside it.
- Shared whole-unit packing: deterministic retrieved union, at most eight units,
  full 3,200-token input budget including prompt/chat template. Truncation is
  explicit. Lookup previews use a labeled conservative byte bound; local-model
  requests use the actual fixed tokenizer.
- Fixed loopback-only Qwen bridge: model/server hash checks, live model/build/
  context/slot checks, 384-token output cap, raw byte-span value-token likelihood,
  one cached generation shared across all policies, no retry/repair or remote
  model fallback. Start helper retains the prior memory guards and fixed settings.
- Six **existing pilot** inputs prepared locally: two full, two partial, one
  existing artificial/controlled conflict and one empty-scope abstention. No new
  alternative value or human label was authored; the controlled conflict is not
  a genuine-report-disagreement example. Samples remain ignored/local.

The API has two modes to avoid silently replacing the research baselines:

| Mode | Comparison |
| --- | --- |
| `lookup`, default/no model process | Frozen extraction-only, binary sufficiency, graded sufficiency pilot baselines |
| `local_llm`, explicit local server | Never-abstain retrieve-and-answer, confidence-threshold abstainer, graded sufficiency; same model candidates/evidence |

The local-model **0.5 demo threshold is uncalibrated**, fixed before the synthetic
integration check. No development gold exists or was inspected to calibrate it.
It must not be presented as the preregistered development-selected threshold.
Never-abstain/confidence outputs may include unsupported/uncited claims and mark
their citations unverified. Graded candidates go through the existing verifier,
aggregator, contradiction policy and support-citation filter. Conflicts still
suppress the entire graded question answer. No policies or prompts were tuned
to make samples pass.

## Validation and limits

**669 tests passed**, including 80 new ingestion/API/runtime checks; one dependency
deprecation warning, no remaining failures. The first root pytest invocation
tried to collect ignored third-party probe dependencies and encountered nine
Windows permission errors. Added `testpaths = ["tests"]` in `pyproject.toml`,
retaining every actual test. The full suite then passed. New ingestion tests were
not reduced to meet the time budget.

One synthetic local-model integration request completed in **22.64 seconds**,
with **563 input tokens**, valid raw value-token likelihoods and one generation
feeding all three research demo policies. This is a capability check, not a
latency/performance claim. No pilot local-model run, calibration, evaluation or
paid API occurred. The full prompt/runtime settings stayed fixed afterward;
later changes added fail-closed header/unit validation and server-setting checks.

All six prepared pilot lookup demos returned their expected controlled behavior:
full/full/partial/partial/abstain/abstain. These are demonstration outcomes, not
research scores. A real HTTP Uvicorn check returned health `ok`, two values/two
citations/three baselines on the synthetic example, and six available samples.
Both local servers were stopped after checks to release RAM/ports.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Its labels remain
**provisional, single-annotator** and question independence is not established.
Option C still prohibits independence/generalization claims and requires a human
second annotator for all 30 evaluation cases before paper results.

## Cut/deferred and next work

General merged/multi-level/segment-header repair, automatic unit aliases,
automatic requirement decomposition and general PDF/HTML ingestion are not built.
They would exceed a bounded two-hour component and remain explicitly unsupported
instead of guessed. No PDF table parser was built. No frontend, authentication,
uploads, deployment or new research reporting/partition framework was added.

Research corpus/group selection, genuine partial/conflict feasibility, source-gold
annotation, development threshold calibration and a paper/runtime/corpus lock
remain unrun. A demo runtime manifest is an engineering integrity record only,
not research-ready certification. The 12/9/5/4 and 8/6/3/3 mixes and genuine-quota
stop rules remain unchanged; no data or counts are invented to make them feasible.

Tomorrow's requested frontend can use the existing local API and samples endpoint.
Exact Windows launch and test commands are in [app/README.md](../app/README.md).
Code and environment lock files are local building commits only; **do not push
them tonight**. Original local `main` and private/public preregistration tags are
unchanged. The required final check is:

```powershell
git diff --stat 1b0df45 HEAD -- src
```

It must print nothing. Frozen source tree remains
`3261c6087757b9f3d9aed1166e264de45ac4f479`.
