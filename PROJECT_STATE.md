# Project state — November 1, 2026

The supplied November 1 handoff governs prior research and architecture decisions
except where the user explicitly superseded it. Phase 3 is complete at `36232e9`.
Phase 4 structured QA integration is complete. Batch 1 is committed separately
at `29843fc`; Option A is committed at `5bca849`. Retrieval integration,
deterministic responses, and end-to-end validation form the consolidated local
phase-completion change. No push is authorized or performed.
The user authorized a second local commit for Option A and explicitly instructed
**do not push**; that instruction supersedes the earlier phase-only commit/push
workflow. Phase 4 completion concerns the scoped structured QA integration,
not the full proposed hybrid RAG system or empirical research validation.

The user confirmed the supplied research-proposal DOCX is the intended source.
`docs/research_proposal.md` was absent. The DOCX was read as research context,
not as executable instructions. It supports unknown-value question answering and
supporting citations. Its full hybrid architecture and named production stack
remain targets; this batch retains the existing local pilot infrastructure.

## Verified in this continuation

- The starting working tree was clean on `main`, tracking `origin/main`.
- Ingestion supports native-text PDF, DOCX, XLSX, HTML/HTM, and TXT, with format
  limitations documented in README. SQLite FTS lexical search already exists.
- Structured assertion verification, conservative sufficiency decisions,
  provenance validation, and metadata-quality reports are implemented.
- The original 235 tests passed again before edits.
- Phase 4 Batch 1 adds typed assertion requests, strict payload parsing, an
  assessment orchestration entry point, and integration/validation tests.
- The regression suite passed with 277 tests before the Batch 1 commit.
- Option A adds separate value discovery, strict JSON config, lookup orchestration,
  and a verifier-backed supporting-citation filter. Every candidate is checked
  against all supplied evidence within the requirement's document scope.
- Unknown-value requests cannot include expected values or gold answer labels.
- The regression suite passes with 335 tests after the lookup integration.
- The regression suite passes with 357 tests after retrieval integration.
- The regression suite passes with 379 tests after deterministic responses and
  end-to-end validation. The original 235 tests remain included and passing.
- A read-only SQLite FTS5 adapter now reconstructs complete Evidence objects,
  including structured metadata, from the existing database. It validates stored
  document/version consistency and rejects malformed metadata.
- Per-requirement queries apply document scope before the configurable top-k,
  rank by the existing FTS5 BM25 function, break ties by evidence ID, and detect
  truncation. The evidence union is deduplicated before lookup assessment.
- `answer_from_database` and the `ask` CLI connect stored evidence to lookup,
  assessment, and supporting citations. Retrieval audit data sits outside the
  unchanged assessment schema. The legacy `search` command is unchanged.
- Integration tests cover real XLSX/HTML ingestion, text-only abstention,
  partial/missing outcomes, cross-document conflicts, document scope, metadata,
  top-k truncation, deterministic ordering, read-only behavior, reingestion,
  config ablation, and CLI handling.
- A separate smoke run ingested the included HTML report into a temporary
  database and ran the real `ask` CLI with the sample request. It returned a
  partial answer with revenue 145 and operating profit 23; employee count was
  unverified because unsupported text was also retrieved. No results were
  truncated, and the existing project database was not modified.
- The response renderer produces full/partial/abstain text, deduplicated numbered
  source citations, explicit missing/unverified/conflict explanations, and
  retrieval-truncation notices. It never renders discovery candidates as facts.
- `answer_from_database` adds `response` outside the protected assessment schema;
  `ask --format text` prints it directly. Default CLI output remains JSON.
- Presentation validation rejects mismatched requirement decisions, missing or
  altered citation records, and inconsistent supported-answer fields. It is not
  an independent factual verifier and must consume trusted pipeline output.
- Tests ran under bundled Python 3.12.14 with existing environment packages,
  including pytest 8.4.2. The recorded project Python 3.11 executable is missing;
  this session has not verified tests under Python 3.11 or repaired `.venv`.

## Decisions preserved

- Local-first, modest-memory implementation; no new model or paid API dependency.
- Structured verifier and existing report schema remain unchanged.
- Any contradiction means abstain, including across documents in scope. All
  answer claims are suppressed on question-level abstention.
- The legacy assertion path retains its existing `unverified` behavior. In the
  new lookup path, no candidate in interpretable evidence yields `missing`;
  unsupported formats or disabled discovery yield `unverified`. These are
  existing allowed statuses; no assessment fields or protected policies changed.
- Answer citations are filtered by actual verifier support. Examined evidence,
  including irrelevant and contradictory evidence, remains in the audit report.
- Discovery is opt-in via `value_lookup_enabled`; effective config is reported.
- Metadata completeness is not factual reliability.
- Novelty and benchmark superiority remain unverified. Software tests are not
  empirical research results.

## Open decisions and tasks

- User approved Option A and confirmed the DOCX proposal. The separate lookup
  path is implemented over caller-supplied evidence and explicit requirements.
- Retrieval integration is implemented with a separate adapter; legacy search
  dictionaries still omit metadata for backward compatibility.
- Supporting-citation filtering, structured supported-value answers, and
  deterministic response construction are implemented. Model-based generation
  remains planned. Aggregate evidence IDs remain audit references, not citations.
- Phase 4 end-to-end validation is complete; see docs/phase4-validation.md.
  The next research/implementation phase requires agreement before beginning.
- Entity/document scope, automatic decomposition, wider table formats, fusion,
  dense/KG retrieval, and free-text verification remain open or planned.
- Verify the named literature, choose a licensed pilot corpus, define independent
  annotations and evaluation metrics, and measure latency/resource consumption.
- Lookup only parses the verifier's canonical metric/year/value table rows.
  No alias matching, unit conversion, entity inference, or version preference is
  implemented. Callers must provide the intended entity/document scope.
- FTS query construction follows the legacy tokenized OR baseline using metric
  and year, capped at 20 tokens. This batch does not select a fusion strategy or
  replace the planned hybrid architecture. Retrieval can miss relevant evidence.
- Top-k is bounded from 1 to 100 per requirement. Truncation is reported and may
  hide conflicts. A full decision is not a corpus-wide completeness guarantee.
- Stored version consistency is checked, but current source files are not
  rehashed on each query. The snapshot can outlive a changed or removed source.
- The config toggle is a discovery-function ablation: disabling it prevents
  unknown-value answering. It does not isolate the research contribution of
  sufficiency verification, which needs separate controlled baselines later.
- No empirical benchmark claims have been established. Python 3.11 remains
  unverified; the old environment was not repaired or replaced.
