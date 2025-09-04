from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExitResult:
    pnl: float
    r_multiple: float
    total_pnl: float
    commission: float
    reason: str


@dataclass
class BarProcessResult:
    atr: float
    stop_hit: bool
    exit_result: Optional[ExitResult]
    stop_price: Optional[float] = None
