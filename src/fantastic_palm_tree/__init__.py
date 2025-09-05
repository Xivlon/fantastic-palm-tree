"""Public package surface (initial).
Re-export only the stable protocol / dataclass entities.
"""
from .strategy.base import Strategy, Bar
from .engine.base import Engine
from .orders import Order, OrderSide, OrderType
from .position import Position
from .results import TradeResult
from .metrics.base import MetricsPipeline, Metric, EquityPoint

__all__ = [
    "Strategy",
    "Bar",
    "Engine",
    "Order",
    "OrderSide",
    "OrderType",
    "Position",
    "TradeResult",
    "MetricsPipeline",
    "Metric",
    "EquityPoint",
]