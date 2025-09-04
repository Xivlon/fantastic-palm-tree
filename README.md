# Fantastic Palm Tree - Advanced Backtesting Framework

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

```bash
pip install -e ".[dev]"
pytest
```

## Test Coverage Summary

A detailed matrix of covered behaviors lives in `docs/TEST_COVERAGE.md`. The modular architecture enables comprehensive testing:

**Core Modules:**
- **Strategy Framework**: Base strategy interface and enhanced strategy implementation
- **Trailing Stop Engine**: ATR-based trailing logic with dynamic/static modes
- **Typed Results**: Strongly-typed dataclasses for exit results and bar processing
- **Configuration System**: Validation and default value management
- **Position Management**: Trade position lifecycle and PnL calculations

**Behavioral Coverage:**
- ATR sizing, equity caps, short-sell enable flag
- Partial exits (single-per-bar constraint, priority over trailing stops)
- Trailing stops: activation thresholds, percent & ATR (dynamic vs static)  
- Drawdown kill switch
- Dynamic ATR expansion affecting trailing distance
- R-multiple calculations with deterministic ATR values

**Migration Support:**
- Backward compatibility with legacy `enhancements_strategy.py` interface
- Comprehensive migration guide with breaking change documentation

Planned additions: daily loss kill, multi-symbol concurrency limits, cost model validation, reversals, trailing-after-partials nuances.

Run tests:
```bash
pytest -q
pytest --cov=fantastic_palm_tree --cov-report=term-missing
```

**Migration Note**: See `MIGRATION.md` for detailed guide on migrating from the legacy interface to the new modular architecture.

Contribute:
- Use fixtures in `tests/conftest.py`.
- Parametrize similar behaviors rather than cloning tests.
- Prefer public APIs over internal attribute access; open an issue if missing.
- Test both the new modular components and legacy compatibility layer.
