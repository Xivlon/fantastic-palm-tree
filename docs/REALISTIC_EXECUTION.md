# Realistic Execution Models

This document describes the enhanced execution models that address the "perfect fill" issue in backtesting by adding realistic slippage, commissions, spreads, market impact, and optional execution delays.

## Overview

The enhanced execution system provides several models to simulate realistic trading costs:

1. **Slippage Models** - Account for market impact and timing delays
2. **Commission Models** - Simulate broker fees and transaction costs  
3. **Spread Models** - Account for bid-ask spreads
4. **Market Impact Models** - Model price impact for large orders
5. **Execution Engine** - Coordinates all execution effects

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

## Market Impact Models

### LinearMarketImpactModel
Linear relationship between order size and price impact.

```python
from enhancements_strategy import LinearMarketImpactModel

model = LinearMarketImpactModel(impact_rate=0.0001)
order = Order(symbol="AAPL", side="BUY", qty=10000)  
impact = model.calculate_impact(order, volume=1_000_000, market_price=150.0)

# Order value: 10000 * $150 = $1.5M
# Volume value: 1M * $150 = $150M  
# Impact ratio: $1.5M / $150M = 0.01
# Price impact: $150 * 0.01 * 0.0001 = $0.0015
```

### SquareRootMarketImpactModel
Square root relationship (common in academic literature).

```python
from enhancements_strategy import SquareRootMarketImpactModel

model = SquareRootMarketImpactModel(impact_coefficient=0.01)
order = Order(symbol="AAPL", side="BUY", qty=50000)
impact = model.calculate_impact(order, volume=1_000_000, market_price=100.0)

# Participation rate: 50000 / 1000000 = 0.05
# Impact rate: 0.01 * sqrt(0.05) ≈ 0.00224
# Price impact: $100 * 0.00224 ≈ $0.224
```

## Enhanced Execution Engine

The `ExecutionEngine` now coordinates all execution effects including market impact:

```python
from enhancements_strategy import (
    ExecutionEngine, FixedSlippageModel, PerShareCommissionModel,
    LinearMarketImpactModel
)

# Create models
slippage_model = FixedSlippageModel(0.02)
commission_model = PerShareCommissionModel(0.005, 1.0)
impact_model = LinearMarketImpactModel(0.0001)

# Create enhanced execution engine
engine = ExecutionEngine(
    slippage_model=slippage_model,
    commission_model=commission_model,
    market_impact_model=impact_model,
    execution_delay_ms=50,  # 50ms execution delay
    spread_bps=20           # 20 basis point bid-ask spread
)

# Execute order with all effects
order = Order(symbol="AAPL", side="BUY", qty=10000)
fill = engine.execute_order(order, market_price=150.0, volume=1_000_000)

print(f"Fill price: ${fill.price:.4f}")      # Market + spread + slippage + impact
print(f"Commission: ${fill.commission:.2f}")  # Commission charged
```

## Execution Cost Breakdown

A typical order execution includes these cost components:

1. **Bid-Ask Spread**: Buy at ask, sell at bid
2. **Slippage**: Market movement and execution delays  
3. **Market Impact**: Price impact from large orders
4. **Commission**: Broker fees

```python
# Example cost breakdown for $150 stock, 5000 shares
market_price = 150.00
spread_cost = 150.00 * 0.002 / 2     # 20 bps spread ÷ 2 = $0.15
slippage_cost = 0.03                  # Fixed $0.03 slippage
impact_cost = 0.0001                  # Minimal for small order
commission = 50.00                    # $0.01 per share

total_execution_cost = spread_cost + slippage_cost + impact_cost + commission
# Total: $0.18 price impact + $50 commission = $50.18
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

## Using with EnhancedStrategy

The `EnhancedStrategy` class now supports automatic realistic execution:

```python
from enhancements_strategy import EnhancedStrategy, StrategyConfig

# Create strategy
config = StrategyConfig()
strategy = EnhancedStrategy(config)

