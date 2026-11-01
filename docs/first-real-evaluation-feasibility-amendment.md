# Preregistration v1 feasibility and staged-plan amendment

Plan revision before approval or evaluation selection. Local tag **prereg-v1**
points to `6b1d04eed42e159b73ea0ac9388786ec99803a79`; the tagged v1 remains
unchanged. This amendment records the requested feasibility-only scan and
hardware smoke, and proposes staged recruitment. No evaluation questions have
been selected, labeled, generated, or scored. No paid inference API is authorized.

The completed pilot had **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from that pilot**. Facts share nine
contexts and are not asserted statistically independent. Its labels remain
**provisional, single-annotator**. This scan does not upgrade them.

## A. Feasibility count: what can actually be established

Scanned the pinned TAT-QA training JSON only, checked against the committed
source audit. Aggregate evidence: [tatqa-feasibility-counts.json](tatqa-feasibility-counts.json).
The scan does not author/sample questions or run a retriever/answerer on them.

| Count | Observed | Meaning |
| --- | ---: | --- |
| Training source contexts | 2,201 | Audited raw contexts |
| Exact pilot contexts excluded | 9 | UID matches to the existing pilot |
| Further pilot table similarity flags excluded | 2 | Conservative exact/5-shingle/row-overlap checks |
| Remaining contexts | 2,190 | Context-disjoint leads; report identity is unverified |
| Remaining noncomparison table-only span questions | 895 | Label screen, not independently established eligibility |
| Plausible partial-question lead contexts | 167 | At least one extraction question with an explicit matching year header and apparent unit header |
| Repeated-label/year discrepancy contexts | 166 | Unverified discrepancies, not genuine conflicts |
| Discrepant repeated-label/year keys | 932 | Can include section/region/quantity differences |
| Discrepant table groups with matching layout and identical nonempty paragraphs | 0 | Strict corroborating-context screen found none |
| Verified report-disjoint partial questions | 0 established | Actual yield unknown |
| Verified report-disjoint genuine-conflict questions | 0 established | Actual yield unknown |

**A report-disjoint count cannot currently be certified.** The raw contexts have
table/paragraph/question fields but no original report ID, source URL or issuer
metadata fields. Original report identities of the nine pilot contexts have not
been recovered. Therefore 2,190 contexts cannot be called "outside the pilot's
reports," and 167 leads cannot be called 167 genuinely partial questions. A
missing value in one table may appear in another context from the same report.

Repeated names with different numbers are especially unsafe conflict evidence.
Three inspected discrepancy contexts illustrated stockholder net income versus
comprehensive income, travel revenues in different geographic regions, and
segment revenues versus operating income. They are different quantities/scopes,
not verified contradictions. Those inspections were feasibility checks, not
evaluation selections. No claim is made that all 166 leads were manually reviewed,
or that genuine conflicts do not exist somewhere in the corpus.

Scan rules: exclude the nine UIDs and pilot-normalized table equality, table
token 5-shingle Jaccard >=0.80 or row overlap >=0.50 relative to the smaller
table. Partial leads require a noncomparison span/table question mentioning one
year that matches a header in the first three table rows plus an apparent unit
header. Discrepancy screening compares repeated row labels/year columns and
numeric cell values; it does not establish entity, section, unit or version
priority. Numeric normalization is for lead detection only; no source is edited.
The screen uses upstream question-type labels, not upstream answer values or
model outputs, to determine these counts.

### Shortage decision, fixed now

The current strict feasibility gate **has not passed**. Do not select evaluation
questions until pilot-report identities and source scopes can be established.
Do not weaken "genuine conflict" into repeated row labels or use synthetic values.

- Stage 1 needs at least 15 verified partial and 7 genuine conflict opportunities,
  plus the other strata and source-family exclusions, before its sample is selected.
- Continuation to the 100-question v1 mix requires a verified cumulative pool of
  at least 30 partial and 15 genuine conflict opportunities in eligible source
  families. These are recruitment opportunities, not evaluation outputs.
- If those yields cannot be established within a **four-hour identity/feasibility
  work budget**, stop and ask for a corpus/scope amendment before selecting data.
  If Stage 1 is already complete but the full quota cannot be met, stop at Stage 1.
- Do not silently fill vacancies with easy full questions, reduce the conflict
  definition, delete source rows, manufacture contradictions or extend recruitment
  indefinitely. A different corpus or a separately reported synthetic-conflict
  supplement needs explicit user approval and a committed amendment; neither
  would count as genuine conflicts in the primary real-data sample.

## B. Proposed 50-question first stage

This replaces an unconditional 100-question spend. It does not authorize selection
now, and does not add new policy tuning after Stage 1. Corpus/development/evaluation
families remain disjoint from the pilot and from each other.

| Corpus-level stratum | Stage 1 | Additional Stage 2 | Cumulative |
| --- | ---: | ---: | ---: |
| Full | 20 | 20 | 40 |
| Partial | 15 | 15 | 30 |
| Missing | 8 | 7 | 15 |
| Genuine conflict | 7 | 8 | 15 |
| Total | 50 | 50 | 100 |

