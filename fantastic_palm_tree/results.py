from __future__ import annotations

from dataclasses import dataclass


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
    exit_result: ExitResult | None
    stop_price: float | None = None
