"""
Public interfaces for the fantastic-palm-tree trading system.

This module defines minimal public interfaces using Protocols and ABCs 
that can be implemented by various components of the trading system.
These interfaces provide a contract for extension while maintaining
flexibility in implementation.
"""

from .strategy import StrategyProtocol
from .engine import EngineProtocol
from .order import OrderProtocol
from .position import PositionProtocol
from .trade_result import TradeResultProtocol
from .metrics import MetricsAggregatorProtocol

__all__ = [
    "StrategyProtocol",
    "EngineProtocol", 
    "OrderProtocol",
    "PositionProtocol",
    "TradeResultProtocol",
    "MetricsAggregatorProtocol",
]