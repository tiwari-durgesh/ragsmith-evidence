# Retrieval to verified answers

This batch connects the existing ingestion database to value lookup. The new
`ragsmith.retrieval` adapter opens the database read-only and preserves complete
evidence records, including metadata JSON. It does not change the legacy search
API, ingestion schema, assertion verifier, contradiction policy, or assessment
schema. No additional dependency or model is introduced.

## Windows PowerShell example

Use a working project Python from the repository root:

```powershell
python -m ragsmith.cli ingest data/raw/sample_report.html
python -m ragsmith.cli ask configs/database_question.json --lookup-config configs/lookup-enabled.json --top-k 10
```

For a human-readable answer and numbered sources, append `--format text` to the
`ask` command. The JSON default includes the same output in `response`, outside
the unchanged `assessment` report. Missing, unverified, and conflicting facts
are explained separately, and question-level abstention suppresses every factual
answer claim and answer citation. Truncation notices appear in both formats.

The sample report is synthetic and contains revenue of 145 million USD and
operating profit of 23 million USD for 2025. Employee count is absent from that
sample. The request contains explicit requirements without expected answers;
question text is not automatically decomposed.

To query a different existing database, place `--db` before the command:

```powershell
python -m ragsmith.cli --db data/processed/evidence.db ask configs/database_question.json --lookup-config configs/lookup-disabled.json --top-k 10
```

Without `--lookup-config`, discovery is disabled by default. Enabled and disabled
lookup use the same retrieval process. This supports the existing discovery
ablation without introducing expected answers or changing retrieval budgets.

Python 3.11 remains unverified in this continuation. The current `.venv` points
to an unavailable Python 3.11 installation; the 379 tests ran under bundled
Python 3.12.14 with existing environment packages.

## Application interface

```python
from pathlib import Path

from ragsmith.lookup_config import LookupConfig
from ragsmith.retrieval import RetrievalConfig, answer_from_database
from ragsmith.value_lookup import LookupQuestion, MetricLookup

request = LookupQuestion(
    "q-revenue", "What was revenue in 2025?",
    (MetricLookup("req-revenue", "Revenue (million USD)", 2025),),
)
result = answer_from_database(
    Path("data/processed/evidence.db"), request,
    LookupConfig(value_lookup_enabled=True),
    RetrievalConfig(per_requirement_limit=10),
)
```

Each requirement can specify a tuple of `document_ids` (a list in JSON). Scope
is applied before ranking limits, preventing excluded documents from consuming
the retrieval budget. Callers must identify the intended organization and
document scope; the system does not infer them from the question.

## Retrieval behavior and audit

Each requirement is queried using its metric and year. The query follows the
existing lexical baseline: up to 20 alphanumeric tokens, individually quoted,
joined with OR. Results use SQLite FTS5 `bm25` scores, where lower scores rank
first, with evidence IDs breaking ties. The limit is 1 to 100 per requirement;
one extra row is fetched only to detect truncation.

All requirement searches use one read transaction. Their results are combined
into a union keyed by evidence ID before assessment; a requirement's document
scope still applies during verification. Evidence retrieved for one requirement
can also help assess another requirement in that union.

`retrieval` in the application output records the method, candidate budget,
unique evidence count, and per-requirement query, FTS expression, document scope,
ranked hit IDs, source paths, version IDs, scores, and truncation flag. A citation
can be mapped by evidence ID to its source path in this audit; its document,
version, locator, and optional table/page fields remain in the answer citation.

Metadata is loaded from stored JSON and validated through the Evidence model.
Stored document hashes must agree with evidence version IDs. Corrupt metadata,
missing required provenance, or inconsistent stored versions fail explicitly;
they are not silently replaced with empty metadata. A nonexistent database is
an error and is never created by the query path.

## Interpretation limits

This is an initial lexical retrieval baseline, not BM25+dense/table/KG fusion.
OR matching may return unrelated passages and miss useful evidence at small
budgets. `truncated: true` explicitly indicates more lexical candidates existed;
it does not identify whether they contain support or conflicts. Increasing the
budget can reveal a contradiction and change an answerability decision. Even
without truncation, lexical retrieval is not exhaustive semantic coverage.

`full`, `partial`, `missing`, and `unverified` concern the retrieved evidence
union. They do not certify corpus-wide answerability. Unsupported text/table
formats remain unverified by the existing lookup policy. This adapter does not
reshape multi-year tables or extract structured rows from native-text PDFs.

The query path checks stored provenance consistency, not live source-file
integrity. Files may have changed or disappeared since ingestion; use the
existing source-integrity tooling or reingest when current-file checks are needed.
No benchmark accuracy or latency improvement is claimed by integration tests.
