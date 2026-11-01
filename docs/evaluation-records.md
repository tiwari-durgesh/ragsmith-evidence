# Evaluation records and source lineage version 0.2

This batch strengthens the synthetic Track A harness. Production inference,
verification, contradiction handling, and assessment schemas are unchanged.
All pilot labels remain `provisional, single-annotator`; no real pilot or
independent annotation has been performed. Python 3.11 remains unverified.

## Typed boundaries

`ragsmith.evaluation.records` provides frozen GoldFact, GoldRecord, and
FrozenEvidenceRecord containers. The existing production LookupQuestion model
continues to validate inference inputs. Frozen containers do not make the
underlying production Evidence objects deeply immutable; the harness checks
their fingerprints again after inference to detect mutation.

JSONL loading rejects nonobject rows, malformed syntax, duplicate object keys,
and nonfinite JSON constants, with filename/line-number context. Gold models
reject unknown fields, wrong types, missing/duplicate identifiers, unsupported
annotation states, contradictory field combinations, and nonfinite numeric
gold answers. A missing fact cannot list supporting evidence. A conflicted fact
requires at least two distinct source evidence IDs and has no single accepted
answer. Reserved gold fields in nested evidence metadata are rejected.

These checks do not prove that arbitrary text contains no answer leakage. Source
content necessarily contains factual answers. Human review must still ensure
that exported inputs contain only legitimate source information and declared
requirements, rather than annotation hints copied into source text.

## Required manifest

Version 0.2 requires a `lineage.json` file beside the frozen evidence JSONL,
or an explicit `--lineage PATH`. This is an evaluation-record change, not a
production assessment-schema change. Existing synthetic fixtures have migrated;
older custom bundles must supply a manifest instead of silently skipping checks.

The manifest has `schema_version: "1.0"`, a `sources` list and `evidence_links`
list. See the [complete synthetic fixture](../data/evaluation/fixtures/lineage.json).
No gold values or labels belong in it.

Each source declares:

- `source_id`: unique source record identifier.
- `document_id`, `document_version`: exact provenance identity used by evidence.
- `group_id`: source-family partition group; derived versions stay in that group.
- `source_uri`, `source_sha256`, `license`: declared source location, snapshot
  digest and rights record. Source files and rights are not authenticated by this
  schema alone.
- `parent_source_ids`, `transformation`: original sources have no parents;
  canonicalization, masking and synthetic_conflict records require known parents.

Each evidence link declares `evidence_id`, `source_id` and `fingerprint`.
The fingerprint is SHA-256 of compact, sorted-key UTF-8 JSON for the complete
Evidence dataclass, including content, metadata and all provenance fields.
Whitespace or metadata changes are material; reingestion or preprocessing
changes require a new reviewed mapping rather than silently reusing old IDs.

The synthetic fixture's declared source digests are hashes of JSON lists of
sorted evidence fingerprints for each synthetic document; they are not hashes
of real enterprise files. Real source snapshots need their actual byte hashes
recorded during collection. This batch checks digest syntax and record
consistency but does not fetch source URIs or recompute external source hashes.

## Validation sequence and scope

1. Load source declarations and validate unique source/evidence IDs, unique
   document/version declarations, digest syntax, known parents, same-group
   derivation and acyclic parent graphs. All versions of a document share its
   family group; even a no-evidence case must declare a known source family.
2. Validate system requests and their declared document scopes. Reconstruct
   typed frozen evidence records and compare every item with the registered
   document/version and full-record fingerprint.
3. Produce all baseline predictions without opening the gold file. Recheck
   evidence fingerprints and input/evidence/manifest file hashes after inference.
4. Open and validate gold labels. Match question/requirement IDs, link gold
   evidence to the declared frozen Track A set, check each requirement's document
   scope, and require source groups to agree with annotation groups.
5. Score and report the version, lineage status, and all four file hashes.

The existing checks against mixed origins, mixed partitions, missing predictions,
and source-family leakage remain. A run contains only one evaluated partition;
the new group check prevents annotation group names from overriding source
lineage. It does not discover undocumented near-duplicate reports, organizations,
or related tables. Those still require source preparation and review.

Track A gold evidence must be present in the frozen supplied set. Report v0.3
now supports Track B with a separate full-scope universe and frozen ranking log;
gold is validated against the universe and inference sees only the ranked subset.
Retrieval misses are scored, not excluded. See evaluation-metrics-and-resources.md.
The source-link validator does not infer truth, units, or entailment, and does
not use the production verifier to create gold labels.

## Run and migration

With a working project Python and package installation:

```powershell
python scripts/evaluate_synthetic.py
python scripts/evaluate_synthetic.py --directory data/evaluation/fixtures --lineage data/evaluation/fixtures/lineage.json
python -m pytest -q
```

For a custom bundle, provide inputs.jsonl, evidence.jsonl, gold.jsonl and
lineage.json; preserve IDs and parent/version mappings and record transformations.
Keep acceptable answers exclusively in gold.jsonl. Do not regenerate expected
labels from tested system output to make validation pass.

The v0.2 batch passed 445 tests; the expanded v0.3 suite passes 484 tests under
bundled Python 3.12.14.
The prior synthetic metrics are preserved. These are harness correctness checks,
not empirical evidence for the proposed research contribution.
