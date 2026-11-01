# Project state — November 1, 2026

Publication update: the user authorized publishing current progress with private
files excluded. This public history omits private pilot labels and case-level
human annotations; original local history and the preregistration tag stay local.
See [publication provenance](docs/public-publication-history.md). No new evaluation
data selection is authorized by this publication.

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

- Human-only minimal pilot completed once, per revised user instructions. It has
  18 independent source facts and 36 derived cases; no statistical or performance
  claims are made. Facts share nine contexts; statistical independence is unproven.
- The user's sheet passed strict schema/value/ID/null checks, with 18 construction
  labels unchanged. Distribution: 9 full, 9 partial, 18 abstain; no exclusions.
  Separate commit 52d0e1f5ac38270eb62a78824ebc921a5fa15842 is "locked provisional
  labels". The sheet and locked copy have SHA-256
  b027cb335ca582acccf672f6d25ad23406439ba56f3d20259630efe7407dd8e6.
- Ran only pilot36.py lock then pilot36.py run. Neither the LLM labeler nor compare
  was invoked: the user has no API key and explicitly skipped them. No external
  API call, alternative model, tuning or rerun occurred. No LLM cross-check or
  human inter-annotator agreement is reported. All labels remain provisional,
  single-annotator. The prior pending status entries below are historical.
- Frozen src tree remains 3261c6087757b9f3d9aed1166e264de45ac4f479, at pipeline
  commit 1b0df45c5e5fe443c5dd8be463ccf26dd9463de3. There are 108 predictions:
  case-label matches 18/36 extraction, 27/36 binary, 36/36 graded. Partial cases
  returning values: 9/9, 0/9, 9/9. These are controlled-case counts, not claims.
- docs/pilot36-results.md is the one-page results table; docs/pilot36-failures.md
  summarizes 27 baseline/case label mismatches (18 distinct cases), without
  private case IDs or labels in this public copy. Raw outputs are
  local/ignored under pilot36/results. Dataset-reference scores were omitted.
  A second human annotator for 30–50 questions is required before paper results.

- Revised user-approved scope: 18 independent source facts and 36 derived cases;
  no statistical or performance claims are made from this pilot. Distinct facts
  share nine source contexts; statistical independence is not established.
- All 581 existing tests passed before logical local commits c27d60f (adapter),
  18798ba (bindings), 0bf10e3 (families), and 1b0df45 (resource trials). Git status
  was clean before minimal pilot preparation. No push occurred.
- Pipeline/baselines frozen at 1b0df45c5e5fe443c5dd8be463ccf26dd9463de3, src tree
  3261c6087757b9f3d9aed1166e264de45ac4f479. No src changes are permitted between
  labeling and results. New helpers exist only under scripts; source remains frozen.
- Minimal pilot artifacts are local/ignored at data/evaluation/pilot36: 18 original
  extraction-span questions/facts from nine explicitly selected contexts become
  36 paired condition cases. Values come from source cells, not dataset answers.
  18 empty/conflict labels are construction-determined; 18 full/partial labels
  await the user's judgment. All labels are provisional, single-annotator.
- Official pinned README/JSON were checked for CC BY 4.0 and raw format; URLs and
  source SHA-256 are in docs/minimal-pilot.md. Dataset-derived scores are omitted.
- Standalone helpers lock completed human labels, gate auxiliary LLM labeling,
  list human/LLM disagreements separately, and run the existing frozen baselines
  once after the lock. Model gpt-4.1-mini-2025-04-14 / OPENAI_API_KEY was disclosed
  before script creation; official docs mark it deprecated. No real API call,
  human label lock or pilot prediction/results run has occurred.
- Stop infrastructure expansion. The short guide has five synthetic examples.
  docs/roadmap.md requires a second human annotator for 30–50 questions before
  paper results. An LLM is not human inter-annotator agreement. Earlier 60-family
  plans and reviewer availability assumptions are superseded for this pilot.
- Eight new offline helper guard tests bring the complete suite to 589 passing
  tests. They test missing locks, immutable construction labels, one-shot guards
  and mocked API payload isolation; no pilot inference or real API call occurs.

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
- Completed typed-lineage, measurement and reviewer-preparation batches were
  committed locally at 1ab2d92 (feat: add audited evaluation metrics and reviewer
  preparation). The user requested no push until Phase 5 is complete.
- The full software suite passes with 589 tests under bundled Python 3.12.14;
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
- The typed-record/lineage batch is implemented, tested and committed: v0.2
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
  Track A gold links must refer to the fixed supplied set. The Track B scorer
  preserves full-scope gold and counts retrieval misses instead of reusing
  that condition as an exclusion. See docs/evaluation-records.md.
- The measurement batch is implemented, tested and committed:
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
- Native retrieval export and reviewer preparation are implemented, tested
  and committed. Export freezes a single SQLite online-backup snapshot for all
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
- The TAT-QA source-adapter batch is committed at c27d60f:
  offline byte/hash checks anchor training data to the committed audit. Source
  cells/paragraphs and locators are separated from coordinator-only upstream
  answers. Every question/context has a screening disposition. The training gate
  has 1,462/13,215 questions (11.06%), 355 paired candidate contexts and 354
  conservative table-duplicate groups. Semantic acceptance remains unmeasured.
