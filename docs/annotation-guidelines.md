# Reviewer guide for evidence sufficiency annotations

Version 0.1. Audience: the primary annotator and independent second annotator.
All current pilot/fixture labels are `provisional, single-annotator`.
Synthetic fixture authorship is not a claim that a human reviewer has annotated
the data. The user will arrange the second annotator. No real reviewed pilot
labels are supplied in this batch.

## What you receive and what you must not see

Receive the question, explicit fact requirements, complete declared source scope,
source snapshots/locators, provenance map, and whether a case is a controlled
removal or synthetic-conflict condition. Do not see model answers, system
statuses, confidence/metadata scores, or the other annotator's judgments before
submitting your own file. Do not infer what the system can parse when deciding
whether a human can answer from the source.

Annotate the full declared evidence condition. A requirement absent from a
retrieved top-k set but present in that scope is supported at corpus level.
For a separate Track A supplied-set label, inspect the explicitly fixed set;
do not mix those two label targets in the same agreement file.

## Requirement-level decisions

1. Identify the requested entity, metric, year, units and permitted source scope.
2. Locate an explicit supporting cell/span. Record exact source version and
   locator, acceptable value(s), units, and supporting annotation/evidence IDs.
3. Search the rest of the declared scope for incompatible values or version/unit
   ambiguity. A similar topic without the required fact is not support.
4. Assign one state:
   - `supported`: unambiguous fact with a source-linked value.
   - `missing`: required fact is absent after inspecting the entire declared scope.
   - `conflicted`: incompatible values exist and no agreed precedence rule resolves them.
   - `not_adjudicable`: unclear entity/year/unit, insufficient source quality, or
     unsupported reasoning prevents a dependable annotation. Explain the ambiguity.
5. Keep alternatives and notes for conflicts; do not choose a preferred source
   ad hoc. Do not treat every absence of a numeric string as missing if the
   answer is stated in prose or an equivalent representation.

The initial extraction pilot excludes arithmetic, counting, comparison,
multi-span and text-only native questions. Record such cases as screening
exclusions, not as hard questions the system somehow answered correctly.
Within intentionally included diagnostic tests, a human-readable text fact can
still be supported even if the current production verifier returns unverified.

## Question-level policy label

- `full`: every requirement is supported.
- `partial`: at least one is supported, at least one is missing, and none conflict.
- `abstain`: none is supported, or any requirement conflicts under the current
  conservative policy. Keep conflict flags separately from missing facts.
- `not_adjudicable`: any requirement remains unresolved/ambiguous. Retain the
  case for adjudication and report the excluded count; do not silently drop it.

The system status `unverified` is not a human gold label. Gold is determined
from source evidence, not from parser capability or the tested verifier's output.

## Worked examples

All values and documents below are invented training examples, not real company data.

| Declared evidence and requirements | Requirement judgments | Question label and explanation |
| --- | --- | --- |
| Source table: Revenue 145 million USD; Profit 30 million USD, both 2025. Ask both. | Revenue supported at row 2; Profit supported at row 3. | full: both requested facts have explicit support. |
| Same question, declared controlled evidence condition contains Revenue row only. | Revenue supported; Profit missing in that declared condition. | partial: answer revenue and explain the missing profit. Do not consult a deliberately excluded parent row. |
| Ask 2025 employee count; scope contains only revenue/profit rows. | Employees missing. | abstain: topic relevance is not the required employee fact. |
| Two scoped sources give Revenue 145 and 150 million USD for the same entity/year. | Revenue conflicted, record both source locations. | abstain under the fixed policy; do not use majority vote or recency without an agreed precedence rule. |
| Paragraph says revenue was 145 million USD in 2025; no table. | Revenue supported by paragraph. | full for human answerability. Production unverified is a system failure, not evidence that the gold answer is missing. Outside the native table-only pilot, retained as a diagnostic. |
| Value 145 is visible but header/units are cropped or year could be 2024/2025. | not_adjudicable, specify the ambiguity. | not_adjudicable until resolved; no guessed year/unit. |

If the full corpus contains profit but retrieval misses its row, corpus gold
remains full. A response containing only revenue has incomplete corpus coverage,
even if its claims are faithful to the retrieved set. Record the two evaluation
targets explicitly instead of changing gold to partial after seeing retrieval.

## Value and citation rubric

Retain units/signs and source precision. The initial scorer permits finite
numeric equivalence such as 145 and 145.00; otherwise it uses exact trimmed text.
It performs no currency conversion, comma stripping, percent scaling, arithmetic
or tolerance matching. Put agreed alternative representations in gold-only
`acceptable_values` and record the reason. Do not normalize away a unit mismatch.

A valid citation must support the exact attached metric/entity/year/value and
point to the correct source version and locator. A real but unrelated row ID
does not count. Distinguish missing citation links, incorrect links, and a correct
source for a value that is nevertheless disputed by the scoped evidence.

## Reviewer file and agreement command

Keep the original decisions in two separate UTF-8 JSONL files. Each row has
exactly these fields (example only):

```json
{"item_id":"family-001/partial","annotator_id":"reviewer-A","label":"partial"}
```

The second file must use a different annotator ID and the same item IDs.
Use `question_id/requirement_id` as item_id in separate requirement-level files;
the current script's supported categories are question-level labels, so do not
mix requirement statuses into those files. Requirement-level state kappa would
need an explicitly extended category set in a later batch.

```powershell
python scripts/annotation_agreement.py reviewer_A.jsonl reviewer_B.jsonl
```

The script aligns by item ID, not line order; rejects duplicate IDs, mismatched
item sets, unknown labels, and identical annotator IDs; and reports the confusion
matrix, raw agreement, expected agreement, kappa and disagreement IDs. No labels
are silently intersected or dropped. It uses unweighted nominal categories,
including `not_adjudicable`, because no ordinal distance is assumed.

Kappa is `(p_observed - p_expected) / (1 - p_expected)`, with expected agreement
computed from both annotators' marginal frequencies, following the
[documented definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html).
Worked arithmetic: A labels full/full/partial/partial; B labels
full/full/full/partial. Observed agreement is 0.75, expected agreement 0.50,
and kappa 0.50. If both give a single category for every item, expected agreement
is 1 and kappa is undefined; the script reports null and a reason, not 1.0.

Compute agreement before adjudication, report class prevalence and confusion,
and avoid treating an arbitrary kappa threshold as universal quality proof.
Review disagreements together, preserve both original files, and write a third
adjudication log with source-backed explanations. Do not overwrite initial labels
or mark them independently validated merely because the script ran. The current
harness intentionally accepts only provisional labels; a future version must
explicitly add reviewed/adjudicated status after the second annotation pass.
