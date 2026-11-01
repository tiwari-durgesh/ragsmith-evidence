"""Controlled family construction tested entirely on original synthetic tables."""

import pytest

from ragsmith.evaluation.cell_bindings import canonicalize_decisions, decision_templates
from ragsmith.evaluation.harness import predict
from ragsmith.evaluation.lineage import SourceManifest
from ragsmith.evaluation.pilot_families import build_family_drafts, family_templates, group_contexts
from ragsmith.evaluation.records import FrozenEvidenceRecord
from ragsmith.evaluation.tatqa_adapter import REVISION, prepare_screening
from ragsmith.value_lookup import LookupQuestion


@pytest.fixture
def bundle():
    contexts = []
    for i in range(3):
        uid = f"ctx-{i}"
        contexts.append({"table": {"uid": uid, "table": [["USD million", "2025"],
                         ["Revenue", str(145+i)], ["Profit", "30"]]}, "paragraphs": [],
                         "questions": [{"uid": uid + f"-q{j}", "question": f"{metric} in 2025?",
                                        "answer_type": "span", "answer_from": "table", "answer": ["GOLD-SENTINEL"],
                                        "scale": "million", "req_comparison": False}
                                       for j, metric in enumerate(("Revenue", "Profit"))]})
    screen = prepare_screening(contexts, {"revision": REVISION, "split": "train", "sha256": "a"*64,
                                         "url": "fixture://synthetic"})
    screen["sampling_manifest"].update(target_families=3, target_development_families=1)
    bindings = decision_templates(screen)
    for row in bindings:
        uid, index = row["question_id"].rsplit("-q", 1)
        r = int(index)+1
        row.update(decision="accept", reviewer_id="synthetic-author", notes="Explicit synthetic source cells.",
                   binding={"metric_cell_locator": f"table:{uid}/row:{r}/column:0",
                            "year_cell_locator": f"table:{uid}/row:0/column:1",
                            "unit_cell_locator": f"table:{uid}/row:0/column:0",
                            "value_cell_locator": f"table:{uid}/row:{r}/column:1"})
    canonical = canonicalize_decisions(screen, bindings)
    templates = family_templates(screen)
    for row in templates["identities"]:
        row.update(status="declared", report_group_id=row["context_id"], organization="Synthetic Co",
                   period="2025", source_reference="fixture://report", reviewer_id="synthetic-author",
                   notes="Original synthetic report identity.")
    for row in templates["families"]:
        uid = row["context_id"]
        row.update(status="ready", question_ids=[uid+"-q0", uid+"-q1"], conflict_value="999",
                   reviewer_id="synthetic-author", notes="Two distinct synthetic facts.")
    return screen, canonical, templates["identities"], templates["families"]


def test_four_conditions_reach_unchanged_verifier(bundle):
    result = build_family_drafts(*bundle)
    assert result["summary"]["draft_families"] == 3
    assert result["summary"]["draft_cases"] == 12
    assert result["summary"]["gold_generated"] is False
    assert result["summary"]["target_shortfall"] == 0
    for raw, frozen in zip(result["inputs"], result["evidence"]):
        condition = raw["question_id"].rsplit("/", 1)[-1]
        response = predict(LookupQuestion.from_payload(raw), list(FrozenEvidenceRecord.from_payload(frozen).evidence))
        graded = next(row for row in response if row["variant"] == "graded_sufficiency")
        assert graded["answerability"] == {"full":"full", "partial":"partial", "missing":"abstain", "conflict":"abstain"}[condition]
    for start in range(0, 12, 4):
        cases = result["inputs"][start:start+4]
        assert all(row["question"] == cases[0]["question"] and row["requirements"] == cases[0]["requirements"] for row in cases)
    manifest = SourceManifest.from_payload(result["lineage"])
    assert any(source.transformation == "synthetic_conflict" for source in manifest.sources)
    conflicts = [row for row in result["changes"] if row["condition"] == "conflict"]
    assert all(row["changed_fields"][0]["before"] != row["changed_fields"][0]["after"] for row in conflicts)


def test_all_pending_drafts_create_no_pilot(bundle):
    screen, canonical, _, _ = bundle
    template = family_templates(screen)
    result = build_family_drafts(screen, canonical, template["identities"], template["families"])
    assert not result["inputs"]
    assert result["summary"]["draft_families"] == 0
    assert result["summary"]["target_shortfall"] == 3


def test_same_report_group_never_split(bundle):
    screen, canonical, identities, families = bundle
    for row in identities:
        row["report_group_id"] = "same-report-and-versions"
    result = build_family_drafts(screen, canonical, identities, families)
    assert result["summary"]["selected_report_clusters"] == 1
    assert result["summary"]["development_families"] == 3
    assert result["summary"]["held_out_families"] == 0
    assert len({row["partition"] for row in result["families"]}) == 1


def test_report_and_duplicate_links_merge_transitively(bundle):
    screen, _, identities, _ = bundle
    rows = screen["sampling_manifest"]["families"]
    by_uid = {row["context_id"]: row for row in rows}
    by_uid["ctx-0"]["duplicate_table_group"] = by_uid["ctx-1"]["duplicate_table_group"]
    for row in identities:
        if row["context_id"] in {"ctx-1", "ctx-2"}:
            row["report_group_id"] = "shared-report"
    _, groups = group_contexts(screen, identities)
    assert len(groups) == 1
    assert next(iter(groups.values()))["context_ids"] == ["ctx-0", "ctx-1", "ctx-2"]


def test_unresolved_identity_blocks_connected_group(bundle):
    screen, canonical, identities, families = bundle
    for row in identities:
        row["report_group_id"] = "same-report"
    missing_uid = identities.pop()["context_id"]
    candidates = screen["sampling_manifest"]["families"]
    duplicate_group = candidates[0]["duplicate_table_group"]
    for row in candidates:
        row["duplicate_table_group"] = duplicate_group
    result = build_family_drafts(screen, canonical, identities, families)
    assert not result["inputs"]
    assert any(missing_uid in group["unresolved_context_ids"] for group in result["groups"].values())


@pytest.mark.parametrize("mutation", [{"source_content_sha256": "b"*64}, {"reviewer_id": ""},
                                     {"source_reference": ""}, {"annotation_status":"reviewed"}])
def test_invalid_identity_rejected(bundle, mutation):
    screen, canonical, identities, families = bundle
    identities[0].update(mutation)
    with pytest.raises(ValueError):
        build_family_drafts(screen, canonical, identities, families)


@pytest.mark.parametrize("value", ["999; other", "NaN", "Infinity", "145.00"])
def test_invalid_or_equivalent_conflict_rejected(bundle, value):
    screen, canonical, identities, families = bundle
    row = next(row for row in families if row["context_id"] == "ctx-0")
    row["conflict_value"] = value
    with pytest.raises(ValueError):
        build_family_drafts(screen, canonical, identities, families)


def test_duplicate_family_question_rejected(bundle):
    screen, canonical, identities, families = bundle
    families[0]["question_ids"] *= 2
    with pytest.raises(ValueError):
        build_family_drafts(screen, canonical, identities, families)


def test_deterministic_declaration_order(bundle):
    screen, canonical, identities, families = bundle
    first = build_family_drafts(*bundle)
    second = build_family_drafts(screen, canonical, list(reversed(identities)), list(reversed(families)))
    assert first == second


def test_no_upstream_answer_or_gold_in_family_requests(bundle):
    import json
    result = build_family_drafts(*bundle)
    assert "GOLD-SENTINEL" not in json.dumps(result)
    assert "expected_value" not in json.dumps(result["inputs"])
