"""
Tests for the execution interface with PaperBroker and Alpha Vantage integration.
"""

import asyncio
import pytest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtesting.brokers.paper import PaperBroker
from backtesting.brokers.base import BrokerOrder, OrderSide, OrderType
from backtesting.data_providers.mock_alpha_vantage import MockAlphaVantageDataProvider
from backtesting.execution.live_engine import LiveTradingEngine, SimpleTradingStrategy


@pytest.mark.asyncio
async def test_paper_broker_basic_functionality():
    """Test basic PaperBroker functionality."""
    broker = PaperBroker("TEST_ACCOUNT", initial_cash=50000.0)
    
    # Test connection
    assert await broker.connect() == True
    assert broker.is_connected == True
    
    # Test account info
    account_info = await broker.get_account_info()
    assert account_info.account_id == "TEST_ACCOUNT"
    assert account_info.cash_balance == 50000.0
    assert account_info.total_value == 50000.0
    
    # Test placing an order
    order = BrokerOrder(
        symbol="TEST",
        quantity=100,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        price=10.0
    )
    
    order_id = await broker.place_order(order)
    assert order_id is not None
    assert order_id.startswith("PAPER_")
    
    # Check that position was created
    positions = await broker.get_positions()
    assert len(positions) == 1
    assert positions[0].symbol == "TEST"
    assert positions[0].quantity == 100
    assert positions[0].average_price == 10.0
    
    # Check cash was deducted
    account_info = await broker.get_account_info()
    assert account_info.cash_balance == 49000.0  # 50000 - (100 * 10)
    
    await broker.disconnect()


@pytest.mark.asyncio
async def test_paper_broker_sell_order():
    """Test selling functionality."""
    broker = PaperBroker("TEST_ACCOUNT_2", initial_cash=50000.0)
    await broker.connect()
    
    # First buy
    buy_order = BrokerOrder(
        symbol="TEST",
        quantity=100,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        price=10.0
    )
    await broker.place_order(buy_order)
    
    # Then sell
    sell_order = BrokerOrder(
        symbol="TEST",
        quantity=50,
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        price=12.0
    )
    await broker.place_order(sell_order)
    
    # Check position was reduced
    positions = await broker.get_positions()
    assert len(positions) == 1
    assert positions[0].quantity == 50
    
    # Check cash increased
    account_info = await broker.get_account_info()
    expected_cash = 50000.0 - (100 * 10.0) + (50 * 12.0)  # 49600
    assert account_info.cash_balance == expected_cash
    
    await broker.disconnect()


def test_mock_alpha_vantage_provider():
    """Test the mock Alpha Vantage data provider."""
    provider = MockAlphaVantageDataProvider("test_key")
    
    # Test connection
    assert provider.test_connection() == True
    
    # Test price generation
    price1 = provider._generate_price("IBM")
    price2 = provider._generate_price("IBM")
    
    # Prices should be reasonable
    assert 120.0 <= price1 <= 180.0  # Based on base price of 150
    assert 120.0 <= price2 <= 180.0
    
    # Prices should change slightly
    assert price1 != price2


@pytest.mark.asyncio
async def test_mock_alpha_vantage_quote():
    """Test getting quotes from mock provider."""
    provider = MockAlphaVantageDataProvider("test_key")
    
    async with provider as p:
        quote_data = await p.get_quote("IBM")
        assert quote_data is not None
        assert "Global Quote" in quote_data
        
        parsed_quote = p.parse_quote_data(quote_data)
        assert parsed_quote is not None
        assert parsed_quote["symbol"] == "IBM"
        assert isinstance(parsed_quote["price"], float)
        assert parsed_quote["price"] > 0


@pytest.mark.asyncio
async def test_live_trading_engine_integration():
    """Test the full integration with live trading engine."""
    # Create components
    broker = PaperBroker("INTEGRATION_TEST", initial_cash=100000.0)
    data_provider = MockAlphaVantageDataProvider("test_key")
    
    # Create a simple strategy for testing
    class TestStrategy:
        def __init__(self):
            self.call_count = 0
            
        def on_start(self):
            pass
            
        def on_stop(self):
            pass
            
        def on_data(self, symbol, data):
            self.call_count += 1
            # Place a buy order on first call
            if self.call_count == 1:
                return [BrokerOrder(
                    symbol=symbol,
                    quantity=10,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    price=data["price"]
                )]
            return []
    
    strategy = TestStrategy()
    
    # Create engine with very short update interval for testing
    engine = LiveTradingEngine(
        broker=broker,
        data_provider=data_provider,
        symbols=["IBM"],
        update_interval=1  # 1 second for fast testing
    )
    
    # Start engine for a short time
    start_task = asyncio.create_task(engine.start(strategy))
    
    # Let it run for a few seconds
    await asyncio.sleep(3)
    
    # Stop engine
    await engine.stop()
    
    # Cancel task if still running
    if not start_task.done():
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass
    
    # Verify strategy was called
    assert strategy.call_count >= 1
    
    # Verify order was placed
    orders = await broker.get_orders()
    assert len(orders) >= 1
    assert orders[0].symbol == "IBM"
    assert orders[0].side == OrderSide.BUY


def test_broker_swappability():
    """Test that brokers can be swapped easily."""
    from backtesting.brokers.schwab import SchwabBroker
    
    # Both brokers should inherit from the same base class
    paper_broker = PaperBroker("test", 100000)
    schwab_broker = SchwabBroker("test", "client_id", "client_secret")  # Provide required args
    
    # They should have the same interface
    assert hasattr(paper_broker, 'connect')
    assert hasattr(schwab_broker, 'connect')
    assert hasattr(paper_broker, 'place_order')
    assert hasattr(schwab_broker, 'place_order')
    
    # LiveTradingEngine should accept either
    data_provider = MockAlphaVantageDataProvider("test")
    
    engine1 = LiveTradingEngine(paper_broker, data_provider, ["IBM"])
    engine2 = LiveTradingEngine(schwab_broker, data_provider, ["IBM"])
    
    # Both should be valid
    assert engine1.broker == paper_broker
    assert engine2.broker == schwab_broker


if __name__ == "__main__":
    # Run tests manually if not using pytest
    asyncio.run(test_paper_broker_basic_functionality())
    asyncio.run(test_paper_broker_sell_order())
    test_mock_alpha_vantage_provider()
    asyncio.run(test_mock_alpha_vantage_quote())
    asyncio.run(test_live_trading_engine_integration())
    test_broker_swappability()
    print("All tests passed!")