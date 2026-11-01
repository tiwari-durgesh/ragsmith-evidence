# Five worked examples — synthetic training keys

All entities and amounts here are invented. These are training examples with
answers, separate from the blinded practice form. They are not pilot annotations
or research observations. Rows/columns below include the header and row-label
column when counting coordinates. Assume one company and USD millions unless
explicitly stated otherwise. Judge each requested requirement, not a system.

## 1. Direct support

| Metric | 2025 |
|---|---|
| Revenue | 12 |
| Cash | 3 |

Request: Revenue in 2025. **Supported**, raw value `12`, cell row 2 / column 2,
unit USD millions. Cash's cell is not a supporting citation for Revenue.

## 2. Only part of a request is supported

| Metric | 2025 |
|---|---|
| Revenue | 12 |

Request: Revenue and Cash in 2025. Revenue is **supported**, `12` at (2,2).
Cash is **missing** after scanning all rows (1–2), the header year and no supplied
paragraphs for `Cash`. Do not invent Cash from Revenue. A question-level partial
answer is possible, but source labels are recorded per requirement.

## 3. Absence in the supplied scope

| Metric | 2025 |
|---|---|
| Employees | 40 |

Request: Cash in 2025. **Missing**. Scan terms: `Cash`, `2025`; scan coverage:
all rows 1–2 and no paragraphs. There is no relevant Cash row. This does not say
that the company had no cash. `40` is a headcount, not a cash amount.

## 4. Conflicting eligible values

| Metric | 2025 |
|---|---|
| Cash | 3 |
| Cash | 8 |

Request: Cash in 2025. **Contradicted**: same metric/year/unit/scope with `3`
at (2,2) and `8` at (3,2), no explanation or version preference. Record both
values/cells. Do not average or choose the first. If rows instead referred to
different divisions, do not call them a same-scope contradiction.

## 5. Relevant but not verifiable

| Metric | 2025 |
|---|---|
| Cash | — |

Request: Cash in 2025. **Unverified**, raw ambiguous cell `—` at (2,2).
There is a relevant row but no unambiguous numeric value. Do not turn the dash
into zero or mark the row absent. Record no accepted numeric value, cite the
relevant cell and explain the ambiguity in notes. Similarly, an unclear multirow
header is unverified; do not repair it to make an answer possible.
