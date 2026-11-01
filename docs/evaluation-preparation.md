# Retrieval export and reviewer calibration

This batch connects the existing SQLite FTS5/BM25 retriever to frozen-ranking
Track B and prepares local reviewer materials. It changes no production verifier,
contradiction policy or assessment schema. It introduces no corpus labels or
research results. All current pilot labels remain **provisional, single-annotator**.

## Native retrieval export

The input directory must contain `inputs.jsonl`, the registered full-scope
`evidence.jsonl` universe and `lineage.json`. Gold is not an input to preparation.
Use an already ingested SQLite database whose evidence fingerprints match the
declared universe:

```powershell
python scripts/prepare_evaluation.py rankings --directory data/evaluation/my-bundle --database data/processed/evidence.db --output data/evaluation/generated/native-run-001 --limit 100
python scripts/evaluate_synthetic.py --directory data/evaluation/my-bundle --rankings data/evaluation/generated/native-run-001/rankings.jsonl --k 10
```

The exporter uses SQLite's online backup to freeze one consistent database for
all questions. It reads the original database through a read-only connection;
temporary snapshot files are removed after the run. The audit records snapshot
SHA-256, bundle hashes, query expressions, per-requirement ranks, BM25 scores,
document/version/source metadata and truncation flags. The separate rankings file
contains only the strict IDs accepted by Track B. Limits are 1–100 per requirement.
Choose evaluation k no larger than the exported limit. A truncated export cannot
support evaluation of the unseen tail, and an untruncated search does not prove
corpus-wide answer completeness.

Each returned Evidence object must match its manifest fingerprint and the
question's declared universe. Unknown or changed hits fail the export, rather
than silently disappearing from rankings. Empty rankings remain explicit.
Internal consistency cannot prove that the declared universe contains every
relevant source, verify authenticity or rehash original documents. The exporter
does not measure live retrieval latency: backup overhead and temporary-snapshot
queries make it unsuitable for publication resource measurements.

## Reviewer packet workflow

```powershell
python scripts/prepare_evaluation.py calibration --directory data/evaluation/fixtures --output data/evaluation/generated/calibration-001 --annotators reviewer-A reviewer-B
```

Every export requires a new directory and refuses to overwrite existing work.
The command produces:

- `reviewer-packet.json`: questions, explicit requirements, supplied evidence and
  provenance, with neutral item/requirement/evidence/source IDs. Order is shuffled
  deterministically with seed 1729, independently of retrieval rankings.
- Two `reviewer-N-labels.jsonl` templates with distinct annotator IDs and blank
  question labels. Blank files are intentionally rejected by the agreement tool.
- `requirement-worksheet.json`: blank status/value/evidence/notes fields. Give
  each reviewer their own copy; requirement status kappa is not implemented.
- `COORDINATOR-ONLY.json`: private mappings back to original IDs, bundle hashes
  and manifest location. Do not share this file, gold or predictions with reviewers.

Give each reviewer the packet, their template, a separate worksheet copy and
[annotation guidelines](annotation-guidelines.md). Neither sees the other
reviewer's initial decisions. This is label/model blinding: document versions,
locators, question text or source content may reveal experimental conditions.
The packet contains registered extracted evidence, not original report pages;
before real source annotation, the coordinator must provide the matching original
pages and establish that the declared evidence scope is complete. The current
synthetic packet is only a calibration exercise.

Reviewers record each requirement as supported/missing/conflicted/not_adjudicable,
the exact acceptable values for supported facts, decisive evidence IDs and
source-backed notes. They then fill the question label using the guidelines.
For two requirements, support for both gives full; one supported and one missing
gives partial; no support gives abstain; any unresolved conflict gives abstain;
any not-adjudicable requirement gives not_adjudicable. Parsing failure alone does
not make human-supported text missing. These rules assess source evidence, not
whether this implementation can parse it.

After both files are completed independently:

```powershell
python scripts/annotation_agreement.py reviewer-1-labels.jsonl reviewer-2-labels.jsonl
```

Preserve original files, inspect the confusion matrix and disagreements, and
record adjudication separately with reasons. Do not calculate agreement after
replacing disagreements with a consensus. Templates and a successful script run
are not evidence of independent review. No automatic import of these worksheets
into gold or upgrade to reviewed status is implemented in this batch.

## Source preparation continuation

The pinned label gate, source adapter, screening ledgers and draft grouped
sampling queue are now implemented; see the [adapter guide](tatqa-source-adapter.md).
Semantic eligibility remains unmeasured. Next add source-linked manual screening
decisions and validated cell bindings before generating canonical evidence.
Independent annotation and real resource trials remain prerequisites for results.
