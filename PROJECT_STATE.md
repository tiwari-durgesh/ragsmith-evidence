# Project state — November 1, 2026

The supplied November 1 handoff governs prior research and architecture decisions
except where the user explicitly superseded it. Phase 3 is complete at `36232e9`.
Phase 4 structured QA integration is complete. Batch 1 is committed separately
at `29843fc`; Option A is committed at `5bca849`. Retrieval integration,
deterministic responses, and end-to-end validation form the consolidated local
phase-completion commit f652213. The user subsequently explicitly authorized
pushing Phase 4; all three commits were pushed successfully to origin/main.
The working tree was clean and main synchronized at that point. That request
authorized the Phase 4 push; it does not automatically authorize future pushes.
Phase 4 completion concerns the scoped structured QA integration,
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
- Phase 5 direction is approved in principle with the user's extraction-only,
  source-verification, synthetic-first, reviewer, sampling and local-commit
  conditions. The user will arrange a second annotator; none has reviewed labels
  in this session. All current labels are `provisional, single-annotator`.
- The initial offline harness is implemented in ragsmith.evaluation, with six
  original synthetic fixtures, strict request/gold separation, frozen-evidence
  extraction/binary/graded comparisons, core scoring, validation and file hashes.
  Gold files are opened only after inference. Results are marked non-research.
- The initial Phase 5 foundation was committed locally at 807d70f and not pushed.
- The full software suite passes with 500 tests under bundled Python 3.12.14;
  Python 3.11 remains unverified. Production Phase 4 source files are unchanged.
- A separate agreement script measures unweighted Cohen's kappa from aligned,
  independent pre-adjudication labels and handles undefined cases explicitly.
  The reviewer handout includes examples and source-based decision rules.
- TAT-QA raw labeled splits and upstream notices were downloaded into ignored
  audit storage at 870accc41953dcde885aabeb963d94aabdc0fbc3. Hashes/aggregates are
  documented. Its dataset is CC BY 4.0; its code is MIT. This corrects the earlier
  incomplete repository-license shorthand. FinQA was inspected and deferred.
- The audited extraction labels span/multi-span cover 9,209/16,546 (55.66%).
  The chosen narrower table-only span gate covers 1,804/16,546 (10.90%); final
  manually engine-compatible eligibility is unmeasured. The labeled release
  differs from the README headline count, so measured denominators are explicit.
- The revised proposed pilot is 240 derived conditions across 60 context families,
  targeting 48 development/192 held-out cases with source grouping taking
  precedence. This is a diagnostic sample-size proposal, not collected data or
  evidence that small risk differences can be detected. See pilot-sampling-plan.md.
- research-claim-mapping.md ties metrics and controls to proposal sections and
  distinguishes prior-art refutation of originality from empirical benefit tests.
- The typed-record/lineage batch is implemented and tested but uncommitted: v0.2
  uses frozen typed gold/evidence containers and a required source manifest,
  including parent transformations, source versions, license/location declarations,
  evidence fingerprints, scope checks and source-family consistency. Malformed
  JSON, duplicate keys, nonfinite values and reserved gold metadata fail explicitly.
- All gold labels are still opened after inference. Evidence and file hashes
  are rechecked after prediction to detect mutation. Existing synthetic metrics
  are unchanged; 43 new tests cover invalid shapes, stale or unknown links,
  source graph errors, scope mismatches, label leakage and inference mutation.
- Manifest validation is internal consistency only: it does not authenticate
  sources, check legal rights, infer truth, or mark labels as independently reviewed.
  Track A gold links must refer to the fixed supplied set. A future Track B scorer
  must preserve full-corpus gold and count retrieval misses rather than reuse
  that condition as an exclusion. See docs/evaluation-records.md.
- The next measurement batch is also implemented and tested but uncommitted:
  report v0.3 supports frozen-ranking Track B, Recall@k/MRR/binary nDCG and separate
  support/conflict recall. Full source-scope gold remains intact when top-k misses
  support or conflicts. All policy variants receive the same retrieved union.
- Primary paired differences use whole source-cluster bootstrap sampling with
  2,000 replicates/seed 1729 by default. Partial coverage uses paired question
  means; unsupported rate uses pooled claim counts. Single-cluster or undefined
  rate cases explicitly withhold intervals. The six-case fixture has one cluster.
- Diagnostic measurements record named monotonic-clock stages, optional traced
  Python allocation peak and environment/Git metadata. They do not measure live
  retrieval, process RSS, isolated model latency or publication benchmark speed.
- Thirty-nine new tests cover numerical metric examples, rank validation,
  preserved full-scope gold, cluster sampling, undefined rates and profiling.
  Production source and provisional annotation status are unchanged.
- Native retrieval export and reviewer preparation are implemented and tested
  but uncommitted. Export freezes a single SQLite online-backup snapshot for all
  questions, logs query/rank/score/truncation metadata, validates returned evidence
  against the registered universe and produces Track B-compatible ranking JSONL.
  Source files are not authenticated and universe completeness is not established.
- Calibration packets use neutral IDs and shuffled evidence order, omit labels,
  predictions and source-transformation names, and provide separate blank
  reviewer files plus a requirement worksheet. Private mappings remain local.
  This hides labels/model outputs, not necessarily experimental conditions.
  All outputs require a fresh directory to protect existing annotation work.
- Sixteen new tests cover native SQLite export, stable snapshots during live
  changes, empty rankings, evidence mismatches, packet mappings and overwrite
  protection. A synthetic calibration packet was generated under ignored
  data/evaluation/generated/calibration-001. No real reviewer labels were made.
  See docs/evaluation-preparation.md for commands and the reviewer workflow.
- Remaining work: source-derived corpus adapters and screening ledger,
  repeated warm/cold resource trials, process RSS measurement and independent
  source annotation. Real pilot
  annotations and confirmatory results await independent review. The next batch
  must explicitly add reviewed/adjudicated states rather than silently upgrading
  provisional labels. No real pilot benchmark has been run.
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
