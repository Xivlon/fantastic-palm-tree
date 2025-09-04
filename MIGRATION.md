# Migration Guide: Modular Strategy Architecture

## Overview

This release introduces a comprehensive modular architecture for the strategy framework with the following improvements:

- **Modular Strategy Components**: Core strategy logic is now separated into focused modules
- **Typed Dataclasses**: All results use strongly-typed dataclasses for better type safety
- **Trailing Stop Engine**: Dedicated engine for trailing stop logic with extensible design
- **Enhanced Configuration**: Comprehensive configuration system with validation

## Breaking Changes

### 1. Strategy Imports
**Before:**
```python
from enhancements_strategy import EnhancedStrategy, StrategyConfig
```

**After:**
```python
from fantastic_palm_tree.strategy.enhanced import EnhancedStrategy
from fantastic_palm_tree.config import StrategyConfig
```

### 2. Result Types
**Before:**
```python
# Results were returned as dictionaries
result = strategy.process_bar(...)
atr = result["atr"]
stop_hit = result["stop_hit"]
```

**After:**
```python
# Results use typed dataclasses
from fantastic_palm_tree.results import BarProcessResult, ExitResult

result: BarProcessResult = strategy.process_bar(...)
atr = result.atr
stop_hit = result.stop_hit
if result.exit_result:
    pnl = result.exit_result.pnl
```

### 3. Position Model
**Before:**
```python
# Position was a simple dictionary or basic class
```

**After:**
```python
from fantastic_palm_tree.models.position import TradePosition

position = TradePosition(
    entry_price=100.0,
    size=1000.0,
    entry_atr=2.5,
    is_long=True
)
```

### 4. Configuration Structure
The configuration system is now more structured with validation:

```python
from fantastic_palm_tree.config import StrategyConfig

config = StrategyConfig(
    atr_period=14,
    exits={
        "trailing": {
            "enabled": True,
            "type": "atr",
            "use_dynamic_atr": False,
            "dynamic_atr_min_samples": 1,
        }
    }
)
```

## New Features

### 1. Modular Trailing Stop Engine
```python
from fantastic_palm_tree.risk.trailing import TrailingStopEngine

# The trailing stop engine is now a separate, testable component
engine = TrailingStopEngine(config, atr_calculator)
distance = engine.compute_distance(position)
stop_price = engine.update_trailing_stop(position, current_price)
```

### 2. Dedicated ATR Calculator
```python
from fantastic_palm_tree.indicators.atr import ATRCalculator

atr_calc = ATRCalculator(period=14)
atr_value = atr_calc.add_bar(high, low, prev_close)
```

### 3. Structured Logging
```python
from fantastic_palm_tree.logging import get_logger

logger = get_logger()
logger.info("Strategy event occurred")
```

### 4. Custom Exceptions
```python
from fantastic_palm_tree.exceptions import (
    PositionExistsError, 
    NoPositionError, 
    InvalidConfigError
)
```

## Migration Steps

1. **Update Imports**: Change all imports to use the new modular structure
2. **Update Result Handling**: Replace dictionary access with dataclass attribute access
3. **Update Configuration**: Use the new `StrategyConfig` class with proper validation
4. **Update Exception Handling**: Use the new exception classes
5. **Test Integration**: Ensure all tests pass with the new architecture

## Benefits

- **Better Type Safety**: Strongly typed dataclasses prevent runtime errors
- **Modular Design**: Each component can be tested and modified independently
- **Extensibility**: Easy to add new trailing stop types, indicators, etc.
- **Configuration Validation**: Catch configuration errors early
- **Better Testing**: Modular design enables focused unit tests

## Compatibility

The old `enhancements_strategy.py` interface is maintained for backward compatibility during the transition period, but it's recommended to migrate to the new modular architecture as soon as possible.