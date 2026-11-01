# Verified value lookup

The user authorized Option A after confirming the research-proposal DOCX as the
intended proposal. This implements unknown-value lookup over supplied evidence,
not automatic natural-language decomposition or the full hybrid retrieval stack.
The Batch 1 assertion API remains available and unchanged.

## Run the example

Run this Python example from the repository root with the package installed:

```python
import json
from pathlib import Path

from ragsmith.evidence.models import Evidence
from ragsmith.lookup_config import LookupConfig
from ragsmith.lookup_pipeline import assess_lookup_question
from ragsmith.value_lookup import LookupQuestion

request = LookupQuestion.from_payload(json.loads(
    Path("configs/lookup_question.json").read_text(encoding="utf-8")
))
evidence = [
    Evidence("ev-revenue", "synthetic-report", "v1", "table_row",
             "Metric: Revenue (million USD); 2025: 145", "table:1/row:2"),
    Evidence("ev-profit", "synthetic-report", "v1", "table_row",
             "Metric: Profit (million USD); 2025: 30", "table:1/row:3"),
]
for config_file in ("lookup-enabled.json", "lookup-disabled.json"):
    config = LookupConfig.from_file(Path("configs") / config_file)
    result = assess_lookup_question(request, evidence, config)
    print(json.dumps(result, indent=2))
    if config.value_lookup_enabled:
        assert result["assessment"]["answerability"] == "partial"
        assert len(result["answers"]) == 2
        assert result["assessment"]["requirements"][2]["status"] == "missing"
    else:
        assert result["assessment"]["answerability"] == "abstain"
        assert result["answers"] == []
```

The values in this synthetic example are evidence content, not expected answers
in the request. Question text is retained for display; an application must supply
the metric/year requirements. Request fields containing `expected_value`,
`gold_answer`, or other unknown keys are rejected.

## Discovery and verification

`value_lookup.py` extracts candidates from the same narrow table-row format
accepted by the existing verifier. It records the evidence IDs behind each raw
value, retains conflicting values, and records unsupported formats separately.
It does not judge extracted values as true.

`lookup_pipeline.py` sends every discovered candidate to `verify_metric_value`
against every scoped evidence item. The existing judgment aggregator and
question-level decision policy then determine support and abstention. Numerically
equivalent candidates such as `145` and `145.00` are accepted by the unchanged
numeric rules. Distinct values that contradict one another cause abstention;
the system does not choose a preferred source or majority value. Nonfinite
numeric values do not bypass the verifier's existing rejection rules.

The `assessment` object has exactly the existing Phase 3 fields, provenance,
and metadata-quality reports. Additional application fields outside it contain
the effective config, untrusted discovery diagnostics, and structured `answers`.
Discovery candidates must not be treated as verified output. `answers` contains
only supported facts and is empty whenever the question-level decision abstains.

## Status meanings

In this lookup path:

- `supported`: at least one candidate has verifier support without contradiction.
- `contradicted`: candidate verification encountered conflicting evidence; the
  unchanged policy requires question-level abstention.
- `missing`: no candidate was found, and all supplied evidence in scope was
  interpretable by the supported grammar, or the scoped set was empty.
- `unverified`: no candidate could be established because evidence includes an
  unsupported format, or because discovery was disabled.

Unsupported formats conservatively prevent a missing judgment when there are no
candidates. If a candidate is supported, the legacy aggregator's support policy
still applies; unparsed evidence does not by itself introduce a contradiction.
`missing` concerns the evidence supplied to this call, not the entire corpus.
The legacy assertion pipeline retains its existing behavior, including
`unverified` for no evidence, to preserve compatibility.

## Supporting citations and scope

`supporting_citations.py` rechecks the chosen assertion with the existing
verifier, selects only `supports` judgments, and preserves their document,
version, locator, and optional page/table metadata. A conflicting claim receives
no supporting answer citations. The lookup orchestration additionally suppresses
all answer claims when any requirement causes question-level abstention.
Irrelevant, unsupported, and contradictory examined evidence remains available
in the unchanged assessment audit references; it is not cited as answer support.

Each requirement may specify `document_ids` as a JSON list. An omitted or empty
list means all supplied evidence. Callers must scope evidence to the intended
company/entity and document set; the pipeline does not infer identity, choose
document versions, reconcile units, or resolve conflicting authoritative sources.
It cannot verify whether the caller omitted a requirement from the question.
Provenance consistency and metadata completeness do not prove source authenticity.

## Configuration and evaluation limits

The only config key is the strict boolean `value_lookup_enabled`. The default
is false. Load the enabled or disabled JSON config to run identical requests
and evidence with and without discovery. Disabled lookup skips both discovery
and candidate verification, reports `unverified`, and returns no factual answers.
It never fills in gold values or falls back to a model.

This toggle supports a discovery-function ablation, not a measurement isolating
the sufficiency layer. Testing that layer's research contribution requires
holding retrieval, value extraction, and generation constant while varying
sufficiency behavior in a separately agreed experimental baseline. No accuracy,
hallucination-reduction, or novelty claims follow from these software tests.

Run the regression suite with a working project Python:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

Python 3.11 remains unverified in this continuation because its recorded
installation is unavailable. Tests ran under bundled Python 3.12.14 using
existing environment packages; the original `.venv` was not repaired.
