# RAGSmith-Evidence — Phase 4 structured QA integration

A **local-only research prototype** with ingestion, lexical search, structured
evidence-sufficiency assessment, an assertion interface, and optional verified
value lookup with supporting citations.
All example content is synthetic. The complete hybrid RAG system and research
evaluation remain planned.

## Windows PowerShell setup

```powershell
cd ragsmith-evidence
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m pytest -q
python -m ragsmith.cli ingest-dir data/raw
python -m ragsmith.cli search "revenue"
```

If activation is blocked, run `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"` and use that Python executable for subsequent commands.

Python 3.11 is **unverified in this continuation**: the existing `.venv` refers
to an unavailable Python installation. The 379-test suite passed under bundled
Python 3.12.14 using the environment's existing packages. That does not establish
Python 3.11 compatibility or verify a fresh dependency installation.

## Your own files

Copy PDF, DOCX, XLSX, HTML or TXT documents into `data/raw` and run `python -m ragsmith.cli ingest-dir data/raw`.

## Data design

SQLite database: `data/processed/evidence.db`. Append-only ingestion audit manifest: `data/manifests/ingestion.jsonl`. Each evidence unit includes a stable content/version-derived ID, document ID, type, source locator, optional page, section, table and row, extraction method and structured metadata. The sample corpus contains no sensitive documents.

## Explicit limitations

- Native-text PDFs only; scanned PDF OCR is not yet implemented.
- PDF tables are text, not yet extracted into structured cells.
- XLSX assumes the first row is the header and reads cached formula values.
- HTML and DOCX tables use basic row/header extraction; complex merged cells are not supported.
- FTS5 lexical search is an initial diagnostic baseline, not the full hybrid RAG pipeline.
- Table row metadata is structured JSON in SQLite, not yet a relational SQL table query engine.
- Structured metric/year/value verification and full/partial/abstain decisions
  are implemented. Free-text verification, automatic requirement extraction,
  dense retrieval, Knowledge Graph retrieval, LLM generation, access control,
  and cloud inference remain unimplemented.
- File paths determine document identity; moving files produces new document IDs.
- Repeated ingestion appends to the audit manifest, but replaces evidence for that path in SQLite.
- Avoid sensitive documents until access controls and encryption are implemented.
- Only ingest documents you have permission to process.

## Application-level assessment

The Batch 1 assertion interface accepts explicit claims and caller-supplied
evidence. It verifies a supplied expected value.
Question text is retained for display, and the caller supplies the requirements.
`full` applies to those supplied claims, not to the completeness of the caller's
decomposition of the natural-language question.

See [the Batch 1 usage guide](docs/phase4-batch1.md) and the
[example request](configs/assertion_request.json). The existing Phase 3 report
is retained under `assessment` in a versioned application envelope. No existing
verification or contradiction policy changes in that interface.

## Optional value lookup

`ragsmith.lookup_pipeline.assess_lookup_question` accepts explicit metric/year
requirements without expected answers. Its separate discovery module extracts
candidates from supported table rows and passes every candidate through the
unchanged verifier against all supplied evidence in scope. Conflicts still cause
abstention. Supported values appear in `answers` with support-only provenance
citations; the unchanged assessment schema retains examined evidence for auditing.

Load `LookupConfig.from_file(Path("configs/lookup-enabled.json"))` to enable
discovery, or use `configs/lookup-disabled.json` to disable it with identical
inputs. The default is disabled. The effective config is recorded in each result.
See the [value lookup guide](docs/value-lookup.md) for a runnable example,
status definitions, scope constraints, and ablation limitations.

In the new lookup path, `missing` means no matching candidate was found in
supplied interpretable evidence in scope. `unverified` means evidence could not
be interpreted or discovery was disabled. Missing evidence in a retrieved set
does not prove the answer is absent from the corpus. Legacy assertion behavior
remains unchanged for compatibility.

## Answer from ingested documents

The new `ask` command reads the existing SQLite evidence database without
modifying it. It retrieves candidates for each explicit metric/year requirement,
preserves structured metadata, deduplicates evidence IDs, and passes the evidence
union to verified value lookup.

With a working project Python, run the included synthetic report example:

```powershell
python -m ragsmith.cli ingest data/raw/sample_report.html
python -m ragsmith.cli ask configs/database_question.json --lookup-config configs/lookup-enabled.json --top-k 10
```

Add `--format text` for a deterministic answer with numbered sources and explicit
missing/unverified-information explanations. JSON remains the default and now
includes the same presentation under `response`; `assessment` is unchanged.
When the decision is to abstain, no factual values or supporting answer citations
are rendered. Truncated retrieval is explicitly identified in the response.

Answers and citations are under `answers`; scores, source paths, document scopes,
and truncation flags are under `retrieval`. The example supports revenue and
operating profit but does not support employee count. Depending on other indexed
content, the employee requirement may be `missing` or `unverified`. Explicit
document scopes can restrict queries to the intended documents before top-k.

This is SQLite FTS5 lexical retrieval with BM25 ranking, not the full planned
hybrid retriever. Truncation may hide supporting or conflicting evidence, and
`full` describes retrieved-evidence sufficiency only. See the
[retrieval guide](docs/retrieval-integration.md) for scope and integrity limits.

## Phase 4 completion and remaining research

