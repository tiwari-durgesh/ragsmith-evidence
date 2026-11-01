# Project status — November 2, 2026

The project is in **Phase 5 engineering/readiness**, with a working local demo;
the real research evaluation is not complete. A polished UI is not an empirical
result. Current branch: `codex/public-progress`; building commits stay local.

## Built and checked

| Built | Checked | Boundary |
|---|---|---|
| Frozen lookup/verifier and sufficiency policies | Regression and synthetic integration tests | Literal structured values; no broad semantic verification |
| Separate source-table ingestion and packing | Existing ingestion tests retained; whole prompt bounded | No PDF table parser or header repair |
| Local FastAPI and Streamlit | Shared request/response checks; browser checks on all five tabs, light/dark | Model off in frontend; six controlled pilot cases |
| Source-cell highlights, chips and baseline cards | Exact-cell mapping and anchor navigation checks | Baseline references can be wrong; full is scoped to retained evidence |
| Runner skeleton with injected local answerer | Synthetic tests; six pilot-source compatibility probes with lookup stub | No real model run, research scoring, dataset loader or calibration |
| Reviewer kit | Source-only opaque-ID practice packet and blank return inspected | Synthetic training only; no completed real reviewer labels |

The full suite has **720 passing tests**, with one existing Starlette/AnyIO
deprecation warning. No tests were removed to gain time. `src/` remains at tree
`3261c6087757b9f3d9aed1166e264de45ac4f479`; its diff from `1b0df45` is empty.
Python 3.12.14 on Windows is tested; Python 3.11 remains unverified.

## Unproven and limitations

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Source contexts overlap;
statistical independence is not established. Labels are **provisional,
single-annotator**. The LLM label cross-check was not run. Six examples illustrate
software behavior only, including an artificial **controlled test case** conflict.
Its packing-truncation warning remains visible; nothing was tuned to remove it.

Coverage/risk advantage, genuine-conflict yield, citation reliability under real
retrieval, confidence calibration, hybrid retrieval superiority, deployment
safety and generalization remain unproven. Option C accepts unresolved report
overlap. Content hashes and company-name checks cannot establish disjointness;
no question independence, leakage-free partitions, inferential superiority or
generalization claims are permitted. Findings will be descriptive on the declared
scope, conditional on the fixed answerer and manually supplied requirements.

The runner confidence threshold is **unset**, with no confidence decision. Its
synthetic numeric test thresholds do not calibrate anything. The older API's
optional local-model demo constant is uncalibrated and separate from this runner.
Never-abstain generation failures stay failures, not correct abstentions.

## Next research gates — not executed here

1. **Feasibility and authorization:** source-only exclusion/group checks and a
   genuine partial/conflict count under approved Option C rules. Preserve seed
   1729, known pilot-family/company/hash exclusions and the five-question group
   cap. Nothing in this overnight session inspects candidate questions. The
   planned evaluation mix is 12/9/5/4 and development mix 8/6/3/3. If genuine
   partial/conflict quotas cannot be met, stop for another amendment rather than
   manufacture conflicts or proceed with an opportunistic count.
2. **Corpus/selection:** obtain explicit authorization, fix complete source scopes,
   use source-only question authoring and the registered selection procedure;
   lock identities, groups, requirements and samples before any system run.
   No corpus or fresh question set is locked by the demo or skeleton.
3. **Labeling:** annotate source-only without system output; retain cell addresses,
   units and reproducible absence scans. Lock provisional primary labels. Keep
   development and evaluation labels separate and private.
4. **Calibration:** only after authorized development selection and locked
   development labels, apply the existing preregistered threshold procedure.
   Freeze its outcome before evaluation. No pilot tuning or evaluation access.
5. **Reviewer:** an independent human must label a 30–50-question subset before
   paper results; for this reduced plan independently review all 30 evaluation
   questions. Hide primary labels, assigned conditions and model outputs. Preserve
   independent returns, measure agreement before adjudication, retain resolutions.
   Synthetic practice or an LLM is not human inter-annotator agreement.
6. **Frozen run:** after authorization and all applicable locks, confirm the fixed
   model/runtime, shared decomposition/retrieval/candidates, pipeline hash and
   denominator handling. Run once, report descriptive counts and failures without
   tuning. Do not turn Option C content groups into independent statistical units.

These dependencies explain why calibration cannot precede authorized development
selection and labeling. They summarize existing decisions; they do not amend the
preregistration, authorize selection or change its public manifest.
