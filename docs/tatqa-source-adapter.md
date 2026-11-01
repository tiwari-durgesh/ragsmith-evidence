# TAT-QA source adapter and screening ledger

This batch implements the first offline preparation step for the approved
extraction-only pilot. It does not select a final pilot, produce model inputs
from answer labels or run a source-derived benchmark.

## Reproduce

With the pinned files already downloaded by the scope audit:

```powershell
python scripts/screen_tatqa.py --output data/evaluation/generated/tatqa-screening-001
```

Choose a fresh output directory for each run. No network is used. The loader
checks the training file's byte count and SHA-256 against
`docs/tatqa-scope-audit.json`, verifies its official pinned URL/revision, and
rejects a mismatch. A mutable adjacent download manifest cannot override these
checks. The audit file is a local trust anchor, not proof of source authenticity.

The command intentionally uses the source training split. Official development
and test data are not silently substituted. Changing the seed changes only the
review queue; it does not assign experimental partitions.

## Outputs and measured counts

The aggregate [screening audit](tatqa-screening-audit.json) records:

| Training preparation quantity | Count |
| --- | ---: |
| Source contexts | 2,201 |
| Original questions | 13,215 |
| Table-only single-span label gate passes | 1,462 (11.06%) |
| Questions outside that gate | 11,753 |
| Contexts with at least two gate passes | 355 |
| Conservative normalized-table groups among those contexts | 354 |

The 11.06% is a training-split label fraction. The earlier all-labeled-splits
fraction remains 1,804/16,546 = 10.90%; these denominators differ. Semantic
acceptance and its fraction remain **unmeasured**, represented as null. Zero
report identities have been verified. The 354 table groups are not a count of
independent original reports.

Generated artifacts stay under ignored local storage because they contain
upstream question text, table content or answers:

- `sources.jsonl` preserves all original cell strings, ragged row lengths,
  paragraph text/order and zero-based table/row/column locators. Its content
  digest excludes question annotations. Dataset snapshot hashes link each
  extracted context to the pinned source file. There is no automatic unit
  conversion, header inference, cell selection or canonicalization.
- `screening-ledger.jsonl` records every question's label-gate disposition and
  leaves metric/year/unit/cell binding, semantic eligibility, reviewer ID and
  reasons blank or pending. The sole automatic exclusion is outside the
  table-only single-span label gate; it does not assert semantic impossibility.
- `context-screening-ledger.jsonl` records every context, including contexts
  excluded from the paired-family queue for fewer than two table span labels.
- `COORDINATOR-annotation-aids.jsonl` holds upstream answers, answer type/source,
  scale and comparison flags separately. These aids are annotation-only and
  must not be fed to inference or shared with a blinded second annotator.
- `sampling-manifest.json` is a deterministic **draft screening queue**, with
  empty original report/organization/period/reference/reviewer fields and
  pending eligibility and partitions. It retains the approved targets of
  60 families, 12 development families, 48 held-out families and four conditions
  per family. Accepted families are zero because selection has not occurred;
  final sample shortfall is null, not an assertion that all 60 are unavailable.
- `summary.json` contains aggregate counts, provenance, attribution/license and
  explicit provisional/non-research status. Only this aggregate is copied into
  the repository; no upstream question text or raw answers are committed.

## Screening and grouping rules

Exact tables after whitespace normalization and case folding are conservatively
linked for the queue. Sort group hashes, shuffle with seed 1729, and keep all
members of each group adjacent in context-UID order. This operationalizes the
existing instruction to keep overlapping source material together; it does not
establish report identity. It may overgroup identical generic tables and cannot
detect every near-duplicate, report version or shared organization.

The coordinator must recover source report identities, inspect likely
near-duplicates and retain source-backed notes before assigning development or
held-out partitions. Known report versions and overlapping contexts must share
a group even when table hashes differ. Grouping overrides exact split quotas.
If identities cannot be recovered, document the independence limitation and
seek a decision before claiming document-disjoint results.

For each proposed family, manually establish two distinct direct extraction
facts with unambiguous metric, explicit year, unit and source cell/header
locators. Exclude comparison, arithmetic, counting, multi-span, text-only and
ambiguous cases as specified in the sampling plan. An upstream comparison flag
is only a screening aid; it is not a substitute for semantic review. Preserve
rejection reasons and complete bindings before making canonical rows.

All current pilot labels remain `provisional, single-annotator`. The source adapter has
no eligible/accepted semantic labels, independently reviewed annotations,
canonical Evidence records, experimental perturbations or final gold. The source
adapter's cell records deliberately cannot be passed directly to the existing
inference harness. A later validated transformation must construct its strict
evidence/lineage records while keeping source answers out of system inputs.

## Next batch

The [manual binding step](manual-cell-bindings.md) now implements strict
source-linked decisions and validated canonical transforms. It has been tested
on synthetic acceptances and pending-only real templates; real semantic
eligibility remains unmeasured. Final family selection, report identity,
independent annotation and held-out scoring retain their actual prerequisites.
