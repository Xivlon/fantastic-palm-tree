from typing import Protocol, runtime_checkable, Any, Dict, Optional, Sequence
from abc import ABC, abstractmethod

class Strategy(Protocol):
    """
    Interface for trading strategies. Implementations must define how to react to new data and manage orders.
    Extension: Add custom event hooks or parameterization methods as needed.
    Constraint: Must be stateless between on_data calls except via set_params or set_portfolio.
    """
    name: str
    def set_portfolio(self, portfolio: Any) -> None: ...
    def set_data_handler(self, data_handler: Any) -> None: ...
    def set_params(self, **params: Any) -> None: ...
    def on_data(self, timestamp: str, data: Dict[str, Any]) -> None: ...
    def on_start(self) -> None: ...
    def on_finish(self) -> None: ...
    def buy(self, symbol: str, quantity: int, price: Optional[float] = None) -> None: ...
    def sell(self, symbol: str, quantity: int, price: Optional[float] = None) -> None: ...

class Engine(Protocol):
    """
    Interface for a backtesting or live trading engine.
    Extension: Add hooks for event listeners or custom kill switches.
    Constraint: Must provide a run method and support kill switch triggers.
    """
    initial_cash: float
    kill_switch_active: bool
    def add_kill_switch_trigger(self, trigger_func: Any) -> None: ...
    def check_kill_switch(self, portfolio: Any, current_prices: Dict[str, float]) -> bool: ...
    def run(self, strategy: Strategy, data: Any, verbose: bool = False) -> Any: ...

class Order(Protocol):
    """
    Interface for a trading order.
    Extension: Add more order types or status fields as needed.
    Constraint: Must support fill, cancel, and reject operations.
    """
    symbol: str
    quantity: int
    order_type: Any
    side: str
    price: Optional[float]
    stop_price: Optional[float]
    timestamp: Optional[Any]
    status: Any
    fill_price: Optional[float]
    fill_timestamp: Optional[Any]
    order_id: Optional[str]
    def fill(self, price: float, timestamp: Optional[Any] = None) -> None: ...
    def cancel(self) -> None: ...
    def reject(self) -> None: ...

class Position(Protocol):
    """
    Interface for a trade position.
    Extension: Add more analytics or state fields as needed.
    Constraint: Must provide unrealized PnL calculation.
    """
    entry_price: float
    size: float
    entry_atr: float
    is_long: bool
    timestamp: int
    stop_price: Optional[float]
    def unrealized_pnl(self, mark_price: float) -> float: ...

class TradeResult(Protocol):
    """
    Interface for a trade or exit result.
    Extension: Add more result fields as needed.
    Constraint: Must provide at least PnL and reason for exit.
    """
    pnl: float
    r_multiple: float
    total_pnl: float
    commission: float
    reason: str

class MetricsAggregator(Protocol):
    """
    Interface for aggregating and reporting metrics from backtest results.
    Extension: Add more reporting or export methods as needed.
    Constraint: Must provide a calculate method returning metrics.
    """
    def calculate(self, results: Any, benchmark: Optional[Any] = None, risk_free_rate: float = 0.02) -> Any: ...
