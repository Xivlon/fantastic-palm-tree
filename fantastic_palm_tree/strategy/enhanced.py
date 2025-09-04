from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from ..config import StrategyConfig
from ..exceptions import PositionExistsError, NoPositionError
from ..indicators.atr import ATRCalculator
from ..logging import get_logger
from ..models.position import TradePosition
from ..results import ExitResult, BarProcessResult
from ..risk.trailing import TrailingStopEngine
from .base import BaseStrategy

logger = get_logger()


class EnhancedStrategy(BaseStrategy):
    """
    Enhanced trading strategy with modular ATR trailing logic.
    """

    def __init__(self, config: StrategyConfig):
        self.config = config
        self.atr_calc = ATRCalculator(period=config.atr_period)
        self.trailing = TrailingStopEngine(config, self.atr_calc)
        self.position: Optional[TradePosition] = None
        self._realized_pnl = 0.0
        self.commission_rate = 0.0
        self.slippage = 0.0

    def set_fees(self, commission_rate: float = 0.0, slippage: float = 0.0) -> None:
        self.commission_rate = commission_rate
        self.slippage = slippage

    def update_atr(self, high: float, low: float, prev_close: float) -> float:
        return self.atr_calc.add_bar(high, low, prev_close)

    def enter_position(self, price: float, size: float, is_long: bool = True) -> bool:
        if self.position is not None:
            raise PositionExistsError("A position already exists; exit before entering a new one.")
        entry_atr = self.atr_calc.get_atr()
        effective_price = price + (self.slippage if is_long else -self.slippage)
        commission = abs(size * effective_price * self.commission_rate)
        self.position = TradePosition(
            entry_price=effective_price,
            size=size,
            entry_atr=entry_atr,
            is_long=is_long,
        )
        self._realized_pnl -= commission  # record commission cost
        logger.debug(
            "Entered position",
            extra={
                "entry_price": effective_price,
                "size": size,
                "is_long": is_long,
                "entry_atr": entry_atr,
                "commission": commission,
            },
        )
        return True

    def _compute_r_multiple(self, position_pnl: float, position: TradePosition) -> float:
        if position.size == 0:
            return 0.0
        risk_per_share = position.entry_atr if position.entry_atr > 0 else 1.0
        per_share = position_pnl / position.size
        return per_share / risk_per_share if risk_per_share > 0 else 0.0

    def exit_position(self, price: float, reason: str = "manual") -> ExitResult:
        if not self.position:
            raise NoPositionError("No position to exit.")
        position = self.position
        effective_price = price + (-self.slippage if position.is_long else self.slippage)
        commission = abs(position.size * effective_price * self.commission_rate)

        if position.is_long:
            position_pnl = position.size * (effective_price - position.entry_price)
        else:
            position_pnl = position.size * (position.entry_price - effective_price)

        r_multiple = self._compute_r_multiple(position_pnl, position)
        self._realized_pnl += position_pnl - commission

        exit_result = ExitResult(
            pnl=position_pnl,
            r_multiple=r_multiple,
            total_pnl=self._realized_pnl,
            commission=commission,
            reason=reason,
        )

        logger.debug("Exited position", extra=asdict(exit_result))
        self.position = None
        return exit_result

    def process_bar(
        self, high: float, low: float, close: float, prev_close: float
    ) -> BarProcessResult:
        atr = self.update_atr(high, low, prev_close)
        exit_res: Optional[ExitResult] = None
        stop_hit = False
        stop_price = None

        if self.position:
            stop_price = self.trailing.update_trailing_stop(self.position, close)
            if self.trailing.stop_hit(self.position, bar_high=high, bar_low=low):
                assert self.position.stop_price is not None
                exit_res = self.exit_position(self.position.stop_price, reason="stop_loss")
                stop_hit = True

        return BarProcessResult(
            atr=atr,
            stop_hit=stop_hit,
            exit_result=exit_res,
            stop_price=stop_price,
        )

    def get_position_info(self) -> Optional[dict]:
        if not self.position:
            return None
        return {
            "entry_price": self.position.entry_price,
            "size": self.position.size,
            "entry_atr": self.position.entry_atr,
            "stop_price": self.position.stop_price,
            "is_long": self.position.is_long,
        }

    def get_realized_pnl(self) -> float:
        return self._realized_pnl
