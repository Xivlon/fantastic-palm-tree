"""Metric processors for the MetricsPipeline."""

from .base import MetricProcessor
from .equity import EquityCurveProcessor
from .drawdown import DrawdownProcessor
from .trades import TradeListProcessor

__all__ = [
    'MetricProcessor',
    'EquityCurveProcessor',
    'DrawdownProcessor',
    'TradeListProcessor'
]