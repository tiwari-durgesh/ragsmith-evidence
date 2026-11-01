# Minimal pilot results — awaiting locked labels

**18 independent source facts and 36 derived cases; no statistical or performance
claims are made from this pilot.** Facts share nine source contexts and are not
asserted statistically independent. Labels: **provisional, single-annotator**.

Frozen pipeline/baselines: `1b0df45c5e5fe443c5dd8be463ccf26dd9463de3`.
No dataset-derived reference scores, tuning, statistical intervals or speed claims.

| Baseline | Correct case labels / scored | Partial cases returning values / partial | Emitted claims |
| --- | --- | --- | --- |
| Extraction only | Awaiting labels and one run | Awaiting labels and one run | Not run |
| Binary sufficiency | Awaiting labels and one run | Awaiting labels and one run | Not run |
| Graded sufficiency | Awaiting labels and one run | Awaiting labels and one run | Not run |

18 missing/conflict labels are determined by construction. The other 18 full/partial
case labels need the user's source-mapping judgment. Until those are saved and
locked, the pipeline/results run and the LLM labeling stage remain blocked.

**Failure cases:** not yet observed because no pilot inference has run. This does
not mean zero failures. The one-shot run writes results/results.md and a complete
failure-cases.json list locally; not-adjudicable cases are counted and excluded.

The scope is controlled canonical source rows, native HTML ingestion, per-case
SQLite FTS retrieval and frozen baselines. It is not the full proposed hybrid RAG
system, a complete report corpus, or evidence for novelty or generalization.
