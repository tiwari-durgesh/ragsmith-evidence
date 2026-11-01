# Proposed source-genuineness verification procedure

November 2, 2026. **Plan only; execution requires approval.** No candidates were
inspected or sampled in preparing this document. This is a proposed verification
protocol, not a change to the preregistration, amendments, quotas or manifest.

The [aggregate feasibility count](backend-feasibility-count.md) found 16
group-wide discrepancy leads (including the 15 within-context leads), 550
two-fact lead groups, and an explicit-unit subset of 202. These are mechanical
leads, not genuine conflicts, partial questions, independent reports or selections.
The [Option C amendment](option-c-excerpt-corpus-amendment.md) remains controlling.

## 1. Inspectors, blinding and allowed records

After approval, Codex prepares source-only packets and performs a provisional
first pass. The user is the accountable human verifier and reviews every proposed
conflict yes, each unresolved scope/version issue, and the partial yes evidence.
No independent second annotator is assumed available for this screening exercise.
Any certification based on this process is provisional, single-annotator; Codex
assistance does not constitute human inter-annotator agreement. Independent human
review of all 30 evaluation questions remains required before paper results.

Packets contain the pinned training source projection only: original table cells,
complete headers, notes, paragraphs, source anchors, context hashes and group
membership. Include all excerpts in the predeclared group scope, with entity and
version boundaries recorded before judgment. Do not narrow scope or remove
resolving material. Missing referenced material prevents certification.

Exclude upstream TAT-QA questions/answers, pilot labels, any generated answer,
retrieval ranking, verifier output, confidence, policy decision or result report.
No study system runs, question wording, case IDs, decomposition, development or
evaluation assignment are produced. Human verification also uses these blinded
packets only. The inspection task concerns source relationships, not how a system
would answer them. Original-report authentication is not asserted where Option C
provides only an excerpt; unknown entity or applicability still blocks a yes.

Retain a private audit with one row per screened group: stable group ID, input
hashes, yes/no certification, reason code, source anchors, applicability/precision
checks, unresolved flag, inspector and human confirmation. A no means **not
certified**, not necessarily that no conflict exists. Distinguish rejected,
unresolved and not reviewed reasons without adding a third certification value.
Source facts and rationales stay private; publish aggregates and artifact hashes
only. These are screening records, not final question gold labels.

## 2. Conflict certification: inspect all 16 leads

Freeze the 16-group roster and packet hashes before opening source contents.
Visit every group in the existing seed-1729 `source-screen` hash-priority order,
including groups encountered after the seventh yes. Do not stop when the desired
count is reached or replace inconvenient leads. Apply this rubric:

| Check | A genuine conflict requires | Otherwise |
| --- | --- | --- |
| Entity and scope | Same identifiable entity, consolidation/segment, geography and gross/net basis | Different scopes: no; unresolved binding: no, unresolved |
| Metric and time | Same metric definition and exact fiscal period/date, including duration versus point-in-time | Different definitions, calendar/fiscal periods or durations: no |
| Units and precision | Same source-established unit/currency basis and incompatible values after accounting for stated precision | Compatible rounding or unresolved units: no |
| Applicability and version | Both real statements are equally applicable; no correction, restatement, superseding version or explicit source priority resolves the difference | A later corrected/restated value resolving an older one: no |
| Source fidelity | Both values and their bindings are present in the source, with complete headers, notes and adjacent explanation checked | Parser/transcription/header/continuation error: no |
| Remaining contradiction | After those checks, the same fact has incompatible values with no source explanation | Unexplained numbers alone or inaccessible resolving material: no, unresolved |

For rounding, record each reported precision and compare the intervals consistent
with that precision and the source's rounding convention. If nearest rounding is
established, the half-unit interval is a useful check; touching/overlapping
intervals do not certify a conflict. Do not assume a rounding convention when it
would determine the verdict. Source-explicit unit equivalences may be checked
for this audit; no source numbers or pipeline conversion rules are changed.

A table/text discrepancy is not automatically a genuine conflict. First check
whether prose describes another year, segment, definition, rounded amount or
restated number, or whether extraction lost a header or qualifier. Those are no.
If the original excerpt table and prose truly assert incompatible values for
the identical fact, both are equally applicable, and no qualification resolves
them, the different modalities alone do not disqualify a genuine source conflict.
Whether the frozen pipeline can represent that evidence is a separate later
compatibility gate; this audit does not run it or certify that gate.

Record a source-fact fingerprint (entity, definition, period, basis and source
anchors) for each proposed yes. Count at most one certified conflict opportunity
per group, and count a repeated underlying disputed fact only once across groups.
Apply any newly source-verified issuer links and the existing transitive exclusion
rules before reporting the surviving count. Do not waive exclusions or split a
group for yield. Freeze any revised graph and retain the old graph hash; graph
changes can reduce the count and do not establish report disjointness.

The user confirms each proposed yes from the two source statements and scope
checklist. Unconfirmed or ambiguous cases remain no, with a reason. This is
genuineness verification only: a yes is not a selected or authored question.

## 3. Sampled partial-opportunity audit

After approval, draw a fixed **20-group source-screen sample**, without looking
at contents first: ten from the 202 explicit-unit groups and ten from the other
348 two-fact groups. Within each stratum take the first ten in the existing
seed-1729 `source-screen` priority order, with the existing stable-ID tie break.
This sampling is for a feasibility audit only, not development/evaluation
selection. Freeze the roster, strata and group hashes before inspection. If
identity/exclusion updates change the frame before inspection, first record the
new frame and its sizes, then make the same fixed draw from that frame. If they
change it after inspection begins, report affected groups as uncertified and do
not substitute new ones. Insufficient stratum capacity requires approval of a
revised audit plan rather than silent redistribution.

