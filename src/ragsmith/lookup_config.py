"""Strict JSON configuration for reproducible lookup ablations."""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LookupConfig:
    """Discovery is opt-in; disabling it never substitutes an expected answer."""

    value_lookup_enabled: bool = False

    def __post_init__(self) -> None:
        if type(self.value_lookup_enabled) is not bool:
            raise ValueError("value_lookup_enabled must be a boolean")

    @classmethod
    def from_file(cls, path: Path) -> "LookupConfig":
        """Load one explicit switch; reject misspellings and truthy strings."""
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping) or set(payload) != {"value_lookup_enabled"}:
            raise ValueError("config must contain value_lookup_enabled only")
        return cls(value_lookup_enabled=payload["value_lookup_enabled"])
