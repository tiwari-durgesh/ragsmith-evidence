# Corpus options after one SEC HTML compatibility probe

November 1, 2026. **Plan and one engineering probe only. No option adopted,
corpus locked, evaluation data selected, gold labels created or model inference
performed.** No PDF table parser is proposed. Source tree remains
`3261c6087757b9f3d9aed1166e264de45ac4f479`.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Pilot labels remain
**provisional, single-annotator**. This probe is not another evaluation result.

## One filing: native HTML does not produce canonical verifier rows

Probe source: Apple Inc., CIK 320193, FY ended 2023-09-30, Form 10-K accession
0000320193-23-000106. The [official filing index](https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/0000320193-23-000106-index.html)
records filing date 2023-11-03, the report period and the primary HTML document.
Apple is outside all eight excluded pilot issuer families. Reserve this inspected
filing family for engineering only if a future corpus is approved; it is not an
evaluation or development source chosen by this probe.

Both direct SEC HTML URL forms returned HTTP403. The probe used the same filing's
[public HTML mirror](https://cdn.yahoofinance.com/prod/sec-filings/0000320193/000032019323000106/aapl-20230930.htm),
corroborating issuer, fiscal date and independent multi-year table fingerprints
against the [official SEC HTML](https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm).
The mirror has 1,558,924 bytes, equal to the index's listed size. Its SHA-256 is
`bda1f34435199672c16ecdf2034c650872d2cac8399ed0d179fc25450b080b90`.
Equal size and content checks do **not** prove byte equality to SEC bytes; this
hash identifies the archived mirror. No rendering-to-text reconstruction was
substituted for the HTML file. Raw HTML and caches remain ignored/local.

| Probe observation | Measured result |
| --- | ---: |
| Native HTML tables | 66 |
| Tables containing colspan/rowspan greater than one | 66 |
| Frozen ingestion output | 671 `table_row` records + 1 narrative `text` record |
| Rows matching frozen `Metric: ...; YYYY: ...` grammar | **0** |
| Source-integrity check / question-interface JSON round-trip | Passed / passed |
| Two technical metric/year queries, up to 8 hits each | 16 distinct retrieved units |
| Transport prototype: first 8 intact units | 8 table rows |
| Eight-unit JSON transport envelope, fixed Qwen tokenizer | **3,018 tokens** |
| Headroom below 3,200 before final prompt/chat template | **182 tokens** |
| Model inference / evaluation cases | **0 / 0** |

The transport prototype orders by minimum per-requirement rank, then evidence ID,
and takes eight intact units. It is not an adopted production packing rule.
The existing parser assumes the first table row supplies headers, does not expand
merged cells into a semantic grid, and may overwrite duplicate header keys in
its cells dictionary. Merely emitting `table_row` does not establish preserved
column semantics or canonical metric/year/value evidence. Both technical
requirements yielded zero discovery candidates and all 16 retrieved units were
unsupported by the frozen discovery grammar. These are format diagnostics, not
answer-quality or sufficiency scores and not source-absence labels.

**Budget conclusion:** this particular envelope fits 3,200, but the complete
answerer prompt/chat template was not included or frozen. With only 182 tokens
left, full compatibility cannot be claimed. Other tables, inclusion of narrative,
and required header/unit/provenance retention may change the footprint. No evidence
was clipped or manually rewritten into a favorable canonical example.

**Effort only:** successful probe execution took **2.43 seconds**, including
**0.69 seconds** of tokenizer work. Elapsed lookup/download/dependency setup/probe
and initial record-preparation time was **33.86 minutes** at the checkpoint;
source inspection began shortly before that clock checkpoint. This is a wall-time
observation, not a precise labor-timesheet estimate or full-corpus throughput.
Direct-download failures are included. No production implementation time was
spent. Installed the repository-pinned beautifulsoup4 4.14.2 plus support packages
in an ignored probe directory; no dependency declaration or global environment
was changed. Bundled Python 3.12.14 was used; **Python 3.11 remains unverified**.
Exact provenance and measurements: [probe record](sec-html-ingestion-probe.json).

## B versus C: estimated incremental work, not measured delivery promises

All estimates below assume **20 development + 30 evaluation questions (50 total)**,
the fixed local answerer, three shared-input policies, and independent human review.
They exclude already spent investigation and later inference runtime. Source-only
quota feasibility remains unmeasured for every option; none guarantees nine genuine
partials/four conflicts plus disjoint development quotas. Engineering estimates
include bounded ingestion work, common runtime-interface work and necessary
synthetic/excluded-source checks, not another general-purpose harness.

| Dimension | B1: structured filing HTML / inline XBRL | B2: structured XBRL facts | C: TAT-QA excerpts + content deduplication |
| --- | --- | --- | --- |
| Additional ingestion/provenance work | 6–12h: table grids/periods/units, source anchors, canonical emission, packing; use inline tags where reliable | 8–16h: accession/context/unit/dimension/taxonomy mapping, restatement precedence and original-filing citations | 2–4h: adapt already structured source cells, retain complete headers/context, connect existing hash screens to a source-only export |
| Shared answerer/citation/log-probability interface and bounded checks | 4–6h | 4–6h | 4–6h |
| Total additional engineering | **10–18h** | **12–22h** | **6–10h** |
| User annotation/review, all 50 | **7–9h**, potentially 10–12h for difficult tables/absence checks | **6–8h** for an explicitly restricted tagged-fact task; 8–12h if checking narrative/source-wide absence | **5–7h**, potentially 8–10h if cross-context scope/absence is difficult |
| Second human, all 50 independently | **7–9h**, potentially 10–12h | **6–8h** under the same restriction; 8–12h otherwise | **5–7h**, potentially 8–10h |
| Leakage / dependence risk | Explicit CIK/accession/period helps enforce family splits; repeated comparative years, overlapping filings and development reuse still need exclusion | Same, plus silent mixing of latest facts/restatements or querying facts outside the frozen accession can leak future information | Higher unresolved report/fact overlap: exact hashes cannot detect different excerpts of one report, near-duplicates, or related facts across partitions |
| Main interpretation limit | One-probe format failure; extraction and packing need validation before any corpus lock | A tagged-fact subset is a narrower task; structured tags can make retrieval easier and omit narrative/segment/custom facts | Cannot certify report-disjoint generalization or report-family independence; absence is only within the declared frozen excerpt scope |

These estimates revise the earlier PDF-era 8–16h estimate for a *different*
implementation choice. They do not claim the HTML probe validated XBRL or that
switching formats is free. Full candidate-model integration remains unbuilt
under all options. Annotation estimates include question finalization/manual
decomposition, source gold/absence/conflict review, post-run unique candidate
value/citation judgments and adjudication. Reuse identical candidate judgments
across policies, not independent labels across people. The reviewer sees neither
primary labels nor system outputs during source-gold review.

The SEC [API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
states that company-facts/concept aggregates cover standard-taxonomy facts that
apply to the entire filing entity. Custom taxonomies exist, and aggregated facts
are updated as filings arrive. Therefore an absent company-facts entry is **not**
proof of absence from the filing, and repeated values from different contexts
are not automatically conflicts. B2 must pin accession/context/date/unit and
inspect original filings; a mutable current-company endpoint is not a frozen
document corpus. No XBRL endpoint was probed here.

TAT-QA's [pinned official README](https://github.com/NExTplusplus/TAT-QA/blob/870accc41953dcde885aabeb963d94aabdc0fbc3/README.md#license)
identifies a financial table-plus-text QA dataset and licenses the dataset under
**CC BY 4.0**. C would use the already pinned raw table/paragraph structure,
not the upstream heuristic `facts`/`mapping` preparations or answer annotations
as inference evidence. Existing `tatqa_adapter` screens contexts; it does **not**
already emit canonical rows, so C still needs the limited adapter estimated above.
No raw corpus/questions were inspected for selection in this comparison.

Public-source exposure is a separate unresolved risk for both options: this probe
cannot establish whether the fixed answerer encountered filings or TAT-QA during
training. Content deduplication and fresh question wording do not prove absence
of model memorization. Keep upstream answers/heuristic mappings out of authoring,
reviewer packets and inference inputs, and disclose that model-training overlap
is unmeasured rather than claiming a contamination-free benchmark.

## Recommendation: C for the next small descriptive study, pending amendment

Recommend **C**, given the limited engineering and annotation budget. Its benefit
is pre-structured cells and shorter source packets; its cost is an explicit loss
of report-disjoint claims. It is **not** a finding that content hashes eliminate
leakage or that C passes feasibility. B1 is the preferable later direction when
verified filing provenance is central and engineering time is available; B2 is
not a drop-in broad enterprise-document replacement.

Both choices can examine the existing paired hypothesis *within their declared
source scope*: whether graded sufficiency returns more correctly cited supported
requirements than the confidence abstainer on partial questions, with the fixed
descriptive risk definitions. B1 can describe results across verified eligible
filing families if independently established. B2 can describe policy behavior on
a declared tagged-fact task. C can describe coverage, unsupported-claim risk and
failures on a content-screened excerpt collection, conditional on the fixed
answerer, shared retrieval and manual decomposition. None of these small designs
establishes novelty, tight comparable-risk guarantees, enterprise-wide performance,
automatic decomposition or hybrid-retrieval superiority. C cannot support unseen-
report or independent-report-family claims, even if content groups are disjoint.

**The required C amendment must be approved and committed before implementation,
corpus lock or selection.** It would specify:

1. Replace the complete-original-report corpus with a pinned, bounded TAT-QA raw
   excerpt collection. Define the source universe and every question's scope
   explicitly before authoring; use complete source contexts and distractors,
   not gold-selected two-row documents. Do not claim an unidentified context is
   a particular company's report. If entity/period scope cannot be supported
   from the allowed sources, exclude it rather than invent metadata.
2. **Explicitly relax the mandatory verified-report-membership gate.** Retain
   exclusions for the nine pilot IDs, all eight recovered pilot families wherever
   attributable, known copies/versions, and every unresolved similarity flag.
   Record unknown identities and the residual inability to exclude *all* unseen
   excerpts of pilot reports. Content deduplication cannot fulfill that earlier
   guarantee; user approval must accept this limitation, not silently waive it.
3. Fix a source-only duplicate graph across the declared pool, pilot and all
   development/evaluation candidates: canonical table/text equality plus existing
   5-shingle >=0.80 and smaller-table row-overlap >=0.50 screens; connected
   components stay together. Preserve numbers/units/signs/years. Retain question
   equality/3-shingle >=0.80 exclusions before any draw. Log every exclusion and
   source-backed false-positive clearance. Do not partition a component to meet
   quotas. Hash equality is a screen, not report identity or independence.
4. Replace the six/four **report-family** allocation with predeclared content-group
   allocation and retain seed 1729 / hash-priority first-feasible selection. The
   candidate amendment must define stable component IDs and allocation precisely;
   components are not asserted independent. Keep report-family inference withheld
   and report per-case counts/descriptive metrics only. No group bootstrap or
   effective-sample-size claim may substitute for missing report identities.
5. Keep the source-only templates/human authorship/manual decomposition rules and
   the reproducible keyword/table/narrative absence procedure, adapted explicitly
   to the full frozen excerpt scope. A fact absent from excerpts may be elsewhere
   in the original report. Missing extraction or unsupported formats never become
   gold `missing`. Two divergent values only qualify as genuine conflict when
   entity, metric, period, unit and equally applicable version scope are established.
   Unknown identity/definition is `not_adjudicable`, not a conflict.
6. Retain the 12/9/5/4 evaluation and 8/6/3/3 development targets and **stop for
   another amendment** if genuine quotas cannot be met. No claim that the
   discrepancy leads are genuine conflicts, synthetic backfill, value edits,
   dropped resolving contexts or automatic actual-count evaluation. Feasibility
   must be established separately; this probe did not count opportunities.
7. Put any future ingestion/canonicalization in a **separate module outside the
   frozen `src/` tree**, preserving original cell coordinates, complete multirow
   headers, source byte hashes and lineage. Convert all unambiguously interpretable
   source facts by a fixed source-only rule, not just question/gold cells. Preserve
   unsupported material in retrieval and an audit, rather than dropping it to
   manufacture missing evidence. Do not use question wording to rewrite source
   labels into oracle aliases. Freeze provenance/units/period normalization and
   the 3,200-token packing contract before model runs. Candidate claims still
   pass through the existing verifier; it may reject them. Keep contradiction
   policy and assessment schema unchanged. No such module is written here.
8. Retain metrics, three baselines/policies, model/runtime, confidence calibration
   rule and source freeze; lock any separate module and shared runtime interface
   before source-gold authoring/inference. Commit the amendment and its exact
   Git-blob SHA-256 in the public manifest. Preserve prior tags as history. Human
   independent review of all 30 evaluation cases remains required before paper
   results; no reviewer means provisional/internal only. The <=9h user cap and
   existing active-work feasibility budget do not reset; engineering needs its
   own explicit authorization rather than unused search-time reallocation.

For **B** instead, a different amendment would replace the corpus with specifically
pinned HTML filings or a declared XBRL-fact subset, preserve verified filing-family
disjointness, define amendments/restatements/dimensions and source completeness,
and authorize only the separate adapter plus bounded synthetic compatibility
checks. It would freeze that interface before locking a corpus and retain the
same genuine-quota stop gate. It cannot use this one filing to certify general
HTML ingestion readiness or adopt XBRL silently.

This document recommends a direction; it does not implement either amendment or
change earlier approved decisions. Stop for the user's choice. Commit this plan
and probe metadata locally on `codex/public-progress`; no push.
