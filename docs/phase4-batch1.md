# Phase 4 Batch 1: application-level assertion assessment

Run from the repository root with the package installed, as described in README.
This Python example uses synthetic evidence supplied by the application:

```python
import json
from pathlib import Path

from ragsmith.evidence.models import Evidence
from ragsmith.qa import QuestionRequest, assess_question_request

request = QuestionRequest.from_payload(
    json.loads(Path("configs/assertion_request.json").read_text(encoding="utf-8"))
)
evidence = Evidence(
    evidence_id="ev-demo",
    document_id="synthetic-report",
    document_version="v1",
    kind="table_row",
    content="Metric: Revenue (million USD); 2025: 145",
    locator="table:1/row:2",
    table_id="table:1",
    row_index=2,
    extraction_method="synthetic",
)
result = assess_question_request(request, [evidence])
print(json.dumps(result, indent=2))
assert result["assessment"]["answerability"] == "full"
```

The envelope has `schema_version`, `mode`, `question_id`, `question`,
`requirements`, and `assessment`. Its mode is `assertion_verification`.
`assessment` has the unchanged Phase 3 schema, including provenance and
metadata-completeness reports. Optional page metadata may be absent; a missing
document identifier or locator remains invalid under the existing evidence model.

Requests must have at least one explicit requirement. Each requirement has an
ID, metric string, four-digit integer year, and nonempty expected-value string.
Unknown payload fields, missing fields, duplicate requirement IDs, and implicit
type conversions are rejected. Duplicate evidence IDs are rejected by the
existing assessment pipeline.

The question text is not parsed or executed. A caller must supply the complete
decomposition; this interface cannot verify whether a requirement was omitted.
Expected values are caller-supplied assertions, not answers discovered by the
system. Gold answers must not be passed here and then used to claim ordinary
question-answering accuracy.

The current verifier accepts only the supported table-row text format. Metric
names are matched ignoring case and surrounding whitespace; no alias or unit
conversion is attempted. `145` and `145.00` compare equal under the existing
numeric rules. Missing support remains `unverified`. Any contradiction causes
question-level abstention, even when other requirements are supported.

The legacy aggregator includes examined evidence IDs even when they do not
support a requirement. This batch preserves that contract. These references
must not be treated as support-only answer citations; response construction
needs to identify supporting evidence explicitly in a later batch.

Run the regression suite in Windows PowerShell with a working project Python:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```
