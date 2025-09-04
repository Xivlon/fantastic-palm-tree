from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..models.position import TradePosition
from ..results import BarProcessResult, ExitResult


class BaseStrategy(ABC):
    position: Optional[TradePosition]

    @abstractmethod
    def enter_position(self, price: float, size: float, is_long: bool = True) -> bool: ...

    @abstractmethod
    def exit_position(self, price: float, reason: str = "manual") -> ExitResult: ...

    @abstractmethod
    def process_bar(
        self, high: float, low: float, close: float, prev_close: float
    ) -> BarProcessResult: ...
