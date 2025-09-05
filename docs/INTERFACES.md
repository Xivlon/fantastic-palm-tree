# Trading System Interfaces

This document describes the minimal public interfaces for the fantastic-palm-tree trading system. These interfaces define contracts for extension while maintaining implementation flexibility.

## Overview

The interfaces are designed using Python's Protocol and ABC (Abstract Base Class) mechanisms:

- **Protocols**: Use duck typing for maximum flexibility where exact type isn't crucial
- **ABCs**: Use inheritance for enforcement where we need guaranteed implementation

## Available Interfaces

### 1. StrategyProtocol

Defines the minimal interface for trading strategies.

```python
from interfaces import StrategyProtocol

class MyStrategy:
    name: str = "MyStrategy"
    
    def on_data(self, timestamp: str, data: Dict[str, Any]) -> None:
        # Process market data and generate signals
        pass
    
    def on_start(self) -> None:
        # Initialize strategy
        pass
    
    def on_finish(self) -> None:
        # Cleanup strategy
        pass
    
    def set_params(self, **params: Any) -> None:
        # Configure parameters
        pass
```

**Extension Guidelines:**
- Implement signal generation in `on_data`
- Use `on_start` for strategy initialization
- Use `on_finish` for cleanup and finalization
- Keep strategy state minimal and well-defined

**Constraints:**
- `on_data` must be thread-safe if used in multi-threaded environments
- Strategy should not directly access market data outside of provided callbacks
- All parameters should be configurable via `set_params`

### 2. EngineProtocol

Defines the minimal interface for trading engines.

```python
from interfaces import EngineProtocol

class MyEngine:
    def run(self, strategy: Any, **kwargs: Any) -> Any:
        # Execute strategy against market data
        pass
    
    def add_kill_switch(self, trigger: Any) -> None:
        # Add risk management trigger
        pass
```

**Extension Guidelines:**
- Implement data feeding and order execution in `run`
- Use dependency injection for strategy, data sources, and brokers
- Support configurable execution parameters
- Provide progress reporting for long-running operations

**Constraints:**
- Engine must be thread-safe for concurrent strategy execution
- Must handle strategy errors gracefully without crashing
- Should provide consistent behavior across different data sources
- Must support clean shutdown and resource cleanup

### 3. OrderProtocol

Defines the minimal interface for trading orders.

```python
from interfaces import OrderProtocol, OrderSide, OrderType

class MyOrder:
    symbol: str = "AAPL"
    quantity: float = 100.0
    side: OrderSide = OrderSide.BUY
    order_type: OrderType = OrderType.MARKET
    # ... other required fields
    
    def fill(self, price: float, timestamp: Optional[datetime] = None) -> None:
        # Mark order as filled
        pass
    
    def cancel(self) -> None:
        # Cancel the order
        pass
    
    def reject(self, reason: Optional[str] = None) -> None:
        # Reject the order
        pass
```

**Extension Guidelines:**
- Always include symbol, quantity, side, and order_type
- Use standard enums for side, type, and status
- Implement proper state transitions (pending → filled/canceled/rejected)
- Track timing information for analysis

**Constraints:**
- Order state must be immutable once filled
- Price and stop_price must be positive numbers when set
- Quantity must be positive
- State transitions must follow valid order lifecycle

### 4. PositionProtocol

Defines the minimal interface for position tracking.

```python
from interfaces import PositionProtocol

class MyPosition:
    symbol: str = "AAPL"
    size: float = 100.0  # positive=long, negative=short
    entry_price: float = 150.0
    
    def unrealized_pnl(self, current_price: float) -> float:
        # Calculate unrealized P&L
        pass
    
    def update_position(self, quantity: float, price: float) -> None:
        # Update position with new trade
        pass
    
    def close_position(self, price: float) -> float:
        # Close position and return realized P&L
        pass
```

**Extension Guidelines:**
- Track entry price, size, and direction consistently
- Calculate unrealized P&L based on current market price
- Support partial position closures
- Maintain position history for analysis

