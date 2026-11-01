# Provisional manual screening and cell bindings

This preparation step validates explicit manual decisions and transforms accepted
source cells into the existing canonical table-row format. It changes no verifier,
contradiction policy, lookup config default or assessment schema. It does not
create final pilot families, experimental conditions, answer labels or gold files.

## Workflow

Generate a fresh template from the same pinned training file and trusted audit:

```powershell
python scripts/bind_tatqa_cells.py template --output data/evaluation/generated/tatqa-bindings-template-001
```

The template has one pending record per table-only single-span label-gate pass
(1,462 in the pinned training split). Use the previously generated source cells
and original report pages to review cases. Leave decisions pending when evidence
is insufficient. The schema is separate from the earlier screening ledger so
source records and immutable hashes do not need manual edits.

Each decision has exactly `question_id`, `source_content_sha256`,
`question_sha256`, `decision`, `reviewer_id`, `notes`, `rejection_reasons`,
`binding`, and `annotation_status`. Allowed decisions are pending/accept/reject.
The status must remain `provisional, single-annotator`. Accept/reject require a
nonempty reviewer ID and source-backed notes. Reject additionally requires
nonempty rejection reasons and no binding. Pending decisions have no binding
or rejection reasons. Only accepted decisions have bindings; extra fields such
as an expected value are rejected. Partial decision files are allowed; omitted
label-gate questions remain pending in the summary.

Do not treat acceptance as a model correctness label. The reviewer must establish
that the question asks directly for the bound metric/year/unit/value, without
arithmetic, comparison, counting or ambiguity. The program cannot infer that
meaning from the question or prove that the chosen unit applies to the value.

## Worked synthetic binding

For this source table, using zero-based coordinates:

| Row | Column 0 | Column 1 |
| --- | --- | --- |
| 0 | USD million | 2025 |
| 1 | Revenue | 145.00 |
| 2 | Profit | 30 |

A provisional acceptance for the direct revenue question binds:

```json
{
  "metric_cell_locator": "table:ctx/row:1/column:0",
  "year_cell_locator": "table:ctx/row:0/column:1",
  "unit_cell_locator": "table:ctx/row:0/column:0",
  "value_cell_locator": "table:ctx/row:1/column:1"
}
```

Put that object in the accepted decision's `binding`; preserve the generated
question/source hashes. It produces `Metric: Revenue; 2025: 145.00` with unit
`USD million` and all four cell locators in provenance metadata. The value comes
from the original cell, never a manually supplied value or upstream answer.
Only leading/trailing cell whitespace is trimmed. There is no comma removal,
currency conversion, arithmetic, alias expansion or numeric reformatting.

For this initial lossless transform, all four cells must be distinct. The metric
must be a row label to the left of the value, the year a column header above it,
and the unit an explicit header above it. The year must be exactly four digits.
Blank cells, semicolons and multiline canonical fields are rejected. Wider or
hierarchical header layouts need a later explicit transform; do not replace
their cells with guessed strings to make the binding pass.

A binding to another context, a stale hash, a moved header, a rejected label-gate
question or an unrecognized field fails compilation. Two accepted facts with
the same context/metric/year and different bound units also fail: the existing
verifier does not validate units. Distinct same-unit conflicting values remain
separate evidence items and reach the existing contradiction policy at inference.

Compile completed or partially completed decisions into a new directory:

```powershell
python scripts/bind_tatqa_cells.py compile --decisions data/evaluation/generated/tatqa-bindings-template-001/manual-decisions.jsonl --output data/evaluation/generated/tatqa-bound-001
```

The command reconstructs the source screen from the pinned dataset, verifies its
bytes against the committed audit, and checks the decision hashes. No editable
source export is trusted instead. Output directories must be new, protecting
existing manual work. Store generated upstream content in ignored local storage.

## Output boundaries and lineage

- `inputs.jsonl` contains one supplied decomposition per accepted original
  question, with metric/year and an explicit canonical document scope. There is
  no expected value or automatic multi-requirement family construction.
- `evidence.jsonl` contains the union of accepted bound rows in each accepted
  question's context. Duplicate identical bindings share an evidence item;
  conflicting bound rows remain visible. This is **accepted bound cells only**,
  not a complete source universe or a neutral corpus for retrieval benchmarking.
- `lineage.json` declares original extracted context and derived canonical
  source records, parent links and evidence fingerprints. Version hashes are
  digests of the extracted context or canonical binding artifact, respectively;
  dataset file hashes are recorded separately. They are not hashes of an
  original annual-report PDF. Groups explicitly say `context-pending` and cannot
  establish report-disjoint sampling or independent clusters.
- `transformations.jsonl` maps original question IDs to evidence IDs and the
  exact source-cell bindings. The coordinator decision log separately retains
  reviewer IDs, reasons and notes. Neither belongs in a blinded reviewer packet.
- `summary.json` reports accepted/rejected/pending counts, decision-file and
  source provenance hashes, provisional status and the restricted evidence
  scope. `pilot_selected`, `gold_generated` and `research_evidence` are false.

Compilation produces candidate evidence, not a verified answer. Existing lookup
must pass discovered candidates through the existing verifier when queried.
Synthetic integration tests exercise both full support and conflict abstention.
The pending-only real-data smoke check creates empty inputs/evidence and no
semantic acceptance decisions; it is not a source-derived model evaluation.

Independent reviewer decisions and adjudication are still outstanding. Do not
upgrade status or generate held-out results from this tool. The
[family construction step](pilot-family-construction.md) now adds source-report
declarations and grouped four-condition drafts, retaining unresolved prerequisites.
