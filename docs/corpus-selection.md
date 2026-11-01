# Extraction-only corpus selection and source audit

Verified November 1, 2026. Primary sources were read, and pinned TAT-QA JSON
files were counted locally. This document corrects the earlier draft's incomplete
license description: the TAT-QA repository's MIT code license is not its dataset
license. No real pilot question has been annotated or evaluated yet.

## Candidates actually considered

| Dataset | Source-verified format and license | Decision and reason |
| --- | --- | --- |
| TAT-QA | The [official README](https://github.com/NExTplusplus/TAT-QA/blob/870accc41953dcde885aabeb963d94aabdc0fbc3/README.md#license) explicitly identifies the dataset as CC BY 4.0; the separate [code LICENSE](https://github.com/NExTplusplus/TAT-QA/blob/870accc41953dcde885aabeb963d94aabdc0fbc3/LICENSE) is MIT. Raw JSON contains contexts with table, paragraphs, questions, answer types and origins. | Choose its table-only single-span extraction screen as the first eligible pool. Explicit answer-type/source labels allow arithmetic and counting to be excluded without guessing from prose. |
| FinQA | The [official README](https://github.com/czyssrs/FinQA#dataset) documents pre_text, post_text, table, id, and qa fields including question, reasoning program, gold_inds, and exe_ans. The [repository LICENSE](https://github.com/czyssrs/FinQA/blob/main/LICENSE) is MIT; a separate dataset-specific license statement was not identified in the inspected README. | Defer: its documented program/execution task emphasizes numerical reasoning and does not provide TAT-QA's convenient extraction type/source gate. No verified extraction-only fraction is claimed for FinQA. |

These are the two datasets inspected for this decision. Other names in the
research proposal remain literature/benchmark investigation tasks, not datasets
whose access, license, or compatibility has already been verified here.

The [TAT-QA paper](https://aclanthology.org/2021.acl-long.254/) establishes the
hybrid text/table task; the [FinQA paper](https://aclanthology.org/2021.emnlp-main.300/)
describes its annotated reasoning programs. Neither supplies native gold labels
for our three-way evidence-sufficiency task. Derived questions and controlled
missing/conflict conditions require new annotations and explicit attribution.

## Exact label screen and observed fraction

Pinned revision: `870accc41953dcde885aabeb963d94aabdc0fbc3`.
See [the machine-readable audit](tatqa-scope-audit.json) for SHA-256 hashes,
source URLs, byte sizes, field inventory, and the full label distributions.

| Released labeled split | Questions | span or multi-span | Fraction | span AND table-only | Fraction |
| --- | ---: | ---: | ---: | ---: | ---: |
| train | 13,215 | 7,367 | 55.75% | 1,462 | 11.06% |
| dev | 1,668 | 918 | 55.04% | 171 | 10.25% |
| test_gold | 1,663 | 924 | 55.56% | 171 | 10.28% |
| all labeled files | 16,546 | 9,209 | 55.66% | 1,804 | 10.90% |

The chosen label-based eligibility rule is `answer_type == "span"` and
`answer_from == "table"`. Text-only spans, multi-span, arithmetic and count
questions are excluded from this initial pool. General extraction labels cover
55.66%, but that is not our operational scope. The narrower pool covers 10.90%.

There are 430 released contexts with at least two questions passing the narrow
label gate. That supports screening for paired facts; it does not prove those
facts satisfy the additional engine constraints below. The source README's
headline is 16,552 questions/2,757 contexts; the pinned labeled files counted
here contain 16,546 questions/2,756 contexts. Do not use the headline count as
the denominator for these measured fractions or infer labels for missing items.
The cause of the release/headline discrepancy is not established by this audit.

### Manual gate after the label screen

For actual Phase 4 engine use, require an unambiguous existing table cell, an
explicit year, identifiable metric and unit, and a faithful source-linked
single-year row representation. Exclude comparisons, selecting a largest/smallest
value, ambiguous unit/date references, calculations, and unsupported text spans.
Gold source answers are used to annotate and screen, never as inference inputs.

The fraction surviving this additional manual gate is **not measured yet**.
10.90% is an eligibility upper bound, not a claim that all 1,804 examples run
through the existing verifier unchanged. Report the manual gate's accepted and
rejected counts with reasons before any real pilot result. If insufficient
eligible families remain, revise the pilot size transparently rather than
broadening scope silently.

## Label format inspected from the files

Each context contains `table`, `paragraphs`, and `questions`. `table` has `uid`
and a nested cell array named `table`; paragraphs have `uid`, `order`, `text`.
Question keys observed in train/dev include `uid`, `question`, `answer_type`,
`answer_from`, `answer`, `derivation`, `rel_paragraphs`, `req_comparison`,
`scale`, and `order`. The test-gold release additionally has fields such as
`facts`, `mappings`, `consts`, and `tree_derivation`; do not assume these exist
across splits or use them in model/retrieval inputs.

Observed answer types are `span`, `multi-span`, `arithmetic`, and `count`.
Origins are `table`, `text`, and `table-text`. Train spans and multi-spans store
answers as lists; arithmetic answers include numbers and an exceptional string;
count answers are strings. Inference must not rely on a guessed universal answer
type. The source README also notes that TagOp preprocessing heuristically creates
facts/mapping fields; use raw source snapshots and document transformations.

## License and artifact handling

For TAT-QA adaptations preserve attribution, the CC BY 4.0 link, the pinned
source/revision, and a description of changes, consistent with the
[license deed](https://creativecommons.org/licenses/by/4.0/). Keep MIT notices
if reusing the upstream code; this project does not import its training stack.
Retain source-report provenance and review separate rights before republishing
original reports. Dataset access is not a claim of ownership over source PDFs.

Raw source snapshots and upstream notices are stored only in ignored
`data/evaluation/generated/tatqa-source`. Commit only aggregate audit counts,
hashes, our scripts, and original synthetic fixtures; do not commit source
question text or raw answers in this batch. All real pilot labels remain
`provisional, single-annotator` until the second annotator independently reviews
them and disagreements are adjudicated under a future schema revision.

## Reproduce the audit

With an installed package and working project Python:

```powershell
python scripts/audit_tatqa.py --fetch --output docs/tatqa-scope-audit.json
python scripts/audit_tatqa.py --output docs/tatqa-scope-audit.json
```

Only `--fetch` accesses the network. The offline audit verifies data-file hashes
against the pinned source manifest before counting. Inspecting type frequencies
does not evaluate models or create our held-out labels.
