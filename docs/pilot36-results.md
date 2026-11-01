# Minimal pilot results — provisional, single-annotator

**18 independent source facts and 36 derived cases; no statistical or performance
claims are made from this pilot.** Facts share nine source contexts and are not
asserted statistically independent. Labels: **provisional, single-annotator**.

Frozen pipeline/baselines: `1b0df45c5e5fe443c5dd8be463ccf26dd9463de3`.
The src tree remained `3261c6087757b9f3d9aed1166e264de45ac4f479` before and
after the single run. Separate labels commit:
`52d0e1f5ac38270eb62a78824ebc921a5fa15842` (`locked provisional labels`).
Label SHA-256: `b027cb335ca582acccf672f6d25ad23406439ba56f3d20259630efe7407dd8e6`.
No dataset-derived reference scores, tuning, reruns, statistical intervals or speed claims.

| Baseline | Correct case labels / scored | Partial cases returning values / partial | Emitted claims |
| --- | --- | --- | --- |
| Extraction only | 18 / 36 | 9 / 9 | 45 |
| Binary sufficiency | 27 / 36 | 0 / 9 | 18 |
| Graded sufficiency | 36 / 36 | 9 / 9 | 27 |

All 36 labels passed schema/value/ID/null checks, including 18 unchanged
construction labels and 18 user-judgment labels. Distribution: 9 full, 9 partial,
18 abstain; no exclusions. The user's labels were committed, locked and used in
one frozen pipeline/baseline run. These are descriptive counts only; returning
values is not proof of factual correctness or citation precision. The graded
result on these constructed cases does not establish novelty, superiority,
generalization or real-world reliability.

**Failure cases:** 27 baseline/case label mismatches across 18 distinct cases.
The [complete case failure list](pilot36-failures.md) groups every affected case;
raw answers/citations are in data/evaluation/pilot36/results/failure-cases.json.

**LLM cross-check was not run.** The user has no OPENAI_API_KEY and explicitly
requested human-only evaluation. Neither label_pilot36_llm.py nor pilot36.py
compare was invoked. No external API was called, no other model substituted,
and no human inter-annotator agreement is claimed. A second human annotator for
30–50 questions remains required before paper results. Nothing was pushed.

The scope is controlled canonical source rows, native HTML ingestion, per-case
SQLite FTS retrieval and frozen baselines. It is not the full proposed hybrid RAG
system, a complete report corpus, or evidence for novelty or generalization.
