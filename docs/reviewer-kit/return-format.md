# Return format

Copy `practice-return.json` to a private local working location; fill your copy.
Do not commit completed annotations. Return it to the coordinator through the
agreed private channel; this kit sends nothing automatically. Keep the original
independent return for later adjudication. This blank public template contains
no completed labels or answer key.

Fill every blank string. Use an anonymous reviewer ID, elapsed minutes as a
nonnegative number, and preserve packet, case and requirement IDs exactly.
Keep `label_status` as `provisional, single-annotator`. This training return is
not a paper result or a claim of human agreement.

For each requirement:

- `status`: exactly `supported`, `missing`, `contradicted` or `unverified`.
- `raw_values`: strings copied from eligible numeric cells; use `[]` when none
  is accepted. For contradiction list all incompatible values.
- `cells`: objects such as `{"row":2,"column":2}`, one-based including headers.
  Cite relevant ambiguous cells even when `raw_values` is empty; missing has no
  supporting value cell. Explain any distinction in `notes`.
- `unit`: the stated unit, or the literal `unclear` if it cannot be established.
- `notes`: a short source-based reason. Use `none` when there is no further note.
- `absence_scan`: for missing, the keywords, year, row range and paragraphs
  scanned; for other statuses, the literal `not applicable`.

Do not add a system decision, condition/category, another reviewer's label,
confidence score or performance judgment. Do not browse, run the model or compare
answers before locking the independent return. Worked examples can be consulted
as general instructions; they are not a key to the opaque practice IDs.
