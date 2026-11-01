# Report declarations and controlled family drafts

This batch implements provisional report grouping and the approved four-condition
family structure. It changes no production verifier, contradiction policy or
assessment schema. All current labels remain `provisional, single-annotator`.
No real pilot family, independent annotation, gold file or research result has
been created.

## Declaration workflow

Create fresh templates for the 355 paired candidate training contexts:

```powershell
python scripts/build_pilot_families.py template --output data/evaluation/generated/pilot-family-template-001
```

Both templates pin the context's source content SHA-256 and require explicit
reviewer notes for completed declarations. Missing declarations remain pending.

`report-identities.jsonl` has exactly context_id, source_content_sha256, status,
report_group_id, organization, period, source_reference, reviewer_id, notes and
annotation_status. Status is pending or declared. Declared identities require
all text fields. Pending identities must leave report/organization/period/reference
empty. Source references and notes should establish which original report and
version the context came from. A declaration is a manual assertion, not independent
verification. Use one stable report_group_id for known overlapping report material
and versions; review near-duplicates that exact table matching misses.

`family-decisions.jsonl` has exactly context_id, source_content_sha256, status,
question_ids, conflict_value, reviewer_id, notes and annotation_status. Status is
pending or ready. Ready declarations require exactly two distinct, accepted
question IDs from the context, two distinct metric/year keys and source value
cells, source-backed notes, and an explicit synthetic conflict value for the
first requirement. Pending declarations have empty question_ids and conflict_value.
The synthetic value must differ numerically or textually from the original;
equivalent values such as 145/145.00, nonfinite numbers, semicolons and multiline
values are rejected. The first declared fact is retained in partial cases and
perturbed in conflict cases, so preserve that order in the declaration.

Compile using completed manual cell bindings and declarations:

```powershell
python scripts/build_pilot_families.py compile --bindings data/evaluation/generated/tatqa-bindings-template-001/manual-decisions.jsonl --identities data/evaluation/generated/pilot-family-template-001/report-identities.jsonl --families data/evaluation/generated/pilot-family-template-001/family-decisions.jsonl --output data/evaluation/generated/pilot-family-draft-001
```

The command reloads the pinned training source, reconstructs its screening queue,
and compiles accepted bindings. It checks declaration hashes and refuses existing
output directories. Declaration bytes and dataset provenance are hashed in the
summary; coordinator copies preserve identity references and decision notes.

## Grouping and proposed partitions

Duplicate-table links and declared report/version links are merged transitively.
If any context in a connected group lacks a declaration, that group cannot produce
family drafts. A context UID, table hash or a filled reference field alone does
not establish document independence. Unresolved links and known duplicates remain
visible in the coordinator group report.

Ready families follow the previously seeded screening queue, up to the approved
60-family target. All selected members of a connected report group receive the
same proposed partition. Assign groups to development until at least the target
12 families is reached, then assign remaining groups to held-out. Grouping takes
priority over exact counts: a large group may overshoot development and leave
fewer than 48 held-out families, or none. The summary reports achieved counts and
selected source clusters; it does not silently split a report to satisfy quotas.
Partitions are draft planning assignments, not authorization to run held-out scores.
Freeze and review the resulting manifest before any such run.

The target_shortfall is the number of currently available drafts below 60. With
all declarations pending it is 60; this does not establish that the dataset lacks
60 eligible families. Contexts outside the target and pending decisions are logged.

## Four controlled evidence conditions

Each draft family uses exactly two manually bound facts. Its generated question,
metric/year requirements and explicit document scope are identical across cases:

| Condition | Supplied evidence |
| --- | --- |
| full | Both bound facts |
| partial | First fact only |
| missing | Neither fact |
| conflict | Both facts plus a synthetic alternative value for the first |

The evidence scope is **two bound facts under controlled interventions**, not
the complete original report or a neutral retrieval benchmark corpus. These cases
are derived stress questions, not original natural multi-fact TAT-QA questions.
Removing a row means withholding it from this declared experimental scope; it
does not assert that the original report lacked that fact.

Each condition gets an explicit artifact version and source transformation
(canonicalization, masking or synthetic_conflict), with parent links back through
the accepted canonical cells to the extracted context. Artifact version digests
describe logical construction records, not original PDF files. Evidence retains
cell locators and parent evidence IDs. The private condition log records removed
IDs and the synthetic before/after content, so a manufactured conflict cannot be
mistaken for an observed report contradiction.

`inputs.jsonl`, `evidence.jsonl` and `lineage.json` use existing strict types and
can feed reviewer packet preparation. There is deliberately no gold.jsonl. Keep
all COORDINATOR files private: they reveal conditions, decisions and identities.
The family manifest and summary remain provisional/non-research. Synthetic tests
exercise full/partial/abstain/abstain with the unchanged verifier; they do not
validate real labels or the research hypothesis.

The real-data smoke check generated 355 pending identity/family templates and
compiled them with pending bindings into zero drafts. Real semantic eligibility,
source-report recovery and independent review remain outstanding. The separate
[resource runner](resource-trials.md) now implements process RSS and fresh/warmed
timing diagnostics while those annotation prerequisites remain pending.