Use ten report families in Stage 1 and ten fresh families in Stage 2, five
questions per family. The separate 20-question development set is unchanged and
does not count toward the 50/100. Stage 1 is a feasibility/estimation run only;
it cannot satisfy v1's requirement for 15 report families contributing partial
questions, or certify its tight risk margin. Preserve the v1 primary endpoint
and risk definitions for the eventual 100; no formal efficacy decision at 50.

Before viewing policy comparison scores, commit a continue/stop decision using
only these predeclared operational criteria:

1. Source identity/exclusion checks pass, the remaining real-data quota is
   feasible, and no unresolved critical entity/unit/year/version mapping exists.
2. At least 45/50 Stage-1 questions are adjudicable; retain and disclose the rest,
   never replace them after inference with more convenient cases.
3. At least 95% of scheduled generations complete without crash/timeout. Any
   generation failure remains a failure in denominators; do not retry, repair,
   tune the model, change decomposition or change confidence thresholds.
4. User annotation/candidate-review time is <=9 hours excluding one-time report
   recovery, and the additional 50 are estimated to need <=7 user hours. The user
   explicitly approves that additional time; continuation is never automatic.
5. Second-human review of 30–50 questions is arranged before any paper results.
   If unavailable, Stage 1 remains internal/provisional; any further internal
   annotation requires an explicit time decision, not a paper-readiness claim.

The continue decision must not use a favorable coverage effect, risk difference,
p-value or leaderboard position. Do not run v1's hypothesis tests at both 50 and
100, select a winning stage, or pool results after outcome-dependent continuation.
After a blinded operational continuation, report the fixed cumulative 100 once;
if stopped, report only descriptive Stage-1 findings and why it stopped.

Expected first-stage user effort: 6–9 hours for labels, development/practice,
cached-candidate review and limited adjudication, plus 2–4 hours for source
identity/setup. This is 8–13 hours initially rather than the v1 13–22-hour full
study estimate; it is not a promise of completion in a few hours. A second
annotator's 30-case first-stage subset is about 4–7 hours. Additional 50: 4–7 user
hours; ten further independent reviewer cases approximately 1.5–2.5 hours.

The 30-case independent first-stage review subset targets 12 full, 9 partial,
5 missing and 4 conflict. If continuing, add 4/3/1/2 respectively to obtain the
v1 40-case human-review subset (16/12/6/6). Preserve both original label files
and pre-adjudication human agreement. The LLM is not a second human annotator.
Batch source viewing by report and reuse source-gold and identical candidate
judgments across policies; do not show one human the other's original decisions.

## C. Requirement decomposition: one fixed input for every policy

Use **manual, question-only decomposition**, not an LLM-generated or policy-
specific decomposition. Before retrieval, an annotator writes exactly two atomic
requested facts per question with requirement_id, entity/report scope, metric,
explicit fiscal period/year and the requested unit if the question specifies one.
If no unit is requested, record it as unspecified; source units belong to gold
annotation, not an invented inference hint. No expected values, answer labels or
supporting cell/span IDs enter requirements. Questions requiring arithmetic,
comparison, unresolved pronouns or ambiguous periods are out of the declared
extraction scope or not-adjudicable, as recorded before model output.

Do not inspect answer cells to rewrite the requested metric into an oracle table
alias. A question-wording metric the existing verifier cannot handle remains a
system limitation, not permission for policy-specific manual repairs. Review
the question/requirements for semantic fidelity before inference and hash-lock
one serialized decomposition file. All three policies receive **identical
requirement IDs, text, scope, period and unit fields**, byte-identical retrieved
chunks and the same cached answerer candidates. Verify those hashes per run.
Only the answer-selection/abstention rule differs. This study does not evaluate
automatic decomposition; its annotation time is included in the workload above.

## D. Confidence signal and development-only calibration

For requirement j, use the fixed local answerer's generated value-token log
probabilities: c_j = exp(sum(log p(value token | preceding prompt/output))/L_j).
Include generated tokens belonging to that value string, including its sign,
decimal/currency characters; exclude JSON keys, citations, explanation and quote
delimiters. Resolve token/character overlap by including every generated token
whose decoded span intersects the value content. Average in log space then
exponentiate. This length-normalized likelihood is a ranking signal, **not** a
calibrated probability that the fact is true. Do not use a self-reported score,
verifier verdict, gold source match or a policy-specific prompt as confidence.

Each requirement is thresholded independently, allowing the confidence baseline
to return partial answers. Missing, malformed, refused or empty candidate values
are recorded generation failures; assign them score 0 and emit no valid fact,
but keep their coverage failures in the denominator. Their empty output is not
a successful never-abstain answer. A candidate whose token spans/log probabilities
cannot be recovered is a technical failure, not a feature-substitution opportunity.