**Constraints:**
- Position size can be positive (long) or negative (short)
- Entry price must be positive
- P&L calculations must be accurate for both long and short positions
- Position must track total cost basis correctly

### 5. TradeResultProtocol

Defines the minimal interface for trade results.

```python
from interfaces import TradeResultProtocol

class MyTradeResult:
    symbol: str = "AAPL"
    entry_price: float = 150.0
    exit_price: Optional[float] = None
    quantity: float = 100.0
    is_long: bool = True
    entry_time: datetime
    exit_time: Optional[datetime] = None
    
    def gross_pnl(self) -> float:
        # Calculate gross P&L before costs
        pass
    
    def net_pnl(self) -> float:
        # Calculate net P&L after costs
        pass
    
    def r_multiple(self, risk_amount: float) -> float:
        # Calculate risk-adjusted return
        pass
    
    def duration(self) -> Optional[float]:
        # Calculate trade duration in seconds
        pass
```

**Extension Guidelines:**
- Capture all essential trade details for analysis
- Calculate risk-adjusted returns (R-multiples)
- Track both gross and net P&L (including costs)
- Support both completed and partial trades

**Constraints:**
- Entry and exit prices must be positive when set
- Quantities must be positive
- P&L calculations must be consistent with position direction
- Risk metrics should be meaningful and comparable

### 6. MetricsAggregatorProtocol

Defines the minimal interface for metrics aggregation.

```python
from interfaces import MetricsAggregatorProtocol

class MyMetricsAggregator:
    def add_trade_result(self, trade_result: Any) -> None:
        # Add completed trade to aggregator
        pass
    
    def add_equity_point(self, timestamp: str, equity_value: float) -> None:
        # Add equity curve data point
        pass
    
    def calculate_metrics(self, benchmark: Optional[Any] = None) -> Dict[str, Any]:
        # Calculate comprehensive performance metrics
        pass
    
    def get_equity_curve(self) -> List[Dict[str, Any]]:
        # Get equity curve as time series
        pass
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        # Get trade history as structured data
        pass
    
    def reset(self) -> None:
        # Reset aggregator to initial state
        pass
```

**Extension Guidelines:**
- Support incremental metric updates as trades complete
- Calculate both return-based and risk-adjusted metrics
- Provide metrics at multiple time scales (daily, monthly, total)
- Support benchmark comparison and relative metrics

**Constraints:**
- Metrics should be calculated consistently across strategies
- Must handle edge cases (no trades, all losing trades, etc.)
- Should provide meaningful defaults for missing data
- Calculations must be mathematically correct and industry-standard

## Usage Examples

### Protocol vs ABC

Choose based on your needs:

```python
# Use Protocol for duck typing flexibility
def process_strategy(strategy: StrategyProtocol):
    # Any object with the right methods works
    strategy.on_start()

# Use ABC for inheritance enforcement
class MyStrategy(StrategyABC):
    # Must implement abstract methods
    def on_data(self, timestamp: str, data: Dict[str, Any]) -> None:
        pass
```

### Interface Compatibility

The interfaces are designed to work with existing code:

```python
# Existing code can be checked for compatibility
from backtesting.core.strategy import Strategy
from interfaces import StrategyProtocol

# Check if existing strategy follows protocol
if isinstance(my_existing_strategy, StrategyProtocol):
    print("Compatible with StrategyProtocol")
```

## Best Practices

1. **Use Protocols for flexibility**: When you need duck typing and don't care about exact implementation
2. **Use ABCs for enforcement**: When you need guaranteed implementation and want to provide common functionality
3. **Follow constraints**: Each interface documents constraints that must be followed
4. **Extend gradually**: Existing code can gradually adopt these interfaces
5. **Document implementations**: When implementing interfaces, document any additional constraints or features

## Migration Guide

To adopt these interfaces in existing code:

1. **Review existing implementations** against the interface requirements
2. **Identify gaps** where current code doesn't match interface contracts
3. **Implement gradually** by having classes optionally implement the interfaces
4. **Update type hints** to use the protocol types for better type checking
5. **Test compatibility** using `isinstance()` checks with protocols