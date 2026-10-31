# RAGSmith-Evidence — Phase 3 / Milestone 1

A **local-only ingestion pilot**, not a complete RAG system. All example content is synthetic.

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
- No FAISS, Knowledge Graph, LLM, sufficiency classifier, access control or cloud inference yet.
- File paths determine document identity; moving files produces new document IDs.
- Repeated ingestion appends to the audit manifest, but replaces evidence for that path in SQLite.
- Avoid sensitive documents until access controls and encryption are implemented.
- Only ingest documents you have permission to process.

## Next milestone

Add PDF table extraction, OCR fallback, format-aware chunking, table SQL materialization, quality checks and benchmark corpus manifest.
