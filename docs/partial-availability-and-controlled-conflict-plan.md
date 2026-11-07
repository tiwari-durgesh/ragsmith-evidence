# Planning note: genuine partial availability and a controlled conflict test

November 7, 2026. **Plan only.** This is not an amendment or authorization to
inspect sources, author or select questions, run systems, or change quotas.
The conflict gate remains closed. This note uses only existing aggregate and
methodology documents.

## What the partial audit establishes

The [aggregate audit](source-genuineness-verification-results.md) found one
proposed witness, 17 groups with no witness among the first three checked pairs,
and two unresolved groups. The proposal is awaiting human confirmation. The
two strata each contributed ten groups and one unresolved result; the only
proposed witness came from the 348-group stratum. On the original 202/348 lead
frame, the observed proposed yield is 1/20 (5.0%) unweighted and
`(202/550)(0/10) + (348/550)(1/10)` = **6.33%** weighted.

| Interpretation of the bounded audit | Raw sample interval | Weighted interval |
| --- | ---: | ---: |
| Existing proposal is confirmed; zero to both unresolved groups turn positive | 5–15% | 6.33–16.33% |
| Existing proposal is also allowed to fail confirmation | 0–15% | 0–16.33% |

These are **sensitivity intervals**, holding the 17 bounded-search negatives
fixed. They are not confidence intervals or bounds on all genuine partials in
the frame. A negative can hide a valid pair outside the first three, and the
lead frame omitted other surviving groups. There is no defensible nontrivial
interval for the underlying corpus-wide availability rate from this audit alone.
This distinction respects [Option C](option-c-excerpt-corpus-amendment.md): the
content groups do not establish independent reports, and no inferential or
performance claims follow from these figures.

## How to estimate availability with actual questions

Under the current amendment, a partial question is a neutral T1/T2/T3 request
for exactly two direct extraction facts. A human author confirms the wording and
manual decomposition. One fact must have an unambiguous, correctly scoped
source value and citation; the other must be plausible for the entity/period
and absent from **all** excerpts in the scope fixed before authoring. Freeze
search terms and scan the complete tables, headers, notes, cross-references and
relevant prose independently of keyword hits. Retain resolving evidence. A
retrieval miss, unsupported format, unreadable cell or unresolved scope does
not establish absence. No arithmetic, source deletion or upstream QA labels.
See the [authorship and absence rules](thirty-question-reduced-scope-amendment.md)
and [Option C scope rules](option-c-excerpt-corpus-amendment.md).

If separately approved, run a **40-group source-only authoring audit**, fixed in
advance: 15 explicit-unit leads, 15 other two-fact leads, and 10 surviving groups
outside the two-fact lead frame. The third stratum checks whether the mechanical
filter misses real opportunities. Freeze the updated exclusion graph, all three
frame sizes and the group rosters before reading any new source. Take the first
eligible groups in each stratum using the existing seed-1729 source-screen order,
excluding the already reviewed partial sample from this fresh draw. Report the
fresh frame separately; do not pool the old witness search with this audit. Keep
timeouts and exclusions visible; no replacement draws or success-based top-ups.

1. Codex prepares complete source packets. For each group, fix entity, metric,
   period and unit scope first. Inventory up to six plausible pairs by taking up
   to two per approved template, sorted by canonical entity, metric and period
   with source anchors as tie breaks. Use source-attested
   periods and related metrics; do not manufacture an absence by narrowing scope
   or pairing unrelated slots. Record the inventory before checking absence.
2. Screen the frozen pairs against the full source rubric in template and
   canonical order. The user, as accountable author, verifies up to the first
   two passing pairs per group as actual audit-only drafts, with wording,
   decomposition and support/absence records. Log why each check fails, is not
   reached or cannot be completed. A second human rechecks every proposed positive
   and up to ten nonpositive groups in the existing seed-1729 `reviewer` order,
   blinded to first-pass findings, intended status and all system outputs. Disagreement
   stays unresolved unless source evidence resolves it. No independent reviewer
   means no independently checked yield; report provisional counts only.
3. Report verified distinct questions per inspected group and groups with at
   least one verified question, by stratum. Deduplicate underlying requested
   facts, including the absent fact. Track negatives after checking all frozen
   pairs, unfinished checks and capped searches separately. Report raw and
   frame-weighted yields
   for the bounded procedure, with unresolved-as-no and unresolved-as-yes
   sensitivity endpoints for the group rate. Those endpoints do not bound the
   yield beyond the search cap. Do not multiply the group rate by five or treat
   repeated facts as additional supply. Report how many distinct fact pairs
   survive and whether they are concentrated in a few groups; neither a count
   nor a projection certifies joint partition capacity.

