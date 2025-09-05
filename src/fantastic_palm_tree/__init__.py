"""Public package surface (initial).
Re-export only the stable protocol / dataclass entities.
"""

from .engine.base import Engine
from .metrics.base import EquityPoint, Metric, MetricsPipeline
from .orders import Order, OrderSide, OrderType
from .position import Position
from .results import TradeResult
from .strategy.base import Bar, Strategy

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
