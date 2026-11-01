# Local Streamlit prototype

The frontend imports the existing `app.service.answer` directly. One process is
enough; no FastAPI or model server is required. It forces `answerer="lookup"`.
The local model is off and there is no external inference API or API key.

## Launch on this Windows machine

The prepared sample packet already exists locally. In PowerShell:

```powershell
Set-Location 'C:\Users\YOUR_USERNAME\Desktop\ragsmith-evidence'
.\.venv-api\Scripts\python.exe -m streamlit run app\frontend\streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Open <http://127.0.0.1:8501>. Stop with Ctrl+C. Telemetry is disabled in this
command. Do not start the optional local model for this demonstration.

Choose one of six pilot cases, inspect the question and explicit requested facts,
then click **Run**. Numbered citations focus source cells, outlined in blue.
Green cells support the graded answer; amber cells are baseline references and
are not verified support. The three cards compare the frozen extraction-only,
binary and graded pilot policies on identical retained evidence. No scores or
new research baseline results are presented.

The optional paste tab accepts a rectangular JSON array of string cells, with
explicit unique year columns in its first row, and a JSON list of requested
facts. For example:

```json
[{"requirement_id":"revenue","metric":"Revenue","year":2025}]
```

```json
[["Metric","2025"],["Revenue","10"]]
```

Invalid JSON, ragged rows and unsupported headers produce a plain error.
Header repair is unsupported. Changing an input hides stale results until Run.
All supplied strings are escaped before source/answer HTML rendering.

## Recreate dependencies and samples

Python 3.12.14 is tested; Python 3.11 remains unverified. With an existing
Python 3.12 virtual environment:

```powershell
.\.venv-api\Scripts\python.exe -m pip install -e . -r app\frontend\requirements-lock.txt
.\.venv-api\Scripts\python.exe -m app.prepare_samples
```

Sample preparation requires the existing local pilot public-source packet.
It does not read private human labels or download data. Samples remain ignored
and uncommitted. A public clone without that packet still supports the paste tab
with the synthetic defaults; it shows a clear message for unavailable samples.
The frontend lock describes the tested combined backend/frontend environment;
the earlier backend-only lock remains its historical snapshot.

## Demo and boundaries

Use [the four-case demonstration script](DEMO_SCRIPT.md). The in-app Limitations
tab displays [the one-page limitations](limitations.md).

**Prototype. Provisional pilot only. No performance claims.** The prior pilot
has **18 independent source facts and 36 derived cases; no statistical or
performance claims are made from it**. Labels are **provisional,
single-annotator**. Question independence is not established. The conflict is
a **controlled test case** using an existing artificial alternative value.
No evaluation/development data is selected or loaded, and no tuning is performed.

Checks use synthetic inputs. Run the complete regression suite from the root:

```powershell
.\.venv-api\Scripts\python.exe -m pytest -q
git diff --stat 1b0df45 HEAD -- src
```

The source-diff command must print nothing.

Validation on November 2: **695 tests passed**, with the existing Starlette/AnyIO
deprecation warning. The 26 frontend checks cover synthetic six-case interactions,
source-cell mapping, escaped HTML, stale-result hiding, parse errors and forced
model-off behavior. All six actual prepared pilot cases also ran through the UI
with zero inference requests. Browser inspection checked full, partial,
controlled-conflict and abstain displays, the limitations tab, and a citation
click focusing the exact source cell. The controlled conflict displays a packing
truncation warning; packing was not changed or tuned. No requested feature was
cut. The optional input tab is JSON-only, with header repair unsupported.
