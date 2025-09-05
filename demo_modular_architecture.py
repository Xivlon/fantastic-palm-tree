#!/usr/bin/env python3
"""
Demonstration of the modular strategy architecture.

This script shows how to use the new modular components:
- EnhancedStrategy with typed results
- TrailingStopEngine with configurable behavior
- Typed dataclasses for results
- Configuration with validation
"""

from fantastic_palm_tree.config import StrategyConfig
from fantastic_palm_tree.results import BarProcessResult, ExitResult
from fantastic_palm_tree.strategy.enhanced import EnhancedStrategy


def demonstrate_modular_architecture():
    """Demonstrate the key features of the modular architecture."""
    print("🌴 Fantastic Palm Tree - Modular Strategy Demo")
    print("=" * 50)

    # 1. Configuration with validation
    print("\n1. Creating strategy configuration...")
    config = StrategyConfig(
        atr_period=14,
        exits={
            "trailing": {
                "enabled": True,
                "type": "atr",
                "use_dynamic_atr": True,
                "dynamic_atr_min_samples": 3,
            }
        },
    )
    print(f"   ✅ Configuration created: ATR period={config.atr_period}")
    print(f"   ✅ Trailing config: {config.trailing}")

    # 2. Strategy instantiation
    print("\n2. Creating enhanced strategy...")
    strategy = EnhancedStrategy(config)
    strategy.set_fees(commission_rate=0.001, slippage=0.01)
    print("   ✅ Strategy created with fees configured")

    # 3. Processing bars with typed results
    print("\n3. Processing market data...")

    # Simulate a sequence of bars
    bars = [
        (102.0, 98.5, 101.0, 99.0),  # high, low, close, prev_close
        (103.5, 100.0, 102.5, 101.0),
        (105.0, 101.8, 104.2, 102.5),
        (106.0, 103.0, 105.5, 104.2),
    ]

    for i, (high, low, close, prev_close) in enumerate(bars):
        result: BarProcessResult = strategy.process_bar(high, low, close, prev_close)
        print(f"   Bar {i + 1}: ATR={result.atr:.2f}, Stop Hit={result.stop_hit}")

    # 4. Enter a position
    print("\n4. Entering a position...")
    try:
        success = strategy.enter_position(price=105.0, size=1000.0, is_long=True)
        print(f"   ✅ Position entered: {success}")

        # Show position info
        if strategy.position:
            pos = strategy.position
            print(
                f"   Position: price={pos.entry_price:.2f}, size={pos.size}, atr={pos.entry_atr:.2f}"
            )
    except Exception as e:
        print(f"   ❌ Error entering position: {e}")

    # 5. Process more bars with position active
    print("\n5. Processing bars with active position...")

    trailing_bars = [
        (107.0, 104.8, 106.2, 105.5),
        (108.0, 105.0, 107.5, 106.2),
        (109.0, 106.0, 108.0, 107.5),
        (109.5, 105.0, 105.5, 108.0),  # This should trigger stop
    ]

    for i, (high, low, close, prev_close) in enumerate(trailing_bars):
        result: BarProcessResult = strategy.process_bar(high, low, close, prev_close)
        print(
            f"   Bar {i + 5}: ATR={result.atr:.2f}, Stop Hit={result.stop_hit}, Stop Price={result.stop_price}"
        )

        if result.exit_result:
            exit_res: ExitResult = result.exit_result
            print(
                f"   🎯 Position exited: PnL=${exit_res.pnl:.2f}, R-Multiple={exit_res.r_multiple:.2f}"
            )
            print(
                f"      Reason: {exit_res.reason}, Commission: ${exit_res.commission:.2f}"
            )
            break

    # 6. Show final state
    print("\n6. Final strategy state...")
    print(f"   Total realized PnL: ${strategy.get_realized_pnl():.2f}")
    print(f"   Current position: {strategy.position}")

    print("\n🎉 Demo completed! The modular architecture provides:")
    print("   • Typed dataclasses for better type safety")
    print("   • Modular components for easier testing")
    print("   • Configuration validation")
    print("   • Extensible trailing stop engine")
    print("   • Clean separation of concerns")


if __name__ == "__main__":
    demonstrate_modular_architecture()
