# Pilot sample size and selection plan

Superseded for the current pilot by [the minimal plan](minimal-pilot.md):
**18 independent source facts and 36 derived cases; no statistical or performance
claims are made from this pilot.** Facts share nine contexts and are not asserted
statistically independent. Labels remain provisional, single-annotator. The larger
plan below is historical; no further partition/harness expansion is authorized.

Proposal: 240 derived evaluation questions from 60 screened source-context
families, with four documented evidence conditions per family. This replaces
the earlier tentative 120-question draft; it is not a collected sample or a
claim of statistical power. Preserve the approximately 50-source-document
pilot objective where original source identities can be recovered.

The [source adapter](tatqa-source-adapter.md) now generates an offline screening
queue: 355 candidate training contexts in 354 conservative duplicate-table
groups. This is preparation only; accepted families, semantic eligibility and
original report identities have not been established. The aggregate counts
are recorded in [the screening audit](tatqa-screening-audit.json).
The [family builder](pilot-family-construction.md) now implements provisional
report grouping and controlled condition drafts. Real declarations remain pending;
the approved target and independent-review requirements are unchanged.

## Why 240

Four paired conditions directly test the research question: full support,
one missing requirement (partial), all required facts missing, and a conflicting
value (policy abstain). With 60 base families, this gives 60 full, 60 partial,
60 missing-abstain and 60 conflict-abstain cases. Pairing changes the available
evidence while holding questions and requirements fixed. It is more informative
than simply doubling unrelated QA rows, but the 240 cases are not 240 independent
observations.

The sample is deliberately a diagnostic stress distribution: half its policy
labels are abstain. It is not an estimate of real enterprise query prevalence.
Report each condition separately and any deployment-prevalence weighting only
with an independently justified prevalence estimate.

As an illustrative independence-only bound, a proportion near 0.5 over 192
held-out question rows has an approximate 95% half-width of 7.1 percentage
points. Using only 48 independent families gives roughly 14.1 points. These
are planning illustrations, not cluster-adjusted confidence intervals or a
power analysis. The pilot is for detecting large failures and estimating paired
variance; it cannot credibly certify a 1-point risk margin or tiny improvements.
Use observed development variance and the number of actual source clusters to
plan any confirmatory study before reviewing held-out system scores.

## Sampling procedure

1. Pin TAT-QA at the audited revision and enumerate the table-only single-span
   pool. There are 1,804 eligible labels and 430 contexts with at least two such
   questions; final manual compatibility remains unmeasured.
2. Prefer the source training partition for this custom pilot. It has no model
   training role here; using it keeps published dev/test available as later
   external challenge sets. Label-frequency auditing across splits did not
   evaluate a model. Never describe a custom split as the official TAT-QA test.
3. Sort candidate context UIDs, shuffle deterministically with seed 1729, and
   sample contexts rather than question rows. Log every rejected context and its
   reason. Require two direct extraction facts with unambiguous metric, year,
   unit and source cell. No arithmetic, counting, comparison, multi-span or
   text-only answers. Stop at 60 accepted families, or report an explicit shortfall.
4. Recover document/report, organization, period and near-duplicate identities
   before splitting. Raw context/table UIDs alone do not establish distinct
   source documents. Keep all variants, overlapping tables and report versions
   in the same group. If original identities cannot be established, flag the
   context-level independence limitation; do not claim document-disjoint results.
5. Target 12 development families (48 cases) and 48 held-out families (192 cases).
   Assign source groups before finalizing cases; grouping overrides exact ratios.
   Record achieved counts and never split a family/report merely to hit quotas.
6. Assemble four explicit evidence sets per family. The partial/missing cases
   deliberately withhold support from the declared experimental source scope.
   Conflict cases use clearly labeled synthetic perturbations of a separate
   evidence item. Record transformations, parent/source hashes and changed
   fields. Never suggest a manufactured conflict appeared in the original report.
7. Preserve source cells and headers in a provenance map when creating canonical
   rows. Never copy the gold answer into request fields. Dataset answer annotations
   may assist annotation but are gold-only, not extraction hints at inference.
8. Until the reviewer arrives, label every proposed pilot record exactly
   `provisional, single-annotator`. Do not run a real held-out benchmark or
   represent the single-annotator pilot as independently validated.

## Annotation workload and review

The user will arrange the second annotator. Use a small calibration set first;
measure actual annotation minutes and disagreements before committing to all
240 cases. Estimate work from those observations rather than claiming a fixed
annotation time. Both annotators independently label every pilot item, blinded
to system predictions and each other's decisions. Compute pre-adjudication
kappa and raw agreement, then retain adjudication notes and both original files.

Questions derived from one source context count as a source-linked stress family,
not as four newly observed natural questions. Keep native QA and derived-case
results separate. The restricted corpus is a first test of graded evidence
sufficiency; later domains, real missing/conflicting documents, and the proposed
hybrid retrieval matrix remain necessary for the broader research claims.