Budget **at most 15 combined active person-hours**: up to 8 for packet preparation
and first-pass source checks, 4 for the user's authoring and verification, and 3
for independent review and reconciliation. Aim for up to 10 minutes of first-pass
inspection per group within the preparation/checking budget. If full absence
verification or independent review cannot fit, record unresolved or unreviewed
and stop at the cap. These are budget estimates, not measured throughput.
Audit drafts stay private and unassigned. No candidate pool, study partition,
calibration or performance run is produced; later use of any audited draft
requires an explicit eligibility rule agreed before executing this audit.

## Is nine plus six realistic?

**Possible, but not a reliable planning assumption.** There is one provisional
opportunity and none human-confirmed. If the current weighted rate repeated,
and each successful group yielded one distinct partial, finding 15 would take
roughly 237 lead-group checks before losses to deduplication or allocation. That
is budget arithmetic, not a corpus estimate. The deeper audit could find more
per group, but 9 evaluation and 6 development partials must fit the other strata
simultaneously, in six and four separate groups with at most five questions per
group and no reused requested facts. The current evidence establishes neither
that capacity nor a true shortage.

The [preregistered primary metric](first-real-evaluation-preregistration.md#1-hypothesis-primary-metric-and-fixed-decision-rule)
is graded minus confidence-abstainer coverage of correctly returned and cited
supported requirements on corpus-partial evaluation questions. With one
supported requirement per question it is a mean of paired differences. Under
Option C it is descriptive. Whole-evaluation unsupported-claim risk is separate;
changing the mix can change pooled risk even when within-stratum behavior does
not change.

| Future option, only after separate approval | Effect on the metric and claims |
| --- | --- |
| Reduce the genuine partial quotas | Keep the endpoint and strict partial definition. Fewer evaluation partials make the mean coarser and more sensitive to individual cases (one case moves a nine-case mean by 11.1 points for a one-unit change). Fewer development partials can make calibration less representative of these cases. Report the revised mix and stratum risks; claims remain descriptive and narrower. |
| Broaden what qualifies as partial | For example, allow three direct requirements with at least one genuinely supported and one genuinely absent. Keep correctly cited supported-requirement coverage per question, but scores can now be fractions and the average targets a different mix of requirement counts. Report strict and broadened cases separately; no claim of having tested the original two-requirement endpoint with the broadened cases. Never treat ambiguity or a retrieval miss as corpus absence. |
| Use a different corpus | Keep the strict partial definition and paired endpoint if the corpus supports them. Reverify license, report identity, pilot exclusion, source coverage, ingestion and annotation cost before data use. Redo feasibility and development calibration under an approved protocol. Results apply to that corpus and pipeline configuration; a different corpus alone does not establish report independence or generalization. |

## Optional controlled conflict test

If separately authorized, freeze a small **constructed diagnostic suite** before
any run. Use synthetic tables with two equally applicable but incompatible values
for the same entity, metric, period, unit and version. Include a second supported
fact where appropriate to test whether the policy retains it. Pair each fixture
with controls where the values agree or where a clear scope, rounding or version
distinction resolves the apparent discrepancy. Fix expected decisions and citation
checks before running; do not tune on the fixtures.

Share the same decompositions and candidate evidence across policies. Record
whether both competing statements reached the decision stage so that retrieval
omission is distinguishable from mishandling visible conflict. Report constructed
counts, missed and false conflict flags, unsupported emissions, supported facts
retained and citation mistakes in a separate table. Keep these fixtures out of
natural development/calibration, evaluation quotas, primary coverage and pooled
natural risk. Matched variants are controls, not independent observations.

This can show whether the frozen pipeline handles specified conflict and resolution
patterns under controlled inputs. It cannot establish that it finds or resolves
natural filing conflicts, their prevalence, enterprise safety, statistical
superiority, generalization or novelty. It supplies **zero** genuine conflicts
toward the current seven-conflict gate.

## Recommendation

Keep the strict partial definition. Resolve the single pending positive and the
two unresolved outcomes only in a separately authorized review. Before spending
on the larger audit, decide whether a future natural study without a genuine
conflict stratum would still answer the research question. A separate constructed
test can document conflict behavior without distorting the natural endpoint. If
that narrower study is useful and review time is available, run the bounded audit
before deciding whether to keep or reduce partial quotas. If genuine conflict
performance is essential, prioritize feasibility of a different corpus over
broadening partials to fill this one. The current stop and all existing decisions
remain in force.
