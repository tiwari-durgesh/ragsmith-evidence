"""Local-first provenance-preserving ingestion and SQLite lexical search."""
import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass, asdict
from .evidence.models import Evidence
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED = {'.pdf', '.docx', '.xlsx', '.html', '.htm', '.txt'}

def _clean(x):
    return ' '.join(str(x).split()) if x is not None else ''

def parse(path: Path):
    ext = path.suffix.lower()
    if ext == '.txt':
        text = path.read_text(encoding='utf-8').strip()
        if text: yield ('text', text, 'text:body', None, None, None, None, 'utf8', {})
    elif ext == '.pdf':
        import fitz
        with fitz.open(path) as doc:
            for page_num, page in enumerate(doc, 1):
                text = page.get_text('text').strip()
                if text: yield ('text', text, f'page:{page_num}', page_num, None, None, None, 'pymupdf', {})
    elif ext == '.docx':
        from docx import Document
        doc = Document(path)
        heading = None
        for idx, paragraph in enumerate(doc.paragraphs, 1):
            text = _clean(paragraph.text)
            if not text: continue
            if paragraph.style and paragraph.style.name.lower().startswith('heading'): heading = text
            yield ('text', text, f'paragraph:{idx}', None, heading, None, None, 'python-docx', {})
        for ti, table in enumerate(doc.tables, 1):
            rows = [[_clean(cell.text) for cell in row.cells] for row in table.rows]
            if not rows: continue
            headers = rows[0]
            for ri, row in enumerate(rows[1:], 2):
                cells = {(headers[i] or f'column_{i+1}'): value for i,value in enumerate(row) if i < len(headers)}
                yield ('table_row', '; '.join(f'{k}: {v}' for k,v in cells.items()), f'table:{ti}/row:{ri}', None, None, f'table:{ti}', ri, 'python-docx', {'cells': cells, 'headers': headers})
    elif ext == '.xlsx':
        from openpyxl import load_workbook
        wb = load_workbook(path, read_only=True, data_only=True)
        try:
            for ws in wb.worksheets:
                iterator = ws.iter_rows(values_only=True)
                first = next(iterator, None)
                if first is None: continue
                headers = [_clean(v) or f'column_{i}' for i,v in enumerate(first, 1)]
                for ri, row in enumerate(iterator, 2):
                    if all(v is None for v in row): continue
                    cells = {headers[i]: _clean(v) for i,v in enumerate(row) if i < len(headers)}
                    yield ('table_row', '; '.join(f'{k}: {v}' for k,v in cells.items()), f'sheet:{ws.title}/row:{ri}', None, None, f'sheet:{ws.title}', ri, 'openpyxl', {'cells': cells, 'headers': headers})
        finally: wb.close()
    elif ext in {'.html', '.htm'}:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        for tag in soup(['script','style','nav']): tag.decompose()
        for ti, table in enumerate(soup.find_all('table'), 1):
            rows = table.find_all('tr')
            if not rows: continue
            headers = [_clean(c.get_text(' ', strip=True)) for c in rows[0].find_all(['td','th'])]
            for ri, row in enumerate(rows[1:], 2):
                values = [_clean(c.get_text(' ', strip=True)) for c in row.find_all(['td','th'])]
                cells = {(headers[i] if i < len(headers) and headers[i] else f'column_{i+1}'): v for i,v in enumerate(values)}
                if cells: yield ('table_row', '; '.join(f'{k}: {v}' for k,v in cells.items()), f'table:{ti}/row:{ri}', None, None, f'table:{ti}', ri, 'beautifulsoup', {'cells': cells, 'headers': headers})
            table.decompose()
        text = soup.get_text(' ', strip=True)
        if text: yield ('text', text, 'html:body', None, None, None, None, 'beautifulsoup', {})
    else: raise ValueError(f'Unsupported file format: {ext}')