# Configure realistic execution
strategy.configure_realistic_execution(
    slippage_config={"bps": 20},        # 20 bps slippage
    commission_config={"per_share": 0.01, "min_commission": 1.0},
    spread_bps=15                       # 15 bps bid-ask spread
)

# Or set an advanced execution engine directly
from enhancements_strategy import ExecutionEngine, LinearMarketImpactModel

impact_model = LinearMarketImpactModel(impact_rate=0.0001)
engine = ExecutionEngine(
    slippage_model=create_slippage_model({"bps": 20}),
    commission_model=create_commission_model({"per_share": 0.01}),
    market_impact_model=impact_model,
    spread_bps=15
)
strategy.set_execution_engine(engine)

# Strategy will now use realistic execution automatically
strategy.update_atr(high=102, low=98, prev_close=100)
success = strategy.enter_position(price=100.0, size=1000)
exit_result = strategy.exit_position(price=105.0)

print(f"Entry was realistic: {strategy.position.entry_price > 100.0}")
print(f"Total cost: ${exit_result['commission']:.2f}")
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

## Volume-Dependent Execution Quality

Large orders in low-volume stocks experience higher costs:

```python
# Small order in high-volume stock
small_order = Order(symbol="AAPL", side="BUY", qty=100)
small_fill = engine.execute_order(small_order, 150.0, volume=10_000_000)

# Large order in low-volume stock  
large_order = Order(symbol="SMALL", side="BUY", qty=10000)
large_fill = engine.execute_order(large_order, 150.0, volume=100_000)

# Large order will have significantly higher execution costs
print(f"Small order cost: ${small_fill.price - 150.0:.4f}")
print(f"Large order cost: ${large_fill.price - 150.0:.4f}")
```

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

1. **Market Impact**: Large orders now have higher slippage and price impact
2. **Bid-Ask Spreads**: Buy orders pay ask, sell orders receive bid  
3. **Transaction Costs**: Commissions reduce available capital
4. **Volume Sensitivity**: Execution quality depends on liquidity
5. **Execution Delays**: Optional millisecond delays (for future use)

### Before and After Comparison

```python
# Perfect execution (old)
fill_price = market_price  # Exact market price
commission = 0.0          # No costs

# Realistic execution (new)  
fill_price = market_price + spread/2 + slippage + market_impact  # For buy orders
commission = calculated_commission                               # Real broker fees
```

## Testing

Run the comprehensive test suite to see realistic execution in action:

```bash
# Test execution models
python tests/test_realistic_execution.py

# Test integration with strategy
python tests/test_execution_integration.py

# Test enhanced strategy integration
python tests/test_enhanced_strategy_integration.py

# Test market impact models
python tests/test_market_impact.py
```

The tests demonstrate:
- Different slippage models and their impact
- Commission calculations for various trade sizes
- Volume-dependent execution costs
- Market impact for large orders
- Before/after equity comparisons
- Strategy-level integration

## Migration from Perfect Execution

Existing code continues to work unchanged. To enable realistic execution:

1. **In strategies**: Use `configure_realistic_execution()` method or `set_execution_engine()`
2. **In tests**: Set `enable_realistic_execution=True` when creating `TrackingBroker`
3. **In configuration**: Add slippage and commission sections

The system defaults to perfect execution for backward compatibility.

### Progressive Enhancement

You can gradually add realism:

```python
# Step 1: Add basic slippage and commissions
strategy.configure_realistic_execution(
    slippage_config={"bps": 10},
    commission_config={"per_share": 0.005}
)

# Step 2: Add spreads
strategy.configure_realistic_execution(
    slippage_config={"bps": 10},
    commission_config={"per_share": 0.005},
    spread_bps=15
)

# Step 3: Add market impact for large orders
impact_model = LinearMarketImpactModel(impact_rate=0.0001)
engine = ExecutionEngine(
    slippage_model=create_slippage_model({"bps": 10}),
    commission_model=create_commission_model({"per_share": 0.005}),
    market_impact_model=impact_model,
    spread_bps=15
)
strategy.set_execution_engine(engine)
```