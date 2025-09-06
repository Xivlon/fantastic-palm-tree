"""
Test market impact models for large order execution.
"""

from enhancements_strategy import (
    Order, ExecutionEngine, FixedSlippageModel, PerShareCommissionModel,
    LinearMarketImpactModel, SquareRootMarketImpactModel
)


def test_linear_market_impact_model():
    """Test linear market impact model"""
    model = LinearMarketImpactModel(impact_rate=0.0001)
    
    # Large order in small volume stock - high impact
    large_order = Order(symbol="SMALL", side="BUY", qty=10000)
    market_price = 50.0
    daily_volume = 100000  # Small daily volume
    
    impact = model.calculate_impact(large_order, daily_volume, market_price)
    
    # Order value: 10000 * $50 = $500K
    # Volume value: 100000 * $50 = $5M  
    # Impact ratio: $500K / $5M = 0.1
    # Expected impact: $50 * 0.1 * 0.0001 = $0.0005
    expected_impact = 50.0 * 0.1 * 0.0001
    assert abs(impact - expected_impact) < 0.0001
    
    # Same order in high volume stock - low impact
    high_volume = 10000000  # Large daily volume
    low_impact = model.calculate_impact(large_order, high_volume, market_price)
    assert low_impact < impact  # Should be much lower
    
    # Sell order should have negative impact
    sell_order = Order(symbol="TEST", side="SELL", qty=10000)
    sell_impact = model.calculate_impact(sell_order, daily_volume, market_price)
    assert sell_impact < 0


def test_square_root_market_impact_model():
    """Test square root market impact model"""
    model = SquareRootMarketImpactModel(impact_coefficient=0.01)
    
    order = Order(symbol="TEST", side="BUY", qty=50000)
    market_price = 100.0
    daily_volume = 1000000
    
    impact = model.calculate_impact(order, daily_volume, market_price)
    
    # Participation rate: 50000 / 1000000 = 0.05
    # Impact rate: 0.01 * sqrt(0.05) = 0.01 * 0.2236 ≈ 0.002236
    # Expected impact: $100 * 0.002236 ≈ $0.22
    participation_rate = 50000 / 1000000
    expected_impact_rate = 0.01 * (participation_rate ** 0.5)
    expected_impact = market_price * expected_impact_rate
    
    assert abs(impact - expected_impact) < 0.01


def test_execution_engine_with_market_impact():
    """Test ExecutionEngine with market impact"""
    
    # Create models
    slippage_model = FixedSlippageModel(0.02)
    commission_model = PerShareCommissionModel(0.005, 1.0)
    impact_model = LinearMarketImpactModel(impact_rate=0.0002)
    
    engine = ExecutionEngine(
        slippage_model=slippage_model,
        commission_model=commission_model,
        market_impact_model=impact_model,
        spread_bps=10
    )
    
    # Small order - minimal impact
    small_order = Order(symbol="TEST", side="BUY", qty=100)
    market_price = 100.0
    daily_volume = 1000000
    
    small_fill = engine.execute_order(small_order, market_price, daily_volume)
    
    # Large order - significant impact
    large_order = Order(symbol="TEST", side="BUY", qty=50000)
    large_fill = engine.execute_order(large_order, market_price, daily_volume)
    
    # Large order should have higher fill price due to market impact
    assert large_fill.price > small_fill.price
    
    print(f"Small order fill price: ${small_fill.price:.4f}")
    print(f"Large order fill price: ${large_fill.price:.4f}")
    print(f"Market impact difference: ${large_fill.price - small_fill.price:.4f}")
    
    # Both should have costs but different amounts
    assert small_fill.price > market_price  # Above market due to spread + slippage
    assert large_fill.price > small_fill.price  # Higher due to market impact
    
    return {
        "small_order_price": small_fill.price,
        "large_order_price": large_fill.price,
        "market_impact_cost": large_fill.price - small_fill.price
    }


