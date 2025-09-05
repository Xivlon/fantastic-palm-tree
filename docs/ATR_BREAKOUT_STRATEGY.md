# ATR Breakout Strategy - Reference Implementation

## Overview

The ATR Breakout Strategy is a comprehensive reference implementation that demonstrates how to build trading strategies within the Fantastic Palm Tree framework. It combines technical analysis (ATR-based breakout detection) with robust risk management (trailing stops and position sizing) to create a complete trading system.

## Key Features

- **ATR-Based Breakout Detection**: Identifies price breakouts using Average True Range (ATR) to account for volatility
- **Dynamic Position Sizing**: Calculates position sizes based on risk management rules and current volatility  
- **Integrated Trailing Stops**: Uses the framework's trailing stop engine for risk management
- **Comprehensive Configuration**: Fully configurable with sensible defaults and validation
- **Type-Safe Implementation**: Uses dataclasses and type hints throughout
- **Complete Metrics Pipeline**: Integrates with logging and performance tracking
- **Extensible Design**: Easy to modify and extend for custom requirements

## How It Works

### 1. Breakout Detection

The strategy monitors price action and detects breakouts when the current price exceeds recent highs/lows by a multiple of the Average True Range (ATR):

```
Long Breakout Threshold = Recent High + (ATR × Multiplier)
Short Breakout Threshold = Recent Low - (ATR × Multiplier)
```

### 2. Position Entry

When a breakout is detected:
1. Calculate position size based on risk management rules
2. Set initial stop loss at `Entry Price ± (ATR × Stop Loss Multiplier)`
3. Enter position with commission and slippage accounting

### 3. Risk Management

- **Initial Stop Loss**: Set based on ATR to account for normal volatility
- **Trailing Stops**: Dynamic trailing stops that follow favorable price movement
- **Position Sizing**: Risk-based sizing to limit maximum loss per trade
- **Maximum Risk**: Configurable maximum risk percentage per trade

## Configuration

### Basic Configuration

```python
from fantastic_palm_tree.config import ATRBreakoutConfig

config = ATRBreakoutConfig(
    # ATR calculation
    atr_period=14,
    
    # Breakout detection
    breakout={
        "enabled": True,
        "multiplier": 2.0,           # ATR multiplier for breakout threshold
        "lookback_period": 20,       # Bars to look back for high/low
        "direction": "both",         # "long", "short", or "both"
        "min_atr_threshold": 0.01,   # Minimum ATR to consider trades
    },
    
    # Position sizing
    position_size=1000.0,            # Default position size
    max_position_pct=0.02,           # Max 2% of portfolio per position
    
    # Risk management
    max_risk_per_trade=0.01,         # Max 1% risk per trade
    stop_loss_atr_multiplier=2.0,    # Initial stop loss distance
    
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
```

### Strategy Variants

#### Conservative Setup
```python
conservative = ATRBreakoutConfig(
    atr_period=20,                   # Longer ATR period
    breakout={
        "multiplier": 2.5,           # Higher threshold
        "lookback_period": 30,       # Longer lookback
        "direction": "long",         # Long only
    },
    max_risk_per_trade=0.005,        # 0.5% risk per trade
    stop_loss_atr_multiplier=3.0,    # Wider stops
)
```

#### Aggressive Setup
```python
aggressive = ATRBreakoutConfig(
    atr_period=7,                    # Shorter ATR period
    breakout={
        "multiplier": 1.0,           # Lower threshold
        "lookback_period": 10,       # Shorter lookback
        "direction": "both",         # Both directions
    },
    max_risk_per_trade=0.03,         # 3% risk per trade
    stop_loss_atr_multiplier=1.5,    # Tighter stops
)
```

## Usage Examples

### Basic Usage

```python
from fantastic_palm_tree.strategy.atr_breakout import ATRBreakoutStrategy
from fantastic_palm_tree.config import ATRBreakoutConfig

# Create configuration
config = ATRBreakoutConfig(
    breakout={"multiplier": 1.5, "direction": "both"},
    max_risk_per_trade=0.02
)

# Initialize strategy
strategy = ATRBreakoutStrategy(
    config=config,
    commission_rate=0.001,  # 0.1% commission
    slippage=0.01          # $0.01 slippage
)

# Process market data
result = strategy.process_bar(
    high=102.5, 
    low=99.8, 
    close=101.2, 
    prev_close=100.0
)

# Check results
print(f"ATR: {result.atr:.2f}")
print(f"Stop Hit: {result.stop_hit}")

if result.exit_result:
    print(f"Trade P&L: ${result.exit_result.pnl:.2f}")
    print(f"R-Multiple: {result.exit_result.r_multiple:.2f}")
```

### Backtesting Loop

```python
# Sample backtesting implementation
def backtest_atr_breakout(price_data, config):
    strategy = ATRBreakoutStrategy(config)
    
    for bar in price_data:
        result = strategy.process_bar(
            high=bar['high'],
            low=bar['low'], 
            close=bar['close'],
            prev_close=bar['prev_close']
        )
        
        # Log trades
        if result.exit_result:
            print(f"Trade completed: P&L=${result.exit_result.pnl:.2f}")
    
    # Final statistics
    stats = strategy.get_stats()
    print(f"Total P&L: ${stats['realized_pnl']:.2f}")
    print(f"Total Bars: {stats['total_bars_processed']}")
```

### Live Trading Integration