Use 20 source-family-disjoint development questions only, target mix 8 full,
6 partial,3 missing,3 genuine conflict, after the same feasibility gate. On the
fixed grid t in {0,0.1,...,1,+infinity}, retain valid values with c_j >= t. Infinity
is the explicit always-abstain fallback. Choose the threshold maximizing macro
supported-requirement coverage across development questions with supportable
requirements, subject to **at most one unsafe development question out of 20**.
Ties: fewer unsafe questions, then higher threshold. All-abstain has coverage zero.

Cache the same candidate/value-token log probabilities for all three policies;
never regenerate for a different threshold. Commit the chosen threshold,
development IDs/labels hash, prompt/token-span rule and model/runtime hashes
before any evaluation sample is selected. Freeze it for both 50-question stages.
No threshold selection, recalibration or risk/coverage matching on either stage.
Twenty development questions do not certify the five-percent risk target.

The hardware smoke below tests speed/memory only, not confidence calibration,
token-span correctness, model accuracy or verifier integration. A separate
synthetic capability check is still required before evaluation selection.

## E. Requested local hardware smoke

The initial attempt below is preserved as history. The user authorized one retry
after closing applications; it completed 1/5 questions and then hit the RAM guard.
See the [retry and smaller-answerer amendment proposal](first-real-evaluation-smaller-model-amendment.md).
No further 4B retries are authorized. The replacement was subsequently approved
for non-evaluation checks; [results](qwen15-runtime-checks.md) record 5/5 successful
synthetic runs and one local token-likelihood computation. Evaluation selection
remains unauthorized, with the feasibility gates unchanged.

**Attempted, blocked by current host memory; 0/5 questions completed.** This is
not a successful five-question benchmark. Measurements are preserved in
[local-model-hardware-smoke.json](local-model-hardware-smoke.json); the standalone
[smoke script](../scripts/smoke_local_qwen.py) imports no production code.

The fixed Qwen3-4B-Instruct-2507 Q4_K_M artifact was fully downloaded (2,497,280,736
bytes) and its preregistered SHA-256 verified:
`2fde00ce69dd4899c70d020845e2638353015bba0fdf161b3eb965f2bca4464e`.
Model [artifact source](https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF/blob/main/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf).
Runtime: [official llama.cpp b6096 Windows CPU release](https://github.com/ggml-org/llama.cpp/releases/tag/b6096),
`llama-cli.exe` SHA-256
`09aa8455c58d479cdb929db7ffa8a932757d351a91c35add9214f391ae7c747d`.

Hardware: AMD Ryzen 5 5500U, 12 logical processors; 7,893,950,464 bytes physical
RAM (7.35 GiB). Settings: CPU only, six threads, concurrency one, context 4,096,
batch/microbatch 128, greedy decoding, seed 1729, maximum 64 generated tokens,
no warmup. The five prepared prompts contain invented entities/values and 20
synthetic distractor rows each. No corpus/pilot/evaluation questions or labels
were provided. Five fresh processes were planned; the remaining four were not
started after the first resource-guard failure.

| Requested measurement | Observed |
| --- | --- |
| Questions completed | 0/5; one loading attempt, four not attempted |
| Time until first attempt was stopped | 2.391 seconds; **not answer latency** |
| Child peak resident working set before stop | 1,106,268,160 bytes (1.03 GiB); **not full-model peak memory** |
| Host available physical RAM before start | 1,173,929,984 bytes (1.09 GiB) |
| Host available physical RAM at guard | 66,584,576 bytes (63.5 MiB) |
| Prompt evaluation / generation speed | Not available; neither completed |
| Answer quality or evaluation scores | Not measured |
| Paid inference API calls | 0 |

Memory was sampled every 50 ms using Win32 process counters and physical-memory
status. The guard terminates the child below 64 MiB available host RAM, above
6 GiB child working set, or after 240 seconds per question. The first guard
triggered while loading tensors, before prompt evaluation. Loader logs advertised
a 1,683.28 MiB CPU_REPACK buffer and 2,362.55 MiB CPU-mapped buffer; these are
buffer descriptions, not measurements of simultaneous resident physical memory.

The requested five-question speed/memory test **remains incomplete**. The current
host state does not establish model feasibility or any inference-time estimate.
The subsequent authorized retry is documented separately above. Reliable hardware
feasibility is still required before a runtime manifest or evaluation selection.
Do not infer that this model
can never run on this machine. Do not substitute a smaller model, reduce the
evaluation context, change policy code, or use a remote service to bypass this
failure. Any broader model/scope change needs a pre-selection amendment and user
approval. Even a successful retry on these short prompts would not establish
throughput for the eventual 3,200-token input / 384-token output workload.

Downloaded files and raw synthetic logs remain in ignored local storage.
The smoke is separate from the skipped pilot LLM cross-check, which remains
**not run**. Production tests: **589 passed**, using bundled Python 3.12.14;
Python 3.11 remains unverified.

Current frozen production src tree:
`3261c6087757b9f3d9aed1166e264de45ac4f479`. All work in this amendment is
pre-approval feasibility/planning plus the explicitly requested hardware smoke.
There is no permission to push.
