# RAGSmith-Evidence — Phase 4, Batch 1

A **local-only research prototype** with ingestion, lexical search, structured
evidence-sufficiency assessment, and an application-level assertion interface.
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

Phase 4 Batch 1 accepts explicit claims and caller-supplied evidence. It verifies
an expected value; it does not yet answer questions whose values are unknown.
Question text is retained for display, and the caller supplies the requirements.
`full` applies to those supplied claims, not to the completeness of the caller's
decomposition of the natural-language question.

See [the Batch 1 usage guide](docs/phase4-batch1.md) and the
[example request](configs/assertion_request.json). The existing Phase 3 report
is retained under `assessment` in a versioned application envelope. No existing
verification or contradiction policy changes in this batch.

## Next batches

Connect existing document retrieval to assessment, construct evidence-bounded
responses, then validate the complete workflow. A separate value-lookup path for
questions without expected values requires a decision before implementation.
Full hybrid retrieval, OCR, richer PDF tables, and research benchmarks remain
future work. Current automated tests establish software behavior, not research
superiority or novelty.
