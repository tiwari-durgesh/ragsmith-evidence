# Project state — November 1, 2026

The supplied November 1 handoff governs prior research and architecture
decisions. Phase 3 is complete at `36232e9`. Phase 4 is in progress; Batch 1
changes are uncommitted. Commit and push once after the entire phase is complete.

## Verified in this continuation

- The starting working tree was clean on `main`, tracking `origin/main`.
- Ingestion supports native-text PDF, DOCX, XLSX, HTML/HTM, and TXT, with format
  limitations documented in README. SQLite FTS lexical search already exists.
- Structured assertion verification, conservative sufficiency decisions,
  provenance validation, and metadata-quality reports are implemented.
- The original 235 tests passed again before edits.
- Phase 4 Batch 1 adds typed assertion requests, strict payload parsing, an
  assessment orchestration entry point, and integration/validation tests.
- The regression suite passes with 277 tests after Batch 1.
- Tests ran under bundled Python 3.12.14 with existing environment packages,
  including pytest 8.4.2. The recorded project Python 3.11 executable is missing;
  this session has not verified tests under Python 3.11 or repaired `.venv`.

## Decisions preserved

- Local-first, modest-memory implementation; no new model or paid API dependency.
- Structured verifier and existing report schema remain unchanged.
- Any contradiction means abstain; missing support remains `unverified` in the
  current structured path.
- Metadata completeness is not factual reliability.
- Novelty and benchmark superiority remain unverified. Software tests are not
  empirical research results.

## Open decisions and tasks

- User decision requested: add a separate evidence-value lookup path for ordinary
  questions without supplied expected values, preserving the assertion verifier,
  or retain assertion-only scope for now. No lookup path has been implemented.
- Batch 2: adapt existing retrieval results to complete Evidence objects,
  preserving metadata and provenance. Existing search dictionaries omit metadata.
- Batch 3: construct responses only from supporting evidence. Existing aggregate
  evidence IDs include examined but irrelevant evidence and cannot be used as
  support-only citations.
- Batch 4: end-to-end validation and review before the phase commit/push.
- Entity/document scope, automatic decomposition, wider table formats, fusion,
  dense/KG retrieval, and free-text verification remain open or planned.
- Verify the named literature, choose a licensed pilot corpus, define independent
  annotations and evaluation metrics, and measure latency/resource consumption.
- No prior architecture or research decisions have been changed.
