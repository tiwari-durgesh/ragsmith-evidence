# Draft amendment: natural study without a conflict stratum

**Plan only; concrete amendment awaits approval.** This draft does not reopen
the feasibility gate. It authorizes no confirmation, adjudication, allocation,
selection, calibration, model run or constructed test. It changes no existing
document or recorded result. If approved, it supersedes the natural conflict
quotas and the associated totals in the
[Option C amendment](option-c-excerpt-corpus-amendment.md).

## Natural evaluation and development

| Proposed partition | Excerpt groups | Full | Partial | Missing | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Evaluation | 6 | 12 | 9 | 5 | 26 |
| Development | 4 other | 8 | 6 | 3 | 17 |

Remove the four evaluation and three development natural-conflict slots. The
[source audit](source-genuineness-verification-results.md) did not certify the
required seven, so retaining that stratum would make the design infeasible on
the evidence currently available. Do not backfill those slots. Nine evaluation
partials preserve the sample targeted by the primary endpoint; six development
partials retain the intended mixed-support cases for threshold calibration. The
existing full counts preserve evidence-complete controls, and the existing
missing counts preserve explicit tests of unsupported emission when neither
requested fact is available. These counts are design targets, not a demonstration
of power, safety, quota feasibility or natural stratum prevalence.

Keep the strict two-requirement definition and neutral T1/T2/T3 templates. Full
requires two directly supported facts; partial requires one directly supported
fact and one plausible fact absent across the entire predeclared excerpt scope;
missing requires two plausible facts separately checked absent over that scope.
Check all original tables, notes, headers, versions and relevant narrative, not
the retriever's output. Unreadable, ambiguously scoped, contradictory or missing
referenced material does not prove absence. Do not relabel a genuine conflict as
missing or remove evidence to create a stratum. Keep the pinned source, exclusions,
seed 1729, source-only ordering, stable IDs, and requested-fact deduplication
across both partitions. Groups remain disjoint by excerpt component, with **at
most five questions per group across all strata**; there is no requirement to
fill each group to five. This does not establish disjoint underlying reports.

After separate execution approval, follow the
[confirmation and reservation plan](partial-confirmation-and-allocation-plan.md).
If this concrete amendment is approved, the 23 prior audit drafts may be
considered as **unconfirmed inputs** to the new source-only eligibility screen;
none is grandfathered, eligible by default, or selected. This is a prospective
eligibility rule for a new phase, not a revision of the historical audit or an
upgrade to its labels. Before confirmation, freeze the group roles, provisional
9/6 nominations and same-role reserves with capacity for the full and missing
mixes. Stop if the required mix cannot be reserved and confirmed, if fewer than
15 eligible distinct partials remain, or if no joint allocation meets the caps
and exclusions. No unresolved-group top-up or smaller design takes effect
automatically. Independent human review covers **all 26 evaluation cases**
before any paper results, replacing the prior 30-case review count only upon
approval. Source gold is reviewed blind to other labels and system outputs and
locked independently before adjudication. Without a reviewer, results remain
provisional and internal.

## Metrics, policies and calibration

Keep the primary paired difference in correctly returned and correctly cited
supported-requirement coverage, graded sufficiency minus confidence abstention,
on the nine evaluation partials. Keep the question-level unsupported-claim risk
definition, the 3-point risk-difference and 5% absolute graded-risk targets,
and secondary metrics. Risk uses all 26 evaluation questions as its denominator
(including abstentions and failures); report counts and per-stratum denominators.
With 26 questions, one risk event is about 3.85 percentage points. The changed
mix and denominator affect interpretation; do not treat pooled risk as directly
comparable to a study containing natural conflicts. All comparisons remain
descriptive under Option C, with no significance or risk-guarantee claim.

Keep the never-abstain retrieve-and-answer baseline, confidence-threshold
abstainer and graded sufficiency, with shared scope, manual decomposition,
retrieved/packed evidence and candidates. Keep the fixed local
Qwen2.5-1.5B-Instruct Q4_K_M, its pinned runtime, confidence signal, retrieval
and generation budgets, seed 1729, and all of `src/` unchanged. Preserve the
development-only threshold grid, macro supported-coverage objective,
**at most one unsafe development question**, and the existing tie breaks.
Apply that same integer cap to the 17 locked development cases (1/17, about
5.88%, rather than 1/20). It is a calibration rule, not a population-risk bound.
No pilot, evaluation or constructed case participates in calibration.

