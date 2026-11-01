# Minimal pilot: labeling guide

**18 independent source facts and 36 derived cases; no statistical or performance
claims are made from this pilot.** The facts share nine source contexts; this
wording counts distinct source facts, not statistical independence. Every label
is **provisional, single-annotator**. There is no human second annotator.

## Your task: fill 18 labels

Open `data/evaluation/pilot36/review.html` beside
`data/evaluation/pilot36/labels-to-fill.json`. The HTML groups the nine source
tables, highlights the 18 selected cells, shows original questions and units,
and lists the evidence actually available for every derived case. Coordinates
are zero-based. The JSON has 36 short rows:

- Fill only the 18 `null` labels marked `needs_your_judgment`. Full-scope cases
  require checking both source-cell mappings; partial-scope cases require
  checking the retained fact and that the other requested fact is unavailable.
- The other 18 rows say `determined_by_construction` and already contain
  `abstain`: nine empty-scope cases and nine explicit conflicting-value cases.
  These are controlled-policy labels, not independent human observations. Note
  any construction concern in `notes`; do not silently change a construction label.
- Use `full`, `partial`, `abstain` or `not_adjudicable`. Notes are optional except
  when you see ambiguity, a faulty mapping or an unexpected label.
- Judge only the supplied case scope. The original table lets you check mapping
  fidelity, but a fact deliberately removed from that case is unavailable.
  Preserve signs, currency, scale and year. Do not calculate or guess.

`full`: both requested facts are unambiguously supported. `partial`: at least
one is supported and at least one missing, with no unresolved contradiction.
`abstain`: neither fact is supported, or a requested fact has conflicting values.
`not_adjudicable`: ambiguity prevents a defensible decision.

### Five worked examples (synthetic; not pilot answers)

| Requested facts / supplied evidence | Label | Reason |
| --- | --- | --- |
| Revenue 2025 and profit 2025; same source/unit gives revenue 145, profit 30 | full | Both facts supported |
| Same request; only revenue 145 is supplied | partial | Revenue supported; profit unavailable |
| Same request; no factual rows supplied | abstain | Neither fact is available in scope |
| Same request; revenue 145 and revenue 150 have equal priority; profit 30 | abstain | Unresolved conflict blocks the answer |
| Two requested amounts; year/unit headers cannot be mapped reliably | not_adjudicable | Do not invent a mapping or unit conversion |

This is deliberately small enough for a focused review session; actual time is
not measured or guaranteed. No source questions or conditions were chosen using
pipeline output. No tuning on these cases is permitted.

## Freeze and source verification

Pipeline and all three baselines were tested (581 tests), committed in logical
batches, and `git status` was clean before pilot preparation began. Frozen commit:
`1b0df45c5e5fe443c5dd8be463ccf26dd9463de3`; src tree:
`3261c6087757b9f3d9aed1166e264de45ac4f479`. No file under src may change between
labeling and results. Pilot artifact and helper hashes are recorded in freeze.json.
Preparation ran source ingestion only, not inference. Nothing was pushed.

The dataset is TAT-QA, by Fengbin Zhu and coauthors (ACL 2021). The official
[pinned README license section](https://github.com/NExTplusplus/TAT-QA/blob/870accc41953dcde885aabeb963d94aabdc0fbc3/README.md#license)
was checked and states **CC BY 4.0** for the dataset; the repository's MIT code
license is separate. Attribution: [TAT-QA paper](https://aclanthology.org/2021.acl-long.254/).
Changes here are manual source-cell extraction, canonical HTML serialization,
paired questions, controlled removals and explicitly synthetic added values.

Format was verified against the official
[pinned training JSON](https://github.com/NExTplusplus/TAT-QA/blob/870accc41953dcde885aabeb963d94aabdc0fbc3/dataset_raw/tatqa_dataset_train.json)
and its downloaded bytes, SHA-256
`2df6e722cdbaaa37efcbfb280f5c9a15be29a6ec18f618ef936fe63cc6d07c69`.
The file is a JSON array of contexts with table, paragraphs and questions; tables
contain a uid and nested cell arrays; questions have uid, question, answer_type,
answer_from, answer and other fields. All 18 selected source questions are
`answer_type=span`, `answer_from=table`, with comparison=false. Original answer
annotations are not used to build values, human labels or reference scores.

Selection used a seed-1729 source-only review and nine explicit eligible contexts.
Repeated ambiguous row names were skipped. Source report identities and document
independence have not been established. The 36 cases are nine derived two-fact
questions under four scopes, not 36 independently sampled natural questions.
There are no new partitions, diagnostics or readiness reports.

## Save, lock, then run

Once your labels are complete, tell the assistant they are ready. With a working
project Python, these commands implement the required order:

```powershell
python scripts/pilot36.py lock
python scripts/label_pilot36_llm.py --packet data/evaluation/pilot36/public/cases.json --lock data/evaluation/pilot36/public/labels.lock.json --output data/evaluation/pilot36/llm
python scripts/pilot36.py compare --llm data/evaluation/pilot36/llm/labels.json
python scripts/pilot36.py run
```

The lock copies completed labels to private/human-locked.json, marks the copy
read-only and writes a public hash receipt. This is an accidental-edit guard plus
hash validation, not tamper-proof storage. Original labels are preserved; review
LLM disagreements separately rather than editing labels to improve results.

The optional auxiliary labeler uses **gpt-4.1-mini-2025-04-14**, via the OpenAI
Chat Completions API, and needs an API-enabled `OPENAI_API_KEY` environment
variable. Do not put the key in files or chat. The model was disclosed before
the script was written. Official [model documentation](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
lists it as deprecated; unavailable access causes failure, not model substitution.
[API authentication](https://developers.openai.com/api/reference/overview#authentication)
documents bearer credentials. The account's access/billing have not been verified.

No API calls have been made. The labeler refuses to run without a label-lock
receipt. It reads only the public case packet and hash receipt, never accepts
a human-label-file argument, and never opens that file. The model receives only
one case's question/requirements/evidence per request, with no labels, source
cards, condition tags, pipeline output, file tools or local filesystem access.
Comparison is a separate operation that reads the human file after LLM labeling.
This prevents label exposure to the model; it is not a general OS sandbox for
arbitrary modified Python programs. Calls are API-billed, have no automatic retry,
and preserve prompt, model, request IDs and usage. Model output is provisional.

**Human/LLM disagreements are not human inter-annotator agreement.** No kappa,
second-human validation or independent reliability claim is reported. Do not
replace the planned human second annotator with this model.

The single pipeline run is blocked until labels are locked. It performs native
HTML ingestion's prepared per-case SQLite FTS retrieval, followed by the frozen
extraction-only/binary/graded baseline function. Source-cell extraction and
decomposition are manually supplied, not automatic parsing of arbitrary reports.
Top-k is fixed at 10 before results; no real model output has been inspected.
Results and failure cases will be written once under pilot36/results. The table
reports case-label counts and descriptive emitted/partial-return counts, not
factual correctness, citation precision, performance or statistical claims.
Dataset-derived reference scores are omitted entirely. A second run is refused.
Python 3.11 remains unverified; validation uses bundled Python 3.12.14.
