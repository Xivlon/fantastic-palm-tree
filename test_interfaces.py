"""
Simple test to verify interface compatibility with existing implementations.

This test verifies that the new minimal interfaces work correctly
and can be implemented by concrete classes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces.strategy import StrategyProtocol, StrategyABC
from interfaces.engine import EngineProtocol, EngineABC
from interfaces.order import OrderProtocol, OrderABC, OrderSide, OrderType, OrderStatus
from interfaces.position import PositionProtocol, PositionABC
from interfaces.trade_result import TradeResultProtocol, TradeResultABC
from interfaces.metrics import MetricsAggregatorProtocol, MetricsAggregatorABC

from typing import Dict, Any
from datetime import datetime


class SimpleStrategy(StrategyABC):
    """Simple strategy implementation for testing."""
    
    def on_data(self, timestamp: str, data: Dict[str, Any]) -> None:
        """Simple strategy that does nothing."""
        pass


class SimpleEngine(EngineABC):
    """Simple engine implementation for testing."""
    
    def run(self, strategy: Any, **kwargs: Any) -> Any:
        """Simple engine that runs strategy lifecycle."""
        strategy.on_start()
        # Simulate some data
        strategy.on_data("2023-01-01", {"price": 100.0})
        strategy.on_finish()
        return "completed"


class SimpleMetricsAggregator(MetricsAggregatorABC):
    """Simple metrics aggregator for testing."""
    
    def calculate_metrics(self, benchmark=None) -> Dict[str, Any]:
        """Calculate basic metrics."""
        basic_metrics = self._calculate_basic_metrics()
        
        # Add some additional metrics
        basic_metrics.update({
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'total_return': 0.0,
        })
        
        return basic_metrics


def test_interfaces():
    """Test that interfaces work correctly."""
    print("Testing interface implementations...")
    
    # Test Strategy
    strategy = SimpleStrategy("TestStrategy")
    assert isinstance(strategy, StrategyProtocol)
    strategy.set_params(param1=10, param2="test")
    strategy.on_start()
    strategy.on_data("2023-01-01", {"price": 100.0})
    strategy.on_finish()
    print("✓ Strategy interface works")
    
    # Test Engine
    engine = SimpleEngine()
    assert isinstance(engine, EngineProtocol)
    result = engine.run(strategy)
    assert result == "completed"
    print("✓ Engine interface works")
    
    # Test Order
    order = OrderABC("AAPL", 100.0, OrderSide.BUY, OrderType.MARKET)
    assert isinstance(order, OrderProtocol)
    assert order.status == OrderStatus.PENDING
    order.fill(150.0)
    assert order.status == OrderStatus.FILLED
    assert order.fill_price == 150.0
    print("✓ Order interface works")
    
    # Test Position
    position = PositionABC("AAPL", 100.0, 150.0)
    assert isinstance(position, PositionProtocol)
    pnl = position.unrealized_pnl(160.0)
    assert pnl == 1000.0  # 100 shares * $10 profit
    position.update_position(50.0, 155.0)  # Add 50 shares at $155
    assert abs(position.entry_price - 151.67) < 0.01  # Average price
    print("✓ Position interface works")
    
    # Test TradeResult
    trade = TradeResultABC("AAPL", 150.0, 100.0, True)
    assert isinstance(trade, TradeResultProtocol)
    trade.close_trade(160.0)
    assert trade.gross_pnl() == 1000.0  # 100 * (160 - 150)
    assert trade.net_pnl() == 1000.0  # No commission set
    assert trade.r_multiple(500.0) == 2.0  # $1000 profit / $500 risk
    print("✓ TradeResult interface works")
    
    # Test MetricsAggregator
    aggregator = SimpleMetricsAggregator()
    assert isinstance(aggregator, MetricsAggregatorProtocol)
    aggregator.add_trade_result(trade)
    aggregator.add_equity_point("2023-01-01", 100000.0)
    
    metrics = aggregator.calculate_metrics()
    assert metrics['total_trades'] == 1
    assert metrics['winning_trades'] == 1
    assert metrics['total_pnl'] == 1000.0
    print("✓ MetricsAggregator interface works")
    
    print("\n✅ All interface tests passed!")


if __name__ == "__main__":
    test_interfaces()