Existing allocation and calibration tooling still enforces the old mixes and
20-case guard. A later approved engineering pass must adapt and test only those
size/mix checks outside `src/` on synthetic inputs, with the algorithm, metrics
and policies unchanged. Re-freeze the affected tooling before authoring or
selection. This draft does not change or run that tooling.

## Separate constructed conflict diagnostic

Label the suite **Constructed conflict diagnostic — synthetic, not natural data**.
After separate authorization, freeze a small set of matched synthetic fixtures
and expected outcomes before inference. Use two incompatible, equally applicable
statements about the same entity, metric, period, units and version. Include an
unrelated supported fact to check that suppressing a disputed fact need not
suppress all useful output. Include matched controls for agreement, legitimate
scope differences, compatible rounding and an explicitly superseding version.
Use the same three policies, shared inputs and frozen settings. Record whether
both assertions reached the decision stage; report counts of correctly withheld
disputed facts, missed or false conflict handling, unsupported emissions, retained
supported facts and citation errors. Matched variants are controls, not independent
samples. No tuning on fixture results.

The diagnostic can show how the frozen pipeline behaves on the specified
patterns, conditional on which evidence it receives. It cannot establish natural
conflict detection or resolution performance, prevalence, generalization,
statistical superiority, novelty or enterprise safety. It contributes no cases
to the natural development/evaluation mix, calibration, primary coverage or
pooled risk. Report it in a separate table with its own denominators.

## Human effort and smaller option

Estimates assume complete, readable packets, separate blinded review materials
and no source discovery charged to annotators. The author may reuse their own
confirmation evidence only when scope, wording, version and search log are
identical; the reviewer repeats source checks independently. The estimate includes
candidate value/citation judgments after an authorized run, deduplicated across
policies, plus disagreement review after the original judgments are locked.

| Work | User, 43 natural cases | Reviewer, all 26 evaluation cases |
| --- | ---: | ---: |
| Practice and setup | 0.25–0.50 h | 0.25–0.50 h |
| Partial draft confirmation, including frozen reserves | Up to 4.00 h | Included in independent evaluation gold below |
| Final natural source labels and evidence records | 2.83–3.68 h | 2.80–3.55 h |
| Unique candidate value/citation checks | 0.55–0.80 h | 0.55–0.80 h |
| Reconciliation | 0.35–0.65 h | 0.35–0.65 h |
| **Planning total using the full confirmation allowance** | **8.0–9.6 h** | **4.0–5.5 h** |

User label timing assumes 3–4 minutes per full, 2–3 minutes to record a previously
confirmed partial, and 10–12 minutes per missing. Reviewer source timing assumes
3–4, 8–10 and 12–15 minutes respectively, with fresh absence checks. Estimates
are not measured throughput. Confirmation remains capped at four hours; use
roughly two-hour sessions and reserve time for labeling and reconciliation. If
either estimate exceeds nine hours before reservation, prefer the smaller option
below only after explicit approval. If either cap is reached later, stop and
record incomplete work; do not skip a source scan or independent review. The
synthetic diagnostic is separately authorized and budgeted; it cannot consume
time reserved for the required natural labels.

The author's nine-hour limit is cumulative across confirmation, labeling,
candidate checks and reconciliation. Because the main design can take 9.6 hours,
record actual active time by task and pause after development labeling, before
starting evaluation labeling, to compare the remaining budget with the work
still required. If nine hours is reached sooner, stop immediately and preserve
completed records and pending items. If the remainder will not fit, keep
evaluation labeling paused until the author explicitly approves a revised plan
or stops the study. Do not shorten the rubric, trim already labeled development
cases, or reuse a threshold for a different design to fit the cap.

**Smaller option, not adopted:** evaluate **18 (7 full / 9 partial / 2 missing)**
in six groups and develop on **14 (6 full / 6 partial / 2 missing)** in four other
groups, retaining the five-question cap. This preserves the primary partial
sample and 9/6 target while reducing the number of additional full and expensive
missing labels. Estimated **6.9–8.2 user hours** and **3.0–4.3 reviewer hours** for
all 18 evaluation cases. This further weakens descriptive full/missing coverage
and makes aggregate risk and threshold calibration more sensitive to single
cases. Adoption would require explicit approval of the totals, all-18 reviewer
requirement, and retaining the same grid and integer cap on 14 development cases.
It does not solve a partial-quota shortfall and is not an automatic fallback.
