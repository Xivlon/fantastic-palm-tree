"""
Test integration of realistic execution with EnhancedStrategy.
"""

from enhancements_strategy import EnhancedStrategy, StrategyConfig


def test_enhanced_strategy_with_realistic_execution():
    """Test EnhancedStrategy using realistic execution models"""
    
    # Create strategy config
    config = StrategyConfig(
        exits={
            "trailing": {
                "enabled": False,  # Disable for simpler testing
                "type": "atr",
                "use_dynamic_atr": False,
            }
        }
    )
    
    strategy = EnhancedStrategy(config)
    
    # Configure realistic execution
    slippage_config = {"bps": 20}  # 20 basis points
    commission_config = {"per_share": 0.01, "min_commission": 1.0}
    
    strategy.configure_realistic_execution(
        slippage_config=slippage_config,
        commission_config=commission_config,
        spread_bps=10  # 10 bps spread
    )
    
    # Add some ATR data
    strategy.update_atr(high=102, low=98, prev_close=100)
    strategy.update_atr(high=104, low=99, prev_close=101)
    
    # Enter position with realistic execution
    entry_price = 100.0
    position_size = 1000.0
    
    success = strategy.enter_position(entry_price, position_size, is_long=True)
    assert success
    assert strategy.position is not None
    
    # Check that realistic execution was applied
    # Entry price should be higher than market due to spread + slippage
    expected_min_price = entry_price + (entry_price * 0.0015)  # spread/2 + slippage
    assert strategy.position.entry_price > expected_min_price
    
    # Check that commission was deducted from PnL
    assert strategy.pnl < 0  # Should be negative due to commission
    
    initial_pnl = strategy.pnl
    entry_fill_price = strategy.position.entry_price
    
    print(f"Entry price: ${entry_fill_price:.4f} (market: ${entry_price:.2f})")
    print(f"Entry cost (spread + slippage): ${entry_fill_price - entry_price:.4f}")
    print(f"PnL after entry: ${initial_pnl:.2f}")
    
    # Exit position
    exit_price = 105.0
    exit_result = strategy.exit_position(exit_price, reason="test_exit")
    
    assert strategy.position is None  # Position should be closed
    assert exit_result["pnl"] > 0     # Should be profitable trade
    assert exit_result["commission"] > 0  # Should have commission
    
    print(f"Exit commission: ${exit_result['commission']:.2f}")
    print(f"Position PnL: ${exit_result['pnl']:.2f}")
    print(f"Total PnL: ${exit_result['total_pnl']:.2f}")
    
    return {
        "entry_cost": entry_fill_price - entry_price,
        "entry_commission": -initial_pnl,  # Initial negative PnL is entry commission
        "exit_commission": exit_result["commission"],
        "position_pnl": exit_result["pnl"],
        "total_pnl": exit_result["total_pnl"]
    }


def test_enhanced_strategy_backward_compatibility():
    """Test that legacy fee setting still works"""
    
    config = StrategyConfig()
    strategy = EnhancedStrategy(config)
    
    # Use legacy fee setting
    strategy.set_fees(commission_rate=0.001, slippage=0.05)
    
    # Add ATR data
    strategy.update_atr(high=102, low=98, prev_close=100)
    
    # Enter and exit position
    strategy.enter_position(100.0, 1000.0, is_long=True)
    assert strategy.position is not None
    
    # With legacy execution, price should be exactly market + slippage
    expected_price = 100.0 + 0.05  # market + slippage
    assert abs(strategy.position.entry_price - expected_price) < 0.0001
    
    exit_result = strategy.exit_position(105.0)
    
    # Legacy commission calculation: commission = size * price * rate
    expected_commission = 1000.0 * (105.0 - 0.05) * 0.001
    assert abs(exit_result["commission"] - expected_commission) < 0.01
    
    print("✅ Backward compatibility test passed")


def test_enhanced_strategy_comparison():
    """Compare realistic vs legacy execution in EnhancedStrategy"""
    
    config = StrategyConfig()
    
    # Test realistic execution
    realistic_strategy = EnhancedStrategy(config)
    realistic_strategy.configure_realistic_execution(
        slippage_config={"bps": 30},
        commission_config={"per_share": 0.02, "min_commission": 2.0},
        spread_bps=15
    )
    
    # Test legacy execution  
    legacy_strategy = EnhancedStrategy(config)
    legacy_strategy.set_fees(commission_rate=0.002, slippage=0.05)
    
    # Add ATR data to both
    for strategy in [realistic_strategy, legacy_strategy]:
        strategy.update_atr(high=102, low=98, prev_close=100)
        strategy.update_atr(high=104, low=99, prev_close=101)
    
    # Execute same trade on both
    entry_price = 100.0
    exit_price = 103.0
    size = 500.0
    
    # Realistic execution
    realistic_strategy.enter_position(entry_price, size, is_long=True)
    realistic_exit = realistic_strategy.exit_position(exit_price)
    
    # Legacy execution
    legacy_strategy.enter_position(entry_price, size, is_long=True)
    legacy_exit = legacy_strategy.exit_position(exit_price)
    
    print(f"\nExecution Comparison:")
    print(f"Realistic entry price: ${realistic_strategy.position or 'N/A'}")
    print(f"Legacy entry price: ${legacy_strategy.position or 'N/A'}")
    print(f"Realistic total PnL: ${realistic_exit['total_pnl']:.2f}")
    print(f"Legacy total PnL: ${legacy_exit['total_pnl']:.2f}")
    
    # Both should be profitable but different due to execution costs
    assert realistic_exit["total_pnl"] > 0
    assert legacy_exit["total_pnl"] > 0
    assert realistic_exit["total_pnl"] != legacy_exit["total_pnl"]
    
    return {
        "realistic_pnl": realistic_exit["total_pnl"],
        "legacy_pnl": legacy_exit["total_pnl"],
        "execution_difference": abs(realistic_exit["total_pnl"] - legacy_exit["total_pnl"])
    }


if __name__ == "__main__":
    print("Testing EnhancedStrategy with realistic execution...")
    realistic_results = test_enhanced_strategy_with_realistic_execution()
    
    print("\nTesting backward compatibility...")
    test_enhanced_strategy_backward_compatibility()
    
    print("\nTesting execution comparison...")
    comparison_results = test_enhanced_strategy_comparison()
    
    print(f"\n" + "="*60)
    print("ENHANCED STRATEGY INTEGRATION SUMMARY")
    print("="*60)
    print(f"Realistic execution entry cost: ${realistic_results['entry_cost']:.4f}")
    print(f"Total commission paid: ${realistic_results['entry_commission'] + realistic_results['exit_commission']:.2f}")
    print(f"Final PnL: ${realistic_results['total_pnl']:.2f}")
    print(f"Execution method difference: ${comparison_results['execution_difference']:.2f}")
    
    print("\n✅ All EnhancedStrategy integration tests passed!")