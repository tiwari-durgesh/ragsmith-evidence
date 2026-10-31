
import json

from ragsmith.sufficiency.results import SufficiencyResult
from ragsmith.sufficiency.question_assessment import assess_question
from ragsmith.sufficiency.reporting import build_assessment_report


def test_report_contains_summary():
    results = [
        SufficiencyResult("req-001", "supported", ["ev-001"]),
        SufficiencyResult("req-002", "unverified"),
    ]

    report = build_assessment_report(assess_question(results))

    assert report["total_requirements"] == 2
    assert report["supported_requirements"] == 1
    assert report["coverage"] == 0.5
    assert report["answerability"] == "partial"


def test_report_preserves_requirement_details():
    result = SufficiencyResult(
        requirement_id="req-001",
        status="contradicted",
        evidence_ids=["ev-001"],
        reason="Conflicting value",
    )

    report = build_assessment_report(assess_question([result]))
    requirement = report["requirements"][0]

    assert requirement["requirement_id"] == "req-001"
    assert requirement["status"] == "contradicted"
    assert requirement["evidence_ids"] == ["ev-001"]
    assert requirement["reason"] == "Conflicting value"


def test_empty_report():
    report = build_assessment_report(assess_question([]))

    assert report["total_requirements"] == 0
    assert report["coverage"] == 0.0
    assert report["answerability"] == "abstain"
    assert report["requirements"] == []


def test_report_is_json_serializable():
    results = [
        SufficiencyResult("req-001", "supported", ["ev-001"]),
    ]

    report = build_assessment_report(assess_question(results))

    encoded = json.dumps(report)
    decoded = json.loads(encoded)

    assert decoded == report


def test_report_copies_evidence_id_lists():
    result = SufficiencyResult(
        requirement_id="req-001",
        status="supported",
        evidence_ids=["ev-001"],
    )

    report = build_assessment_report(assess_question([result]))

    result.evidence_ids.append("ev-002")

    assert report["requirements"][0]["evidence_ids"] == ["ev-001"]
