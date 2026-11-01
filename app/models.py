"""Strict local API transport models, separate from the frozen assessment schema."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RequestedFact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    requirement_id: str = Field(min_length=1, max_length=80)
    metric: str = Field(min_length=1, max_length=200)
    year: int = Field(ge=1000, le=9999)


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    question: str = Field(min_length=1, max_length=4000)
    requested_facts: list[RequestedFact] = Field(min_length=1, max_length=8)
    table: list[list[str]] = Field(min_length=1, max_length=200)
    paragraphs: list[str] = Field(default_factory=list, max_length=100)
    source_reference: str = Field(default="User-supplied table", min_length=1, max_length=400)
    source_unit: str = Field(default="", max_length=200)
    answerer: Literal["lookup", "local_llm"] = "lookup"
    demo_confidence_threshold: float = Field(default=0.5, ge=0, le=1, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_scope(self):
        if not self.question.strip() or any(not f.metric.strip() or not f.requirement_id.strip() for f in self.requested_facts):
            raise ValueError("Question, metric and requirement IDs cannot be blank")
        ids = [f.requirement_id for f in self.requested_facts]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate requirement IDs")
        if sum(len(cell) for row in self.table for cell in row) > 150000:
            raise ValueError("Table is too large for a local request")
        return self
