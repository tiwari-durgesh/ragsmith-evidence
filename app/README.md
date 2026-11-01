# Local API demo

Run from `C:\Users\YOUR_USERNAME\Desktop\ragsmith-evidence` in PowerShell. The
new `.venv-api` uses Python 3.12.14; the old `.venv` points to a missing Python
3.11 installation. Python 3.11 remains unverified.

## Start and send a request

The environment is installed and the six local pilot samples are prepared.
Start the API in one PowerShell terminal:

```powershell
Set-Location 'C:\Users\YOUR_USERNAME\Desktop\ragsmith-evidence'
.\.venv-api\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second PowerShell terminal:

```powershell
Set-Location 'C:\Users\YOUR_USERNAME\Desktop\ragsmith-evidence'
$demoBody = Get-Content -Raw app\example-request.json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/ask' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($demoBody)) | ConvertTo-Json -Depth 30
```

Interactive API: <http://127.0.0.1:8000/docs>. Health: `/health`. Six prepared
examples: `GET /samples`. To run one prepared sample:

```powershell
$demoSamples = Invoke-RestMethod 'http://127.0.0.1:8000/samples'
$pilotDemoBody = $demoSamples.cases[0].request | ConvertTo-Json -Depth 20
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/ask' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($pilotDemoBody)) | ConvertTo-Json -Depth 30
```

Stop servers with Ctrl+C. The later [Streamlit frontend](frontend/README.md)
imports the shared checked service directly; it requires neither this API server
nor the optional model server. Its local model remains off. The shared outer
request/response schema is in `app/contracts.py`; the frozen assessment is unchanged.

## Two explicitly different baseline modes

**`answerer: "lookup"` (default)** uses the frozen deterministic QA pipeline,
returns `decision`, `values`, numbered `citations`, `gap_explanation`, and the
frozen pilot's **extraction-only / binary sufficiency / graded sufficiency**
side by side. It requires no model process. The `baseline_family` field identifies
these as `frozen_pilot_baselines`. Packing counts use a conservative UTF-8-byte
upper bound plus a reserve, labeled as such, rather than fabricated exact tokens.

**`answerer: "local_llm"`** uses the approved local Qwen model once and compares
**never-abstain retrieve-and-answer / confidence-threshold abstainer / graded
sufficiency** on byte-identical packed evidence and cached candidates. Start the
fixed model server in another PowerShell terminal:

```powershell
Set-Location 'C:\Users\YOUR_USERNAME\Desktop\ragsmith-evidence'
.\.venv-api\Scripts\python.exe -m app.start_runtime
```

Then send a local-model demo request:

```powershell
$localDemo = Get-Content -Raw app\example-request.json | ConvertFrom-Json
$localDemo.answerer = 'local_llm'
$localDemoBody = $localDemo | ConvertTo-Json -Depth 20
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/ask' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($localDemoBody)) | ConvertTo-Json -Depth 30
```

The fixed local model, server and tokenizer already exist under the ignored
`data/evaluation/generated/local-smoke` directory. No API key, paid service,
external inference or automatic download/fallback is used. Server startup checks
the approved model/server SHA-256 and uses loopback, six CPU threads, one slot,
4,096 context, batch/microbatch 128, and the existing 64 MiB available-RAM / 6 GiB
working-set guards. The bridge checks the live model path, context, slots and
runtime build. A runtime failure stops the request; no generation retry or JSON
repair occurs. Standalone tokenization checks the whole prompt/chat envelope.

The **default 0.5 threshold is an uncalibrated demo constant**, fixed before the
synthetic integration check. It is exposed as `demo_confidence_threshold` and
never called a development-calibrated threshold or research result. No development
questions/labels were inspected. A real evaluation still needs authorized,
locked development labels, the preregistered threshold selection, and a separate
research runtime/corpus lock. The in-memory cache holds at most 32 successful
generations and is shared across demo policy comparisons, not durable research
evidence. Restarting the API clears it. Do not tune thresholds/prompts using pilot
results. `generation.inference_requests` is zero on cache hits.

Only graded answers have support-filtered verified citations. Never-abstain and
confidence baselines deliberately expose their generated claims/citations with
`citations_verified: false`; they may be wrong. Empty values are generation
failures, not successful never-abstain answers. Unsupported token spans are errors,
not permission to substitute self-reported confidence. Source lookup `assessment`
and `lookup_response` retain the frozen pipeline's output; in local-model mode
the separate `candidate_assessment` explains the model-policy decision. The API
adds an outer transport envelope without changing the production assessment schema.

## Adapter and packing scope

`scripts/tatqa_excerpt_ingestion.py` is separate from frozen `src/`. It accepts a
table/paragraph snapshot, never dataset question/gold files. It emits every
unambiguously bound numeric cell under an explicit, unique year header, preserves
original row/column/header/unit metadata and stable hashes, and retains unsupported
cells and prose. Blank/dash cells are not converted to zero or silently removed.
Financial punctuation normalization is fixed, with no rounding or unit conversion.
Literal source metrics remain literal; no question-specific aliases are generated.

Repeated labels under different sections/units, duplicate year columns, ragged
rows, segment qualifiers and unrepresentable labels remain unsupported. This is
intentionally a limited adapter, not a general table/parser repair effort. Names,
table hashes, fixed near-duplicate checks, transitive groups and the five-question
cap are tested on synthetic fixtures only; no dataset grouping/selection has run.

Queries use the existing FTS retriever with up to eight hits per requirement.
Merge deterministically by best requirement rank then evidence ID; the shared
packer takes a prefix of at most eight whole units within 3,200 input tokens,
including the entire prompt/chat envelope. Stop at the first unit that does not
fit; never clip a table/header or skip to favorable later hits. The response logs
included/omitted IDs and truncation. All policies see exactly that evidence;
retrieval or packing omission is not corpus truth. The 384-token output allowance
fits within the fixed 4,096 context. No research corpus is locked by this code.

## Six pilot-only samples and privacy

`python -m app.prepare_samples` reads **only** the existing pilot public source
packet and writes `data/evaluation/generated/demo-api/samples.json`, which is
ignored and not committed. It never reads human locked labels/private annotations.
The fixed choices are two full, two partial, one **existing controlled conflict**
and one empty-scope abstention. The controlled conflict copies the old pilot's
artificial alternative unchanged; **it is not a genuine report disagreement**.
These manually scoped pilot tables are demo fixtures, not the Option C corpus.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Its labels remain
**provisional, single-annotator**, and independence is not established. No data,
labels, model binaries, runtime logs or local API config are included in the
building commits. The API reads submitted tables into temporary local databases;
it does not authenticate a user-supplied table as an issuer filing. Source hashes
identify that submitted snapshot and citations identify its cells.

## Recreate the environment and run checks

If `.venv-api` is missing, use the installed bundled Python explicitly:

```powershell
Set-Location 'C:\Users\YOUR_USERNAME\Desktop\ragsmith-evidence'
& 'C:\Users\YOUR_USERNAME\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv-api
.\.venv-api\Scripts\python.exe -m pip install -e . -r app\requirements-lock.txt
.\.venv-api\Scripts\python.exe -m app.prepare_samples
```

The sample-preparation command needs the existing **local** pilot packet; a public
clone without it can still use `app/example-request.json` and the API. It will
return 404 from `/samples` until local samples are prepared; it never downloads
private data. Existing prepared samples are not overwritten automatically.

```powershell
.\.venv-api\Scripts\python.exe -m pytest -q
git diff --stat 1b0df45 HEAD -- src
```

Pytest collects only `tests/`, including every new ingestion test, avoiding ignored
third-party probe trees. No research data access, calibration or evaluation run is
part of these tests. The source-diff command must print nothing.
