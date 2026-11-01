# RAGSmith Evidence — professor briefing

**Local prototype; provisional pilot only; no performance claims.**

The research asks whether evidence-sufficiency decisions can retain supported
parts of an answer while limiting unsupported claims. The intended comparison
holds explicit requirements, retrieved evidence and answer candidates fixed
across response policies. A lack of useful supported-coverage gain, or excessive
unsupported-claim risk, would challenge the empirical advantage. The current
software demonstration does not test or establish historical novelty.

The implemented core discovers literal metric/year/value candidates from
supported table rows and passes them through an unchanged verifier. A graded
policy returns full support, a supported subset, or abstains; detected conflict
withholds the whole answer. Supporting citations link returned values to source
cells. Retrieval is lexical SQLite FTS with bounded whole-unit packing. Dense,
graph and broad semantic retrieval/verification remain beyond the demonstrated
system; it is not the completed proposed hybrid architecture.

A local Streamlit interface now displays six existing pilot examples, source
highlights and numbered citations, plain-language gaps and three frozen pilot
baseline cards. It includes pipeline/research/limitations tabs and a JSON input
page. The model is off. FastAPI shares the same checked outer request/response
contract. A separate import-only runner skeleton exposes retrieval, local-answerer
and candidate/verifier interfaces, with never-abstain and confidence-policy paths.
Its threshold is unset and uncalibrated; no real evaluation or calibration runs.

Software validation reports **720 passing tests**, with one existing dependency
deprecation warning, plus local browser checks. These verify engineering behavior,
not predictive accuracy. The frozen verifier, contradiction policy, schema and
all `src/` bytes are unchanged. Python 3.12.14 is tested; Python 3.11 is unverified.
There are no external inference calls or paid services in this work.

The earlier pilot has **18 independent source facts and 36 derived cases; no
statistical or performance claims are made from it**. Labels remain
**provisional, single-annotator**. Independence is not established. The demo
conflict is an artificial controlled test case, and a visible packing warning
is retained. No system component was tuned to improve the examples. The planned
Option C excerpt study accepts unresolved report overlap: company/hash checks
cannot establish disjointness. Neither independence nor generalization to other
documents, leakage-free evaluation or statistical superiority may be claimed.

Remaining gates are genuine partial/conflict feasibility, authorized source-only
selection, locked labels, development-only confidence calibration, independent
human review, and a frozen descriptive run with failures retained. A second
human must review a 30–50-question subset before paper results; the current
reduced plan requires all 30 evaluation questions. A synthetic reviewer training
kit is ready. It is not completed annotation or agreement evidence. No fresh
evaluation/development questions were selected or inspected during this work.

Next discussion: feasibility and reviewer availability, then the existing
authorization gates. The preregistration, amendments and public manifest have
not been changed. Building work is committed locally and has not been pushed.
