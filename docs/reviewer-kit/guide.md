# Independent source review — one-page guide

**Training material. Synthetic examples only. No research questions or labels.**
This packet is for an engineering student; finance expertise is not assumed.
Read this page and the glossary, then the five worked examples. Complete the
two-case practice packet without opening another person's answers or running the
system. Target 20–30 minutes for training/practice, not a research time estimate.

For each requested metric and year:

1. Identify the table's units, year column and exact row label. Use only the
   supplied snapshot, not web searches or remembered financial facts. Do not
   assume different names or business segments mean the same thing.
2. Record every directly stated eligible value and its cell(s). Cell coordinates
   are **one-based; row 1 is the header, column 1 the row-label column**. Preserve
   the raw printed value, including parentheses, commas, percent signs and units.
   Do not calculate growth, sum rows, convert units or repair headers.
3. Assign a requirement status: **supported** (one unambiguous value), **missing**
   (no relevant value after the fixed scan), **contradicted** (incompatible values
   for the same metric/year/unit/scope, with no source explanation), or
   **unverified** (relevant content exists but cannot be bound reliably, such as
   ambiguous headers, a dash or unclear unit/scope). A blank/dash is not zero.
4. For missing, first scan all row labels and paragraph text for the exact metric
   and its case-insensitive word tokens, then scan all table cells for the year
   and relevant row labels. Record the searched terms and the rows/paragraphs
   scanned. If a plausible related row/header remains ambiguous, use unverified
   with a note, not missing. This is absence in the snapshot, not the real world.
5. Copy your decisions to `practice-return.json`. Add a short source-based reason
   and your elapsed minutes. Mark uncertainty explicitly in notes; do not guess
   to agree with a hypothetical system. Keep your original return unchanged when
   submitting; discuss disagreements only after independent returns are locked.

The practice packet deliberately has no condition/category fields, expected
answers, other annotator labels, system outputs, confidence or performance scores.
Worked examples are separately marked training keys. This packet does not expose
any real pilot labels. For a future research packet, the coordinator must provide
only authorized source snapshots, opaque IDs and identical explicit requirements,
with the same fields and no private metadata.

No paper results follow from practice. Primary pilot labels remain **provisional,
single-annotator**. Independent human review is required before paper results;
under the current 30-question evaluation plan that means all 30 questions (within
the previously required 30–50-question independent subset). No future data is
selected or exported by this kit.
