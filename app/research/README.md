# Offline backend study tools

These tools live outside frozen src/. They do not authorize real selection,
labeling, calibration or inference. Callers supply source snapshots and an answerer;
no external service or model is automatically started.

`build_corpus(excerpts, new_directory)` indexes complete source snapshots into
one SQLite FTS database. Source inputs contain no questions/gold. Study requests
carry a fixed context scope, excerpt group and explicit metric/year requirements.
Scope is applied before retrieval. Stable whole-unit packing takes at most eight
units and 3,200 input tokens including the complete prompt. The answerer's counter
must return a nonnegative integer. The fixed local runtime implements the interface
but must be explicitly supplied and started.

`run_batch` processes stable opaque case IDs, verifies source/database hashes and
shares the requirements, packed evidence and generated candidates across all three
policies. Preparation/generation failures remain denominator entries. Never-abstain
failure is not a correct abstention. The confidence threshold defaults to None;
that policy has `not_run_uncalibrated` and no decision. It is not a complete research
comparison while unset.

The caller supplies a frozen model/runtime/interface identity for the private
content-addressed cache. Keys also bind corpus, prompt, packing and decomposition.
Terminal failures are cached. Exclusive claims prevent duplicate generation;
interrupted or corrupt claims fail closed without automatic retry/expiration.
Logical result hashes exclude operational hit counts and are stable under input
reordering and cached reruns. This does not prove real model numerical determinism.
Cache/corpus outputs stay ignored and private; no labels enter the candidate cache.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Labels remain **provisional,
single-annotator**; independence is not established. Pilot compatibility checks
use a deterministic lookup stub, not model confidence or a new research evaluation.
