# Project state — November 1, 2026

The supplied November 1 handoff governs prior research and architecture decisions
except where the user explicitly superseded it. Phase 3 is complete at `36232e9`.
Phase 4 is in progress. Batch 1 is committed separately at `29843fc`.
The user authorized a second local commit for Option A and explicitly instructed
**do not push**; that instruction supersedes the earlier phase-only commit/push
workflow. Phase 4 as a whole is not complete.

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
- Batch 2: adapt existing retrieval results to complete Evidence objects,
  preserving metadata and provenance. Existing search dictionaries omit metadata.
- Supporting-citation filtering and structured supported-value answers are now
  available. Richer response construction and natural-language generation remain
  planned. Aggregate evidence IDs remain audit references, not answer citations.
- Batch 4: end-to-end validation and review before the phase commit/push.
- Entity/document scope, automatic decomposition, wider table formats, fusion,
  dense/KG retrieval, and free-text verification remain open or planned.
- Verify the named literature, choose a licensed pilot corpus, define independent
  annotations and evaluation metrics, and measure latency/resource consumption.
- Lookup only parses the verifier's canonical metric/year/value table rows.
  No alias matching, unit conversion, entity inference, or version preference is
  implemented. Callers must provide the intended entity/document scope.
- The config toggle is a discovery-function ablation: disabling it prevents
  unknown-value answering. It does not isolate the research contribution of
  sufficiency verification, which needs separate controlled baselines later.
- No empirical benchmark claims have been established. Python 3.11 remains
  unverified; the old environment was not repaired or replaced.
