# Timed identity-only trial: five existing pilot contexts

November 1, 2026. User-authorized Step 1 trial, stopped after five source-context
lookups. **No evaluation questions selected, authored, labeled or scored; no
retriever/answerer/verifier outputs used.** Local question fields and upstream
answer labels were not accessed. Searches used table/prose fingerprints only;
an unsolicited dataset-viewer search result was not opened or used.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Facts share nine contexts;
statistical independence is not established. Labels remain **provisional,
single-annotator**. Source identity matching does not change those labels.

## Trial design and observed times

Started the work clock at **16:39:20 UTC**. Chose five of the nine existing pilot
context IDs, using seed 1729 and the `source-screen` hash-priority stream. This
is an identity-work queue, not an evaluation sample. Starting with pilot sources
avoids speculative eligibility claims before the exclusion list is recovered.
The first lookup began at 16:40:27 UTC; the fifth ended at **16:49:19 UTC**.
The work clock includes setup, failed downloads and record preparation; it does
not reset after this trial. The machine-readable record stores the final work
checkpoint and elapsed time separately from lookup time.

| Trial context | Matched source family | Identity-matching minutes | Result |
| --- | --- | ---: | --- |
| 1 | American Tower, FY ended 2019-12-31 | 3.63 | family matched; excluded as pilot |
| 2 | Carpenter Technology, FY ended 2019-06-30 | 1.91 | family matched; excluded as pilot |
| 3 | Mimecast, FY ended 2019-03-31 | 1.34 | family matched; excluded as pilot |
| 4 | Shopify, FY ended 2019-12-31 | 1.21 | family matched; duplicate filing-copy caveat below |
| 5 | Carpenter Technology, FY ended 2019-06-30 | 0.78 | same family as trial 2; excluded as pilot |

**5/5 context-to-report-family matches, four distinct families; 8.88 lookup
minutes total, mean 1.78 minutes/context.** The four fresh-report lookups averaged
2.03 minutes. The fifth benefited from a cached report and is not an independent
fresh-report lookup. This small pilot-source convenience trial is not a measured
resolution rate for unseen contexts. **Four of nine pilot context identities
remain unattempted** under the instruction to stop after five; the nine-report
exclusion prerequisite is not complete.

Evidence and exact UTC intervals: [trial record](report-identity-five-context-trial.json).
It records context IDs, official sources, filing metadata, archive URLs/byte
counts/SHA-256 and table fingerprints. No human answerability labels are included.

## Identity evidence inspected