def connect(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    db.executescript('''
    CREATE TABLE IF NOT EXISTS documents(document_id TEXT PRIMARY KEY, source_path TEXT, sha256 TEXT, ingested_at TEXT);
    CREATE TABLE IF NOT EXISTS evidence(evidence_id TEXT PRIMARY KEY, document_id TEXT, document_version TEXT, kind TEXT, content TEXT, locator TEXT, page_number INTEGER, section_path TEXT, table_id TEXT, row_index INTEGER, extraction_method TEXT, metadata_json TEXT);
    CREATE INDEX IF NOT EXISTS evidence_document_idx ON evidence(document_id);
    CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts USING fts5(evidence_id UNINDEXED, content);
    ''')
    return db

def ingest(path: Path, db_path: Path, manifest: Path | None = None):
    path = path.resolve()
    if not path.is_file() or path.suffix.lower() not in SUPPORTED: raise ValueError(f'Unsupported input: {path}')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    doc_id = hashlib.sha256(str(path).encode()).hexdigest()[:24]
    units = []
    for kind,content,locator,page,section,table,row,method,metadata in parse(path):
        eid = hashlib.sha256(f'{doc_id}|{digest}|{kind}|{locator}|{content}'.encode()).hexdigest()[:32]
        units.append(Evidence(eid,doc_id,digest,kind,content,locator,page,section,table,row,method,metadata))
    if not units: raise ValueError('No extractable content (scanned PDFs need OCR, not yet implemented)')
    db = connect(db_path)
    now = datetime.now(timezone.utc).isoformat()
    try:
        with db:
            db.execute('INSERT OR REPLACE INTO documents VALUES (?,?,?,?)', (doc_id,str(path),digest,now))
            old = db.execute('SELECT evidence_id FROM evidence WHERE document_id=?',(doc_id,)).fetchall()
            db.executemany('DELETE FROM evidence_fts WHERE evidence_id=?', old)
            db.execute('DELETE FROM evidence WHERE document_id=?',(doc_id,))
            for u in units:
                db.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (u.evidence_id,u.document_id,u.document_version,u.kind,u.content,u.locator,u.page_number,u.section_path,u.table_id,u.row_index,u.extraction_method,json.dumps(u.metadata)))
                db.execute('INSERT INTO evidence_fts(evidence_id,content) VALUES (?,?)',(u.evidence_id,u.content))
    finally: db.close()
    record = {'document_id':doc_id,'source_path':str(path),'sha256':digest,'ingested_at':now,'evidence_count':len(units),'status':'ingested','license':'unspecified'}
    if manifest:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        with manifest.open('a',encoding='utf-8') as f: f.write(json.dumps(record)+'\n')
    return record

def search(db_path: Path, query: str, limit: int = 5):
    tokens = re.findall(r'[^\W_]+', query, flags=re.UNICODE)
    if not tokens: return []
    expression = ' OR '.join('"'+token+'"' for token in tokens[:20])
    db = connect(db_path)
    try:
        
        rows = db.execute(
            """
            SELECT
                e.evidence_id,
                e.document_id,
                e.document_version,
                e.kind,
                e.locator,
                e.content,
                e.page_number,
                e.section_path,
                e.table_id,
                e.row_index,
                e.extraction_method,
                bm25(evidence_fts)
            FROM evidence_fts
            JOIN evidence e ON e.evidence_id = evidence_fts.evidence_id
            WHERE evidence_fts MATCH ?
            ORDER BY bm25(evidence_fts)
            LIMIT ?
            """,
            (expression, max(1, min(limit, 100))),
        ).fetchall()

        fields = [
            "evidence_id",
            "document_id",
            "document_version",
            "kind",
            "locator",
            "content",
            "page_number",
            "section_path",
            "table_id",
            "row_index",
            "extraction_method",
            "score",
        ]

        return [dict(zip(fields, row)) for row in rows]

    finally: db.close()


def verify_source_integrity(db_path: Path, document_id: str) -> dict:
    """Check whether the source file matches its ingested version."""
    db = connect(db_path)

    try:
        row = db.execute(
            "SELECT source_path, sha256 FROM documents WHERE document_id = ?",
            (document_id,),
        ).fetchone()
    finally:
        db.close()

    if row is None:
        return {"status": "not_found", "document_id": document_id}

    source_path, expected_hash = row
    path = Path(source_path)

    if not path.is_file():
        return {"status": "missing", "document_id": document_id}

    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()

    return {
        "document_id": document_id,
        "status": "valid" if actual_hash == expected_hash else "modified",
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
    }

def verify_evidence_consistency(db_path: Path, evidence_id: str) -> dict:
    """Verify that evidence matches its stored document version."""
    db = connect(db_path)

    try:
        row = db.execute(
            """
            SELECT
                e.document_id,
                e.document_version,
                d.sha256
            FROM evidence e
            LEFT JOIN documents d
                ON e.document_id = d.document_id
            WHERE e.evidence_id = ?
            """,
            (evidence_id,),
        ).fetchone()
    finally:
        db.close()

    if row is None:
        return {
            "evidence_id": evidence_id,
            "status": "not_found",
        }

    document_id, evidence_version, document_hash = row

    if document_hash is None:
        return {
            "evidence_id": evidence_id,
            "document_id": document_id,
            "status": "document_missing",
        }

    return {
        "evidence_id": evidence_id,
        "document_id": document_id,
        "status": (
            "consistent"
            if evidence_version == document_hash
            else "version_mismatch"
        ),
        "evidence_version": evidence_version,
        "document_hash": document_hash,
    }
