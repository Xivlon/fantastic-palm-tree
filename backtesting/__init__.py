"""
Fantastic Palm Tree - Advanced Backtesting Framework

A comprehensive backtesting framework with advanced metrics, parameter sweeping,
kill-switch mechanisms, and Schwab broker integration.
"""

from .brokers import BaseBroker, SchwabBroker
from .core import BacktestEngine, DataHandler, Portfolio, Strategy
from .killswitch import KillSwitchManager, create_default_kill_switches
from .metrics import MetricsCalculator, PerformanceMetrics
from .sweep import GridSearchOptimizer, ParameterOptimizer, ParameterSpace

__version__ = "0.1.0"
__author__ = "Trading Team"

__all__ = [
    # Core components
    "BacktestEngine",
    "Strategy",
    "DataHandler",
    "Portfolio",
    # Metrics
    "MetricsCalculator",
    "PerformanceMetrics",
    # Parameter optimization
    "ParameterOptimizer",
    "GridSearchOptimizer",
    "ParameterSpace",
    # Risk management
    "KillSwitchManager",
    "create_default_kill_switches",
    # Broker integration
    "SchwabBroker",
    "BaseBroker",
]
