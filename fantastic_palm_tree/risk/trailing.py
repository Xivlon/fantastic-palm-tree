from __future__ import annotations

from ..config import StrategyConfig
from ..indicators.atr import ATRCalculator
from ..models.position import TradePosition


class TrailingStopEngine:
    """
    Encapsulates trailing stop distance logic.
    Future: plug in percent trailing, volatility contraction, stepped trails, etc.
    """

    def __init__(self, config: StrategyConfig, atr_calc: ATRCalculator):
        self.config = config
        self.atr_calc = atr_calc

    def compute_distance(self, position: TradePosition | None) -> float:
        if not position:
            return 0.0
        trailing_cfg = self.config.trailing
        if not trailing_cfg.get("enabled", True):
            return 0.0
        if trailing_cfg["type"] != "atr":
            return 0.0
        if trailing_cfg["use_dynamic_atr"]:
            min_samples = trailing_cfg["dynamic_atr_min_samples"]
            if self.atr_calc.has_enough_samples(min_samples):
                return self.atr_calc.get_atr()
            return position.entry_atr
        return position.entry_atr

    def update_trailing_stop(
        self, position: TradePosition, current_price: float
    ) -> float | None:
        distance = self.compute_distance(position)
        if distance <= 0:
            return None
        if position.is_long:
            new_stop = current_price - distance
            if position.stop_price is None or new_stop > position.stop_price:
                position.stop_price = new_stop
        else:
            new_stop = current_price + distance
            if position.stop_price is None or new_stop < position.stop_price:
                position.stop_price = new_stop
        return position.stop_price

    @staticmethod
    def stop_hit(position: TradePosition, bar_high: float, bar_low: float) -> bool:
        if position.stop_price is None:
            return False
        if position.is_long:
            return bar_low <= position.stop_price
        return bar_high >= position.stop_price
