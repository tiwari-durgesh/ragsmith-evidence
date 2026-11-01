# RAGSmith Evidence

A local research prototype for evidence-sufficiency-aware table question
answering: inspect what the supplied evidence supports, return a supported subset
when possible, and explain gaps with source-cell citations.

**Prototype. Provisional pilot only. No performance claims.** The earlier pilot
has **18 independent source facts and 36 derived cases; no statistical or
performance claims are made from it**. Labels are **provisional, single-annotator**;
question independence is not established. The complete proposed hybrid system
and research evaluation remain unproven.

## Start the frontend on Windows

On the existing machine, the environment and six local pilot samples are ready:

```powershell
Set-Location 'C:\Users\YOUR_USERNAME\Desktop\ragsmith-evidence'
.\.venv-api\Scripts\python.exe -m streamlit run app\frontend\streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Open <http://127.0.0.1:8501>. No separate API/model server is needed. Stop with
Ctrl+C. The frontend imports the existing service directly and forces the local
model off. No external inference API, key or paid service is used. Telemetry is
disabled by the launch command.

Choose a case in the sidebar, inspect the explicit requested facts, and click
**Run**. The main workspace shows original source cells beside the graded result;
numbered citations focus their cells. Green indicates verified graded support;
amber indicates a baseline reference, not verified support. Cards compare frozen
extraction-only, binary and graded pilot policies. These are not research scores.
The conflict is a **controlled test case** with an existing artificial value.

The paste tab accepts rectangular JSON tables and explicit metric/year facts.
Header repair is unsupported. Further tabs explain the pipeline, limitations
and research hypothesis. **Projector text** changes display only.
Use the [four-case script](app/frontend/DEMO_SCRIPT.md).

## Fresh environment

Python **3.12.14 on Windows x64** is tested. Python **3.11 remains unverified**;
the old `.venv` points to an unavailable interpreter. If Python 3.12 is installed:

```powershell
py -3.12 -m venv .venv-api
.\.venv-api\Scripts\python.exe -m pip install -e . -r app\frontend\requirements-lock.txt
.\.venv-api\Scripts\python.exe -m pytest -q
```

On this machine an alternative venv command uses the installed bundled Python:

```powershell
& 'C:\Users\YOUR_USERNAME\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv-api
```

The dependency command requires registry access when packages are not already
cached; it was not executed in the overnight session. The frontend lock describes
the tested combined environment; `app/requirements-lock.txt` is the older
backend-only snapshot. A public clone can use the synthetic paste-tab defaults.
Prepared samples require the existing local pilot public-source packet:

```powershell
.\.venv-api\Scripts\python.exe -m app.prepare_samples
```

That command never downloads data or reads private human labels. Samples remain
ignored and uncommitted. It is not required for the synthetic paste tab.

## API, architecture and tests

To use the separate local API:

```powershell
.\.venv-api\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/docs>. A synthetic request from PowerShell:

```powershell
$demoBody = Get-Content -Raw app\example-request.json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/ask' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($demoBody)) | ConvertTo-Json -Depth 30
```

The UI and API use `AskRequest`, `AskResponse` and one checked service bridge.
Separate ingestion adapts literal source cells into canonical rows, temporary
SQLite FTS retrieves evidence, and bounded packing feeds the frozen verifier and
policies. The default display uses a conservative token upper bound. The
[architecture diagram](docs/architecture.md) shows these boundaries.

An [import-only evaluation skeleton](app/EVALUATION_SKELETON.md) provides explicit
retrieval/answerer/candidate interfaces. Its confidence threshold is **unset**;
that baseline is not run until a threshold is explicitly supplied. Tests use
fabricated synthetic scores; no calibration or real model execution occurred.
The historical optional API local-model mode is separate and still has an
explicitly uncalibrated demo constant; the frontend does not expose that mode.

```powershell
.\.venv-api\Scripts\python.exe -m pytest -q
git diff --stat 1b0df45 HEAD -- src
```

**720 tests pass**, with one existing Starlette/AnyIO deprecation warning. These
are software checks, not evidence of research performance. The source-diff
command prints nothing; verifier, contradiction policy and assessment schema
remain frozen.

## Research status and review

[Project status and research gates](docs/project-status.md) distinguish built,
tested and unproven work. The [professor summary](docs/professor-summary.md) is a
one-page overview. The [reviewer kit](docs/reviewer-kit/guide.md) contains only
synthetic training examples and blinded practice forms. Completed reviewer
returns must stay private.

Unresolved report overlap is accepted under Option C; company-name/hash
checks cannot establish disjointness. No independence, generalization,
leakage-free, inferential superiority or novelty claims follow. Genuine
partial/conflict feasibility, authorized selection, independent source labels,
development-only calibration and a frozen research run remain gated. Human
second annotation of a 30–50-question subset is required before paper results;
under the current reduced plan that includes all 30 evaluation questions.
The LLM label cross-check was not run and does not substitute for human review.

No evaluation/development questions were selected, inspected or labeled during
the overnight work. No preregistration/amendment/public-manifest files or `src/`
were changed. Work is committed locally on `codex/public-progress`; no push.
See the [overnight log](docs/overnight-log.md).

Public history excludes private labels/case-level annotations; see
[publication provenance](docs/public-publication-history.md). Historical technical
guides remain available: [API/runtime](app/README.md),
[value lookup](docs/value-lookup.md), [retrieval](docs/retrieval-integration.md),
[Phase 4 assertions](docs/phase4-batch1.md), and
[original roadmap](docs/roadmap.md). Earlier counts and planned work in historical
notes reflect their dates; use the current status page for the present state.
