# Explicit-input runner skeleton

`app.evaluation_runner.run_case(payload, answerer, threshold=None)` is an
import-only engineering interface, not an approved real-evaluation command.
It has no dataset loader, sampler, labels, calibration routine or score exporter.
No development/evaluation data was read to build or check it.

`payload` uses the same `AskRequest` as the API/UI. The caller must supply an
answerer implementing `count(prompt)` and `generate(request, packed)`; the existing
fixed `LocalRuntime` implements this interface, but is **never constructed or
started automatically**. This session uses synthetic stubs only, including for
pilot-source compatibility probes. Stub scores are fabricated engineering inputs,
not token probabilities or model results. No model or inference endpoint is run.

Retrieval creates an ephemeral SQLite index from the explicitly supplied table,
uses the existing lexical retriever, and packs the same stable whole-unit prefix
for all three policies. The token counter must return a nonnegative integer;
the complete prompt is bounded by 3,200 input tokens. Actual tokenization with the
fixed model remains a separately controlled runtime step. Synthetic byte counts
are conservative bounds, not exact token counts. Truncation stays visible.

One generated candidate list is validated for requirement order, known citations
and finite confidence, then shared by never-abstain, confidence and graded
policies. The graded adapter delegates judgments, aggregation and supporting
citations to frozen functions. It does not modify the verifier or contradiction
rule. Generated references for the other policies are explicitly unverified.

**The threshold defaults to `None` and remains unset.** The confidence policy is
`not_run_uncalibrated`, with a null decision, not a successful abstention.
Explicit numerical thresholds are supported solely for synthetic interface tests
in this skeleton and remain marked uncalibrated. The existing demo API's historical
0.5 constant is not read or used by this runner. There is no threshold selection
or override of the preregistration in this module.

Malformed/empty generations are failures that remain in denominators. They are
never repaired, retried or replaced with another model. Empty candidate values
also remain flagged when another requirement has a value. Preparation errors
raise before generation; a future authorized batch executor must retain such
failed requests rather than silently dropping them. No statistics are computed.
The result always says `research_ready: false`.

`app.contracts` now defines the shared outer response schema; the inner frozen
assessment remains unchanged. `app.checked_service` checks malformed grids,
validates the response and logs error codes/counts without questions, table
contents, answers, labels or full exception strings. API/UI wiring imports this
bridge. This is transport validation, not a new evidence policy.
