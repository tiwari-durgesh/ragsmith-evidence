# Retrieval metrics uncertainty and diagnostic resource measurements

Evaluation report version 0.3 adds frozen-ranking Track B, retrieval metrics,
paired source-cluster bootstrap comparisons and optional Python-allocation
profiling. Production retrieval, verification, decisions and assessment schemas
remain unchanged. All labels are still `provisional, single-annotator` and all
committed fixtures are synthetic. This batch produces no research result.

## Two evaluation tracks with one gold scope

Default Track A sends the complete frozen evidence set to inference. Track B
uses `--rankings PATH --k N`; the evidence JSONL then defines the full source
universe and the ranking log defines which subset reaches inference. Gold links
are validated against that full universe, not the retrieved subset. A missed
supporting or conflicting fact remains in gold and counts as a retrieval error.

The ranking JSONL has one row per question with `question_id` and `rankings`.
Each ranking has `requirement_id` and an ordered list of unique `evidence_ids`.
See [the synthetic ranking fixture](../data/evaluation/fixtures/rankings.jsonl).
No answer values or gold labels belong in the ranking log. Unknown evidence,
duplicate IDs, missing question/requirement coverage and out-of-scope ranks fail
before inference. IDs beyond the cutoff are also checked for invalid references.

For each question, top-k is applied per requirement. The union is deduplicated
in request order, preserving first occurrence; all policy variants receive that
same union and use its order as the extraction-only baseline's frozen ranking.
The output reports union sizes separately rather than calling them k. Rank logs
are source artifacts produced before labels are read, not an oracle retriever.
The example log is hand-authored synthetic test data, not actual TAT-QA retrieval.

## Ranking scores

Per requirement, gold decisive evidence is its annotated support set or its
conflicting evidence set. Evaluation reports:

- Recall: retained relevant IDs divided by all gold decisive IDs.
- Reciprocal rank: inverse of the first relevant rank, or zero for a miss.
- Binary-gain nDCG: discounted relevance, using `1/log2(rank+1)`, divided by
  ideal discounted gain at the same per-requirement cutoff.

Summary Recall, MRR and nDCG are macro averages over eligible requirements.
Support and conflict recall are also reported separately. No-gold requirements
and not-adjudicable requirements have null scores and explicit exclusion counts.
Other adjudicable requirements can contribute retrieval diagnostics even if an
ambiguous requirement excludes the question from primary answerability scoring.
Empty ranking lists with positive gold evidence score zero, never an exclusion.

`cutoff_truncated` means the supplied ranking log contains more entries than k.
It does not certify whether a previously truncated upstream log was exhaustive.
Do not interpret a false flag as corpus-wide evidence completeness.

The synthetic full-support case puts the profit evidence second in its ranking.
At k=1, the model sees only revenue, but the gold question stays full. Likewise,
retrieving one side of a conflict can produce an erroneous full answer; the gold
conflict is not erased to make that prediction look correct.

## Primary paired comparisons

The report contains these predeclared diagnostic endpoints, both A minus B:

1. Graded minus binary partial-answer completeness: mean per-question paired
   coverage difference over gold partial questions. Undefined per-question pairs
   are excluded and counted.
2. Graded minus extraction-only unsupported-claim rate: difference of pooled
   unsupported/emitted claim counts. Zero-claim questions remain in the sampled
   families; this is not an average of per-question risk ratios.

`paired_cluster_interval` samples source-family groups with replacement and
retains all related questions and both policy outcomes together. Defaults match
the draft protocol: 2,000 replicates, seed 1729, 95% percentile intervals with
linear interpolation between ordered replicate values. Config and estimand
names are recorded in the output.

A valid point estimate needs both compared metrics to be defined. Fewer than
two eligible source clusters yields a null interval. If any bootstrap resample
has an undefined metric, the interval is withheld with an explicit reason and
valid/undefined replicate counts; those samples are not quietly discarded.
No questions is also an explicit undefined case. Duplicate paired IDs and
nonfinite/invalid rate counts are rejected.

The current six-case suite has just one source family. Its point differences
are diagnostic; its inferential intervals are therefore null. Even with two
clusters a computed interval is not proof of reliable inference or sufficient
power. Independent reviewed labels, adequate source groups and the frozen
statistical plan remain prerequisites for research conclusions.

## Timing memory and environment

Named non-overlapping checkpoints use a monotonic `time.perf_counter` clock:
input/lineage/ranking loading, shared inference, post-inference/gold validation,
scoring, uncertainty calculation and environment metadata. Total includes the
whole in-process harness run. It is not isolated query latency and includes
evaluation and bookkeeping overhead. Policies share the verifier execution, so
the recorded shared inference time is not a per-policy timing comparison.

With `--profile-memory`, tracemalloc reports the peak of traced Python
allocations over the harness run. It omits untracked native allocations and is
not process RSS. Process peak RSS and live retrieval latency are explicitly
null, not inferred from Python allocations or ranking replay. An existing tracing
session is left intact and reported as unavailable for isolated profiling.
Owned tracing sessions are stopped even on failure. Profiling itself adds cost.

Run metadata records Python executable/version, platform, installed dependency
metadata, Git commit and a dirty-content digest covering tracked differences and
nonignored untracked file content. Raw diff content is not emitted. Ignored
corpora are covered by the separate input/source hashes, not the Git digest.
Package metadata does not establish that an untested native module can import.
Python 3.11 remains unverified; synthetic tests use bundled Python 3.12.14.

## Reproduce

With a working project Python and package installation:

```powershell
python scripts/evaluate_synthetic.py
python scripts/evaluate_synthetic.py --rankings data/evaluation/fixtures/rankings.jsonl --k 1
python scripts/evaluate_synthetic.py --rankings data/evaluation/fixtures/rankings.jsonl --k 2 --profile-memory --bootstrap-replicates 2000 --bootstrap-seed 1729
python -m pytest -q
```

The current suite has 484 passing software tests. These check formulas, grouping,
leakage prevention, cutoff behavior and measurement contracts. No real held-out
pilot or resource benchmark was run. Native retrieval-log export, real source
screening, independent annotation, process RSS collection, repeated warm/cold
latency trials, and confirmatory study design remain subsequent work.
