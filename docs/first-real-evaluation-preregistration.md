# First retrieval evaluation — preregistration proposal v1

Hardware follow-up: the [smaller-answerer amendment proposal](first-real-evaluation-smaller-model-amendment.md)
records the single authorized retry (1/5 completed, then RAM guard) and proposes
an official fixed 1.54B answerer. It awaits approval; no replacement was run and
no evaluation data was selected. Do not keep retrying the 4B model.

Version history: the original document is preserved by local tag **prereg-v1**
at `6b1d04e`. The [feasibility/staged-plan amendment](first-real-evaluation-feasibility-amendment.md)
records the requested pre-approval scan, explicit shortage rule, proposed first
50 questions, shared decomposition, confidence calibration and hardware smoke.
Read that amendment for current proposed staging; evaluation selection remains
blocked until feasibility and user approval. No policy implementation is approved.

Status: **plan only, awaiting user approval**. Commit this specification before
selecting any new evaluation reports/questions. No evaluation sample, new labels,
model download, model run or implementation is authorized by this document.
Approval and any amendments must be committed before selection, not after scores.
Recorded November 1, 2026. The eventual Git commit is the preregistration record;
this document does not claim registration with an external registry.

The earlier pilot had **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from that pilot**. Those distinct
facts share nine contexts; statistical independence is not established. Pilot
labels remain **provisional, single-annotator**. Its nine contexts, 18 questions,
source reports/versions and near-duplicates are excluded from this evaluation.

## 1. Hypothesis, primary metric and fixed decision rule

Hypothesis: with identical retrieved evidence and candidate answers, graded
requirement-level sufficiency recovers more correctly supported information on
partially answerable questions than a simple confidence abstainer, without a
material increase in unsupported answers. This tests the sufficiency policy,
not hybrid-retriever superiority, automatic decomposition or full-system novelty.

**Primary endpoint:** graded minus confidence-abstainer supported-requirement
coverage on the 30 predesignated corpus-partial questions. For question i,
C_s(i) = correctly returned, correctly cited unambiguous source-supported
requirements / source-supported requirements in the declared complete corpus.
Each partial question has two requirements, exactly one source-supported, so
C_s(i) is 0 or 1. Primary delta is mean(C_graded - C_confidence) across those
30 questions. Missing retrieval or abstention scores zero for a supportable fact;
the denominator is never reduced because a system missed evidence. Human source
annotations define truth; neither model confidence nor verifier output does.

An emitted fact counts correct only if its entity, metric, period, unit/sign and
value agree with source gold AND its citation supports it at the right version
and cell/span. Unsupported formats remain system failures, not missing gold.

**Comparable risk:** R_s is the fraction of all 100 questions on which policy s
emits at least one unsupported, contradicted, wrong-unit/period/entity or falsely
cited factual claim. Abstentions count in the denominator and have zero emitted-
claim risk; they cannot improve coverage. Require both:

- R_graded - R_confidence <= **0.03** (three absolute percentage points), and
- R_graded <= **0.05** (five percent absolute question-level risk).

These are proposed internal evaluation tolerances, not acceptable financial
deployment error rates. They replace no approved safety standard; the earlier
one-point margin was an unapproved proposal, not an established decision.

Preregister a 10-point coverage gain as the minimum practically interesting
point estimate. The joint **support** decision requires primary delta >= 0.10,
its two-sided 95% CI lower bound > 0, a one-sided 95% upper bound for the risk
difference <= 0.03, and a one-sided 95% upper bound for R_graded <= 0.05.
All gates must pass; no choosing a favorable endpoint afterward. The never-
abstainer comparison and pooled claim-risk/citation/recall metrics are secondary.

**Falsification of the empirical advantage:** an upper 95% bound for the coverage
difference <= 0, or a lower one-sided 95% risk-difference bound > 0.03, or a lower
one-sided 95% graded-risk bound > 0.05 contradicts the respective hypothesis.
An upper coverage bound below 0.10 rules out the prespecified practical target,
without proving that the true effect is zero. Everything else that fails the
joint support gates is **inconclusive**, not success. This is not a test of
whether the method is historically original.