The scoped structured QA flow is implemented and tested: ingestion, retrieval,
value discovery, requirement verification, sufficiency assessment, and
deterministic responses with supporting citations. See the
[completion record](docs/phase4-validation.md) for validation and limitations.
Lookup accepts either caller-supplied evidence or database retrieval results.
Automatic natural-language decomposition is not implemented.
Full hybrid retrieval, OCR, richer PDF tables, and research benchmarks remain
future work. Current automated tests establish software behavior, not research
superiority or novelty.

## Current minimal pilot

The revised pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from this pilot**. The facts share nine
contexts and are not asserted statistically independent. All labels remain
**provisional, single-annotator**. See the [short labeling guide](docs/minimal-pilot.md)
and [provisional results table](docs/pilot36-results.md). The user's 18 judgment
labels are complete; construction determines the other 18. Pipeline/baselines are frozen at
`1b0df45c5e5fe443c5dd8be463ccf26dd9463de3`; src must remain unchanged through results.
One human-only pilot run completed: case-label matches were 18/36 extraction-only,
27/36 binary and 36/36 graded. No tuning or dataset-derived reference scores were
used. The LLM cross-check and comparison were explicitly skipped; no external API
was called and no alternative model substituted. See the [failure list](docs/pilot36-failures.md).
A [human second annotator](docs/roadmap.md) for 30–50 questions is required before
paper results; the auxiliary LLM is not human inter-annotator agreement.

## Phase 5 synthetic evaluation foundation

The initial offline harness compares extraction-only, binary sufficiency, and
graded sufficiency on identical frozen evidence. It opens gold labels only after
inference. All fixture/pilot labels remain `provisional, single-annotator` until
independent review; synthetic results are not research findings. The foundation
suite now has 589 passing tests under bundled Python 3.12.14. Python 3.11 remains
unverified.

The [preparation guide](docs/evaluation-preparation.md) covers native SQLite
ranking export and reviewer calibration packets. Exports use one frozen database
snapshot, preserve retrieval audits and check evidence fingerprints. Reviewer
templates contain blank labels; private identifier mappings stay with the
coordinator. Neither preparation path reads gold or changes annotation status.

With a working project Python and the package installed:

```powershell
python scripts/evaluate_synthetic.py
python scripts/annotation_agreement.py reviewer_A.jsonl reviewer_B.jsonl
python scripts/audit_tatqa.py --fetch --output docs/tatqa-scope-audit.json
```

The agreement command requires actual independent label files; no real reviewer
labels are provided. Only the audit's `--fetch` option accesses the network.
Raw upstream data stays in ignored local storage. See the
[evaluation protocol](docs/phase5-evaluation-proposal.md),
[source/license audit](docs/corpus-selection.md),
[research claim mapping](docs/research-claim-mapping.md),
[sampling plan](docs/pilot-sampling-plan.md), and
[reviewer handout](docs/annotation-guidelines.md).

Evaluation version 0.2 adds typed gold/frozen-evidence records and a required
versioned source-lineage manifest. It rejects stale evidence fingerprints,
malformed records, invalid parent graphs and out-of-scope gold links before
scoring. See the [record schema and migration guide](docs/evaluation-records.md).
These are internal consistency checks, not source authentication or annotation
adjudication. Report version 0.3 additionally supports frozen-ranking Track B,
retrieval metrics, paired source-cluster intervals, and optional Python-allocation
profiling:

```powershell
python scripts/evaluate_synthetic.py --rankings data/evaluation/fixtures/rankings.jsonl --k 1 --profile-memory
```

Gold retains the full source scope when top-k evidence is missed. The one-family
synthetic suite correctly reports null inferential intervals. See the
[metrics and resource guide](docs/evaluation-metrics-and-resources.md) for
estimands, exclusions, timing boundaries and profiling limits.

The [TAT-QA source adapter](docs/tatqa-source-adapter.md) prepares source cells,
separate coordinator annotation aids, complete screening ledgers and a draft
grouped review queue offline. The pinned training split has 1,462 label-gate
questions and 355 candidate paired contexts. Semantic eligibility and original
report identities remain pending; no real pilot has been selected or scored.

```powershell
python scripts/screen_tatqa.py --output data/evaluation/generated/tatqa-screening-001
```

[Manual cell binding](docs/manual-cell-bindings.md) adds strict provisional
accept/reject/pending decisions, source/question hash checks and explicit
metric/year/unit/value cell provenance. Accepted bindings generate canonical
candidate evidence for the existing lookup verifier. Templates remain pending;
no real acceptance labels, complete retrieval corpus or final pilot are created.

[Pilot family construction](docs/pilot-family-construction.md) adds provisional
report declarations, transitive duplicate/report grouping and four controlled
evidence conditions per draft family. Connected report groups share a proposed
partition. Synthetic cases are tested; real templates remain pending and no
pilot gold or model scores are generated.

The [resource trial runner](docs/resource-trials.md) measures fresh-process first
passes and warmed repetitions, with OS process RSS, raw timings and descriptive
summaries. Optional SQLite retrieval is measured against one fixed snapshot.
OS cache state is uncontrolled; synthetic diagnostics are not pilot benchmarks.

```powershell
python scripts/measure_resources.py --output data/evaluation/generated/resource-diagnostic-001
```
