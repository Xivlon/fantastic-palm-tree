# Realistic Execution Models

This document describes the enhanced execution models that address the "perfect fill" issue in backtesting by adding realistic slippage, commissions, spreads, and optional execution delays.

## Overview

The enhanced execution system provides several models to simulate realistic trading costs:

1. **Slippage Models** - Account for market impact and timing delays
2. **Commission Models** - Simulate broker fees and transaction costs  
3. **Spread Models** - Account for bid-ask spreads
4. **Execution Engine** - Coordinates all execution effects

## Slippage Models

### FixedSlippageModel
Fixed dollar amount slippage per share.

```python
from enhancements_strategy import FixedSlippageModel, Order

model = FixedSlippageModel(slippage_amount=0.05)  # 5 cents per share
order = Order(symbol="AAPL", side="BUY", qty=100)
slippage = model.calculate_slippage(order, market_price=150.0)
# Buy orders: +$0.05, Sell orders: -$0.05
```

### PercentageSlippageModel  
Percentage-based slippage (basis points).

```python
from enhancements_strategy import PercentageSlippageModel

model = PercentageSlippageModel(slippage_bps=10)  # 10 basis points = 0.1%
order = Order(symbol="AAPL", side="BUY", qty=100)  
slippage = model.calculate_slippage(order, market_price=150.0)
# Slippage = $150.00 * 0.001 = $0.15
```

### VolumeBasedSlippageModel
Slippage increases with trade volume relative to average daily volume.

```python
from enhancements_strategy import VolumeBasedSlippageModel

tiers = [
    {"adv_threshold": 0, "bps": 5},          # 5 bps for small trades
    {"adv_threshold": 1_000_000, "bps": 10}, # 10 bps for medium trades  
    {"adv_threshold": 5_000_000, "bps": 20}  # 20 bps for large trades
]

model = VolumeBasedSlippageModel(tiers)
order = Order(symbol="AAPL", side="BUY", qty=1000)
slippage = model.calculate_slippage(order, market_price=150.0, volume=2_000_000)
# Uses 10 bps tier since volume is 2M
```

## Commission Models

### PerShareCommissionModel
Fixed commission per share with minimum.

```python
from enhancements_strategy import PerShareCommissionModel

model = PerShareCommissionModel(per_share=0.005, min_commission=1.0)
order = Order(symbol="AAPL", side="BUY", qty=100)
commission = model.calculate_commission(order, fill_price=150.0)
# Commission = max(100 * $0.005, $1.00) = $1.00
```

### PercentageCommissionModel
Percentage of trade value with minimum.

```python
from enhancements_strategy import PercentageCommissionModel

model = PercentageCommissionModel(rate=0.001, min_commission=1.0)  # 0.1%
order = Order(symbol="AAPL", side="BUY", qty=100)
commission = model.calculate_commission(order, fill_price=150.0)
# Commission = max(100 * $150 * 0.001, $1.00) = $15.00
```

### TieredCommissionModel
Commission rate depends on trade size.

```python
from enhancements_strategy import TieredCommissionModel

tiers = [
    {"threshold": 0, "rate": 0.001},        # 0.1% for small trades
    {"threshold": 10_000, "rate": 0.0005},  # 0.05% for large trades
]

model = TieredCommissionModel(tiers)
order = Order(symbol="AAPL", side="BUY", qty=1000)
commission = model.calculate_commission(order, fill_price=150.0)
# Trade value = $150,000, uses 0.05% rate = $75.00
```

## Execution Engine

The `ExecutionEngine` coordinates all execution effects:

```python
from enhancements_strategy import ExecutionEngine, FixedSlippageModel, PerShareCommissionModel

# Create models
slippage_model = FixedSlippageModel(0.02)
commission_model = PerShareCommissionModel(0.005, 1.0)

# Create execution engine
engine = ExecutionEngine(
    slippage_model=slippage_model,
    commission_model=commission_model,
    execution_delay_ms=50,  # 50ms execution delay
    spread_bps=20           # 20 basis point bid-ask spread
)

# Execute order
order = Order(symbol="AAPL", side="BUY", qty=100)
fill = engine.execute_order(order, market_price=150.0, volume=1_000_000)

print(f"Fill price: ${fill.price:.4f}")      # Market price + spread + slippage
print(f"Commission: ${fill.commission:.2f}")  # Commission charged
```

## Factory Functions

Use factory functions to create models from configuration:

```python
from enhancements_strategy import create_slippage_model, create_commission_model

# Create from configuration dictionaries
slippage_config = {"bps": 15}  # 15 basis points
commission_config = {"per_share": 0.01, "min_commission": 1.0}

slippage_model = create_slippage_model(slippage_config)
commission_model = create_commission_model(commission_config)
```

## Using with TrackingBroker

Enable realistic execution in tests:

```python
from tests.test_utils import TrackingBroker

# Create broker with realistic execution
broker = TrackingBroker(
    starting_equity=100_000,
    slippage_config={"bps": 20},  # 20 bps slippage
    commission_config={"per_share": 0.01, "min_commission": 1.0},
    enable_realistic_execution=True
)

# Broker will now track commissions and adjust equity
from enhancements_strategy import Fill

fill = Fill(symbol="AAPL", side="BUY", qty=100, price=150.20, commission=1.50)
broker.apply_fills([fill])

print(f"Equity after commission: ${broker.equity:.2f}")
print(f"Total commission paid: ${broker.total_commission:.2f}")
```

## Configuration Examples

### Existing Test Configuration Format
Many tests already use this configuration structure:

```python
config = {
    "slippage": {"tiers": [{"adv_threshold": 0, "bps": 10}]},  # Volume-based
    "commission": {"per_share": 0.005},                        # Per-share
}
```

### Alternative Configurations

```python
# Fixed slippage
{"slippage": {"amount": 0.05}}

# Percentage slippage  
{"slippage": {"bps": 15}}

# Percentage commission
{"commission": {"rate": 0.001, "min_commission": 1.0}}

# Tiered commission
{"commission": {"tiers": [{"threshold": 0, "rate": 0.001}]}}
```

## Impact on Backtesting

The realistic execution models address several "perfect fill" issues:

1. **Market Impact**: Large orders now have higher slippage
2. **Bid-Ask Spreads**: Buy orders pay ask, sell orders receive bid  
3. **Transaction Costs**: Commissions reduce available capital
4. **Execution Delays**: Optional millisecond delays (for future use)

### Before and After Comparison

```python
# Perfect execution (old)
fill_price = market_price  # Exact market price
commission = 0.0          # No costs

# Realistic execution (new)  
fill_price = market_price + spread/2 + slippage  # For buy orders
commission = calculated_commission                # Real broker fees
```

## Testing

Run the test suite to see realistic execution in action:

```bash
# Test execution models
python tests/test_realistic_execution.py

# Test integration with strategy
python tests/test_execution_integration.py
```

The tests demonstrate:
- Different slippage models and their impact
- Commission calculations for various trade sizes
- Volume-dependent execution costs
- Before/after equity comparisons

## Migration from Perfect Execution

Existing code continues to work unchanged. To enable realistic execution:

1. **In tests**: Set `enable_realistic_execution=True` when creating `TrackingBroker`
2. **In strategies**: Use the `ExecutionEngine` for order processing
3. **In configuration**: Add slippage and commission sections

The system defaults to perfect execution for backward compatibility.