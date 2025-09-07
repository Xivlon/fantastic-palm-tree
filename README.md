# Fantastic Palm Tree - Advanced Backtesting Framework

[![CI](https://github.com/Xivlon/fantastic-palm-tree/workflows/CI/badge.svg)](https://github.com/Xivlon/fantastic-palm-tree/actions)
[![codecov](https://codecov.io/gh/Xivlon/fantastic-palm-tree/branch/main/graph/badge.svg)](https://codecov.io/gh/Xivlon/fantastic-palm-tree)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Fantastic Palm Tree** is a comprehensive, professional-grade backtesting framework designed for quantitative trading strategy development. Built with a modular architecture that emphasizes type safety, extensibility, and production readiness, it provides everything you need to develop, test, and deploy algorithmic trading strategies.

## Table of Contents

- [What Is This Framework?](#what-is-this-framework)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Strategy Development](#strategy-development)
- [Backtesting Engine](#backtesting-engine)
- [Performance Metrics](#performance-metrics)
- [Risk Management](#risk-management)
- [Parameter Optimization](#parameter-optimization)
- [Kill-Switch System](#kill-switch-system)
- [Broker Integration](#broker-integration)
- [Advanced Features](#advanced-features)
- [Reference Implementations](#reference-implementations)
- [Extension Guide](#extension-guide)
- [Migration Guide](#migration-guide)
- [Development Setup](#development-setup)
- [Performance & Best Practices](#performance--best-practices)
- [API Reference](#api-reference)
- [Backtesting Dashboard](#backtesting-dashboard)

## What Is This Framework?

Fantastic Palm Tree is designed for quantitative traders, portfolio managers, and researchers who need professional-grade backtesting capabilities. Whether you're developing simple moving average strategies or complex multi-asset algorithms, this framework provides:

**For Beginners**: Clear examples, comprehensive documentation, and sensible defaults that let you start testing strategies immediately.

**For Professionals**: Advanced risk management, robust metrics calculation, parameter optimization, live trading integration, and production-ready components.

**For Researchers**: Extensible architecture, comprehensive interfaces, and detailed performance analytics for strategy research and development.

## Key Features

### 🏗️ **Modular Architecture**
- **Clean Separation**: Strategy logic, risk management, indicators, and configuration are separate, testable modules
- **Type Safety**: Full type annotations with strongly-typed dataclasses prevent runtime errors
- **Interface-Driven**: Well-defined interfaces make testing and extension straightforward
- **Production Ready**: Industrial-strength error handling and logging

### 📊 **Advanced Strategy Framework**
- **Enhanced Strategy Engine**: Sophisticated strategy execution with ATR-based trailing stops
- **Technical Indicators**: Built-in ATR calculator with extensible indicator framework
- **Position Management**: Comprehensive position tracking with unrealized P&L calculation
- **Configuration System**: Validated configuration with sensible defaults and error checking

### 🔄 **Comprehensive Backtesting**
- **BacktestEngine**: Full-featured backtesting with realistic market simulation
- **Portfolio Management**: Multi-asset portfolio tracking with equity curves
- **Order Management**: Support for market, limit, stop, and stop-limit orders
- **Data Handling**: Flexible market data management with historical lookbacks

### 📈 **Professional Metrics**
- **Performance Metrics**: 20+ metrics including Sharpe ratio, Sortino ratio, Calmar ratio
- **Risk Analysis**: VaR, CVaR, maximum drawdown, volatility, downside deviation
- **Trade Statistics**: Win rate, profit factor, average win/loss, R-multiples
- **Benchmark Comparison**: Alpha, beta, information ratio, tracking error
- **Real-Time Pipeline**: Streaming metrics calculation during backtesting

### 🛡️ **Risk Management**
- **Kill-Switch System**: Multiple trigger types for portfolio protection
- **Trailing Stops**: Dynamic ATR-based and percentage-based trailing stops
- **Position Sizing**: Risk-based position sizing with configurable limits
- **Drawdown Protection**: Automatic strategy termination on excessive losses

### ⚡ **Parameter Optimization**
- **Grid Search**: Exhaustive parameter combination testing
- **Random Search**: Efficient sampling for large parameter spaces
- **Parallel Execution**: Multi-worker support for faster optimization
- **Results Analysis**: Statistical analysis, correlation matrices, heatmaps

### 🔗 **Live Trading Integration**
- **Broker Framework**: Abstract broker interface for consistent integration
- **Charles Schwab**: Complete OAuth2 integration scaffold
- **Async Support**: Non-blocking operations for production environments
- **Error Handling**: Robust error handling and automatic token refresh

## Quick Start

### Simple Strategy Example

Here's how to create and run a basic strategy in just a few lines:

```python
from fantastic_palm_tree.strategy.enhanced import EnhancedStrategy
from fantastic_palm_tree.config import StrategyConfig

# 1. Configure your strategy
config = StrategyConfig(
    atr_period=14,                    # Use 14-day ATR for volatility
    exits={
        "trailing": {
            "enabled": True,          # Enable trailing stops
            "type": "atr",           # Use ATR-based trailing
            "use_dynamic_atr": True, # Adjust for changing volatility
        }
    }
)

# 2. Create strategy instance
strategy = EnhancedStrategy(config)
strategy.set_fees(commission_rate=0.001, slippage=0.01)  # 0.1% commission, $0.01 slippage

# 3. Process market data bar by bar
result = strategy.process_bar(
    high=102.5, 
    low=99.8, 
    close=101.2, 
    prev_close=100.0
)

# 4. Check results
print(f"Current ATR: {result.atr:.2f}")
print(f"Stop Hit: {result.stop_hit}")

if result.exit_result:
    print(f"Trade P&L: ${result.exit_result.pnl:.2f}")
    print(f"Risk-Adjusted Return: {result.exit_result.r_multiple:.2f}R")
```

### Full Backtesting Example

Here's how to run a complete backtest with metrics:

```python
from backtesting import BacktestEngine, MetricsCalculator, Strategy
from datetime import datetime
import pandas as pd
import numpy as np

# 1. Create sample data
dates = pd.date_range('2023-01-01', periods=252, freq='D')
prices = 150 + np.random.randn(252).cumsum()
data = pd.DataFrame({
    'timestamp': dates,
    'AAPL': {
        'open': prices,
        'high': prices + np.random.uniform(0, 2, 252),
        'low': prices - np.random.uniform(0, 2, 252),
        'close': prices,
        'volume': 1000000 + np.random.randint(-100000, 100000, 252)
    }
})

# 2. Create and configure strategy
class SimpleStrategy(Strategy):
    def on_data(self, timestamp, data):
        # Simple buy-and-hold strategy
        if not self.portfolio.positions:
            self.buy('AAPL', 100)  # Buy 100 shares

# 3. Run backtest
engine = BacktestEngine(initial_cash=100000)
strategy = SimpleStrategy("Buy and Hold")
results = engine.run(strategy, data)

# 4. Calculate metrics
calculator = MetricsCalculator()
metrics = calculator.calculate_metrics(results)

print(f"Total Return: {metrics.total_return:.2%}")
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
print(f"Maximum Drawdown: {metrics.max_drawdown:.2%}")
```

## Installation

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/Xivlon/fantastic-palm-tree.git
cd fantastic-palm-tree

# Install dependencies
pip install -r requirements.txt

# Install in development mode (optional)
pip install -e .
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/Xivlon/fantastic-palm-tree.git
cd fantastic-palm-tree

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
pytest
```

### Requirements

- **Python 3.10+**: Modern Python features and type hints
- **Core Dependencies**: numpy, pandas, matplotlib for data analysis
- **Web Framework**: fastapi, aiohttp for API server and broker integration
- **Testing**: pytest for development and testing

## Core Concepts

Understanding these core concepts will help you get the most out of the framework:

### Strategy Lifecycle

Every strategy follows this lifecycle:

1. **Configuration**: Set up strategy parameters and risk management rules
2. **Initialization**: Create strategy instance and set up components  
3. **Data Processing**: Process market data bar by bar
4. **Position Management**: Enter and exit positions based on signals
5. **Risk Management**: Apply trailing stops and other risk controls
6. **Results**: Generate typed results with P&L and risk metrics

### Data Flow Architecture

```
Market Data → Strategy Processing → Risk Management → Position Updates → Results
     ↓              ↓                     ↓               ↓              ↓
  Bar Data    → Signal Generation → Stop Calculations → Portfolio → Metrics
```

### Type Safety

The framework uses strongly-typed dataclasses throughout:

```python
from fantastic_palm_tree.results import BarProcessResult, ExitResult
from fantastic_palm_tree.models.position import TradePosition

# All results are typed for better IDE support and error catching
result: BarProcessResult = strategy.process_bar(...)
position: TradePosition = result.position
exit_result: ExitResult = result.exit_result
```

### Configuration System

Centralized configuration with validation and defaults:

```python
from fantastic_palm_tree.config import StrategyConfig

config = StrategyConfig(
    atr_period=14,                  # ATR calculation period
    exits={                         # Exit rules configuration
        "trailing": {
            "enabled": True,
            "type": "atr",          # ATR-based trailing stops
            "use_dynamic_atr": False,
            "dynamic_atr_min_samples": 1
        }
    }
)

# Configuration is validated at creation time
print(config.trailing)  # Access nested configuration easily
```

## Strategy Development

### Basic Strategy Structure

All strategies inherit from `BaseStrategy` and implement key methods:

```python
from fantastic_palm_tree.strategy.base import BaseStrategy
from fantastic_palm_tree.config import StrategyConfig

class MyStrategy(BaseStrategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        # Initialize strategy-specific components
    
    def process_bar(self, high: float, low: float, close: float, prev_close: float):
        # Process each market data bar
        # Returns BarProcessResult with ATR, stop information, and exit results
        pass
    
    def enter_position(self, price: float, size: float, is_long: bool) -> bool:
        # Handle position entry logic
        pass
    
    def exit_position(self, price: float, reason: str):
        # Handle position exit logic
        # Returns ExitResult with P&L and risk metrics
        pass
```

### Using the Enhanced Strategy

The framework provides a ready-to-use `EnhancedStrategy` with ATR-based trailing stops:

```python
from fantastic_palm_tree.strategy.enhanced import EnhancedStrategy

strategy = EnhancedStrategy(config)

# Set trading costs
strategy.set_fees(
    commission_rate=0.001,  # 0.1% commission
    slippage=0.01          # $0.01 slippage per share
)

# Process market data
for bar in market_data:
    result = strategy.process_bar(
        high=bar['high'],
        low=bar['low'], 
        close=bar['close'],
        prev_close=bar['prev_close']
    )
    
    # Check for exits
    if result.exit_result:
        print(f"Position exited: {result.exit_result.reason}")
        print(f"P&L: ${result.exit_result.pnl:.2f}")
        print(f"R-Multiple: {result.exit_result.r_multiple:.2f}")
```

### Technical Indicators

The framework includes built-in technical indicators with an extensible design:

```python
from fantastic_palm_tree.indicators.atr import ATRCalculator

# ATR (Average True Range) Calculator
atr_calc = ATRCalculator(period=14)

# Add bars one by one
for bar in market_data:
    atr = atr_calc.add_bar(
        high=bar['high'],
        low=bar['low'],
        prev_close=bar['prev_close']
    )
    
    print(f"Current ATR: {atr:.2f}")
    print(f"Has enough samples: {atr_calc.has_enough_samples(min_samples=10)}")
```

### Position Management

Positions are tracked with rich data structures:

```python
from fantastic_palm_tree.models.position import TradePosition
from datetime import datetime

position = TradePosition(
    entry_price=100.0,
    size=1000.0,
    entry_atr=2.5,
    is_long=True,
    timestamp=int(datetime.now().timestamp())
)

# Calculate unrealized P&L
current_price = 105.0
pnl = position.unrealized_pnl(current_price)
print(f"Unrealized P&L: ${pnl:.2f}")

# Position supports both long and short
short_position = TradePosition(
    entry_price=100.0,
    size=500.0,
    entry_atr=2.5,
    is_long=False  # Short position
)
```

## Backtesting Engine

The backtesting engine provides realistic market simulation with full order management:

### Basic Backtesting

```python
from backtesting import BacktestEngine, Strategy

class MovingAverageStrategy(Strategy):
    def __init__(self, name="MA Strategy"):
        super().__init__(name)
        self.short_window = 10
        self.long_window = 30
        self.position = 0
    
    def on_data(self, timestamp, data):
        symbol = "AAPL"
        if symbol not in data:
            return
        
        price = data[symbol]['close']
        
        # Calculate moving averages (simplified)
        # In practice, you'd maintain proper rolling windows
        if self.position == 0 and price > 150:  # Simple entry condition
            self.buy(symbol, 100)  # Go long
            self.position = 1
        elif self.position == 1 and price < 140:  # Simple exit condition
            self.sell(symbol, 100)  # Exit long
            self.position = 0

# Run backtest
engine = BacktestEngine(initial_cash=100000)
strategy = MovingAverageStrategy()

# Add kill switches for risk management
from backtesting.killswitch import create_default_kill_switches
kill_switches = create_default_kill_switches(
    max_drawdown=0.20,  # 20% max drawdown
    max_loss=10000,     # $10,000 max loss
)
for ks in kill_switches.triggers:
    engine.add_kill_switch(ks)

# Run the backtest
results = engine.run(strategy, market_data)
print(f"Final portfolio value: ${results.final_portfolio_value:,.2f}")
```

### Advanced Backtesting Features

```python
# Configure detailed backtesting parameters
engine = BacktestEngine(
    initial_cash=100000,
    commission=0.001,           # 0.1% commission
    slippage=0.01,             # $0.01 slippage
    margin_rate=0.02,          # 2% margin requirement
    min_commission=1.0,        # $1 minimum commission
)

# Add multiple strategies
strategies = [
    MovingAverageStrategy("MA_10_30"),
    MovingAverageStrategy("MA_5_20"),
]

for strategy in strategies:
    strategy.set_params(short_window=5, long_window=20)  # Configure parameters
    results = engine.run(strategy, market_data)
    print(f"{strategy.name}: {results.total_return:.2%}")
```

## Performance Metrics

The framework calculates comprehensive performance and risk metrics:

### Basic Metrics

```python
from backtesting.metrics import MetricsCalculator

calculator = MetricsCalculator()
metrics = calculator.calculate_metrics(backtest_results)

# Return Metrics
print(f"Total Return: {metrics.total_return:.2%}")
print(f"Annualized Return: {metrics.annualized_return:.2%}")
print(f"CAGR: {metrics.cagr:.2%}")

# Risk Metrics  
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
print(f"Sortino Ratio: {metrics.sortino_ratio:.2f}")
print(f"Maximum Drawdown: {metrics.max_drawdown:.2%}")
print(f"VaR (95%): {metrics.var_95:.2%}")

# Trade Statistics
print(f"Total Trades: {metrics.total_trades}")
print(f"Win Rate: {metrics.win_rate:.2%}")
print(f"Profit Factor: {metrics.profit_factor:.2f}")
```

### Advanced Metrics

```python
# Risk-Adjusted Metrics
print(f"Calmar Ratio: {metrics.calmar_ratio:.2f}")
print(f"Information Ratio: {metrics.information_ratio:.2f}")
print(f"Tracking Error: {metrics.tracking_error:.2%}")

# Benchmark Comparison (if benchmark provided)
print(f"Alpha: {metrics.alpha:.2%}")
print(f"Beta: {metrics.beta:.2f}")

# Distribution Statistics
print(f"Skewness: {metrics.skewness:.2f}")
print(f"Kurtosis: {metrics.kurtosis:.2f}")
print(f"Downside Deviation: {metrics.downside_deviation:.2%}")
```

### Real-Time Metrics Pipeline

For live monitoring during backtesting:

```python
from backtesting.metrics.pipeline import MetricsPipeline

# Create metrics pipeline
pipeline = MetricsPipeline()
pipeline.initialize(100000.0)  # Starting cash

# Process data in real-time
for timestamp, portfolio_value in equity_curve:
    pipeline.process_bar(timestamp, portfolio_value)

for trade in completed_trades:
    pipeline.process_trade(trade)

# Get current metrics
summary = pipeline.get_summary_metrics()
print(f"Current Drawdown: {summary['current_drawdown']:.2%}")
print(f"Total Trades: {summary['total_trades']}")

# Convert to standard metrics format
final_metrics = pipeline.to_performance_metrics()
```

## Risk Management

### Trailing Stops

The framework provides sophisticated trailing stop functionality:

```python
from fantastic_palm_tree.risk.trailing import TrailingStopEngine

# Create trailing stop engine
trailing_engine = TrailingStopEngine(config, atr_calculator)

# For an active position
position = TradePosition(entry_price=100.0, size=1000, is_long=True, entry_atr=2.0)

# Update trailing stop as price moves
current_price = 105.0
new_stop = trailing_engine.update_trailing_stop(position, current_price)
print(f"New stop price: ${new_stop:.2f}")

# Check if stop was hit
bar_high = 106.0
bar_low = 103.0
if TrailingStopEngine.stop_hit(position, bar_high, bar_low):
    print("Stop loss triggered!")
```

### Configuration Options

```python
# ATR-based trailing stops
config = StrategyConfig(
    exits={
        "trailing": {
            "enabled": True,
            "type": "atr",              # Use ATR for distance calculation
            "use_dynamic_atr": True,    # Adjust distance as volatility changes
            "dynamic_atr_min_samples": 5,  # Minimum samples for dynamic calculation
        }
    }
)

# Static ATR trailing stops
static_config = StrategyConfig(
    exits={
        "trailing": {
            "enabled": True,
            "type": "atr",              # Use ATR for distance calculation
            "use_dynamic_atr": False,   # Use entry ATR (static)
            "dynamic_atr_min_samples": 1,  # Not used when static
        }
    }
)
```

## Parameter Optimization

The framework provides comprehensive parameter optimization capabilities:

### Grid Search Optimization

```python
from backtesting.sweep import ParameterSpace, GridSearchOptimizer

# Define parameter space
param_space = ParameterSpace()
param_space.add_parameter("short_window", [5, 10, 15, 20])
param_space.add_parameter("long_window", [25, 30, 35, 40, 45])
param_space.add_parameter("stop_loss_atr", [1.5, 2.0, 2.5, 3.0])

print(f"Total combinations: {param_space.size()}")  # 4 × 5 × 4 = 80 combinations

# Create optimizer
engine = BacktestEngine(initial_cash=100000)
optimizer = GridSearchOptimizer(
    engine=engine,
    strategy_class=MovingAverageStrategy,
    max_workers=4,  # Parallel processing
)

# Run optimization
print("Running parameter optimization...")
results = optimizer.optimize(market_data, param_space, verbose=True)

# Analyze results
print(f"\nOptimization completed in {results.elapsed_time:.1f}s")
print(f"Best Sharpe Ratio: {results.best_objective_value:.3f}")
print(f"Best Parameters: {results.best_parameters}")

# Get top results
top_results = results.get_top_n_results(5)
for i, result in enumerate(top_results, 1):
    print(f"{i}. Sharpe: {result['objective_value']:.3f}, Params: {result['parameters']}")
```

### Random Search for Large Spaces

```python
from backtesting.sweep import RandomSearchOptimizer

# For large parameter spaces, use random search
param_space = ParameterSpace()
param_space.add_parameter("short_window", list(range(5, 50)))    # 45 options
param_space.add_parameter("long_window", list(range(20, 200)))   # 180 options  
param_space.add_parameter("stop_loss_atr", [x/10 for x in range(10, 50)])  # 40 options
# Total: 45 × 180 × 40 = 324,000 combinations!

# Random search with 1000 samples
random_optimizer = RandomSearchOptimizer(
    engine=engine,
    strategy_class=MovingAverageStrategy,
    max_workers=8,
    n_samples=1000  # Test 1000 random combinations
)

results = random_optimizer.optimize(market_data, param_space)
```

## Kill-Switch System

The kill-switch system provides automatic risk management to protect your portfolio:

### Built-in Kill Switches

```python
from backtesting.killswitch import create_default_kill_switches

# Create default kill switches
kill_switches = create_default_kill_switches(
    max_drawdown=0.15,      # Stop trading at 15% drawdown
    max_loss=25000,         # Stop at $25,000 total loss
    max_volatility=0.40     # Stop if portfolio volatility exceeds 40%
)

# Add to backtest engine
engine = BacktestEngine(initial_cash=100000)
for trigger in kill_switches.triggers:
    engine.add_kill_switch(trigger)

# The engine will automatically stop trading if any trigger activates
results = engine.run(strategy, market_data)

# Check if kill switch was activated
if kill_switches.is_active:
    print("Kill switch activated!")
    summary = kill_switches.get_activation_summary()
    print(f"Triggered by: {summary['triggers'][0]['name']}")
    print(f"Reason: {summary['triggers'][0]['reason']}")
```

### Custom Kill Switches

```python
from backtesting.killswitch.triggers import KillSwitchTrigger
from datetime import datetime

class DailyLossLimitTrigger(KillSwitchTrigger):
    def __init__(self, max_daily_loss: float):
        super().__init__("daily_loss_limit")
        self.max_daily_loss = max_daily_loss
        self.daily_start_value = None
        self.current_day = None
    
    def check_trigger(self, portfolio, current_prices, timestamp):
        current_date = timestamp.date()
        
        # Reset at start of new day
        if self.current_day != current_date:
            self.daily_start_value = portfolio.get_total_value(current_prices)
            self.current_day = current_date
            return False
        
        # Check daily loss
        current_value = portfolio.get_total_value(current_prices)
        daily_loss = self.daily_start_value - current_value
        
        if daily_loss > self.max_daily_loss:
            self.activation_reason = f"Daily loss ${daily_loss:.2f} exceeds limit ${self.max_daily_loss:.2f}"
            return True
        
        return False

# Use custom trigger
custom_trigger = DailyLossLimitTrigger(max_daily_loss=5000)
engine.add_kill_switch(custom_trigger)
```

## Broker Integration

The framework provides a flexible broker integration system for live trading:

### Charles Schwab Integration

```python
from backtesting.brokers.schwab import SchwabBroker
import asyncio

async def schwab_trading_example():
    # Initialize Schwab broker with credentials
    broker = SchwabBroker(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="https://localhost",
        account_id="your_account_id"
    )
    
    # Authenticate (opens browser for OAuth)
    await broker.authenticate()
    
    # Get account information
    account_info = await broker.get_account_info()
    print(f"Account Value: ${account_info['current_balances']['total_cash_value']}")
    
    # Get current positions
    positions = await broker.get_positions()
    for position in positions:
        print(f"{position['instrument']['symbol']}: {position['long_quantity']} shares")
    
    # Place an order
    order = await broker.place_order(
        symbol="AAPL",
        quantity=10,
        side="BUY",
        order_type="MARKET"
    )
    print(f"Order placed: {order['order_id']}")
    
    # Monitor order status
    status = await broker.get_order_status(order['order_id'])
    print(f"Order status: {status['status']}")

# Run async broker operations
asyncio.run(schwab_trading_example())
```

## Advanced Features

### Interface System

The framework provides comprehensive interfaces for extensibility:

```python
from interfaces import StrategyProtocol, EngineProtocol

# Protocol-based interface (duck typing)
def run_any_strategy(strategy: StrategyProtocol, data):
    strategy.on_start()
    for timestamp, bar_data in data:
        strategy.on_data(timestamp, bar_data)
    strategy.on_finish()

# Abstract base class interface (inheritance)
from interfaces import StrategyABC

class MyStrategy(StrategyABC):
    def on_data(self, timestamp: str, data: dict) -> None:
        # Must implement this method
        pass
    
    def on_start(self) -> None:
        print("Strategy starting...")
    
    def on_finish(self) -> None:
        print("Strategy finished.")
```

### Configuration Validation

```python
from fantastic_palm_tree.config import StrategyConfig
from fantastic_palm_tree.exceptions import InvalidConfigError

try:
    # Invalid configuration
    config = StrategyConfig(
        atr_period=-5,  # Invalid: must be positive
        exits={
            "trailing": {
                "enabled": True,
                "type": "invalid_type"  # Invalid: unknown type
            }
        }
    )
except InvalidConfigError as e:
    print(f"Configuration error: {e}")

# Valid configuration with defaults
config = StrategyConfig()  # Uses sensible defaults
print(f"Default ATR period: {config.atr_period}")
print(f"Trailing config: {config.trailing}")
```

## Reference Implementations

### ATR Breakout Strategy

A complete reference implementation demonstrating professional strategy development:

```python
from fantastic_palm_tree.strategy.atr_breakout import ATRBreakoutStrategy
from fantastic_palm_tree.config import ATRBreakoutConfig

# Configure ATR breakout strategy
config = ATRBreakoutConfig(
    # ATR calculation
    atr_period=14,
    
    # Breakout detection
    breakout={
        "enabled": True,
        "multiplier": 2.0,              # ATR multiplier for breakout threshold
        "lookback_period": 20,          # Bars to look back for high/low
        "direction": "both",            # "long", "short", or "both"
        "min_atr_threshold": 0.01,      # Minimum ATR to consider trades
    },
    
    # Position sizing
    position_size=1000.0,               # Default position size
    max_position_pct=0.02,              # Max 2% of portfolio per position
    
    # Risk management
    max_risk_per_trade=0.01,            # Max 1% risk per trade
    stop_loss_atr_multiplier=2.0,       # Initial stop loss distance
    
    # Trailing stops
    exits={
        "trailing": {
            "enabled": True,
            "type": "atr",
            "use_dynamic_atr": True,
            "dynamic_atr_min_samples": 5,
        }
    }
)

# Initialize strategy
strategy = ATRBreakoutStrategy(
    config=config,
    commission_rate=0.001,
    slippage=0.01
)

# Process market data
for bar in market_data:
    result = strategy.process_bar(
        high=bar['high'],
        low=bar['low'],
        close=bar['close'],
        prev_close=bar['prev_close']
    )
    
    # Check for trades
    if result.exit_result:
        print(f"Trade completed:")
        print(f"  P&L: ${result.exit_result.pnl:.2f}")
        print(f"  R-Multiple: {result.exit_result.r_multiple:.2f}")
        print(f"  Reason: {result.exit_result.reason}")

# Get strategy statistics
stats = strategy.get_stats()
print(f"Total P&L: ${stats['realized_pnl']:.2f}")
print(f"Current ATR: {stats['current_atr']:.2f}")
```

## Extension Guide

### Creating Custom Strategies

```python
from fantastic_palm_tree.strategy.base import BaseStrategy
from fantastic_palm_tree.config import StrategyConfig

class CustomStrategy(BaseStrategy):
    """Template for custom strategy development."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        
        # Initialize custom components
        self.custom_indicator = CustomIndicator()
        self.signal_filter = SignalFilter()
    
    def process_bar(self, high: float, low: float, close: float, prev_close: float):
        """Core strategy logic."""
        
        # Update indicators
        atr = self.atr_calculator.add_bar(high, low, prev_close)
        custom_value = self.custom_indicator.update(high, low, close)
        
        # Generate signals
        entry_signal = self._check_entry_conditions(close, atr, custom_value)
        
        if entry_signal and not self.position:
            # Enter position
            position_size = self._calculate_position_size(close, atr)
            self.enter_position(close, position_size, entry_signal.is_long)
        
        # Handle existing position
        stop_hit = False
        exit_result = None
        
        if self.position:
            # Update trailing stop
            new_stop = self.trailing_engine.update_trailing_stop(self.position, close)
            if new_stop:
                self.position.stop_price = new_stop
            
            # Check stop hit
            stop_hit = self.trailing_engine.stop_hit(self.position, high, low)
            if stop_hit:
                exit_result = self.exit_position(close, "trailing_stop")
        
        from fantastic_palm_tree.results import BarProcessResult
        return BarProcessResult(
            atr=atr,
            stop_hit=stop_hit,
            exit_result=exit_result,
            stop_price=self.position.stop_price if self.position else None
        )
    
    def _check_entry_conditions(self, price, atr, custom_value):
        """Implement custom entry logic."""
        # Your entry logic here
        pass
    
    def _calculate_position_size(self, price, atr):
        """Implement custom position sizing."""
        # Your position sizing logic here
        pass
```

### Custom Technical Indicators

```python
from typing import List

class CustomIndicator:
    """Template for custom technical indicators."""
    
    def __init__(self, period: int = 14):
        self.period = period
        self.values: List[float] = []
    
    def update(self, high: float, low: float, close: float) -> float:
        """Update indicator with new bar data."""
        
        # Calculate indicator value
        indicator_value = self._calculate_value(high, low, close)
        
        # Maintain rolling window
        self.values.append(indicator_value)
        if len(self.values) > self.period:
            self.values.pop(0)
        
        return indicator_value
    
    def get_value(self) -> float:
        """Get current indicator value."""
        return self.values[-1] if self.values else 0.0
    
    def has_enough_data(self) -> bool:
        """Check if enough data for reliable calculation."""
        return len(self.values) >= self.period
    
    def _calculate_value(self, high: float, low: float, close: float) -> float:
        """Implement indicator calculation logic."""
        # Your calculation logic here
        pass
```

## Migration Guide

### From Legacy Strategy Interface

If you're migrating from an older version:

```python
# Old way (enhancements_strategy.py)
from enhancements_strategy import EnhancedStrategy, StrategyConfig

# New way (modular architecture)
from fantastic_palm_tree.strategy.enhanced import EnhancedStrategy
from fantastic_palm_tree.config import StrategyConfig
from fantastic_palm_tree.results import BarProcessResult, ExitResult
```

### Configuration Migration

```python
# Old configuration (dictionary-based)
old_config = {
    "atr_period": 14,
    "trailing_enabled": True,
    "trailing_type": "atr"
}

# New configuration (validated dataclass)
new_config = StrategyConfig(
    atr_period=14,
    exits={
        "trailing": {
            "enabled": True,
            "type": "atr",
            "use_dynamic_atr": False
        }
    }
)
```

### Result Handling Migration

```python
# Old way (dictionary results)
result = strategy.process_bar(...)
atr = result["atr"]
stop_hit = result["stop_hit"]

# New way (typed dataclasses)
result: BarProcessResult = strategy.process_bar(...)
atr = result.atr
stop_hit = result.stop_hit
if result.exit_result:
    pnl = result.exit_result.pnl
    r_multiple = result.exit_result.r_multiple
```

### Gradual Migration Strategy

1. **Phase 1**: Start using new imports while keeping existing logic
2. **Phase 2**: Update configuration to use new StrategyConfig
3. **Phase 3**: Update result handling to use typed dataclasses
4. **Phase 4**: Leverage new features (interfaces, kill switches, etc.)

## Development Setup

### Local Development

```bash
# Clone repository
git clone https://github.com/Xivlon/fantastic-palm-tree.git
cd fantastic-palm-tree

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fantastic_palm_tree --cov-report=html

# Run specific test categories
pytest -k "test_strategy"
pytest -k "test_trailing"
pytest -m slow  # Run slow tests (if marked)

# Run integration tests
pytest tests/test_integration.py

# Verbose output
pytest -v -s
```

### Running the API Server

The framework includes a FastAPI server that bridges the Python backtesting framework with web frontends:

```bash
# Start the API server
uvicorn api_server:app --reload --port 8000

# The server will be available at http://localhost:8000
# API documentation available at http://localhost:8000/docs
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy fantastic_palm_tree/

# Run all quality checks
ruff check . && ruff format --check . && mypy fantastic_palm_tree/
```

## Performance & Best Practices

### Performance Optimization

```python
# Efficient indicator calculation
from fantastic_palm_tree.indicators.atr import ATRCalculator

class EfficientATR(ATRCalculator):
    """Optimized ATR calculation."""
    
    def __init__(self, period: int):
        super().__init__(period)
        self._tr_sum = 0.0  # Running sum for efficiency
    
    def add_bar(self, high: float, low: float, prev_close: float) -> float:
        tr = self._calculate_tr(high, low, prev_close)
        
        if len(self.true_ranges) >= self.period:
            # Remove oldest value from sum
            self._tr_sum -= self.true_ranges[0]
        
        # Add new value
        self._tr_sum += tr
        self.true_ranges.append(tr)
        
        # Maintain window size
        if len(self.true_ranges) > self.period:
            self.true_ranges.pop(0)
        
        # Calculate ATR efficiently
        if len(self.true_ranges) == self.period:
            return self._tr_sum / self.period
        
        return sum(self.true_ranges) / len(self.true_ranges)
```

### Best Practices

#### Strategy Development
1. **Start Simple**: Begin with basic strategies and add complexity gradually
2. **Validate Configuration**: Always validate strategy configuration at startup
3. **Use Type Hints**: Leverage type hints for better IDE support and error catching
4. **Test Incrementally**: Write tests for each component as you develop

#### Risk Management
1. **Set Risk Limits**: Always define maximum risk per trade and portfolio
2. **Use Kill Switches**: Implement automatic risk controls for live trading
3. **Monitor Drawdowns**: Track portfolio drawdowns in real-time
4. **Diversify**: Don't put all capital in a single strategy or asset

#### Performance
1. **Profile First**: Identify bottlenecks before optimizing
2. **Efficient Data Structures**: Use appropriate data structures for your use case
3. **Limit State**: Keep strategy state minimal for better performance

#### Production Use
1. **Monitor Everything**: Log strategy decisions and performance metrics
2. **Handle Errors Gracefully**: Implement comprehensive error handling
3. **Test with Real Data**: Validate strategies with actual market data
4. **Gradual Deployment**: Start with small position sizes in live trading

### Troubleshooting Common Issues

```python
# Debug configuration issues
from fantastic_palm_tree.exceptions import InvalidConfigError

try:
    config = StrategyConfig(invalid_param=True)
except InvalidConfigError as e:
    print(f"Configuration error: {e}")
    # Check configuration documentation

# Debug position management
if not strategy.position:
    print("No active position")
else:
    print(f"Position: {strategy.position.size} @ ${strategy.position.entry_price}")
    print(f"Stop: ${strategy.position.stop_price}")

# Debug ATR calculation
if not strategy.atr_calculator.has_enough_samples(min_samples=10):
    print("Not enough ATR samples for reliable calculation")

# Debug trailing stops
distance = strategy.trailing_engine.compute_distance(strategy.position)
print(f"Current trailing distance: {distance:.2f}")
```

## API Reference

### Core Classes

#### BaseStrategy
```python
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """Abstract base class for all strategies."""
    
    @abstractmethod
    def enter_position(self, price: float, size: float, is_long: bool) -> bool:
        """Enter a trading position."""
        pass
    
    @abstractmethod
    def exit_position(self, price: float, reason: str):
        """Exit current position."""
        pass
    
    @abstractmethod
    def process_bar(self, high: float, low: float, close: float, prev_close: float):
        """Process market data bar."""
        pass
```

#### StrategyConfig
```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class StrategyConfig:
    """Configuration for strategy behavior."""
    
    exits: dict[str, Any] = field(default_factory=dict)
    atr_period: int = 14
    
    @property
    def trailing(self) -> dict[str, Any]:
        """Get trailing stop configuration."""
        pass
```

#### Result Classes
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExitResult:
    """Results from position exit."""
    
    pnl: float
    r_multiple: float
    total_pnl: float
    commission: float
    reason: str

@dataclass
class BarProcessResult:
    """Results from processing market data bar."""
    
    atr: float
    stop_hit: bool
    exit_result: Optional[ExitResult]
    stop_price: Optional[float] = None
```

---

## Backtesting Dashboard

The framework now includes a modern React/TypeScript dashboard for interactive backtesting analysis and monitoring.

### Features

- **Real-time Dashboard**: Interactive web interface for monitoring backtests
- **Performance Visualization**: Equity curves, drawdown charts, and comprehensive metrics
- **Trade Analysis**: Detailed trade tables with P&L tracking and performance statistics
- **Strategy Comparison**: Side-by-side comparison of different backtesting results
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Quick Start

To run the dashboard:

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Local Mock Mode Configuration

For pure local development without external services:

1. **Keep Local Mock Mode Active**: Ensure `USE_LOCAL_MOCK=true` in your environment
2. **Delete API Route** (Optional): Remove `pages/api/backtest.ts` to prevent accidental external calls
3. **Use Sample Data**: The dashboard will use realistic mock data for development

```bash
# Set environment variable for local mock mode
export USE_LOCAL_MOCK=true

# Optional: Remove external API integration
rm pages/api/backtest.ts
```

When `USE_LOCAL_MOCK=true`, the dashboard operates entirely with sample data, making it perfect for:
- Frontend development and testing
- Demonstration purposes
- Offline development environments
- UI/UX experimentation

The mock data includes realistic:
- Backtest results with various strategies
- Performance metrics and risk statistics
- Trade histories with P&L tracking
- Equity curves and drawdown data

### Dashboard Components

- **Homepage**: Overview and quick start guide
- **Dashboard**: Main analytics interface with charts and metrics
- **Backtest List**: Historical backtest results and comparison
- **Trade Analysis**: Detailed trade-by-trade breakdown
- **Strategy Management**: Strategy configuration and parameters

### Technology Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS for responsive design
- **Charts**: Recharts for interactive data visualization
- **Icons**: Lucide React for modern iconography

---

## Conclusion

Fantastic Palm Tree provides a comprehensive, professional-grade framework for algorithmic trading strategy development. Whether you're a beginner learning quantitative trading or an experienced developer building production systems, the framework's modular architecture, comprehensive features, and extensive documentation provide everything you need to succeed.

The combination of type safety, extensible design, professional-grade risk management, and production-ready components makes this framework suitable for both research and live trading environments. With built-in support for parameter optimization, comprehensive metrics, broker integration, and now a modern web dashboard, you can take your strategies from development to deployment seamlessly.

Start with the quick examples above, explore the reference implementations, and gradually leverage the advanced features as your needs grow. The framework is designed to scale with you from simple backtests to sophisticated multi-strategy production systems.

For questions, issues, or contributions, please visit the [GitHub repository](https://github.com/Xivlon/fantastic-palm-tree).
