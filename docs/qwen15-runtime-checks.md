# Approved 1.5B answerer: synthetic hardware and log-probability checks

Recorded November 1, 2026, following user approval of the smaller-answerer
amendment. **No evaluation data selected; no production source changes; no push.**
These are hardware/capability checks only, not answer-quality evaluation. The
earlier pilot has **18 independent source facts and 36 derived cases; no statistical
or performance claims are made from that pilot**. Its labels remain
**provisional, single-annotator**, and statistical independence is not established.

## Approved artifact and fixed conditions

Downloaded the official Qwen2.5-1.5B-Instruct Q4_K_M file from the pinned Qwen
repository revision `a615a81362316d7b9f5a7a9c4313adfdf9b54588`. The complete local
file is 1,117,320,736 bytes; computed SHA-256 matches the approved amendment and
the [official artifact pointer](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/raw/a615a81362316d7b9f5a7a9c4313adfdf9b54588/qwen2.5-1.5b-instruct-q4_k_m.gguf):

```text
6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e
```

The official revision's [LICENSE](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/blob/a615a81362316d7b9f5a7a9c4313adfdf9b54588/LICENSE)
is Apache-2.0, as verified in the approved amendment. Downloaded bytes were
checksum-verified before execution; no model substitution occurred.

Runtime remains llama.cpp b6096 Windows CPU x64 on AMD Ryzen 5 5500U, 12 logical
processors. CLI SHA-256:
`09aa8455c58d479cdb929db7ffa8a932757d351a91c35add9214f391ae7c747d`.
Server SHA-256:
`f914f66e4886d3eb6dba76c0285a26d07b3943ac93152d72b470fe3d87ece41c`.
Both binaries came from the previously pinned official release archive.

The five prompts, their invented records/distractors and runtime settings are
the same as the prior smoke: CPU only, six threads, concurrency one, context
4,096, batch/microbatch 128, greedy decoding, seed 1729, maximum 64 output tokens,
no warmup, a fresh process per question. Only the approved model changed.
Cache state was uncontrolled. No corpus, pilot or evaluation questions were used.

## Five-question measurements: 5/5 completed on the first run

Machine-readable evidence: [qwen15-hardware-smoke.json](qwen15-hardware-smoke.json).
Wall time includes process startup/model loading. Decode speed is the runtime's
reported token-evaluation speed; the corresponding counter is called `runs` in
b6096 logs. Peak memory is child-process resident working set, not whole-host
memory or virtual/address-space size. Win32 counters were sampled every 50 ms.

| Synthetic question | Wall seconds | Peak resident MiB | Prompt tokens/s | Decode tokens/s | Outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 8.50 | 1722.87 | 87.58 | 10.59 | completed |
| 2 | 8.27 | 1722.74 | 84.89 | 11.68 | completed |
| 3 | 8.61 | 1722.82 | 94.85 | 10.81 | completed |
| 4 | 8.33 | 1722.84 | 93.55 | 10.41 | completed |
| 5 | 7.70 | 1722.80 | 93.50 | 13.59 | completed |

All five completed without a guard, crash or inference retry. Total wall time
was 41.41 seconds, mean 8.28 seconds. Observed peaks were **1.68236–1.68249 GiB**,
a spread of 135,168 bytes (132 KiB). **Memory was stable across these five fresh
processes.** This does not test a long-lived server for leaks or establish full-
length workload memory stability.

Measured usable physical RAM: **7,893,950,464 bytes / 7.352 GiB total**; available
before the run: **2,588,528,640 bytes / 2.411 GiB**. Minimum available during any
trial was **812,339,200 bytes / 774.71 MiB**; available after the run was
2,889,449,472 bytes / 2.691 GiB. Host availability varies over time. The unchanged
guards were 64 MiB minimum available host RAM, 6 GiB maximum child working set
and 240 seconds per question. No further model was tried.

## One actual value-token likelihood computation

