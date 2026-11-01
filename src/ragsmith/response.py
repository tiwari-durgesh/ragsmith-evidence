"""Deterministic presentation of trusted lookup-pipeline output.

This renderer checks presentation contracts; verification remains the job of the
existing pipeline. It does not independently authenticate a supplied report or
reverify claims without the original evidence.
"""

from collections.abc import Mapping

from ragsmith.sufficiency.question_assessment import assess_question
from ragsmith.sufficiency.results import SufficiencyResult


def _display(value: str) -> str:
    """Keep source-derived labels and values on a single plain-text line."""
    return " ".join(value.split())


def render_lookup_response(result: Mapping) -> dict:
    """Render supported facts, explicit gaps, or abstention without new claims.

    The input must be trusted output from assess_lookup_question or
    answer_from_database, not an unverified, user-authored report. The renderer
    ignores any factual answers on abstention and never displays discovery
    diagnostics as answers. Assessment records are not mutated.
    """
    if not isinstance(result, Mapping) or result.get("mode") != "value_lookup":
        raise ValueError("response requires a value_lookup result")
    report = result["assessment"]
    requirements = result["requirements"]
    declarations = {item["requirement_id"]: item for item in requirements}
    if len(declarations) != len(requirements):
        raise ValueError("Duplicate requirement declarations")
    statuses = report["requirements"]
    derived = assess_question([SufficiencyResult(**item) for item in statuses])
    decision = report["answerability"]
    if decision != derived.answerability:
        raise ValueError("Answerability conflicts with requirement statuses")
    if set(declarations) != {item["requirement_id"] for item in statuses}:
        raise ValueError("Requirement declarations do not match assessment")
    supported = {
        item["requirement_id"]: item for item in statuses
        if item["status"] == "supported"
    }
    provenance = {
        item["evidence_id"]: item for item in report["evidence_provenance"]
    }
    if len(provenance) != len(report["evidence_provenance"]):
        raise ValueError("Duplicate provenance records")
    citations = []
    citation_numbers = {}
    lines = []
    scope = "retrieved" if "retrieval" in result else "supplied"
    if decision == "abstain":
        lines.append(f"I cannot provide a reliable answer from the {scope} evidence.")
        if not result["config"]["value_lookup_enabled"]:
            lines.append("Value lookup is disabled; the requested facts were not checked.")
    else:
        lines.append(f"Based on the {scope} evidence:")
        answers = {item["requirement_id"]: item for item in result["answers"]}
        if len(answers) != len(result["answers"]) or set(answers) != set(supported):
            raise ValueError("Answers must match supported requirements exactly")
        for requirement in requirements:
            rid = requirement["requirement_id"]
            if rid not in answers:
                continue
            answer = answers[rid]
            if (
                answer["metric"] != requirement["metric"]
                or answer["year"] != requirement["year"]
                or not isinstance(answer["value"], str)
                or not answer["value"].strip()
                or not answer["citations"]
            ):
                raise ValueError("Supported answer needs matching fields and citations")
            labels = []
            for citation in answer["citations"]:
                eid = citation["evidence_id"]
                if (
                    eid not in supported[rid]["evidence_ids"]
                    or citation != provenance.get(eid)
                ):
                    raise ValueError("Answer citation does not match assessment provenance")
                if eid not in citation_numbers:
                    citation_numbers[eid] = len(citations) + 1
                    citations.append({"citation_number": citation_numbers[eid], **citation})
                number = citation_numbers[eid]
                if number not in labels:
                    labels.append(number)
            references = " ".join(f"[{number}]" for number in labels)
            lines.append(
                f"{_display(answer['metric'])} in {answer['year']}: "
                f"{_display(answer['value'])}. {references}"
            )

    unsupported = []
    for status in statuses:
        if status["status"] == "supported":
            continue
        requirement = declarations[status["requirement_id"]]
        label = f"{_display(requirement['metric'])} in {requirement['year']}"
        if status["status"] == "missing":
            explanation = f"{label}: no matching value was found in the {scope} evidence."
        elif status["status"] == "contradicted":
            explanation = f"{label}: conflicting evidence prevents a reliable answer."
        elif not result["config"]["value_lookup_enabled"]:
            explanation = f"{label}: not checked because value lookup is disabled."
        else:
            explanation = (
                f"{label}: could not be verified using the supported evidence formats."
            )
        lines.append(explanation)
        unsupported.append({
            "requirement_id": status["requirement_id"],
            "metric": requirement["metric"],
            "year": requirement["year"],
            "status": status["status"],
            "explanation": explanation,
        })

    retrieval = result.get("retrieval", {})
    warnings = []
    if any(item["truncated"] for item in retrieval.get("queries", [])):
        warnings.append(
            "Retrieval was truncated; additional supporting or conflicting "
            "evidence may have been omitted."
        )
    paths = {}
    for query in retrieval.get("queries", []):
        for hit in query["hits"]:
            paths[hit["evidence_id"]] = hit["source_path"]
    if citations:
        lines.append("Sources:")
        for citation in citations:
            path = paths.get(citation["evidence_id"])
            if path is not None:
                citation["source_path"] = path
            source = _display(path or citation["document_id"])
            locator = _display(citation["locator"])
            page = citation["page_number"]
            page_label = f"; page {page}" if page is not None else ""
            lines.append(
                f"[{citation['citation_number']}] {source}; {locator}{page_label}"
            )
    lines.extend(warnings)
    return {
        "answerability": decision,
        "text": "\n".join(lines),
        "citations": citations,
        "unsupported_requirements": unsupported,
        "warnings": warnings,
    }
