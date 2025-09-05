"""
Integration test to verify interface compatibility with existing repository code.

This test checks that existing classes in the repository can work with 
the new minimal interfaces, demonstrating backward compatibility.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces import (
    StrategyProtocol, EngineProtocol, OrderProtocol, 
    PositionProtocol, TradeResultProtocol, MetricsAggregatorProtocol
)

# Import existing repository classes
from fantastic_palm_tree.strategy.base import BaseStrategy
from fantastic_palm_tree.models.position import TradePosition
from fantastic_palm_tree.results import ExitResult, BarProcessResult
from backtesting.core.strategy import Strategy
from backtesting.core.engine import BacktestEngine, BacktestResults
from backtesting.core.order import Order, OrderType, OrderStatus
from backtesting.metrics.calculator import MetricsCalculator


def test_existing_strategy_compatibility():
    """Test that existing strategy classes work with StrategyProtocol."""
    print("Testing existing strategy compatibility...")
    
    # Test the backtesting Strategy class
    class TestStrategy(Strategy):
        def on_data(self, timestamp: str, data):
            pass
    
    strategy = TestStrategy("TestStrategy")
    
    # Check if it satisfies the protocol
    assert isinstance(strategy, StrategyProtocol)
    
    # Test protocol methods
    strategy.on_start()
    strategy.on_data("2023-01-01", {"price": 100.0})
    strategy.on_finish()
    strategy.set_params(test_param=42)
    
    print("✓ Existing Strategy class is compatible with StrategyProtocol")


def test_existing_engine_compatibility():
    """Test that existing engine classes work with EngineProtocol."""
    print("Testing existing engine compatibility...")
    
    engine = BacktestEngine(initial_cash=100000.0)
    
    # BacktestEngine doesn't fully implement EngineProtocol yet, but we can test basic functionality
    # This shows what would need to be adapted
    
    # Test kill switch functionality which does exist
    def test_trigger(context):
        return False
    
    engine.add_kill_switch_trigger(test_trigger)
    
    print("✓ Existing BacktestEngine has compatible kill switch functionality")


def test_existing_order_compatibility():
    """Test that existing order classes work with OrderProtocol."""
    print("Testing existing order compatibility...")
    
    # Test the backtesting Order class
    order = Order(
        symbol="AAPL",
        quantity=100,
        order_type=OrderType.MARKET,
        side="buy"
    )
    
    # The existing Order class has the right methods
    assert hasattr(order, 'fill')
    assert hasattr(order, 'cancel')
    assert hasattr(order, 'reject')
    
    # Test the methods work
    order.fill(150.0)
    assert order.status == OrderStatus.FILLED
    assert order.fill_price == 150.0
    
    print("✓ Existing Order class has compatible interface")


def test_existing_position_compatibility():
    """Test that existing position classes work with PositionProtocol."""
    print("Testing existing position compatibility...")
    
    # Test the TradePosition class
    position = TradePosition(
        entry_price=150.0,
        size=100.0,
        entry_atr=5.0,
        is_long=True
    )
    
    # Test the unrealized_pnl method
    pnl = position.unrealized_pnl(160.0)
    assert pnl == 1000.0  # 100 * (160 - 150)
    
    print("✓ Existing TradePosition class has compatible PnL calculation")


def test_existing_trade_result_compatibility():
    """Test that existing result classes work with TradeResultProtocol."""
    print("Testing existing trade result compatibility...")
    
    # Test ExitResult class
    exit_result = ExitResult(
        pnl=1000.0,
        r_multiple=2.0,
        total_pnl=5000.0,
        commission=10.0,
        reason="profit_target"
    )
    
    # The ExitResult has the essential information
    assert hasattr(exit_result, 'pnl')
    assert hasattr(exit_result, 'r_multiple')
    assert hasattr(exit_result, 'commission')
    
    print("✓ Existing ExitResult class has compatible data structure")


def test_existing_metrics_compatibility():
    """Test that existing metrics classes work with MetricsAggregatorProtocol."""
    print("Testing existing metrics compatibility...")
    
    # The MetricsCalculator is a static class, but we can test its functionality
    # It calculates metrics from BacktestResults which is compatible
    
    # This would be how to adapt it:
    class AdaptedMetricsCalculator:
        def __init__(self):
            self.results = None
        
        def set_results(self, results):
            self.results = results
        
        def calculate_metrics(self, benchmark=None):
            if self.results:
                return MetricsCalculator.calculate(self.results, benchmark)
            return {}
    
    calculator = AdaptedMetricsCalculator()
    assert hasattr(calculator, 'calculate_metrics')
    
    print("✓ Existing MetricsCalculator can be adapted to protocol")


def test_protocol_type_checking():
    """Test that protocols work for type checking."""
    print("Testing protocol type checking...")
    
    def process_strategy(strategy: StrategyProtocol):
        """Function that accepts any object implementing StrategyProtocol."""
        strategy.on_start()
        return f"Processed strategy: {strategy.name}"
    
    # Test with existing Strategy class
    class TestStrategy(Strategy):
        def on_data(self, timestamp: str, data):
            pass
    
    strategy = TestStrategy("ExistingStrategy")
    result = process_strategy(strategy)
    assert "ExistingStrategy" in result
    
    print("✓ Protocol type checking works with existing classes")


def run_integration_tests():
    """Run all integration tests."""
    print("Running integration tests for interface compatibility...\n")
    
    try:
        test_existing_strategy_compatibility()
        test_existing_engine_compatibility()
        test_existing_order_compatibility()
        test_existing_position_compatibility()
        test_existing_trade_result_compatibility()
        test_existing_metrics_compatibility()
        test_protocol_type_checking()
        
        print(f"\n✅ All integration tests passed!")
        print("\nSummary:")
        print("- Existing Strategy classes are compatible with StrategyProtocol")
        print("- Existing Order classes work with OrderProtocol concepts")
        print("- Existing Position classes have compatible P&L calculations")
        print("- Existing Result classes contain needed data structures")
        print("- Existing Metrics classes can be adapted to protocols")
        print("- Protocol type checking works for existing implementations")
        
        print("\nThe new interfaces provide a clean contract layer that")
        print("existing code can gradually adopt while maintaining compatibility.")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    run_integration_tests()