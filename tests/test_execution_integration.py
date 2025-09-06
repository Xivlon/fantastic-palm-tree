"""
Integration test showing realistic execution with enhanced strategy.
"""

import datetime
from enhancements_strategy import Bar, EnhancementsContext
from tests.test_utils import TrackingBroker


def test_realistic_vs_perfect_execution():
    """Compare perfect execution vs realistic execution using direct Fill creation"""
    
    # Test realistic execution with manual fills
    realistic_broker = TrackingBroker(
        starting_equity=100_000,
        slippage_config={"bps": 20},
        commission_config={"per_share": 0.01, "min_commission": 1.0},
        enable_realistic_execution=True
    )
    
    # Test perfect execution
    perfect_broker = TrackingBroker(starting_equity=100_000)
    
    # Create fills - one with realistic costs, one perfect
    from enhancements_strategy import Fill
    
    # Perfect fill (no costs)
    perfect_fill = Fill(symbol="TEST", side="BUY", qty=1000, price=100.00, commission=0.0)
    
    # Realistic fill (with slippage and commission)
    # Simulate buying with 20 bps slippage (0.2%) and $10 commission
    realistic_price = 100.00 * (1 + 0.002)  # 20 bps slippage
    realistic_fill = Fill(symbol="TEST", side="BUY", qty=1000, price=realistic_price, commission=10.0)
    
    # Apply fills
    perfect_broker.apply_fills([perfect_fill])
    realistic_broker.apply_fills([realistic_fill])
    
    # Compare results
    print(f"Perfect execution equity: ${perfect_broker.equity:,.2f}")
    print(f"Realistic execution equity: ${realistic_broker.equity:,.2f}")
    print(f"Commission paid: ${realistic_broker.total_commission:.2f}")
    
    # Realistic execution should have lower equity due to costs
    assert realistic_broker.equity < perfect_broker.equity
    assert realistic_broker.total_commission > 0
    
    # Calculate total trading cost
    cost_difference = perfect_broker.equity - realistic_broker.equity
    
    return {
        "perfect_equity": perfect_broker.equity,
        "realistic_equity": realistic_broker.equity,
        "commission_cost": realistic_broker.total_commission,
        "total_cost": cost_difference
    }


def test_slippage_impact_on_fills():
    """Test how different slippage models affect fill prices"""
    
    from enhancements_strategy import (
        Order, ExecutionEngine, FixedSlippageModel, PercentageSlippageModel,
        PerShareCommissionModel
    )
    
    # Test different slippage models
    models = {
        "no_slippage": FixedSlippageModel(0.0),
        "fixed_5_cents": FixedSlippageModel(0.05),
        "percentage_10bps": PercentageSlippageModel(10),  # 10 bps
    }
    
    commission_model = PerShareCommissionModel(0.01, 1.0)
    market_price = 100.0
    order = Order(symbol="TEST", side="BUY", qty=100)
    
    results = {}
    
    for name, slippage_model in models.items():
        engine = ExecutionEngine(
            slippage_model=slippage_model,
            commission_model=commission_model
        )
        
        fill = engine.execute_order(order, market_price)
        results[name] = {
            "fill_price": fill.price,
            "slippage_cost": fill.price - market_price,
            "commission": fill.commission
        }
    
    # Print comparison
    print("\nSlippage Model Comparison:")
    for name, result in results.items():
        print(f"{name:20}: Price=${result['fill_price']:.4f}, "
              f"Slippage=${result['slippage_cost']:.4f}, "
              f"Commission=${result['commission']:.2f}")
    
    # Verify slippage impacts (with floating point tolerance)
    assert abs(results["no_slippage"]["slippage_cost"] - 0.0) < 0.0001
    assert abs(results["fixed_5_cents"]["slippage_cost"] - 0.05) < 0.0001
    assert abs(results["percentage_10bps"]["slippage_cost"] - 0.10) < 0.0001  # 10 bps of $100
    
    return results


def test_volume_impact_on_execution():
    """Test how trade volume affects execution quality"""
    
    from enhancements_strategy import (
        Order, ExecutionEngine, VolumeBasedSlippageModel, PerShareCommissionModel
    )
    
    # Volume-based slippage tiers
    slippage_tiers = [
        {"adv_threshold": 0, "bps": 5},          # 5 bps for small trades
        {"adv_threshold": 500_000, "bps": 10},   # 10 bps for medium trades  
        {"adv_threshold": 2_000_000, "bps": 20}  # 20 bps for large trades
    ]
    
    slippage_model = VolumeBasedSlippageModel(slippage_tiers)
    commission_model = PerShareCommissionModel(0.01, 1.0)
    
    engine = ExecutionEngine(
        slippage_model=slippage_model,
        commission_model=commission_model
    )
    
    market_price = 100.0
    order = Order(symbol="TEST", side="BUY", qty=1000)
    
    # Test different volume scenarios
    volumes = [100_000, 1_000_000, 5_000_000]  # Small, medium, large
    results = {}
    
    for volume in volumes:
        fill = engine.execute_order(order, market_price, volume)
        slippage_bps = (fill.price - market_price) / market_price * 10000
        
        results[volume] = {
            "fill_price": fill.price,
            "slippage_bps": slippage_bps,
            "commission": fill.commission
        }
    
    print("\nVolume Impact on Execution:")
    for volume, result in results.items():
        print(f"Volume {volume:,}: Price=${result['fill_price']:.4f}, "
              f"Slippage={result['slippage_bps']:.1f}bps, "
              f"Commission=${result['commission']:.2f}")
    
    # Verify volume impact - higher volume should have higher slippage
    assert results[100_000]["slippage_bps"] < results[1_000_000]["slippage_bps"]
    assert results[1_000_000]["slippage_bps"] < results[5_000_000]["slippage_bps"]
    
    return results


if __name__ == "__main__":
    print("Testing realistic vs perfect execution...")
    execution_comparison = test_realistic_vs_perfect_execution()
    
    print("\nTesting slippage model impact...")
    slippage_comparison = test_slippage_impact_on_fills()
    
    print("\nTesting volume impact...")
    volume_impact = test_volume_impact_on_execution()
    
    print("\n" + "="*60)
    print("EXECUTION REALISM SUMMARY")
    print("="*60)
    
    cost_difference = execution_comparison["perfect_equity"] - execution_comparison["realistic_equity"]
    print(f"Trading cost impact: ${cost_difference:.2f}")
    print(f"Commission component: ${execution_comparison['commission_cost']:.2f}")
    print(f"Slippage component: ${cost_difference - execution_comparison['commission_cost']:.2f}")
    
    print(f"\nSlippage models tested: {len(slippage_comparison)}")
    print(f"Volume scenarios tested: {len(volume_impact)}")
    
    print("\n✅ All realistic execution integration tests passed!")