from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TradePosition:
    entry_price: float
    size: float
    entry_atr: float
    is_long: bool
    timestamp: int = 0
    stop_price: Optional[float] = None

    def unrealized_pnl(self, mark_price: float) -> float:
        if self.size == 0:
            return 0.0
        if self.is_long:
            return self.size * (mark_price - self.entry_price)
        return self.size * (self.entry_price - mark_price)