Use source inventories and the existing neutral T1/T2/T3 template families to
audit whether a plausible two-fact request could have exactly one supported
fact and one genuinely absent fact in the fixed excerpt scope. Do not instantiate
final questions or assign study conditions. Before searching for absence, freeze
a small source-derived fact-slot roster in canonical entity/metric/period order:
use metric names and periods attested in the group's own source inventory, and
only semantically plausible combinations for that entity. No invented metrics,
entities or arbitrary periods; no arithmetic. Examine at most the first three
plausible two-slot combinations under that order, logging each disposition.
This bounds opportunistic searching; it does not exhaust every possible request.

For a provisional yes, retain one witness fact pair: one directly supported
value with its original cell/paragraph anchor, and one absent slot verified by
the [fixed absence procedure](thirty-question-reduced-scope-amendment.md).
Freeze scope and literal synonyms/period/unit vocabulary first; search phrases
and individual terms, inspect every hit and its headers/notes, and independently
scan every in-scope table and relevant narrative even if there are no hits.
Log queries, coverage and dispositions. Retrieval failure, unreadable material,
an unsupported parser format or an ambiguous requirement is never absence.
Never hide a supporting row or a resolving excerpt. If complete verification
cannot fit the cap, record no, unresolved; do not shorten the absence procedure.
The user verifies every proposed yes before it enters the certified audit count.

Report screened/confirmed-yes/rejected/unresolved counts by stratum, the raw
20-group yield and a frame-weighted descriptive yield:
`(202/550) * (yes_explicit/10) + (348/550) * (yes_other/10)` for the original frame.
Use recorded frame sizes if exclusion updates occurred before the draw. Unresolved
groups remain in the denominator. A corresponding projected count is only a
planning estimate under this bounded search, not a certified pool size or an
unbiased estimate of every possible partial opportunity. Report the unresolved
fraction alongside it; do not claim binomial independence, statistical confidence
or document generalization from these potentially overlapping groups.

This audit cannot certify 15 unique partial questions or a joint allocation.
Sample membership grants no preference in later selection. No audit witness is
automatically promoted into a question or final gold label. Any later authoring,
selection and review require their own authorization and the unchanged fixed rules.

## 4. Time caps and stopping decisions

Proposed hard cap: **five combined active person-hours**, not an overnight run.
Track Codex and human active time separately; do not count waiting for a reply as
inspection time. No external model/API calls or additional corpus acquisition.

| Activity | Maximum active time |
| --- | ---: |
| Source packet preparation and all 16 conflict first passes | 100 minutes |
| User conflict verification | 60 minutes |
| Partial roster preparation and 20 first passes | 100 minutes |
| User partial verification | 30 minutes |
| Aggregate report, hashes and stop decision | 10 minutes |

Within those caps, allow at most five minutes of source inspection per conflict
group and four minutes per partial group on the first pass. Hard cases become
unresolved rather than receiving repeated searches. At a cap, mark remaining
groups no/not reviewed. No automatic time extensions, sample replacements or
additional lead discovery. The estimate is deliberately bounded; exhaustive
absence checks may cause a low certified partial yield within this cap.

If fewer than **seven distinct surviving group-level conflicts are certified**,
stop before authoring/selection and return for explicit approval. Report whether
the shortfall reflects actual rejections, unresolved cases or unfinished review;
failure to certify seven does not prove fewer than seven exist. Propose, without
applying, these amendment options:

1. **Lower the conflict quota:** specify new development/evaluation counts and
   replacement strata before any selection; restrict conclusions to descriptive
   conflict behavior with the smaller count. Prefer this when a modest genuine
   yield exists and additional annotation time is unavailable.
2. **Add candidates:** approve a bounded source-only search or further review,
   keeping exclusions and the definition fixed. Any corpus expansion, changed
   scope or additional acquisition needs an amendment before access. No open-ended
   search until a quota is met, and no system-guided enrichment.
3. **Drop the conflict stratum:** amend both mixes and explicitly forgo empirical
   claims about genuine-conflict handling. Controlled synthetic conflicts may
   remain separately identified demonstrations, never quota replacements.

Seven yes groups are a necessary screening milestone for four evaluation plus
three development conflicts, **not permission to proceed**. Unique requested
facts, six/four disjoint excerpt-group assignment, the five-question cap, all
other strata and the full 12/9/5/4 plus 8/6/3/3 mixes must still be jointly
feasible. Source representation may impose additional compatibility limits.
The partial sample provides a yield estimate only; inability later to certify
nine evaluation and six development partial opportunities triggers the same
stop-for-amendment rule. No quota, metric, seed, model or policy changes here.

## 5. Deliverable after separately approved execution

Deliver aggregate conflict yes/no counts and reason counts, separately reporting
unresolved/unreviewed groups; the private one-row-per-group audit and hashes;
partial sample-frame/roster hashes and descriptive yields; measured human/Codex
minutes; and a clear stop/remaining-gates statement. Publish no source-level
annotations. Keep `src/`, preregistration, amendments and public manifest unchanged.
Commit only the approved public report locally on `codex/public-progress`;
do not push. This document authorizes none of those execution steps by itself.
