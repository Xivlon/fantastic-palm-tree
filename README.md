# Fantastic Palm Tree - Advanced Backtesting Framework

A comprehensive backtesting framework with advanced metrics, parameter sweeping, kill-switch mechanisms, and Schwab broker integration.

## Features

- **Advanced Backtest Architecture**: Modular strategy framework with comprehensive data handling
- **Performance Metrics**: Extensive performance and risk metrics calculation
- **Parameter Sweep**: Parallel parameter optimization and testing
- **Kill-Switch**: Risk management and emergency stop mechanisms
- **Schwab Broker**: Integration scaffold for Charles Schwab API

## Quick Start

```python
from backtesting import BacktestEngine, Strategy
from backtesting.brokers import SchwabBroker
from backtesting.metrics import MetricsCalculator

# Define your strategy
class MyStrategy(Strategy):
    def on_data(self, data):
        # Your trading logic here
        pass

# Run backtest
engine = BacktestEngine()
results = engine.run(MyStrategy(), data)

# Calculate metrics
metrics = MetricsCalculator.calculate(results)
print(f"Sharpe Ratio: {metrics.sharpe_ratio}")
```

## Installation

```bash
pip install -e .
```

## Development

```bash
pip install -e ".[dev]"
pytest
```