```python
# Example live trading integration
class LiveATRBreakoutTrader:
    def __init__(self, config, broker_interface):
        self.strategy = ATRBreakoutStrategy(config)
        self.broker = broker_interface
    
    def on_new_bar(self, bar_data):
        result = self.strategy.process_bar(
            high=bar_data.high,
            low=bar_data.low,
            close=bar_data.close,
            prev_close=bar_data.prev_close
        )
        
        # Handle position changes
        position_info = self.strategy.get_position_info()
        if position_info:
            # Update broker position
            self.broker.update_stop_loss(position_info['stop_price'])
        
        # Handle exits
        if result.exit_result:
            self.broker.close_position()
            self.log_trade(result.exit_result)
```

## Performance Metrics

The strategy provides comprehensive performance tracking:

### Key Metrics
- **Total Realized P&L**: Cumulative profit/loss from completed trades
- **R-Multiple**: Risk-adjusted returns (positive = profit, negative = loss)
- **Win Rate**: Percentage of profitable trades
- **Average R**: Average R-multiple per trade
- **Maximum Drawdown**: Largest peak-to-trough decline

### Accessing Metrics
```python
# Get current statistics
stats = strategy.get_stats()
print(f"Bars Processed: {stats['total_bars_processed']}")
print(f"Realized P&L: ${stats['realized_pnl']:.2f}")
print(f"Current ATR: {stats['current_atr']:.2f}")

# Get position information
position = strategy.get_position_info()
if position:
    print(f"Entry Price: ${position['entry_price']:.2f}")
    print(f"Stop Price: ${position['stop_price']:.2f}")
    print(f"Bars Held: {position['bars_held']}")
```

## Risk Management Features

### Position Sizing
- **Risk-Based Sizing**: Position size calculated to limit maximum loss
- **ATR-Based Stops**: Stop losses set based on current market volatility
- **Maximum Position Limits**: Configurable maximum position size

### Stop Loss Management
- **Initial Stops**: Set at entry based on ATR
- **Trailing Stops**: Dynamic stops that follow favorable movement
- **Dynamic ATR**: Optional use of current ATR vs. entry ATR for trailing

### Risk Controls
- **Maximum Risk Per Trade**: Limits potential loss on any single trade
- **Minimum ATR Threshold**: Prevents trading in low-volatility conditions
- **Position Sizing Caps**: Maximum position size relative to capital

## Extending the Strategy

### Custom Breakout Logic
```python
class CustomATRBreakout(ATRBreakoutStrategy):
    def _detect_breakout(self, high, low, close, atr):
        # Custom breakout logic here
        # Return (direction, entry_price) or None
        pass
```

### Additional Filters
```python
class FilteredATRBreakout(ATRBreakoutStrategy):
    def _should_check_breakouts(self):
        # Add custom filters (volume, time of day, etc.)
        base_check = super()._should_check_breakouts()
        custom_filter = self._custom_filter_logic()
        return base_check and custom_filter
```

### Custom Position Sizing
```python
class VolatilityATRBreakout(ATRBreakoutStrategy):
    def _calculate_position_size(self, entry_price, atr):
        # Custom position sizing based on volatility
        volatility_factor = self._calculate_volatility_factor(atr)
        base_size = super()._calculate_position_size(entry_price, atr)
        return base_size * volatility_factor
```

## Integration with Framework

The ATR Breakout Strategy is fully integrated with the Fantastic Palm Tree framework:

### Core Components
- **Base Strategy**: Inherits from `BaseStrategy` for consistent interface
- **Configuration**: Uses framework configuration system with validation
- **Indicators**: Leverages `ATRCalculator` for technical analysis
- **Risk Management**: Integrates with `TrailingStopEngine`
- **Results**: Returns typed `BarProcessResult` and `ExitResult` objects

### Logging Integration
```python
# Framework logging automatically captures:
# - Strategy initialization
# - Breakout detection events  
# - Position entry/exit events
# - Risk management actions
# - Performance metrics

# Access logs via the logging system
from fantastic_palm_tree.logging import get_logger
logger = get_logger()
```

### Metrics Pipeline
The strategy automatically feeds data to the metrics pipeline:
- Real-time P&L tracking
- Position monitoring
- Risk metrics calculation
- Performance attribution

## Testing

Comprehensive test suite validates:
- Configuration validation
- Breakout detection logic
- Position management
- Risk calculations
- Integration with core framework

Run tests:
```bash
python -m tests.test_atr_breakout_strategy
```

## Best Practices

### Configuration
1. **Start Conservative**: Begin with higher multipliers and wider stops
2. **Validate Settings**: Use configuration validation to catch errors early
3. **Backtest Parameters**: Test different parameter combinations
4. **Risk Management**: Always set appropriate risk limits

### Implementation
1. **Monitor Performance**: Regularly review strategy statistics
2. **Risk Controls**: Implement additional risk controls as needed
3. **Position Sizing**: Ensure position sizing aligns with risk tolerance
4. **Market Conditions**: Consider market regime in parameter selection

### Production Use
1. **Data Quality**: Ensure high-quality, timely price data
2. **Execution**: Account for slippage and commission in live trading
3. **Monitoring**: Implement real-time monitoring and alerts
4. **Risk Limits**: Set and enforce portfolio-level risk limits

## Conclusion

The ATR Breakout Strategy serves as a comprehensive reference implementation that demonstrates:

- **Complete Strategy Development**: From configuration to execution
- **Framework Integration**: Proper use of all framework components
- **Risk Management**: Professional-grade risk controls
- **Extensibility**: Template for building custom strategies
- **Production Ready**: Suitable for live trading with proper risk management

This implementation provides a solid foundation for developing sophisticated trading strategies while maintaining code quality, type safety, and comprehensive testing.