Machine-readable evidence: [qwen15-logprob-check.json](qwen15-logprob-check.json).
Started the same release's local server on **127.0.0.1 only**, concurrency one,
context 4,096 and the same CPU settings. Sent exactly **one** additional invented
question to `/completion`, requesting `n_probs: 5`, `post_sampling_probs: false`,
`return_tokens: true`, greedy decoding and no prompt cache reuse. There were
**zero remote inference requests or paid API calls**. The server was stopped
after the check; no second request/retry was needed.

The runtime returned `completion_probabilities`, including generated token IDs,
decoded bytes and finite, nonzero-negative `logprob` values. This matches the
[pinned official server documentation](https://github.com/ggml-org/llama.cpp/blob/b6096/tools/server/README.md),
which distinguishes pre-sampling log probabilities from post-sampling probabilities.
Observed nonzero-negative log probabilities also rule out reporting greedy
one-hot probabilities for this check.

For the generated value string `2745.63`, token bytes reconstructed the returned
completion. Selected the seven tokens overlapping its content byte interval
`[18,25)`, excluding key text, quote delimiters and surrounding output. Tokens
were `2`, `7`, `4`, `5`, `.`, `6`, `3`:

```text
mean value-token log probability = -0.003046269399679399
exp(mean value-token log probability) = 0.9969583657710941
```

Thus the specified confidence signal **can be computed with this local model and
runtime**. It remains an uncalibrated ranking signal, not a correctness probability.
No correctness score or threshold was inferred from this value. This one ASCII
value check does not validate every output format, escaped string, citation or
the full candidate/verifier integration. The server peak was 1,799,991,296 bytes
(1.676 GiB); its minimum available host RAM was 1,150,709,760 bytes (1.072 GiB).
Raw synthetic request/response/logs remain in ignored local storage; the response
hash and selected token-level evidence are in the committed JSON.

## Runtime estimate for Stage 1 plus calibration

Count **70 shared answerer generations**: 20 development/calibration questions
plus 50 Stage-1 questions. All three policies reuse each question's retrieved
evidence and cached candidate generation. This is **not 210 model generations**.
Confidence calculation and the three selection/verifier rules are applied to
that cache. No development or evaluation data was selected to make this estimate.

Measured aggregate rates are totals divided by total component time: **90.75
prompt tokens/s** and **11.20 decode tokens/s**. Mean process/load/other overhead,
after subtracting reported prompt/decode time from wall time, was **1.76 s**.
For the preregistered maximum 3,200 input / 384 output token budget:

```text
70 * (3200 / 90.7485 + 384 / 11.1951 + 1.7626)
  = about 4,993 seconds = 83.2 minutes of model generation/load time
```

Using the slowest observed prompt/decode rates and largest observed overhead
instead yields **89.4 minutes**. This is about 59–64 minutes for the 50 evaluation
generations plus 24–26 minutes for 20 calibration generations. With outputs as
short as the smoke (mean 19.4 decode evaluations), the same input assumption
yields about **45 minutes**, but evaluation outputs need not be that short.

**Planning budget: approximately 2–2.5 CPU hours for the 50-question stage,
calibration and all three cached policy passes**, allowing roughly 35–80% above
the full-token-budget model estimates for log-probability extraction,
retrieval, verification, persistence, slowdown and scheduling overhead. That
allowance is a planning judgment, not measured end-to-end overhead or a confidence
interval. It assumes an existing small index and no extra model calls per policy;
initial index construction/downloads, corpus recovery and human annotation are
excluded. No end-to-end evaluation run has occurred.

The smoke used 426–445 prompt tokens and 16–25 decode evaluations per question.
Prefill/attention and decoding costs can change at longer lengths and with memory
pressure, so linear extrapolation may underestimate the full workload. These
numbers are estimates, not a runtime guarantee or evidence about answer quality.

The approved smaller-model interpretation and all primary coverage/risk gates
remain unchanged. A final evaluation prompt/packing/interface manifest and
development calibration must be locked before evaluation selection. Report-
identity exclusion, genuine-conflict feasibility and human second annotation
remain separate gates; a successful hardware smoke does not resolve them.

Production `src/` remains at frozen tree
`3261c6087757b9f3d9aed1166e264de45ac4f479`. Python 3.11 remains unverified.
