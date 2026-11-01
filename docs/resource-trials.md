# Repeatable process resource diagnostics

The separate resource runner measures the existing graded lookup pipeline using
standard-library tools. It does not open gold, score answer correctness or modify
the verifier, contradiction policy, assessment schema or production config default.
It explicitly enables value discovery for this measured workload. Existing
in-process harness instrumentation is unchanged.

## Run

With a working project interpreter/package installation:

```powershell
python scripts/measure_resources.py --output data/evaluation/generated/resource-diagnostic-001
python scripts/measure_resources.py --directory data/evaluation/my-bundle --database data/processed/evidence.db --repeats 5 --warmups 1 --top-k 10 --output data/evaluation/generated/resource-native-001
```

The directory requires registered inputs.jsonl, evidence.jsonl and lineage.json.
It must be nonempty; no gold file is required. Use a fresh output directory so
existing diagnostics are not overwritten. Reports stay local under ignored
storage. No new dependency is installed and no network is used during trials.

Without a database, the runner measures fixed-evidence lookup/verification and
rendering; retrieval fields are null. With a database, it takes one read-only
SQLite online-backup snapshot for all workers. Actual FTS retrieval calls against
that snapshot are timed, and returned evidence must match the declared universe
and lineage fingerprints. Input hashes are checked by each worker and again by
the parent. A stale source or changed output across repetitions fails the run;
there is no silent average over inconsistent work.

## Fresh and warmed processes

Defaults are five timed repetitions, one warm-up pass, seed 1729 and top-k 10.
The runner first launches five fresh Python workers, each measuring one first
pipeline pass after imports and input loading. It then launches one worker with
one excluded warm-up pass followed by five timed passes. Requests are shuffled
deterministically per repetition; corresponding fresh/warm repetitions use the
same order. Warm-up uses a separate deterministic ordering.

These are **process-level conditions**, not verified cold versus warm storage.
OS cache state is uncontrolled, snapshot creation can warm pages, and each
production retrieval call opens/closes its own SQLite connection. The warmed
worker therefore does not imply a persistent SQLite connection cache. Worker
imports and bundle loading occur before pipeline timing in both conditions.
Parent launch-to-result wall time additionally includes startup, loading, work
and serialization; it is recorded separately and is not pure startup latency.

Condition order is fixed (fresh first, warmed second). Machine load, scheduling,
frequency changes and fixed-order drift are uncontrolled. The report makes no
causal speedup or deployment latency claim. Configure repetitions from 1–50,
warm-ups from 1–10 and a per-worker timeout from 1–60 seconds. Warmed repetitions
share one worker timeout. Failed/timed-out workers abort the report rather than
being dropped from its denominator.

## Timing and memory meanings

Every timed question records retrieval, evidence validation, assessment, rendering
and total pipeline seconds using time.perf_counter. Batch time sums question
pipeline durations; it excludes imports, input loading, warm-ups, output hashing,
memory-counter reads and between-question bookkeeping. The broader launch timer
includes them. The pipeline is the graded lookup path, not a timing comparison
between research baselines or an LLM generation experiment.

Raw samples remain in resource-report.json. Summary statistics are the median,
minimum, maximum and **nearest-rank p95**, with explicit sample counts. At five
repetitions p95 is just the maximum; these descriptive summaries are not confidence
intervals or evidence of stable tail performance. Each measured pass also records
an output digest; all repeats must agree, independent of question order.

On Windows, GetProcessMemoryInfo supplies current WorkingSetSize and lifetime
PeakWorkingSetSize in bytes. These describe resident working-set memory, including
native allocations, rather than traced Python allocations or private committed
memory. See Microsoft's [process memory explanation](https://learn.microsoft.com/en-us/windows/win32/psapi/process-memory-usage-information)
and [counter definition](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters).

The Linux implementation uses resource.getrusage(RUSAGE_SELF).ru_maxrss converted
from KiB to bytes, plus /proc/self/statm for current RSS when available. Python's
[resource documentation](https://docs.python.org/3/library/resource.html) documents
the peak counter; its [platform-unit clarification](https://bugs.python.org/issue30513)
explains why units must be handled explicitly. Other platforms and API failures
return null with a reason. Linux support is implemented but has not been exercised
on a Linux host in this session.

Memory counters are captured after loading, after measured passes and at worker
end. The reported peak is the **OS process-lifetime high-water mark**: it includes
imports, bundle loading, warm-ups and retained timing/result records. It is not a
resettable query-only peak. Current RSS snapshots alone cannot capture every brief
allocation spike. The counters exclude the parent process and any descendants;
they do not measure system-wide RAM, available hardware capacity, proportional
shared memory or the full application's deployment footprint. No claim about
fitting the proposed corpus/model into 8 GB follows from the synthetic run.

The report includes UTC timestamps, configuration, worker PIDs, dataset/lineage
hashes, snapshot SHA-256 when used, and parent interpreter/platform/dependency/Git
metadata. The snapshot/query workload is fixed, not a guarantee that original
source files remain authentic or that the universe is complete.

## Validation and remaining work

Twenty-one tests cover actual child workers, Windows memory counters, explicit
unavailability, summary arithmetic, worker failures/timeouts, input mutation and
read-only synthetic SQLite retrieval. A default five-repeat run completed on the
six-question original synthetic fixture, producing six worker records and five
samples per condition with non-null Windows working-set counters. A separate
SQLite integration test measured actual retrieval. These are diagnostic checks,
not a resource benchmark for TAT-QA or evidence for research novelty.

The software suite has 581 passing tests on bundled Python 3.12.14. Python 3.11
remains unverified. Real source eligibility, report identities and independent
annotation are pending. Before publication measurements, freeze a representative
corpus and workload, review trial ordering/cache controls and machine conditions,
and separately measure the remaining hybrid/model components. Next prepare an
explicit Phase 5 readiness report and reviewer handoff so pending evidence cannot
be mistaken for completed research validation.
