# Phase 4 structured QA integration validation

Phase 4 completes the scoped integration described in the handoff: explicit
application requirements flow through retrieval, evidence-value discovery,
existing structured verification, graded sufficiency, and deterministic response
construction. This is not completion of the entire research proposal.

## Completed software checks

- 379 automated tests passed under bundled Python 3.12.14, including all 235
  original Phase 3 tests and the separately committed Batch 1/Option A tests.
- Real XLSX and HTML documents were ingested, retrieved, assessed, and answered
  with supporting citations and retained document/version/location metadata.
- Full support, partial support, absent evidence, unsupported text formats,
  contradictory values, duplicate IDs, multiple documents, optional metadata,
  malformed stored provenance, reingestion, and JSON serialization are covered.
- Enabled/disabled discovery uses identical retrieval inputs and budgets.
- Document scopes apply before top-k, overlapping hits deduplicate, tie ordering
  is deterministic, and truncation is explicitly reported.
- Database retrieval opens read-only and does not create a missing database.
- Default JSON CLI output and `--format text` were exercised end to end.
- The Phase 3 verifier, contradiction policy, assessment-report schema, and
  evidence model remain unchanged. The Batch 1 assertion interface is unchanged.

The tests establish software behavior, not benchmark accuracy, novelty, or an
improvement over research baselines. Python 3.11 remains unverified because the
recorded project interpreter is unavailable; no fresh environment or full PDF
runtime validation was performed in this continuation.

## Response contract

`ragsmith.response.render_lookup_response` presents trusted lookup-pipeline
output. `answer_from_database` adds it as `response`, leaving the assessment
schema intact. Its fields are `answerability`, `text`, `citations`,
`unsupported_requirements`, and `warnings`.

Full and partial responses render only supported facts. Source numbers are
assigned deterministically in requirement/citation order and reused when facts
share evidence. Source records preserve provenance and optionally resolve paths
from the retrieval audit. Missing requirements explain absence from assessed
evidence; unverified requirements explain unsupported formats or disabled lookup.
Any contradiction retains the existing question-level abstention behavior:
no factual values or supporting answer citations are rendered, including values
for other supported requirements. Discovery diagnostics are never answer text.

The renderer checks status/decision consistency, required supported-answer
fields, and citation identity against the assessment provenance. This catches
presentation inconsistencies; it does not independently authenticate an external
report or prove that a source supports a changed value. Callers must pass trusted
pipeline output, not user-authored answer reports.

## Practical example

With a working project Python, from the repository root:

```powershell
python -m ragsmith.cli ingest data/raw/sample_report.html
python -m ragsmith.cli ask configs/database_question.json --lookup-config configs/lookup-enabled.json --format text
python -m pytest -q
git diff --check
```

The included synthetic report supports revenue 145 and operating profit 23 for
2025. Employee count is not supported. Its status can be `unverified` when the
retrieved union includes unsupported text; otherwise absent interpretable facts
are `missing`. The rendered answer explicitly explains the gap without guessing
an employee count.

## Known boundaries and next work

- Questions still require explicit metric/year requirements and caller-selected
  document/entity scope. Natural-language decomposition is not implemented.
- Value discovery and verification accept only canonical single-year table rows.
  Wider tables, unit conversion, aliases, free-text inference, entity resolution,
  and version precedence remain open.
- Retrieval is the existing SQLite FTS5 lexical/BM25 baseline, not the proposed
  BM25+dense+table+KG system. No fusion strategy is silently selected here.
- Top-k retrieval can omit supporting or contradictory evidence. Tests show a
  limited set can produce `full`, while a larger set reveals a contradiction
  and abstains. Responses display truncation notices without changing policy.
- Stored source-version consistency is checked; source files are not rehashed
  for every query. A citation refers to the ingested snapshot.
- Literature verification, corpus licensing/collection, independent annotation,
  evaluation definitions, baseline/ablation design, measured latency/memory, and
  empirical reliability comparisons remain research tasks for the next phase.
- Preserve the explicit no-push instruction. The earlier two local commits
  remain separate; remaining retrieval/response work belongs in one consolidated
  local Phase 4 completion commit.
