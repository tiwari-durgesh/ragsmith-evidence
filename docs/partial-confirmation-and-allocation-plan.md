# Plan for confirming partials and reserving group roles

**Plan only.** No group roles, review decisions or study questions are assigned
by this note. The [40-group audit](partial-authoring-audit-results.md) remains
provisional: 23 proposed drafts, no author-confirmed partials. The rejection
spot check changes no audit judgment and confirms no positive draft. Removing
natural conflicts and admitting audit drafts to a future study pool both need
explicit approval in a revised protocol before implementation. The existing
feasibility stop remains in force.

## Reserve roles before showing confirmation packets

1. For a separately authorized round, freeze the eligible source graph, complete
   excerpt scopes, draft wording, two requirements and stable IDs. Keep all pilot,
   near-duplicate and shared-issuer exclusions. Use only source facts and draft
   records; no upstream QA labels, system outputs, calibration or performance.
2. Preserve the existing natural quotas as the proposed planning target:

   | Proposed partition | Groups | Full | Partial | Missing | Total |
   | --- | ---: | ---: | ---: | ---: | ---: |
   | Evaluation | 6 | 12 | 9 | 5 | 26 |
   | Development | 4 other | 8 | 6 | 3 | 17 |

   This proposal leaves the seven former conflict slots empty, rather than
   redistributing them. Constructed conflicts are separate and count toward
   neither partition. The smaller totals and the impact on the existing
   20-question development calibration and risk denominators must be explicitly
   settled in an amendment. Until then, these counts are planning assumptions,
   not changes to the registered design. Retaining 30/20 instead would require
   specifying the seven replacement slots before reserving groups.
3. A source-only coordinator privately enumerates provisional joint allocations.
   Find six evaluation and four different development excerpt groups with room
   for the complete proposed mixes. Use source-screened full and missing drafts
   as capacity evidence; a group with unused slots is not presumed to have the
   right candidates. Enforce **at most five questions total per group across
   all three strata**, and no reused requested fact across either role, including
   absent facts. For example, two nominated partials leave room for at most
   three full or missing questions combined. Excerpt group separation does not
   prove separation by underlying report.
4. Use the existing seed-1729 hash priority and first-feasible lexicographic
   order: development groups, development drafts, evaluation groups, evaluation
   drafts, with `development` and `stage1` streams respectively. Before seeing
   any new confirmation, freeze and hash a private reservation of the group
   roles, nine provisional evaluation partial nominations, six provisional
   development partial nominations, and the ordered alternate drafts within
   those roles. A nomination is a feasibility reservation, not an eligible or
   final study selection. Keep the roles and nominations hidden in the author's
   packets. Other groups are not automatic reserves. If no provisional joint
   allocation is feasible, stop before asking the author to confirm.

## How the author confirms each draft

Visit review groups in ascending SHA-256 priority of canonical JSON
`[1729, "source-screen", stable_group_id]`, breaking ties by stable ID. Within
each group, review the frozen drafts in the same source-screen hash order using
stable draft IDs. This order is separate from the allocation priority and uses
no outcomes. Stop after **four active hours total** of the author's time, in two
sessions of up to two hours. Use roughly ten minutes per draft as a planning
target. If a check cannot be finished, mark it `unresolved` or `not reviewed`;
do not skip a necessary absence check to stay within budget.

For each draft, record `confirm`, `reject` or `unresolved`, the reason, and
source anchors in a private return sheet:

- Verify that the wording is natural, asks for exactly two distinct direct
  extraction facts, and matches a two-item question-only decomposition. Check
  entity, metric, period, units, sign, scope and applicable version. No implied
  subtraction or calculation, and no inference from question wording to gold.
- For the supported requirement, locate one unambiguous value and cite its
  original cell or passage, with headers and applicable notes checked.
- For the other requirement, confirm that it is plausible for that entity and
  period. Check the frozen keyword/variant search, inspect every relevant hit,
  and independently scan all tables, headers, continuations, notes and relevant
  prose in the fixed excerpt scope. Record coverage and why apparent matches do
  not answer it. A missing referenced source, damaged entry, version ambiguity,
  unsupported format or retrieval miss does not establish absence. Explicit
  zero or nonoccurrence can answer a requirement; it is not missing.
- Confirm only when exactly one fact is supported and the other is absent in
  scope. A substantive wording or scope correction is not approval of the
  frozen draft. Keep the original decision and refer any new draft to a
  separately authorized freeze. Independent review remains a separate step;
  the author's confirmations do not replace it.

## After confirmation, and what happens on shortfall

Recheck joint capacity using only confirmed, eligible drafts and the frozen
group roles. For a failed nomination, use the first jointly feasible confirmed
alternate from the frozen list **within that partition**, respecting the same
five-question limit, full and missing capacity, and fact deduplication. Do not
move a group to the other role or count the same fact twice. Final evaluation
materialization still waits for the development calibration freeze under the
separately approved protocol.

If fewer than 15 eligible distinct partials are confirmed, or if 15 or more
cannot fill **9 evaluation and 6 development** along with full and missing
quotas, stop and report both partition shortfalls and the reason. Do not
redistribute slots, relax the rubric, extend the clock or run the study.

The **14 unresolved groups are not eligible reserves by default**. A separately
authorized, bounded resolution pass may use them in seed-1729 source-screen
order **before** the reservation is frozen. It may resolve source binding or
complete an unfinished check under the existing source scope. It may not guess
a damaged value, treat an unavailable note as absence, narrow a scope, or add
new sources to make a draft pass. Preserve old audit records and record any new
adjudication separately. If the reservation already failed, using newly resolved
groups requires explicit approval and a new source-only freeze, never a quiet
post-review top-up.

## Source full and missing drafts

Use the same eligible excerpt groups, source-only T1/T2/T3 authoring and fixed
scopes as for partials. **Full** drafts ask for two related facts with separately
verified values and source anchors in scope. **Missing** drafts ask for two
plausible facts about an attested entity and period; each needs its own complete
absence check under the same rubric. Derive plausible requests from source
terminology and neighboring disclosed metrics or periods, not invented entities,
arbitrary out-of-range years, deleted rows or system failures. Apply the same
requested-fact deduplication to full, partial and missing drafts. A draft with
an ambiguous fact or unavailable resolving material stays unresolved and does
not fill a quota. Freeze wording, scopes and evidence before any system run;
report outcomes only for the design ultimately approved.
