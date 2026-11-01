"""Shared input checks, response validation and content-free operational logging."""

import logging

from pydantic import ValidationError

from app.contracts import AskRequest, AskResponse
from app.service import answer

LOG = logging.getLogger("ragsmith.transport")


class InputError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def validate_table(payload: AskRequest) -> None:
    table = payload.table
    if not table[0] or len(table[0]) > 30 or any(not row or len(row) != len(table[0]) for row in table):
        LOG.warning("request_rejected code=malformed_table")
        raise InputError("malformed_table", "Table rows must be rectangular, nonempty and at most 30 columns. Header repair is unsupported.")
    if any(len(cell) > 4000 for row in table for cell in row):
        LOG.warning("request_rejected code=oversized_cell")
        raise InputError("oversized_cell", "A table cell exceeds the 4,000-character limit. Header repair is unsupported.")


def checked_answer(payload: AskRequest, runtime=None) -> dict:
    validate_table(payload)
    try:
        raw = answer(payload, runtime)
    except ValueError as exc:
        if "exceed" in str(exc).lower() and "input" in str(exc).lower() and "budget" in str(exc).lower():
            LOG.warning("request_rejected code=input_budget_exceeded budget=3200")
            raise InputError("input_budget_exceeded", "Question and requested facts exceed the 3,200 input-token budget before evidence. Shorten the request; evidence is never clipped or repaired.") from exc
        LOG.warning("request_rejected code=unsupported_input error_type=%s", type(exc).__name__)
        raise
    try:
        result = AskResponse.model_validate(raw)
    except ValidationError as exc:
        LOG.error("response_rejected code=response_contract")
        raise RuntimeError("Pipeline response failed the shared transport contract") from exc
    if result.packing["truncated"]:
        LOG.warning("evidence_truncated input_tokens=%s budget=3200 omitted_units=%s",
                    result.packing["input_tokens"], len(result.packing["omitted_ids"]))
    else:
        LOG.info("request_completed input_tokens=%s budget=3200", result.packing["input_tokens"])
    return result.model_dump(exclude_unset=True)