- A deterministic draft queue keeps normalized duplicate tables together, with
  pending semantic eligibility, report identities and partitions. Targets remain
  60 families, 12 development/48 held-out, four conditions each; no pilot families
  have been selected. Original report identity and near-duplicate review are still
  required. Generated upstream content stays ignored in tatqa-screening-001;
  docs/tatqa-screening-audit.json contains only aggregates and provenance.
- Seventeen new synthetic tests cover source preservation, answer separation,
  trusted-byte checks, deterministic grouping, malformed inputs and no automatic
  semantic acceptance. No production verifier or assessment schema was changed.
- The manual-binding batch is committed at 18798ba. Strict
  provisional decisions pin question/source hashes and require source-backed
  reviewer notes; only accepted decisions bind metric/year/unit/value cells.
  Cell geometry and canonical delimiters are validated. Values come from source
  cells with edge whitespace trimming only. No upstream answers are used by
  the binding compiler, and no verifier/schema/policy was changed.
- Canonical output has original/derived source declarations, parent links,
  evidence fingerprints, explicit document scopes and cell transformation maps.
  It contains accepted bound cells only, not a full retrieval corpus. Provisional
  context groups do not establish report identity; no gold or pilot is created.
  Unit semantics remain a manual responsibility; inconsistent same-key bound
  units are rejected because the verifier does not validate units.
- Twenty-seven new synthetic tests cover strict decisions, stale hashes, cell
  errors, answer separation, deterministic transforms and the unchanged verifier's
  full-support/conflict-abstention behavior. Real-data smoke checks generated
  1,462 pending templates and compiled only pending decisions into empty evidence.
  Real semantic eligibility remains unmeasured. See docs/manual-cell-bindings.md.
- The report/family construction batch is committed at 0bf10e3.
  Strict source-hash-bound manual declarations require report references and
  reviewer notes; they remain provisional assertions, not verified identities.
  Duplicate-table and declared report/version links merge transitively. Any
  unresolved member blocks drafts for its connected group. Grouping overrides
  partition quotas, with actual development/held-out counts reported.
- Two distinct accepted source facts form each draft family. Question text and
  scoped requirements stay fixed across full/partial/missing/synthetic-conflict
  cases. Removal and synthetic before/after changes are logged with parent links,
  artifact versions and evidence fingerprints. The scope is controlled bound
  facts, not a complete report or retrieval corpus. No gold is generated.
- Sixteen synthetic tests cover four-condition verifier behavior, shared-report
  partition integrity, transitive grouping, unresolved identities, stale records,
  invalid conflicts and deterministic construction. Real smoke checks generated
  355 pending declaration pairs and compiled them into zero drafts. Semantic
  eligibility and original report recovery remain pending. The guide is
  docs/pilot-family-construction.md; all upstream content stays ignored/local.
- The resource-trial batch is committed at 1b0df45. Separate
  child processes measure fresh first passes and warmed repetitions. Optional
  SQLite runs query one read-only backup snapshot; fixed-evidence runs report
  retrieval time as null. Timings cover retrieval/validation/assessment/rendering,
  with separate parent launch-to-result time, raw samples, descriptive medians
  and nearest-rank p95. No per-policy speedup comparison is implemented.
- OS memory reports current/lifetime-peak Windows working-set bytes; Linux has
  an implemented but host-unverified getrusage/proc path. Unavailable counters
  remain null. Worker lifetime peak includes loading/warmups and excludes the
  parent, so this is not total deployment RAM or query-only memory. OS cache state
  is uncontrolled; fresh process does not establish cold disk/cache performance.
- Twenty-one new tests cover worker isolation, memory APIs, timing arithmetic,
  failure/timeout handling, input mutation and synthetic SQLite retrieval. A
  five-repeat six-question synthetic run completed with non-null Windows memory
  counters and five samples per condition. No real pilot performance was measured.
  See docs/resource-trials.md. Production code and annotation status are unchanged.
- Remaining work: Phase 5 readiness/reviewer handoff, completed source declarations,
  bindings, representative resource workloads and independent source annotation. Real pilot
  annotations and confirmatory results await independent review. A future schema
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

## November 2 local engineering update

The Option C amendment was published through public commit `b5ffc6f` before
building. Subsequent building work stays local on `codex/public-progress`.
Separate source-only ingestion, packing/runtime adapters and a thin FastAPI demo
now wrap the frozen pipeline. The new `.venv-api` uses Python 3.12.14; Python 3.11
is still unverified. **669 tests pass**; one synthetic model integration and six
existing pilot lookup examples were checked without tuning or private-label reads.
The prior pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Labels remain **provisional,
single-annotator**, and independence is not established.

No evaluation/development data selected, no corpus lock, no real calibration or
research run. Default API comparisons are the frozen pilot baselines; optional
local Qwen mode compares the three research policies with an explicitly
uncalibrated demo threshold. Genuine-quota feasibility and independent human
review remain prerequisites for paper results. See [API commands](app/README.md)
and the [engineering handoff](docs/tonight-engineering-handoff.md). Frontend work
awaits the user's next request. Frozen `src/` tree remains
`3261c6087757b9f3d9aed1166e264de45ac4f479`.
