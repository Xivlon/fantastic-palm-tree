#!/usr/bin/env python3
"""
Quick validation test for paper trading and metrics functionality.
"""

import asyncio
import sys
import os

sys.path.insert(0, '/home/runner/work/fantastic-palm-tree/fantastic-palm-tree')

from backtesting.brokers.paper import PaperBroker
from backtesting.brokers.base import BrokerOrder, OrderSide, OrderType
from backtesting.execution.bridge import BacktestToLiveBridge


async def test_paper_broker():
    """Test paper broker functionality."""
    print("Testing Paper Broker...")
    
    broker = PaperBroker("TEST_ACCOUNT", initial_cash=10000.0)
    await broker.connect()
    
    # Place a test order
    order = BrokerOrder(
        symbol="TEST",
        side=OrderSide.BUY,
        quantity=10,
        order_type=OrderType.MARKET,
        price=100.0
    )
    order.average_fill_price = 100.0
    
    order_id = await broker.place_order(order)
    assert order_id is not None, "Order placement failed"
    
    # Update prices
    broker.update_market_prices({"TEST": 105.0})
    
    # Get metrics
    metrics = broker.get_portfolio_metrics()
    assert metrics['total_return'] > 0, "Should have positive return"
    assert metrics['unrealized_pnl'] == 50.0, "Should have $50 unrealized profit"
    
    # Export CSV
    files = broker.export_to_csv("/tmp/test_results")
    assert len(files) > 0, "Should export files"
    
    await broker.disconnect()
    print("✓ Paper Broker test passed")


def test_bridge():
    """Test bridge functionality."""
    print("Testing Bridge...")
    
    bridge = BacktestToLiveBridge("test_key")
    
    # Test setup creation
    setup = bridge.create_paper_trading_setup(
        initial_cash=5000.0,
        symbols=["TEST1", "TEST2"]
    )
    
    assert setup['initial_cash'] == 5000.0, "Initial cash should match"
    assert len(setup['symbols']) == 2, "Should have 2 symbols"
    assert setup['broker'] is not None, "Should have broker"
    assert setup['engine'] is not None, "Should have engine"
    
    print("✓ Bridge test passed")


async def main():
    """Run validation tests."""
    print("Paper Trading Validation Tests")
    print("=" * 40)
    
    try:
        await test_paper_broker()
        test_bridge()
        
        print("\n✅ All validation tests passed!")
        print("Paper trading functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)