Use paired whole-report-family bootstrap intervals (10,000 replicates, seed
1729) retaining all questions and all policies together. Report group counts and
undefined replicates; do not discard undefined draws to narrow intervals. If
fewer than 15 distinct report families contribute partial questions, primary
inference is withheld. For rare/zero unsafe events or harmful discordances,
do not use a degenerate zero-width bootstrap interval as a safety guarantee:
also compute a conservative one-sided exact binomial upper bound on the fraction
of independently sampled report families containing any such event. With five
questions per family, that bounds question risk/harmful-discordance risk from
above. Use the larger applicable upper bound for the support gates. Identity or
independence assumptions that cannot be justified invalidate inferential claims.

## 2. Sample size: what 100 can and cannot establish

Plan **100 evaluation questions across 20 report families, five per family**,
plus **20 separate calibration questions from at least four other report
families**, all excluded from the pilot. The evaluation is deliberately a
diagnostic mix, not an estimate of enterprise question prevalence.

Illustrative 80%-power normal approximation for a paired binary difference:
MDE approximately (1.96 + 0.84) sqrt(q/n), where q is the probability that the
two policies disagree in success. These are planning assumptions, not empirical
power computed from the constructed pilot. They ignore clustering and are
optimistic for small partial strata; exact attainable power is discrete.

| Endpoint size | q = 0.30 | q = 0.50 | q = 1.00 |
| --- | ---: | ---: | ---: |
| 100 questions, secondary binary outcomes | 15.3 pp | 19.8 pp | 28.0 pp |
| 30 partial questions, primary endpoint | 28.0 pp | 36.1 pp | 51.1 pp |

Thus there is **no single defensible MDE without a variance assumption**. A
illustrative planning range is 28–36 points for the primary endpoint before
clustering, not a 5–10-point improvement. For illustration, five questions per
report and intraclass correlation 0.10 give design effect 1.4 and approximately
18% larger standard errors/MDEs. This is a sensitivity example, not a measured
ICC or an exact correction for the 30-partial stratum. A worst-case independent
proportion near 0.5 with n=100 has about +/-9.6-point Wilson 95% precision.

Even zero events in 100 independent questions gives a one-sided 95% upper
bound 1 - 0.05^(1/100) = **2.95%**, not zero risk. With only 20 independent
report groups, zero affected groups gives **13.9%** for the conservative
group-event bound. Consequently this 100-question design cannot establish the
tight three-point risk gate using that conservative clustered bound, even when
no harmful events are observed. It is a **first estimation/failure-discovery
evaluation, not an adequately powered confirmatory study**. Do not loosen the
margin or change the CI method after seeing this limitation or the results.

