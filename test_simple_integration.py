"""
Simple integration test to verify interface compatibility with existing repository code.

This test checks core compatibility without external dependencies.
"""

import sys
import os
# NOTE: Removed fragile sys.path manipulation. Run this test with `python -m test_simple_integration` from the project root.

from interfaces import (
    StrategyProtocol, OrderProtocol, PositionProtocol, TradeResultProtocol
)

# Import existing repository classes that don't require pandas
from fantastic_palm_tree.strategy.base import BaseStrategy
from fantastic_palm_tree.models.position import TradePosition
from fantastic_palm_tree.results import ExitResult, BarProcessResult


def test_base_strategy_compatibility():
    """Test that BaseStrategy concepts align with StrategyProtocol."""
    print("Testing BaseStrategy compatibility...")
    
    # BaseStrategy is an ABC, so we create a concrete implementation
    class TestStrategy(BaseStrategy):
        def __init__(self):
            self.position = None
            self.name = "TestStrategy"
            self.params = {}
        
        def enter_position(self, price: float, size: float, is_long: bool = True) -> bool:
            return True
        
        def exit_position(self, price: float, reason: str = "manual"):
            return ExitResult(pnl=100.0, r_multiple=1.0, total_pnl=100.0, commission=0.0, reason=reason)
        
        def process_bar(self, high: float, low: float, close: float, prev_close: float):
            return BarProcessResult(atr=2.0, stop_hit=False, exit_result=None)
        
        # Add StrategyProtocol methods
        def on_data(self, timestamp: str, data):
            """Adapter method for StrategyProtocol."""
            if 'high' in data and 'low' in data and 'close' in data:
                prev_close = data.get('prev_close', data['close'])
                return self.process_bar(data['high'], data['low'], data['close'], prev_close)
        
        def on_start(self):
            """Initialize strategy."""
            pass
        
        def on_finish(self):
            """Cleanup strategy."""
            pass
        
        def set_params(self, **params):
            """Set strategy parameters."""
            self.params.update(params)
    
    strategy = TestStrategy()
    
    # Test that it can work as StrategyProtocol
    assert hasattr(strategy, 'on_data')
    assert hasattr(strategy, 'on_start')
    assert hasattr(strategy, 'on_finish')
    assert hasattr(strategy, 'set_params')
    
    # Test the methods
    strategy.on_start()
    strategy.on_data("2023-01-01", {"high": 155.0, "low": 145.0, "close": 150.0})
    strategy.on_finish()
    strategy.set_params(test_param=42)
    
    print("✓ BaseStrategy can be adapted to work with StrategyProtocol")


def test_trade_position_compatibility():
    """Test that TradePosition aligns with PositionProtocol concepts."""
    print("Testing TradePosition compatibility...")
    
    position = TradePosition(
        entry_price=150.0,
        size=100.0,
        entry_atr=5.0,
        is_long=True
    )
    
    # Test compatibility with PositionProtocol concepts
    assert hasattr(position, 'entry_price')
    assert hasattr(position, 'size')
    assert hasattr(position, 'unrealized_pnl')
    
    # Test the unrealized_pnl method
    pnl = position.unrealized_pnl(160.0)
    expected_pnl = 100.0 * (160.0 - 150.0)  # size * (current - entry)
    assert pnl == expected_pnl
    
    # Test short position
    short_position = TradePosition(
        entry_price=150.0,
        size=100.0,
        entry_atr=5.0,
        is_long=False
    )
    
    short_pnl = short_position.unrealized_pnl(140.0)
    expected_short_pnl = 100.0 * (150.0 - 140.0)  # size * (entry - current) for short
    assert short_pnl == expected_short_pnl
    
    print("✓ TradePosition is compatible with PositionProtocol concepts")


def test_exit_result_compatibility():
    """Test that ExitResult aligns with TradeResultProtocol concepts."""
    print("Testing ExitResult compatibility...")
    
    exit_result = ExitResult(
        pnl=1000.0,
        r_multiple=2.0,
        total_pnl=5000.0,
        commission=10.0,
        reason="profit_target"
    )
    
    # Test compatibility with TradeResultProtocol concepts
    assert hasattr(exit_result, 'pnl')
    assert hasattr(exit_result, 'r_multiple')
    assert hasattr(exit_result, 'commission')
    assert hasattr(exit_result, 'reason')
    
    # The ExitResult contains the key data needed for TradeResultProtocol
    assert exit_result.pnl == 1000.0
    assert exit_result.r_multiple == 2.0
    assert exit_result.commission == 10.0
    
    print("✓ ExitResult contains data compatible with TradeResultProtocol")


def test_interface_adaptation_patterns():
    """Test patterns for adapting existing classes to interfaces."""
    print("Testing interface adaptation patterns...")
    
    # Pattern 1: Wrapper class
    class PositionAdapter:
        """Adapter to make TradePosition work with PositionProtocol."""
        
        def __init__(self, trade_position: TradePosition):
            self._position = trade_position
        
        @property
        def symbol(self):
            return getattr(self._position, 'symbol', 'UNKNOWN')
        
        @property
        def size(self):
            return self._position.size if self._position.is_long else -self._position.size
        
        @property
        def entry_price(self):
            return self._position.entry_price
        
        def unrealized_pnl(self, current_price: float) -> float:
            return self._position.unrealized_pnl(current_price)
        
        def update_position(self, quantity: float, price: float) -> None:
            # This would need more complex logic to update TradePosition
            pass
        
        def close_position(self, price: float) -> float:
            return self.unrealized_pnl(price)
    
    # Test the adapter
    trade_pos = TradePosition(entry_price=100.0, size=50.0, entry_atr=2.0, is_long=True)
    adapter = PositionAdapter(trade_pos)
    
    assert adapter.entry_price == 100.0
    assert adapter.size == 50.0  # Positive for long
    assert adapter.unrealized_pnl(110.0) == 500.0
    
    print("✓ Adapter pattern works for interface compatibility")


def run_simple_integration_tests():
    """Run integration tests without external dependencies."""
    print("Running simple integration tests for interface compatibility...\n")
    
    try:
        test_base_strategy_compatibility()
        test_trade_position_compatibility()
        test_exit_result_compatibility()
        test_interface_adaptation_patterns()
        
        print(f"\n✅ All simple integration tests passed!")
        print("\nSummary:")
        print("- BaseStrategy can be adapted to work with StrategyProtocol")
        print("- TradePosition aligns well with PositionProtocol concepts")
        print("- ExitResult contains data compatible with TradeResultProtocol")
        print("- Adapter patterns enable interface compatibility")
        
        print("\nThe new interfaces provide a clean contract layer that")
        print("existing code can adopt through adaptation patterns.")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    run_simple_integration_tests()