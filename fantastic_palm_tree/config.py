from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .exceptions import InvalidConfigError

DEFAULT_TRAILING = {
    "enabled": True,
    "type": "atr",  # future: 'percent', 'vol_contraction', etc.
    "use_dynamic_atr": False,
    "dynamic_atr_min_samples": 1,
}


@dataclass
class StrategyConfig:
    exits: dict[str, Any] = field(default_factory=dict)
    atr_period: int = 14

    def __post_init__(self) -> None:
        trailing = self.exits.setdefault("trailing", {})
        for k, v in DEFAULT_TRAILING.items():
            trailing.setdefault(k, v)
        self._validate()

    def _validate(self) -> None:
        trailing = self.exits["trailing"]
        if trailing["type"] not in {"atr"}:
            raise InvalidConfigError(f"Unsupported trailing.type={trailing['type']}")
        min_samples = trailing["dynamic_atr_min_samples"]
        if not isinstance(min_samples, int) or min_samples < 1:
            raise InvalidConfigError("dynamic_atr_min_samples must be positive int")

    @property
    def trailing(self) -> dict[str, Any]:
        return self.exits["trailing"]
