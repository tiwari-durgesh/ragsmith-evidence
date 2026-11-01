# Proposed smaller fixed answerer after the single authorized hardware retry

Recorded November 1, 2026, before any evaluation data selection. **Approved by
the user for artifact verification, five synthetic hardware questions and one
token-log-probability check.** The [result record](qwen15-runtime-checks.md)
documents successful checksum verification, 5/5 completion and the capability
check. Evaluation selection remains unauthorized. Preserve
`prereg-v1` at `6b1d04e` and the existing feasibility/staging amendment. This
document proposes changing only the fixed answerer because of measured host
memory pressure. No further 4B retries were made after the requested retry stopped.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from that pilot**. Facts share nine
contexts, and statistical independence is not established. Pilot labels remain
**provisional, single-annotator**. These hardware measurements do not evaluate
the pilot or supply human inter-annotator agreement.

## 1. Measured hardware retry: incomplete, 1/5 completed

Source: [retry measurements](local-model-hardware-smoke-retry.json). Exactly one
five-question run was attempted after the user closed applications. Question 1
completed; question 2 hit the existing RAM guard during loading. Questions 3–5
were not attempted. No answer correctness, citation correctness or confidence
calibration was inspected/scored. There was no evaluation selection or inference.

Measured total physical RAM was **7,893,950,464 bytes (7.352 GiB)**; measured
available physical RAM immediately before the run was **3,263,438,848 bytes
(3.039 GiB)**. This is usable physical RAM as reported by Windows, distinct from
the nominal installed 8 GB. Available RAM after stopping was 4,237,299,712 bytes
(3.946 GiB). Availability is dynamic, not a fixed model memory budget.

| Synthetic question | Status | Wall time including loading | Peak child resident memory | Prompt speed | Decode speed |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | Completed | 22.890 s | 3,479,781,376 bytes / 3.241 GiB | 33.60 tokens/s | 4.81 tokens/s |
| 2 | RAM guard during loading | 3.883 s until stop, not answer latency | 4,025,905,152 bytes / 3.749 GiB before stop | unavailable | unavailable |
| 3–5 | Not attempted after guard | unavailable | unavailable | unavailable | unavailable |

Question 1's runtime reported 428 prompt tokens in 12,737.63 ms, and 20 decode
evaluation runs in 4,159.66 ms. Speed was recovered from existing stderr: b6096
prints `runs` in its generation timing, whereas the original parser expected
`tokens`. The helper now accepts both; **this was offline log parsing, not an
inference retry**. The original raw report and stderr are preserved in ignored
storage; their hashes are included in the committed measurement JSON.

At the second stop, host available physical RAM was **40,529,920 bytes
(38.65 MiB)**, below the unchanged 64 MiB guard. The 3.749 GiB figure is an
observed pre-stop peak, not the full memory requirement for that question. Peak
working set was sampled through Win32 every 50 ms. Host RAM variation means one
successful question cannot establish reliable feasibility.

The fixed model/runtime/configuration were unchanged: Qwen3-4B-Instruct-2507
Q4_K_M with its already verified artifact hash; llama.cpp b6096 CPU x64; six
threads, concurrency one, context 4,096, batch/microbatch 128, greedy decoding,
seed 1729, maximum 64 generated tokens and no warmup. Prompts were the same five
invented, non-evaluation questions with synthetic distractors. OS cache state
was uncontrolled. These short-prompt observations do not estimate throughput at
the proposed 3,200-token input / 384-token output evaluation workload. There is
no five-question average, performance comparison or answer-quality claim.

## 2. Proposed fixed replacement and verified official provenance

Propose **Qwen/Qwen2.5-1.5B-Instruct-GGUF, Q4_K_M**, local CPU only. The
[official model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)
reports 1.54 billion parameters. This is a different model generation as well as
a smaller parameter count; it is not a controlled size ablation of Qwen3.

Pin the official Qwen repository revision
`a615a81362316d7b9f5a7a9c4313adfdf9b54588` and filename
`qwen2.5-1.5b-instruct-q4_k_m.gguf`. Its
[official raw Git-LFS pointer](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/raw/a615a81362316d7b9f5a7a9c4313adfdf9b54588/qwen2.5-1.5b-instruct-q4_k_m.gguf)
was checked directly on November 1, 2026 and specifies:

```text
size: 1117320736 bytes
SHA-256: 6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e
```

The [LICENSE at that same official revision](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/blob/a615a81362316d7b9f5a7a9c4313adfdf9b54588/LICENSE)
was read and identifies **Apache License 2.0**. This verifies the publisher's
checksum and license, not the contents of a locally downloaded model. A future
download must match the full published SHA-256 before execution. The 1.12 GB
file size is not a peak-RAM estimate; hardware fit and speed remain unverified.
No API key or paid inference service is required; model/API cash cost is $0,
excluding electricity/bandwidth already qualified in v1.

## 3. Controls and interpretation if approved

Use the replacement as the **sole fixed answerer for all three policies**.
Keep shared question-only decomposition, identical retrieved chunks and cached
candidates, verifier, contradiction policy, assessment schema, primary endpoint,
risk gates, sampling/stopping rules and human second-annotator requirement.
Keep context 4,096, greedy decoding, seed 1729 and the evaluation output cap
384. Pin its tokenizer/chat template/prompt and the existing runtime binary in
the manifest after synthetic compatibility checks. Do not choose among models
or prompts based on evaluation results.

The value-token likelihood remains an uncalibrated ranking signal. Calibrate its
threshold for this replacement on the separately designated 20 development
questions using the already declared grid/objective/risk constraint. Do not
transfer a 4B threshold, use evaluation labels for calibration, or relax the
primary coverage or risk criteria to compensate for the smaller answerer.

Interpret eventual paired results as evidence about **the sufficiency policies
conditional on this fixed 1.54B, quantized local answerer and this retrieval
setup**. Candidate extraction/format/citation failures may limit achievable
coverage; a verifier cannot recover facts never proposed. Low coverage or an
inconclusive primary endpoint cannot establish that the policy would fail with
a stronger answerer. Conversely, low emitted-claim risk with heavy abstention
does not establish useful performance: retain the joint coverage/risk gates.

Do not generalize to Qwen3-4B, larger/API answerers, enterprise-wide accuracy,
or a causal model-size effect. Do not compare the single successful 4B synthetic
timing with future evaluation scores or pool hardware runs with task evaluation.
Report generation failures and abstention explicitly under every policy.

This amendment must be committed and approved before any evaluation selection.
After approval, verify the downloaded replacement checksum, perform a separate
synthetic hardware/compatibility check, and freeze the runtime manifest before
selection. If hardware/compatibility still fails, stop for an explicit amendment;
do not automatically try additional models. Report identity and genuine-conflict
feasibility remain unresolved gates regardless of model size. A second human
annotator for 30–50 questions remains required before any paper results.

At proposal creation, production `src/` remained frozen at tree
`3261c6087757b9f3d9aed1166e264de45ac4f479`. No evaluation data was selected,
no paid API was called, and no model replacement had been executed. The approved
synthetic checks are recorded separately above. Python 3.11
remains unverified. Nothing is authorized to push.
