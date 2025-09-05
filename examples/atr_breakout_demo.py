"""
ATR Breakout Strategy Example

This example demonstrates how to use the ATRBreakoutStrategy class
for backtesting and live trading. It shows:

1. Configuration setup
2. Strategy initialization 
3. Processing market data
4. Monitoring breakouts and risk management
5. Performance analysis

This serves as a reference implementation and template for building
custom breakout strategies.
"""

from fantastic_palm_tree.strategy.atr_breakout import ATRBreakoutStrategy
from fantastic_palm_tree.config import ATRBreakoutConfig
from fantastic_palm_tree.results import BarProcessResult, ExitResult


def demonstrate_atr_breakout_strategy():
    """Demonstrate the ATR breakout strategy with sample market data."""
    
    print("🎯 ATR Breakout Strategy Demo")
    print("=" * 50)
    
    # 1. Create strategy configuration
    print("\n1. Setting up strategy configuration...")
    
    config = ATRBreakoutConfig(
        # ATR settings
        atr_period=14,
        
        # Breakout detection
        breakout={
            "enabled": True,
            "multiplier": 1.0,  # Lower threshold for demo
            "lookback_period": 15,  # Shorter lookback for demo
            "direction": "both",  # Trade both long and short breakouts
            "min_atr_threshold": 0.50,  # Minimum ATR to consider trades
        },
        
        # Risk management
        position_size=1000.0,
        max_risk_per_trade=0.02,  # Risk 2% per trade
        stop_loss_atr_multiplier=2.0,  # Initial stop = 2 * ATR
        
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
    
    print(f"   ✅ Breakout multiplier: {config.breakout['multiplier']}")
    print(f"   ✅ Lookback period: {config.breakout['lookback_period']}")
    print(f"   ✅ Max risk per trade: {config.max_risk_per_trade * 100}%")
    print(f"   ✅ Stop loss multiplier: {config.stop_loss_atr_multiplier}")
    
    # 2. Initialize strategy
    print("\n2. Initializing ATR breakout strategy...")
    
    strategy = ATRBreakoutStrategy(
        config=config,
        commission_rate=0.001,  # 0.1% commission
        slippage=0.02  # $0.02 slippage
    )
    
    print(f"   ✅ Strategy initialized with {config.atr_period}-period ATR")
    
    # 3. Simulate market data - gradual buildup then breakout
    print("\n3. Processing market data...")
    
    # Initial data to build ATR and price history
    initial_bars = [
        # high, low, close, prev_close
        (100.5, 99.2, 100.0, 99.5),   # Building base
        (101.0, 99.8, 100.2, 100.0),
        (100.8, 99.5, 100.1, 100.2),
        (101.2, 99.9, 100.5, 100.1),
        (100.9, 99.7, 100.3, 100.5),
        (101.1, 100.0, 100.8, 100.3),
        (101.3, 100.2, 101.0, 100.8),
        (101.5, 100.5, 101.2, 101.0),
        (101.8, 100.8, 101.5, 101.2),
        (102.0, 101.0, 101.7, 101.5),
        (102.2, 101.2, 101.9, 101.7),
        (102.5, 101.5, 102.1, 101.9),
        (102.8, 101.8, 102.4, 102.1),
        (103.0, 102.0, 102.6, 102.4),
        (103.2, 102.2, 102.8, 102.6),
        (103.5, 102.5, 103.0, 102.8),
        (103.8, 102.8, 103.2, 103.0),
        (104.0, 103.0, 103.5, 103.2),
        (104.2, 103.2, 103.8, 103.5),
        (104.5, 103.5, 104.0, 103.8),  # Bar 20 - establishing range
    ]
    
    print("   Building price history and ATR...")
    for i, (high, low, close, prev_close) in enumerate(initial_bars):
        result: BarProcessResult = strategy.process_bar(high, low, close, prev_close)
        if i % 5 == 0:  # Print every 5th bar
            print(f"   Bar {i+1:2d}: ATR={result.atr:.2f}, Close={close:.2f}")
    
    print(f"   📊 After {len(initial_bars)} bars: ATR={result.atr:.2f}")
    
    # 4. Simulate breakout scenario
    print("\n4. Simulating breakout scenario...")
    
    breakout_bars = [
        # Strong upward breakout
        (107.0, 104.8, 106.5, 104.0),  # Breakout bar! (stronger)
        (108.2, 106.8, 107.8, 106.5),  # Continuation
        (109.5, 107.5, 108.9, 107.8),  # Strong follow-through
        (110.0, 108.2, 109.4, 108.9),  # More upside
        (110.8, 109.0, 110.2, 109.4),  # Peak
        (110.5, 108.8, 109.2, 110.2),  # Pullback starts
        (109.0, 107.5, 108.0, 109.2),  # Deeper pullback
        (108.5, 106.8, 107.2, 108.0),  # Should hit trailing stop
    ]
    
    trade_count = 0
    for i, (high, low, close, prev_close) in enumerate(breakout_bars):
        bar_num = len(initial_bars) + i + 1
        result: BarProcessResult = strategy.process_bar(high, low, close, prev_close)
        
        position_info = strategy.get_position_info()
        
        print(f"   Bar {bar_num:2d}: H={high:.2f} L={low:.2f} C={close:.2f} | "
              f"ATR={result.atr:.2f} | Stop Hit={result.stop_hit}")
        
        if position_info and not result.stop_hit:
            print(f"           Position: Entry={position_info['entry_price']:.2f}, "
                  f"Stop={position_info['stop_price']:.2f}, "
                  f"Bars Held={position_info['bars_held']}")
        
        if result.exit_result:
            trade_count += 1
            exit_res: ExitResult = result.exit_result
            print(f"   🎯 Trade #{trade_count} completed:")
            print(f"      💰 P&L: ${exit_res.pnl:.2f}")
            print(f"      📊 R-Multiple: {exit_res.r_multiple:.2f}")
            print(f"      📋 Reason: {exit_res.reason}")
            print(f"      💸 Commission: ${exit_res.commission:.2f}")
    
    # 5. Show final strategy statistics  
    print("\n5. Final strategy performance...")
    
    stats = strategy.get_stats()
    print(f"   📊 Total bars processed: {stats['total_bars_processed']}")
    print(f"   💰 Total realized P&L: ${stats['realized_pnl']:.2f}")
    print(f"   📈 Current ATR: {stats['current_atr']:.2f}")
    print(f"   🔄 ATR samples: {stats['atr_samples']}")
    
    if stats['current_position']:
        pos = stats['current_position']
        print(f"   📍 Open position: Entry=${pos['entry_price']:.2f}, "
              f"Size={pos['size']:.0f}, Long={pos['is_long']}")
    else:
        print("   📍 No open positions")
    
    print("\n🎉 Demo completed!")
    print("\nThis example demonstrates:")
    print("  • ATR-based breakout detection")
    print("  • Dynamic position sizing based on volatility")
    print("  • Trailing stop risk management")
    print("  • Comprehensive logging and metrics")
    print("  • Type-safe configuration and results")


def demonstrate_configuration_options():
    """Show various configuration options for the ATR breakout strategy."""
    
    print("\n" + "=" * 60)
    print("🔧 Configuration Options Demo")
    print("=" * 60)
    
    # Conservative configuration
    print("\n1. Conservative Breakout Strategy:")
    conservative = ATRBreakoutConfig(
        atr_period=20,  # Longer ATR period
        breakout={
            "multiplier": 2.5,  # Higher threshold
            "lookback_period": 30,  # Longer lookback
            "direction": "long",  # Long only
            "min_atr_threshold": 1.0,  # Higher minimum ATR
        },
        max_risk_per_trade=0.005,  # 0.5% risk per trade
        stop_loss_atr_multiplier=3.0,  # Wider stops
    )
    
    print(f"   • ATR Period: {conservative.atr_period}")
    print(f"   • Breakout Multiplier: {conservative.breakout['multiplier']}")
    print(f"   • Direction: {conservative.breakout['direction']}")
    print(f"   • Risk per Trade: {conservative.max_risk_per_trade * 100}%")
    
    # Aggressive configuration
    print("\n2. Aggressive Breakout Strategy:")
    aggressive = ATRBreakoutConfig(
        atr_period=7,  # Shorter ATR period
        breakout={
            "multiplier": 1.0,  # Lower threshold
            "lookback_period": 10,  # Shorter lookback
            "direction": "both",  # Both directions
            "min_atr_threshold": 0.1,  # Lower minimum ATR
        },
        max_risk_per_trade=0.03,  # 3% risk per trade
        stop_loss_atr_multiplier=1.5,  # Tighter stops
    )
    
    print(f"   • ATR Period: {aggressive.atr_period}")
    print(f"   • Breakout Multiplier: {aggressive.breakout['multiplier']}")
    print(f"   • Direction: {aggressive.breakout['direction']}")
    print(f"   • Risk per Trade: {aggressive.max_risk_per_trade * 100}%")
    
    # Trend following configuration
    print("\n3. Trend Following Configuration:")
    trend_following = ATRBreakoutConfig(
        breakout={
            "multiplier": 1.5,
            "direction": "both",
        },
        exits={
            "trailing": {
                "enabled": True,
                "use_dynamic_atr": True,
                "dynamic_atr_min_samples": 10,  # More samples for smoother trailing
            }
        }
    )
    
    print(f"   • Dynamic ATR: {trend_following.exits['trailing']['use_dynamic_atr']}")
    print(f"   • Min Samples: {trend_following.exits['trailing']['dynamic_atr_min_samples']}")
    print("   • Optimized for trend following with adaptive trailing stops")


if __name__ == "__main__":
    demonstrate_atr_breakout_strategy()
    demonstrate_configuration_options()