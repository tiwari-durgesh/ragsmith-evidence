# Four-case demonstration (about five minutes)

Launch using the [Windows command](README.md), open localhost:8501 and keep
**Prepared pilot cases** selected. Read the visible banner aloud:
“Prototype. Provisional pilot only. No performance claims.” The model is off.
Do not edit inputs, thresholds or policies to improve an example.

## 1. Full support — Q01

**Click:** Choose **Q01 · Full**, inspect the question, requested facts and source
table, then **Run**. Click answer citation **[1]**; the linked cell receives a
blue outline inside its green highlight. Compare the three baseline cards.

**Say:** “Every requested fact in this supplied table is supported by the
retained evidence. Each returned value links to its source cell. Full refers to
this evidence scope, not everything in a company's reports.”

## 2. Partial support — Q02

**Click:** Choose **Q02 · Partial**, then **Run**. Read the returned value and
plain-language gap. Follow its citation. Compare extraction-only, binary and
graded in the three columns.

**Say:** “Graded returns the supported subset and names the gap. Binary withholds
an incomplete answer. The frozen extraction-only policy calls an answer full
when it extracts any value; that badge does not establish full coverage. This
is a behavior demonstration, not an accuracy or superiority result.”

## 3. Controlled conflict — Q04

**Click:** Choose **Q04 · Conflict · controlled test case**, read the controlled
case notice, then **Run**. Inspect the conflicting rows and gap explanation.
Any amber baseline citation can be followed back to its cell.
Read the evidence-truncation warning when it appears; no packing settings were
changed to improve this example.

**Say:** “This is a controlled test case with the pilot's pre-existing artificial
alternative value, not a genuine filing disagreement. The unchanged graded
contradiction policy withholds the whole answer and its answer citations. Amber
is a baseline reference, not verified support.”

## 4. Abstention — Q03

**Click:** Choose **Q03 · Abstain**, then **Run**. Inspect the empty answer and
missing-fact explanations. Open **Limitations** before ending.

**Say:** “The supplied evidence scope contains no matching answer values.
Missing means missing from evidence used for this run, not absent from the real
world. The pilot has 18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it. Its labels are provisional,
single-annotator, and independence between questions is not established.”

If samples are unavailable, stop this prepared demonstration and use the setup
guide. Do not substitute evaluation/development questions. The optional paste
tab's synthetic default can illustrate input handling separately; malformed
JSON produces a clear error and header repair is unsupported.
