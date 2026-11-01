# Research roadmap

The current minimal pilot has **18 independent source facts and 36 derived cases;
no statistical or performance claims are made from this pilot.** Distinct facts
share nine source contexts and are not asserted statistically independent. All
labels remain **provisional, single-annotator**.

1. Complete the 18 human-judgment labels, save and lock them. Construction
   determines the remaining 18 labels. Preserve the frozen src tree.
2. Obtain auxiliary LLM labels only after that lock, without exposing human
   labels. Review disagreements separately. This is **not human inter-annotator
   agreement** and does not supply a second human annotator.
3. Run the frozen pipeline and baselines once without tuning. Publish only the
   small descriptive case table and failure list as provisional internal findings;
   omit dataset-derived reference scores and all statistical/performance claims.
4. **Before any paper results, an independent human second annotator must label
   a 30–50-question subset.** Preserve both independent original label sets,
   measure human agreement before adjudication, and record source-backed
   adjudication. The LLM cannot satisfy this requirement.
5. Before research conclusions, expand and validate source-report identity,
   representative workloads, complete evidence scope, evaluation controls and
   the broader hybrid architecture described in the research proposal.

Stop additional harness infrastructure work. Add tooling only when this pilot
needs it. No push until Phase 5 is complete and the user's push instruction applies.
