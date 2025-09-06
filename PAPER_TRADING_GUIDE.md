# Paper Trading Mode with Metrics Reporting

## Overview

This implementation provides a comprehensive paper trading mode with mock fills and advanced metrics reporting, bridging the gap between backtesting and live trading.

## Key Features

### 🎯 Paper Trading with Mock Fills
- **Enhanced PaperBroker**: Realistic order simulation with market prices
- **Real-time P&L Tracking**: Live position updates and unrealized P&L calculation
- **Portfolio History**: Complete tracking of portfolio value over time
- **Trade Execution**: Mock fills with configurable slippage simulation

### 📊 Comprehensive Metrics Reporting
- **Real-time Metrics**: Sharpe ratio, drawdown, volatility calculated live
- **Portfolio Analytics**: Total return, win rate, profit factor
- **Risk Metrics**: Maximum drawdown, current drawdown, Sortino ratio
- **Performance Tracking**: Session-based monitoring and analysis

### 📁 CSV Export Capabilities
- **Portfolio History**: `portfolio_history_*.csv` - Equity curve data
- **Trade History**: `trade_history_*.csv` - Detailed trade execution records
- **Current Positions**: `positions_*.csv` - Real-time position details
- **Metrics Summary**: `portfolio_metrics_*.csv` - Performance metrics
- **Live Sessions**: `live_metrics_*.csv` - Real-time trading session data

### 🌉 Backtest-to-Live Bridge
- **Seamless Transition**: Transfer configurations from backtest to live trading
- **Performance Analysis**: Analyze backtest results and generate recommendations
- **Risk Assessment**: Automated risk warnings and position sizing suggestions
- **Bridge Reports**: Comprehensive transition documentation

## Usage Examples

### Basic Paper Trading

```python
from backtesting.brokers.paper import PaperBroker
from backtesting.brokers.base import BrokerOrder, OrderSide, OrderType

# Create paper broker
broker = PaperBroker("DEMO_ACCOUNT", initial_cash=100000.0)
await broker.connect()

# Place orders
buy_order = BrokerOrder(
    symbol="AAPL",
    side=OrderSide.BUY,
    quantity=100,
    order_type=OrderType.MARKET,
    price=150.0
)
order_id = await broker.place_order(buy_order)

# Update market prices for P&L calculation
broker.update_market_prices({"AAPL": 152.0})

# Get portfolio metrics
metrics = broker.get_portfolio_metrics()
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
print(f"Total Return: {metrics['total_return_percent']:.2f}%")

# Export to CSV
files = broker.export_to_csv("trading_results")
```

### Live Trading with Metrics

```python
from backtesting.execution.live_engine import LiveTradingEngine
from backtesting.execution.bridge import BacktestToLiveBridge

# Create bridge utility
bridge = BacktestToLiveBridge(api_key="your_alpha_vantage_key")

# Set up paper trading
setup = bridge.create_paper_trading_setup(
    initial_cash=100000.0,
    symbols=["IBM", "AAPL"],
    update_interval=60
)

# Create and start live trading engine
engine = setup['engine']
strategy = SimpleTradingStrategy()

await engine.start(strategy)

# Monitor metrics
metrics = engine.get_current_metrics()
print(f"Portfolio Value: ${metrics['total_value']:,.2f}")
print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")

# Export results
files = engine.export_results("live_results")
```

### Bridge from Backtest to Live

```python
from backtesting.execution.bridge import BacktestToLiveBridge

# Analyze backtest results
bridge = BacktestToLiveBridge(api_key="your_key")
analysis = bridge.analyze_backtest_performance(backtest_results)

# Create live trading setup based on backtest
setup = bridge.create_paper_trading_setup(
    backtest_results=backtest_results,
    initial_cash=50000.0,
    symbols=["IBM", "AAPL", "MSFT"]
)

# Generate bridge report
report = bridge.export_bridge_report(
    backtest_results=backtest_results,
    live_setup=setup,
    output_file="transition_report.txt"
)
```

## Integration with Alpha Vantage

The system supports real Alpha Vantage data feeds with automatic fallback to mock data:

```python
from backtesting.data_providers.alpha_vantage import AlphaVantageDataProvider
from backtesting.data_providers.mock_alpha_vantage import MockAlphaVantageDataProvider

# Try real API, fallback to mock
data_provider = AlphaVantageDataProvider(api_key)
if not data_provider.test_connection():
    data_provider = MockAlphaVantageDataProvider(api_key)
```

## Demo Script

Run the comprehensive demo to see all features:

```bash
python enhanced_live_trading_demo.py
```

This demonstrates:
- Enhanced paper trading with P&L tracking
- Live trading engine with real-time metrics
- CSV export functionality
- Bridge utilities for backtest-to-live transitions

## Generated Files

The system generates several types of CSV files for analysis:

- **Portfolio History**: Time series of portfolio values and returns
- **Trade History**: Complete record of all trade executions
- **Position Details**: Current holdings with P&L calculations
- **Performance Metrics**: Comprehensive performance summary
- **Live Session Data**: Real-time trading session metrics

## Architecture

### Core Components

1. **PaperBroker**: Enhanced paper trading with realistic order simulation
2. **LiveMetricsAggregator**: Real-time performance metrics calculation
3. **LiveTradingEngine**: Live trading coordination with metrics integration
4. **BacktestToLiveBridge**: Transition utility from backtest to live trading

### Metrics Pipeline

The system uses a modular metrics pipeline that calculates:
- Return-based metrics (total return, annualized return)
- Risk-adjusted metrics (Sharpe ratio, Sortino ratio)
- Drawdown analysis (maximum drawdown, current drawdown)
- Trade statistics (win rate, profit factor, average win/loss)

### Data Export

All trading data is exportable to CSV format for:
- External analysis tools
- Performance reporting
- Risk management
- Strategy validation

## Benefits

1. **Realistic Testing**: Paper trading with mock fills bridges backtesting and live trading
2. **Real-time Monitoring**: Live metrics calculation for immediate feedback
3. **Data Export**: CSV export for external analysis and reporting
4. **Seamless Transition**: Bridge utilities make moving from backtest to live trading smooth
5. **Risk Management**: Comprehensive metrics help monitor and control risk
6. **Alpha Vantage Integration**: Real market data feeds for realistic simulation