For orientation, detecting a 10-point paired difference needs roughly 157 or
392 independent partial questions under q=0.20 or 0.50, respectively, before
clustering. A later confirmatory design would need more independent reports and
its own precommitted power plan. No automatic sample expansion or repeated
testing follows this first evaluation. Statistical background:
[NIST confidence intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm),
[NIST sample-size planning](https://www.itl.nist.gov/div898/handbook/prc/section2/prc242.htm).

## 3. Question composition and retrieval

| Corpus-level stratum | Target among 100 | How obtained before inference |
| --- | ---: | --- |
| Fully supported | 40 | Two direct extraction requirements with source-verified cells/spans |
| Partial | 30 | Newly authored two-fact questions: one fact present, one genuinely unavailable in the complete declared document collection |
| Missing | 15 | Plausible requests whose two facts are unavailable in that declared collection, confirmed by source inventory/search |
| Conflict | 15 | Same entity/metric/period/unit with genuinely inconsistent, equally applicable sources and no resolving scope/version priority |

These are **recruitment targets**, not an observed or guaranteed yield. TAT-QA
does not natively label this sufficiency mix. Partial/missing questions are
authored stress questions against naturally incomplete collections; no source
rows are deleted. Conflict targets must come from actual source disagreement;
different years, units or entities are not conflicts, and a clearly resolved
restatement is not an unresolved conflict. No invented values fill this stratum.
If 30 valid partial or 15 genuine conflicts cannot be found, stop and commit a
user-approved sampling amendment before evaluation inference; never silently
backfill synthetic cases or report achieved quotas as natural prevalence.

Keep at least 15 report families represented in the partial stratum. Balance
strata across families as feasible under five questions per family; otherwise
amend before freezing the sample. Screening exclusions and shortfalls are logged
without looking at model outputs. Calibration targets are 8/6/3/3 across these
strata; missing genuine conflicts triggers the same feasibility gate.

Use the already licensed TAT-QA raw table/text collection as the starting corpus,
with all available contexts for each accepted report plus unrelated distractor
reports. Dataset license is [CC BY 4.0](https://github.com/NExTplusplus/TAT-QA/blob/870accc41953dcde885aabeb963d94aabdc0fbc3/README.md#license).
These are available report excerpts, not necessarily full original reports;
"missing" means absent from the declared indexed collection, not never reported
by the company. No gold-selected two-row documents or per-case databases.

BM25 retrieves up to eight shared chunks per question, deterministic evidence-ID
tie breaks, within the declared entity/report scope; preserve complete table
headers and source locators. Pack to a fixed 3,200-token input budget, logging
truncation. Gold answers and supporting-cell IDs never guide retrieval/packing.
The same retrieved context, decomposition and candidate answers feed all policies.
Corpus answerability and retrieved-evidence sufficiency are separately annotated;
missing retrieval is an end-to-end failure, not a relabeling of corpus truth.

## 4. Fixed answerer, policies and budget

Fix **Qwen/Qwen3-4B-Instruct-2507**, non-thinking, **local CPU**, Q4_K_M GGUF
under llama.cpp, concurrency one, context 4,096 tokens, greedy decoding, seed
1729, maximum 384 generated tokens, one generation per question with no retry
or repair. All policies share that cached candidate generation. The proposed
model's [official card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
and [license](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE)
identify Apache-2.0. This is an open-weight model, not an API answerer.

Fixed artifact: bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF,
Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf; published size approximately 2.50 GB,
SHA-256 `2fde00ce69dd4899c70d020845e2638353015bba0fdf161b3eb965f2bca4464e`.
The [quantizer's file page](https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF/blob/main/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf)
is the artifact source, distinct from the original model publisher. At v1 no file
had been downloaded or checksum-verified locally; the linked amendment now
records successful checksum verification and a memory-blocked hardware attempt.
Pin the runtime binary/commit,
chat template, tokenizer, full prompt and packing rules in a committed runtime
manifest after non-evaluation compatibility checks and before evaluation
selection. Runtime source: [llama.cpp](https://github.com/ggml-org/llama.cpp).

All three policies use one fixed structured answerer prompt requesting a best
candidate value/citation for each supplied requirement, including when uncertain.
No self-reported certainty or independent model-specific prompting advantage.

- **Never-abstain:** emit every candidate; missing/refusal/malformed generation
  counts as a generation failure, remains in denominators, and is not silently
  converted to a correct abstention.
- **Confidence abstainer:** score each candidate with exp(mean value-token log
  probability); retain candidates above one global threshold. It may return
  partial answers, making it stronger than an all-or-nothing strawman. This is
  an uncalibrated model score, not a probability of correctness. Choose threshold
  from 0,0.1,...,1 plus an always-abstain fallback, on the separate 20 calibration
  questions only: maximize supported coverage subject to <=1 unsafe calibration
  question; ties favor fewer unsafe questions then higher threshold. This small
  calibration set cannot certify safety. Freeze threshold before evaluation;
  no evaluation risk/coverage matching or threshold search afterward.
- **Graded:** apply the existing requirement verifier/sufficiency/conflict policy
  to the same candidates/evidence, without oracle aliases, manual repairs or
  verifier tuning. Unit/citation mistakes are judged independently and count
  against it; the current verifier does not establish semantic unit correctness.

Local compatibility must demonstrate value-token log probabilities and the
structured candidate/verifier interface on synthetic examples. If unavailable,
or the model fails on the 8 GB host, stop for a pre-selection amendment—no silent
smaller model, feature substitution, cloud service or paid API fallback.

Expected API/model license cash cost: **$0**. No API key, cloud GPU or paid call.
120 maximum generations (20 calibration + 100 evaluation), reused across policies.
Runtime/RAM are unmeasured: allow a planning 4–12 CPU hours and roughly 5–6 GB
process memory at short context, not a hardware-fit guarantee. Illustrative
50–150 W and $0.30/kWh give $0.06–$0.54 electricity over 4–12 hours; this is an
assumed tariff/load scenario, not the user's bill. Download/bandwidth charges
are unknown. Staying under $5 assumes existing hardware, unmetered internet and
volunteer annotation; reviewer compensation is not covered by that budget.
**Do not call any paid API without explicit user approval.** No paid API is
part of this plan and none has been called to prepare it.

## 5. Annotation hours and reduction options

Planning estimates, not measured annotation speed:

| Work | User | Second annotator |
| --- | ---: | ---: |
| Source identity, duplicate checks and setup | 2–4 h | 0–0.5 h |
| Corpus gold: 100 questions / 40-question review subset | 6–9 h | 2.5–4 h |
| Separate calibration gold and short guideline practice | 1–2 h | 0.5 h |
| Blind candidate/citation review across policies | 3–5 h | 1.5–2.5 h |
| Disagreement adjudication | 1–2 h | 1–1.5 h |
| Total | **13–22 h** | **5.5–9 h** |

The second annotator independently covers a prespecified 40-question stratified
subset (16 full,12 partial,6 missing,6 conflict), with source gold and blinded
outputs, before seeing the first annotator's labels. This lies within the required
**30–50-question second-human subset before any paper results**. Preserve both
original files, measure human agreement before adjudication and disclose that
the remaining 60 questions have single-annotator gold. No LLM replaces a human.

Reduce effort by grouping source viewing by report, reusing one source-gold
inventory across all three policies, highlighting raw cells/headers without
suggesting correctness labels, and judging identical cached candidate claims once
then projecting those judgments onto policy selections. These reductions are
planning hopes, not guaranteed savings. A five-question non-evaluation practice
session can measure actual speed; revise the effort estimate before selection.
Do not reduce the second-human subset or skip difficult negatives to save time.
If the above hours are unaffordable, propose a smaller estimation study and
commit its weaker precision plan before selection; do not pretend 100 questions
can be thoroughly annotated within a few hours.

## 6. Freshness, report identity and near-duplicates

First resolve the nine pilot contexts and candidate corpus contexts to original
report identity using issuer/legal entity, fiscal period, report type, filing
date and accession/source URL or PDF hash. Use paragraph/header clues to locate
the official issuer/regulator report, then retain page/table match evidence and
an exact reference. Pilot raw UIDs alone do not identify reports. Versions,
restatements and overlapping tables share a report-family ID; conservatively
group the same issuer/fiscal-period family where boundaries are uncertain.

Before choosing questions, exclude every pilot report family and its duplicates.
Calibration and evaluation must also be family-disjoint. Perform:

1. Exact SHA-256 checks on document bytes and canonical text/table artifacts.
2. Whitespace/Unicode/case-normalized whole-table equality, preserving numbers,
   units and signs; normalized row hashes detect overlapping table excerpts.
3. Candidate near-duplicate flags at token 5-shingle Jaccard >=0.80, or row-hash
   overlap >=0.50 relative to the smaller table, or exact normalized question
   match/token 3-shingle Jaccard >=0.80 against the 18 pilot questions.
4. Manual review of flagged pairs and issuer/period matches; different UIDs or
   low textual similarity do not override a known shared report. Log source
   identity, similarity flags, disposition and reasons before any model output.

These are conservative screening rules, not proof that all duplicates are found.
Freshness is relative to this pilot/calibration corpus, not a guarantee that the
public financial reports or TAT-QA were absent from Qwen's pretraining data.
Unresolved pilot identity or unresolved candidate overlap is a **stop/exclude
gate**, not permission to claim report-disjoint evaluation. If TAT-QA cannot
supply source identities, enough distinct report families or genuine conflicts,
request a corpus/sampling amendment before selecting the evaluation set. Do not
quietly broaden scope or declare context UIDs to be independent documents.

## Approval and freeze order

Commit this plan now; obtain user approval before any new selection or code.
Then resolve source identities and feasibility, check the fixed local runtime on
synthetic inputs, and commit required implementation/runtime hashes. Use separate
calibration data to freeze the confidence threshold. Lock the evaluation sample,
annotations and complete corpus; run each cached generation once and apply all
three frozen policies without tuning. Any changed metric, margin, model, sample
mix or exclusion rule needs a dated, committed amendment before evaluation
selection/inference as applicable, with the reason recorded.

Current production src remains frozen at tree
`3261c6087757b9f3d9aed1166e264de45ac4f479`; this proposal changes no code or
prior pilot result. There is no approval to push.
