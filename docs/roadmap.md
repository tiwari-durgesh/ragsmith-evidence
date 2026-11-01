# Research roadmap

The current minimal pilot has **18 independent source facts and 36 derived cases;
no statistical or performance claims are made from this pilot.** Distinct facts
share nine source contexts and are not asserted statistically independent. All
labels remain **provisional, single-annotator**.

Current status: human labels were locked and one frozen pilot/baseline run is
complete, without tuning. **LLM cross-check was not run**; the user explicitly
skipped the labeler and comparison because no API key is available. No external
API call or model substitution occurred. See [results](pilot36-results.md).

**Paper-results gate: a human second annotator must independently label a
30–50-question subset before any paper results.** Preserve independent labels,
measure human agreement before adjudication, and retain source-backed resolution
notes. An LLM cross-check cannot replace this requirement.

The [first real evaluation preregistration proposal](first-real-evaluation-preregistration.md)
defines the primary endpoint, risk gates, sample-size limits, local model budget,
annotation effort and report-exclusion rules. It is plan only, awaiting approval;
no fresh evaluation sample has been selected. Commit and approve the specification
before selection or implementation. Approximately 100 clustered questions are
an estimation study, not adequate evidence for a tight comparable-risk claim.

The original specification is preserved by local tag `prereg-v1` at `6b1d04e`.
The [feasibility and staged-plan amendment](first-real-evaluation-feasibility-amendment.md)
proposes 50 questions first, shared question-only decomposition, and a confidence
threshold calibrated only on separate development data. Feasibility remains
unestablished: context-level leads cannot certify exclusion of pilot reports or
genuine conflicts. Do not select evaluation data until source identities and
stratum quotas are verified and the revised plan is approved. If the declared
four-hour recovery budget cannot establish the quotas, request a corpus/scope
amendment before selection; do not manufacture or silently replace conflicts.
The fixed local model passed its artifact checksum, but the requested five-
question hardware smoke remains incomplete: the first loading attempt hit the
available-RAM guard, and no generation completed. Establish hardware feasibility
before evaluation selection; no smaller model or API fallback is authorized.

1. Complete the 18 human-judgment labels, save and lock them. Construction
   determines the remaining 18 labels. Preserve the frozen src tree.
2. The auxiliary LLM labeler and comparison were skipped by explicit instruction.
   No external API or replacement model is authorized for the completed pilot.
   An LLM comparison would not be human inter-annotator agreement.
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
