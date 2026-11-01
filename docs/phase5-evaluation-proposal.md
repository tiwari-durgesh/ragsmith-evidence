# Phase 5 evaluation foundation proposal

Status: direction approved in principle with the user's extraction-only,
independent-review, source-verification and synthetic-first conditions. The
initial synthetic harness is implemented; no real pilot is evaluated. Practical
margins and final manual eligibility remain proposals. Production architecture,
verifier, contradiction policy and assessment schema are unchanged.

Companion documents provide the current details and supersede earlier tentative
counts/license shorthand: [corpus and scope audit](corpus-selection.md),
[claim-to-metric/baseline mapping](research-claim-mapping.md),
[240-question sampling proposal](pilot-sampling-plan.md), and
[reviewer guidelines](annotation-guidelines.md).

## Purpose and scope

Establish an independently annotated pilot and reproducible evaluation harness
before adding retrieval complexity. The central comparison holds retrieved
evidence, extraction, requirement decomposition, and response mechanism fixed
while varying the sufficiency policy in experimental baselines. The discovery
enable/disable switch alone cannot test the sufficiency hypothesis.

The current system takes explicit metric/year requirements and supports only
canonical single-year table rows. Initial experiments must be labeled structured
fact lookup with supplied requirements. They cannot establish general enterprise
QA, automatic question decomposition, free-text reasoning, or the full hybrid
retrieval architecture's performance.

## Proposed delivery batches

1. Freeze annotation and scoring definitions after review. Implement typed gold
   records, input/gold separation, corpus manifests, validators, and diagnostic
   fixtures. Fixtures test the harness; they are not research evidence.
2. Select and license-check sources, pin source versions, and create a small
   independently annotated calibration subset. Build a source-to-evidence map.
   Implement offline scoring and a reproducible run manifest.
3. Run frozen retrieval and controlled policy baselines on the calibrated pilot.
   Audit errors, then lock the held-out test set and experiment configurations.
4. Execute the held-out comparison with uncertainty estimates and limitations.
   Expand retrieval only after measured error analysis justifies the next module.

## Two separate evaluation tracks

### Track A requirement verification under controlled evidence

Human-authored requirements are paired with a fixed, independently annotated
evidence set. Include complete support, partial support, no support, contradictory
values, relevant-looking distractors, unsupported formats, and cross-document
evidence. Record the supplied evidence IDs before running any system variant.

This isolates evidence checking and response policy from retrieval errors.
Report results for synthetic diagnostic fixtures separately from independently
annotated source-derived cases. A transformation that makes tables canonical
must be recorded as a preprocessing condition, not hidden as native PDF ability.

### Track B retrieval to response

Use a fixed source-document scope per question. Retrieve at the same per-
requirement budget for every policy variant, persist the deduplicated union,
and run policies on that frozen union. Gold corpus answerability is fixed from
the full question scope and must never be relabeled to match what was retrieved.

Report corpus-level answer completeness alongside retrieved-evidence sufficiency.
For example, a supported partial response after a retrieval miss may be faithful
to its context while failing to recover all gold-supported requirements.

Natural-language requirement extraction is outside these initial tracks. Its
quality must later be evaluated separately, including omitted requirements.

## Corpus and question targets

Retain the approximately 50-source-document pilot objective, subject to recovered
source identities. The revised proposal is 240 derived cases from 60 manually
screened context families: full, partial, missing and synthetic-conflict conditions.
Target 12 development families and 48 held-out families with source grouping
taking precedence over exact counts. These are plans, not collected samples or
a power justification; see pilot-sampling-plan.md for precision limits.

Multi-requirement questions are essential: a single atomic requirement cannot
demonstrate a useful partial answer. Include both genuine missing information
and controlled evidence removal, labeling their origins separately. All variants
of the same question/document family must remain in the same partition.

Split by source family, organization, and near-duplicate/version clusters, not
individual passages or question rows. Propose approximately 20% development and
80% held-out test groups, with no training partition until training is needed.
Do not force exact proportions by splitting groups. Report achieved counts and
class distributions. Freeze annotation, prompts/configs, and normalization on
development data before opening held-out results.

## Source candidates newly investigated

Primary pages were checked November 1, 2026. Pinned raw TAT-QA files have now
been downloaded into ignored audit storage; only aggregates/hashes are committed.
No real pilot labels or model benchmark results have been produced.

