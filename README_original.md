# Fantastic Palm Tree - Advanced Backtesting Framework

[![CI](https://github.com/Xivlon/fantastic-palm-tree/workflows/CI/badge.svg)](https://github.com/Xivlon/fantastic-palm-tree/actions)
[![codecov](https://codecov.io/gh/Xivlon/fantastic-palm-tree/branch/main/graph/badge.svg)](https://codecov.io/gh/Xivlon/fantastic-palm-tree)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A comprehensive backtesting framework with advanced metrics, parameter sweeping, kill-switch mechanisms, and Schwab broker integration.

## Features

- **Modular Strategy Framework**: Clean separation of concerns with dedicated modules for strategy, risk management, indicators, and configuration
- **Typed Dataclasses**: Strongly-typed result objects for better type safety and development experience  
- **Trailing Stop Engine**: Extensible trailing stop system with ATR-based logic and dynamic adjustment capabilities
- **Advanced Configuration**: Comprehensive configuration system with validation and sensible defaults
- **Performance Metrics**: Extensive performance and risk metrics calculation
- **Parameter Sweep**: Parallel parameter optimization and testing
- **Kill-Switch**: Risk management and emergency stop mechanisms
- **Schwab Broker**: Integration scaffold for Charles Schwab API

## Quick Start

```python
from fantastic_palm_tree.strategy.enhanced import EnhancedStrategy
from fantastic_palm_tree.config import StrategyConfig
from fantastic_palm_tree.results import BarProcessResult

# Configure strategy with modular settings
config = StrategyConfig(
    atr_period=14,
    exits={
        "trailing": {
            "enabled": True,
            "type": "atr", 
            "use_dynamic_atr": True,
            "dynamic_atr_min_samples": 5
        }
    }
)

# Create strategy instance
strategy = EnhancedStrategy(config)
strategy.set_fees(commission_rate=0.001, slippage=0.01)

# Process market data
result: BarProcessResult = strategy.process_bar(
    high=102.5, low=99.8, close=101.2, prev_close=100.0
)

# Access typed results
print(f"ATR: {result.atr}")
print(f"Stop Hit: {result.stop_hit}")
if result.exit_result:
    print(f"PnL: {result.exit_result.pnl}")
    print(f"R-Multiple: {result.exit_result.r_multiple}")
```

## Installation

```bash
pip install -e .
```

## Development

### Setup

```bash
# Install with development dependencies
pip install -e ".[dev]"