def test_market_impact_volume_sensitivity():
    """Test how market impact changes with volume"""
    
    impact_model = LinearMarketImpactModel(impact_rate=0.0001)
    engine = ExecutionEngine(market_impact_model=impact_model)
    
    order = Order(symbol="TEST", side="BUY", qty=10000)
    market_price = 100.0
    
    # Test different volume scenarios
    volumes = [100_000, 500_000, 1_000_000, 5_000_000]  # Low to high volume
    results = {}
    
    for volume in volumes:
        fill = engine.execute_order(order, market_price, volume)
        impact_cost = fill.price - market_price
        results[volume] = {
            "fill_price": fill.price,
            "impact_cost": impact_cost
        }
    
    print("\nMarket Impact vs Volume:")
    for volume, result in results.items():
        print(f"Volume {volume:,}: Price=${result['fill_price']:.4f}, "
              f"Impact=${result['impact_cost']:.4f}")
    
    # Higher volume should have lower impact
    volumes_sorted = sorted(volumes)
    for i in range(len(volumes_sorted) - 1):
        low_vol = volumes_sorted[i]
        high_vol = volumes_sorted[i + 1]
        assert results[low_vol]["impact_cost"] > results[high_vol]["impact_cost"]
    
    return results


def test_execution_cost_breakdown():
    """Break down all execution costs"""
    
    # Create execution engine with all models
    slippage_model = FixedSlippageModel(0.03)
    commission_model = PerShareCommissionModel(0.01, 1.0)
    impact_model = LinearMarketImpactModel(impact_rate=0.0001)
    
    engine = ExecutionEngine(
        slippage_model=slippage_model,
        commission_model=commission_model,
        market_impact_model=impact_model,
        spread_bps=20  # 20 bps spread
    )
    
    order = Order(symbol="TEST", side="BUY", qty=5000)
    market_price = 150.0
    daily_volume = 500000
    
    # Calculate individual components
    spread_cost = market_price * (20 / 10000) / 2  # Half spread for buy
    slippage_cost = 0.03  # Fixed slippage
    
    # Market impact calculation
    order_value = order.qty * market_price
    volume_value = daily_volume * market_price
    impact_ratio = order_value / volume_value
    impact_cost = market_price * impact_ratio * 0.0001
    
    # Commission
    commission = max(order.qty * 0.01, 1.0)
    
    # Execute order
    fill = engine.execute_order(order, market_price, daily_volume)
    
    total_price_impact = fill.price - market_price
    expected_price_impact = spread_cost + slippage_cost + impact_cost
    
    print(f"\nExecution Cost Breakdown:")
    print(f"Market price: ${market_price:.2f}")
    print(f"Spread cost: ${spread_cost:.4f}")
    print(f"Slippage cost: ${slippage_cost:.4f}")
    print(f"Market impact: ${impact_cost:.4f}")
    print(f"Total price impact: ${total_price_impact:.4f}")
    print(f"Commission: ${commission:.2f}")
    print(f"Final fill price: ${fill.price:.4f}")
    
    # Verify calculations (with floating point tolerance)
    assert abs(total_price_impact - expected_price_impact) < 0.001
    assert abs(fill.commission - commission) < 0.01
    
    return {
        "spread_cost": spread_cost,
        "slippage_cost": slippage_cost,
        "impact_cost": impact_cost,
        "commission": commission,
        "total_cost": total_price_impact + commission
    }


if __name__ == "__main__":
    print("Testing linear market impact model...")
    test_linear_market_impact_model()
    
    print("Testing square root market impact model...")
    test_square_root_market_impact_model()
    
    print("Testing execution engine with market impact...")
    impact_results = test_execution_engine_with_market_impact()
    
    print("Testing market impact volume sensitivity...")
    volume_results = test_market_impact_volume_sensitivity()
    
    print("Testing execution cost breakdown...")
    cost_breakdown = test_execution_cost_breakdown()
    
    print(f"\n" + "="*60)
    print("MARKET IMPACT TESTING SUMMARY")
    print("="*60)
    print(f"Market impact between small/large orders: ${impact_results['market_impact_cost']:.4f}")
    print(f"Total execution cost components: ${cost_breakdown['total_cost']:.4f}")
    print(f"Volume sensitivity test passed for {len(volume_results)} scenarios")
    
    print("\n✅ All market impact tests passed!")