| Candidate | Verified relevance | Limitation for this pilot |
| --- | --- | --- |
| [TAT-QA paper](https://aclanthology.org/2021.acl-long.254/) and [official README](https://github.com/NExTplusplus/TAT-QA#license) | Dataset CC BY 4.0; separate code license MIT. Released labels distinguish extraction from arithmetic/counting. | Chosen initial eligibility gate: table-only single-span, 1,804/16,546 labeled questions (10.90%). Further manual engine-compatibility screening is required. |
| [FinQA paper](https://aclanthology.org/2021.emnlp-main.300/) and [official repository](https://github.com/czyssrs/FinQA) | Financial-report QA with annotated reasoning programs; official code/data repository identifies an MIT license. | Multi-step numerical reasoning is outside current capabilities. Its existing question labels do not establish our full/partial/abstain task. |

Selected direction under the user's conditions: inspect a TAT-QA extraction-only subset,
retain a fully documented transformation to source-linked canonical rows where
necessary, and keep the unrestricted dataset as a future challenge set. A
finance pilot does not replace the domain-agnostic research goal. Policies,
manuals, and other domains still require a later generalization study.

Before collecting or redistributing artifacts, record the dataset revision,
license file, notices, source-report provenance, and any separate source terms.
A repository license label alone is not recorded as blanket clearance for every
underlying report. Unreviewed sources remain ineligible for a released corpus.
The original handoff's named literature and novelty comparisons remain open;
these two checks do not constitute a systematic literature review.

## Annotation contract

Gold annotations are authored from sources, not from system predictions. Use a
primary annotator and an independent reviewer for every held-out pilot case;
resolve disagreements and keep both initial judgments plus adjudication notes.
If independent review is unavailable, mark the limitation and do not label the
set independently reviewed. An assistant can draft annotations, but its own
verifier output is not an independent gold standard.

Each question records its scope, partition/group, question origin, explicit
requirements, gold facts, units, source versions/locators, supporting evidence,
conflicting evidence, and missing requirements. Evidence annotation IDs are
source-linked; any mapping to content-derived Evidence IDs is versioned so
reingestion or a changed chunker cannot silently redefine the gold set.

Keep two logical records:

- System input: question ID/text, explicit requirement ID/metric/year, allowed
  document scope, and retrieval/lookup settings. No expected values or labels.
- Gold-only record: independently annotated acceptable answers, evidence
  references, conflicts, requirement states, and question policy label.

Join by IDs only in the scorer after inference. A system-input export must
explicitly reject expected values, answer labels, annotated support IDs, and
other gold fields. Gold evidence is supplied to Track A only as its declared
oracle-evidence condition; report that advantage.

Distinguish requirement states:

- Supported: the scoped source contains the requested unambiguous fact.
- Missing: inspection of the defined source scope finds no required fact.
- Conflicted: scoped sources give incompatible values without an agreed
  precedence rule. Preserve alternatives rather than inventing one gold value.
- Not adjudicable: ambiguity, unsupported reasoning, or unresolved source/unit
  interpretation prevents a reliable annotation. Exclude from primary scoring,
  but retain and report its count and reasons.

Map adjudicated facts to the existing conservative policy: all supported means
full; some supported and no conflict means partial; none supported or any
conflict means abstain. Keep conflict flags separately: policy abstention is not
a claim that all other facts are unavailable. A system's `unverified` status is
an operational limitation and must not automatically become a gold missing label.

## Proposed baseline controls

The proposal's eventual dense, hybrid, table, and KG baselines remain planned.
The following smaller diagnostic baselines precede them; they do not replace
the research comparison matrix.

| Variant | Fixed inputs | Experimental behavior |
| --- | --- | --- |
| Extraction only | Same requirements, evidence union, candidate extraction/order | Emit the highest-ranked available candidate per requirement without sufficiency verification. Leave absent candidates absent. Treat a nonempty response as its binary answer decision. |
| Binary sufficiency | Same evidence, extraction, verifier judgments, source handling | Return a complete answer only if every requirement is supported; otherwise abstain. |
| Graded sufficiency | Same evidence, extraction, verifier judgments, source handling | Existing full/partial/abstain policy and evidence-bounded responses. |

Implement experimental variants in an evaluation namespace; preserve production
policy. Use the same deterministic presentation mechanism for comparable facts.
Do not introduce a different generator, retriever, budget, or gold-derived
candidate selection for one variant. Audit whether any observed gain comes from
verification, graded response coverage, or retrieval, rather than attributing
every change to the complete proposed architecture.

## Proposed scoring definitions

All metrics must include numerators, denominators, excluded counts, and per-class
or per-stratum breakdowns. Empty denominators produce null, not a fabricated
perfect score. Report counts of unanswerable/conflicted and non-adjudicable cases.

- Answerability: accuracy, a 3x3 confusion matrix, and macro-F1 across the fixed
  labels full/partial/abstain. A class with no predicted or gold examples has
  F1 zero in the fixed-label macro average; disclose absent gold classes.
- Retrieval: Recall@k, MRR, and binary-gain nDCG over annotated decisive evidence
  (supporting plus conflict evidence), with supporting and conflict recall also
  reported separately. Exclude no-gold-evidence questions from these retrieval
  averages and report their count. In Track B, k is per requirement and the
  deduplicated union size must also be reported; do not call union size top-k.
- Gold-supported requirement coverage: correctly returned supported requirements
  divided by gold-supported requirements. Report macro per-question coverage
  where the denominator is positive, and pooled micro coverage separately.
- Partial-answer completeness: the same coverage restricted to gold partial
  questions. A wrong or missing value receives no credit for its requirement.
- Unsupported-claim rate: emitted factual claims without valid scoped supporting
  evidence divided by emitted claims. Return null if no claims were emitted;
  pair with coverage so universal abstention cannot appear superior by omission.
- Citation precision: emitted citation links that independently support their
  attached claim divided by emitted citation links. A matching ID alone is not
  support. Separately count unknown references and uncited factual claims.
- Abstention precision: gold policy-abstain cases among predicted abstentions.
  Over-abstention: predicted abstentions among gold full/partial cases.
- Answer EM and token-F1: secondary only, with canonical requirement order and
  predeclared formatting/normalization; do not confuse lexical overlap with
  evidence support. Unsupported formats still count as failures in overall
  Track B results rather than disappearing from the denominator.

Compare values with independently specified annotation normalization, including
explicit units, signs, and permitted numeric tolerance. Freeze those rules on
development data. Do not call the production verifier to manufacture gold labels
or use metadata completeness as a correctness score.

Record which variant produced each result and run coverage/risk summaries at
its available policy settings. Confidence calibration is deferred until the
system exposes a scientifically defined confidence signal; no such signal
exists now. Do not substitute evidence metadata completeness for confidence.

## Reproducibility and uncertainty

Record repository commit plus dirty diff hash, Python/dependency versions,
dataset and manifest hashes, partition hash, input/gold record versions,
retrieval budget and query outputs, extracted candidates, effective lookup
config, predictions, and scoring version. Failed runs are reported as failures,
not silently discarded questions.

Measure retrieval, verification/lookup, rendering, and total latency separately
with a monotonic clock; report warm/cold conditions and sample counts. Record
memory measurement method and distinguish process RSS from Python-only allocation
tracking. Do not describe process startup or data-download time as retrieval.

For paired differences, propose 2,000 bootstrap replicates with seed 1729 over
document/question-family clusters, not independent passages. Report 95% intervals,
cluster counts, and the limits of a small pilot; these settings do not supply a
power analysis. Keep all related variants together within each sampled cluster.

## Current implementation and remaining decisions

The user approved the direction in principle and will arrange the second
annotator. Until then, all labels are `provisional, single-annotator`. The
synthetic harness validates input/gold separation, frozen-evidence policy
comparisons, core answerability/coverage/claim/citation metrics, and label/group
checks. The independent-annotation script calculates unweighted Cohen's kappa.
Typed gold/evidence records, source lineage, frozen-ranking Track B retrieval
metrics, primary paired cluster intervals, and diagnostic instrumentation are now
implemented and tested on synthetic examples. Real source adapters, independent
pilot annotation and held-out experiments remain later batches. Process RSS and
live retrieval timing are not measured by the frozen-ranking harness.

The corpus label gate is selected; final manual eligibility, annotation
adjudication, practical margins and the full held-out statistical plan are not
frozen by synthetic checks. No result in this batch establishes research benefit.
