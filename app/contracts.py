"""Shared outer UI/API contract; the frozen assessment remains an opaque field."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import AskRequest  # One request schema, re-exported for both callers.

Decision = Literal["full", "partial", "abstain"]


class Citation(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)
    citation_number: int = Field(ge=1)
    evidence_id: str
    document_id: str
    document_version: str
    locator: str


class AnswerValue(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)
    requirement_id: str
    metric: str
    year: int
    value: str
    citation_numbers: list[int]


class PolicyResponse(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)
    variant: str
    decision: Decision
    values: list[AnswerValue]
    citations: list[Citation]
    gaps: list[dict]

    @model_validator(mode="after")
    def check_references(self):
        numbers = [c.citation_number for c in self.citations]
        if len(numbers) != len(set(numbers)):
            raise ValueError("Duplicate citation number")
        if any(n not in numbers for v in self.values for n in v.citation_numbers):
            raise ValueError("Value references an unavailable citation")
        return self


class AskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    question_id: str
    decision: Decision
    values: list[AnswerValue]
    citations: list[Citation]
    gap_explanation: list[dict]
    baseline_family: str
    baselines: list[PolicyResponse]
    assessment: dict
    assessment_scope: str
    lookup_response: dict
    candidate_assessment: dict | None
    retrieval: dict
    packing: dict
    generation: dict
    source: dict
    source_audit: list[dict]
    notices: list[str]

    @model_validator(mode="after")
    def check_answer(self):
        PolicyResponse(variant="graded_sufficiency", decision=self.decision,
                       values=self.values, citations=self.citations, gaps=self.gap_explanation)
        if self.decision == "abstain" and (self.values or self.citations):
            raise ValueError("A graded abstention cannot expose answer values/citations")
        count, budget = self.packing.get("input_tokens"), self.packing.get("input_budget")
        if type(count) is not int or type(budget) is not int or not 0 <= count <= budget <= 3200:
            raise ValueError("Invalid bounded input-token audit")
        return self