- **American Tower:** [official 2019 Form 10-K](https://www.sec.gov/Archives/edgar/data/1053507/000105350720000028/amt1231201910k.htm),
  CIK 1053507, accession 0001053507-20-000028, filed 2020-02-25. Item 6 balance-
  sheet table, printed page 22, matches years, million-unit header and multiple
  rows; the independent acquisition discussion and restricted-cash footnote
  match. The [issuer filing page](https://americantower.gcs-web.com/sec-filings/sec-filing/10-k/0001053507-20-000028)
  independently confirms report period and filing date.
- **Carpenter Technology:** [official 2019 Form 10-K](https://www.sec.gov/Archives/edgar/data/17843/000001784319000058/crs630201910k.htm),
  CIK 17843, accession 0000017843-19-000058, filed 2019-08-29. Trial 2 matches
  Note 21 Supplemental Data, printed page 86, including row meanings, three
  fiscal years and units. Trial 5 independently matches the deferred-tax table
  and accompanying loss-carryforward discussion, printed page 80. These are
  two pilot contexts from one source family, not two independent reports.
- **Mimecast:** [official 2019 Form 10-K](https://www.sec.gov/Archives/edgar/data/1644675/000156459019020753/mime-10k_20190331.htm),
  CIK 1644675, accession 0001564590-19-020753, filed 2019-05-29. Item 6's
  adjusted-EBITDA reconciliation, printed page 39, and the separate definition/
  management-use discussion match. Archived reconciliation page was explicitly
  distinguished from an earlier summary table containing some of the same values.
- **Shopify:** [original Form 40-F MD&A exhibit](https://www.sec.gov/Archives/edgar/data/1594805/000159480520000010/exhibit13mda2019.htm),
  CIK 1594805, accession 0001594805-20-000010, filed 2020-02-12 for 2019-12-31.
  The R&D comparison table and independent employee-cost explanation match
  MD&A printed page 17. The same material also appears in accession
  0001594805-20-000018. **Family identity is recovered; which filing copy the
  dataset extractor used is not uniquely established.** Both are excluded as
  the same pilot issuer/period family. No version priority or conflict label
  was inferred from these copies.

Original SEC/issuer material was inspected through browsing. Direct SEC/issuer
downloads returned HTTP 403 in several cases. Four annual-report mirrors were
downloaded, checked locally for the correct company/year and corresponding
table, then hashed. **Recorded hashes identify those archived mirror bytes,
not an asserted official published checksum or a direct SEC download.** PDFs
remain ignored/local; only provenance metadata is committed. The web tool's
American Tower mirror opening redirected to an unrelated report; that result
was disregarded. The actual local download was separately identified as American
Tower 2019 and matched to the official filing. No questionable redirect was
accepted as identity evidence.

## Exclusion ledger and genuine-candidate counts

[Every context exclusion and reason](report-identity-trial-exclusions.json) is
recorded against the pinned training-file SHA-256. Table comparison reads only
table cells, not questions. Findings:

- **Nine exact pilot context IDs excluded**, including the four whose identity
  lookups were deferred.
- **Two additional contexts excluded pending source-backed clearance**, under
  the already fixed smaller-table row-overlap threshold: 0.60 and 0.50. Their
  5-shingle Jaccard scores are below 0.80; they are conservative similarity
  flags, not verified common-report identities. Neither was silently cleared.
- **Four matched pilot families excluded in full**, including versions and
  overlapping excerpts. The ledger records these family-level exclusion rules;
  assignment of every raw context to those families is not yet certified.
- The remaining **2,190 contexts are not identity-certified survivors**. They
  remain unavailable for selection until report membership and overlap are
  established. The question-similarity screen is intentionally **not run** in
  this identity-only batch; it must precede any later approved selection.

**Genuine partial candidates verified eligible: 0 established. Genuine conflict
candidates verified eligible: 0 established. Actual surviving counts: unknown.**
All five timed contexts are pilot material and excluded. No absence/conflict
answerability judgment was authorized or made. Previously reported 167 partial
leads and 166 discrepancy contexts were never genuine eligible-question counts
and are not upgraded by this trial. Missing corpus facts cannot be established
by identity matching alone. This is not evidence that no such questions exist.

## Projection against the four-hour cap, and stop

Separate two materially different planning scenarios:

1. **Report-lookups only:** the completed 8.88 minutes plus four remaining pilot
   context lookups and 14 new report-family lookups at 2.03 minutes each is
   about **45.3 minutes**. This optimistic scenario excludes split-wide context
   reconciliation, duplicate/version adjudication, corpus-completeness proof,
   and genuine partial/conflict feasibility. It is not an end-to-end estimate.
2. **Manual split reconciliation:** 2,201 contexts at the observed mean of
   1.776 minutes/context projects to **65.1 hours**, well above four hours. This
   assumes separate manual context work. Grouping, a verified upstream mapping
   or automated source fingerprints could reduce it substantially; those savings
   have not been measured or established by this five-context trial. This is a
   conservative manual-workflow scenario, not a proven minimum or a statistically
   representative forecast.

Thus the trial does **not** establish a complete 50-question feasibility pass
within four hours. Under the user's requested stop rule, do not continue the
full manual split workflow or make more source lookups. A [30-question reduced-
scope amendment proposal](thirty-question-reduced-scope-proposal.md) is recorded
instead. Reducing only the question count would not solve the provenance burden;
that proposal explicitly identifies the necessary corpus-boundary change and
its interpretation cost. **It awaits user approval; nothing is changed in the
approved evaluation design by this report.**

No `src/` changes, no inference, no evaluation data selection and no push.
All commits for this batch are local on `codex/public-progress` only. Original
local `main` and preregistration tags remain unchanged.
