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
The fixed local model passed its artifact checksum. The initial attempt completed
0/5; the single authorized retry after applications were closed completed 1/5
and then hit the available-RAM guard. No further 4B retries were made. The
[smaller-answerer amendment proposal](first-real-evaluation-smaller-model-amendment.md)
pins official Qwen2.5-1.5B-Instruct Q4_K_M provenance, checksum and Apache-2.0
license, and limits interpretation to policies conditional on that fixed answerer.
The user approved its synthetic checks. The [runtime check record](qwen15-runtime-checks.md)
documents a matching downloaded checksum, 5/5 successful synthetic runs at about
1.68 GiB peak resident memory, and one usable value-token likelihood calculation.
Planning runtime for 50 questions plus 20 calibration questions and all three
cached policy passes is about 2–2.5 CPU hours, subject to the documented extrapolation
limits. No evaluation data has been selected. Full prompt/interface freezing and
report-identity/conflict feasibility remain prerequisites; no API fallback is authorized.

The user accepted the runtime checks. The next [pre-selection amendment](first-real-evaluation-selection-amendment.md)
is plan only: recover and verify every pilot report family, exclude unidentified
or overlapping candidate families, and stop for a corpus/scope amendment if the
existing four-hour identity/feasibility budget cannot establish eligibility and
quotas. Seed 1729 fixes a source-only quota-constrained selection procedure for
20 development and 50 Stage-1 questions. Budget about 8–9 user hours in five
sessions, plus 2–4 hours of identity work; prepare a blinded 30-case second-human
packet. No selection or implementation was performed; execution awaits approval.

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
