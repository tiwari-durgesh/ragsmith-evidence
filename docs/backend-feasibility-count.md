# Option C source-only feasibility count — November 2, 2026

**Count only. No questions selected, authored, decoded, labeled or sampled. No
calibration, model run or performance claims.** This report records the last
backend-session item and does not amend the study or authorize selection.

## Fixed source/exclusion procedure

The pinned TAT-QA raw training file matched SHA-256
`2df6e722cdbaaa37efcbfb280f5c9a15be29a6ec18f618ef936fe63cc6d07c69` and 12,845,647 bytes.
A selective parser decoded only table UID/cells and paragraph source text; upstream
question/answer values were skipped structurally without JSON decoding. Official
dev/test splits, upstream gold answers and question text were not used. Synthetic
parser tests instrumented decoder calls to check that skipped values never enter
the source projection.

All nine pilot context identities and eight known families were applied, along
with all retained UID exclusions, normalized pilot table hashes, fixed company
names, exact/5-shingle/row-overlap screens and transitive whole-component
quarantine. Source-verified issuer metadata was not invented for unnamed excerpts.
No additional non-pilot issuer identities were source-certified in this count.
The graph therefore includes content links and supplied verified-name links,
not guessed issuer links from arbitrary mentions. Later verified issuer edges
could merge groups or expand quarantine; this is not a locked selection graph.
Unresolved hidden report overlap remains accepted under Option C; name/hash checks
do not establish disjointness or independence. No exclusion was waived for counts.

| Source-only inventory | Count |
|---|---:|
| Training source contexts | 2201 |
| Content-linked groups before quarantine | 1992 |
| Excluded contexts / groups | 124 / 42 |
| Surviving contexts / groups | 2077 / 1950 |
| Direct pilot-name matches | 41 |
| Transitive-only quarantined contexts | 75 |

Exclusion reasons overlap: UID, family and hash matches are not additive counts.
The complete source-only exclusion ledger remains in ignored local storage; no
source/candidate/question IDs or case-level annotations are published here.

## Leads versus genuine opportunities

| Mechanical source lead | Candidate groups |
|---|---:|
| At least two canonical numeric fact leads | 550 |
| At least two explicit-unit-bound fact leads | 202 |
| Within-context same-key numeric discrepancy leads | 15 |
| Group-wide same-key numeric discrepancy leads | 16 |

The within-context and group-wide discrepancy counts overlap; do not add them.
A two-fact inventory is only an authoring lead, not a partial question: partial
eligibility needs a fixed question scope and exhaustive absence verification for
its unsupported requirement. Likewise numeric discrepancies do not establish the
same entity/metric/fiscal period/units, equal applicability or absence of a
resolving version/definition priority. Content-linked groups can mix issuers;
a repeated fact can appear in multiple contexts. These counts cannot be converted
into unique eligible questions or a guaranteed joint allocation.

**Certified genuine question opportunities: none established by this count.**
The reported zero certified opportunities is not evidence that zero genuine
opportunities exist. No candidate questions or labels were created to make that
certification. Genuine source/absence adjudication remains unresolved.

| Gate | Required | Certified by this count |
|---|---:|---|
| Evaluation partial / genuine conflict | 9 / 4 | Not established |
| Development partial / genuine conflict | 6 / 3 | Not established |
| Combined unique partial / conflict opportunities | 15 / 7 | Not established |
| Separate evaluation/development groups | 6 / 4 | Group inventory alone is large enough; joint mix/fact constraints unverified |

**Decision: STOP; feasibility gate does not pass.** Do not select data, calibrate,
lock a corpus, weaken quotas, replace genuine conflicts with controlled cases or
assume a feasible assignment from the lead counts. The narrower factual claim
“fewer than the required genuine opportunities exist” is **not established**.
Operationally we stop because required genuine yields and simultaneous allocation
cannot be certified. If later authorized source-only adjudication establishes
insufficient genuine yield, the fixed stop-for-another-amendment rule applies.
This report does not perform that later work or request a new corpus automatically.

## Provenance hashes

| Artifact | SHA-256 |
|---|---|
| Source-only projection | `a8f77ee44e20b1497ec46043fd9d8260ed70d9f245884d362f14f90e5e4c00e2` |
| Group graph | `87f8290273004b8793eeb3cfd53a5f54f760f739f793de4da2d87514ab490679` |
| Private exclusion ledger | `59d7fbcf1dfc41f634620dd96ec9dbf95462c4f307f98354f0be3c02d23cddb7` |
| Existing exclusion registry bytes | `5f0befb1d936e20b3146ff7ed5b7ae7b4820eb92a1816c73228ef40b480aa527` |
| Count-tool working bytes | `ce4c7db35e3fdab4a4b4e5f21e3baeddeb1fcca0deeae5f7ea0972e1e5424ffa` |

The exclusion-ledger digest above covers canonical ledger content; physical files
are separately hashable. The code supplement in backend-freeze-checklist.md records
staged blob hashes. Raw source/cache/labels/model files are not committed. No
source group is asserted to be an independent report, and no inferential or
performance result follows from this count.
