# Execution Interface Documentation

This document explains how to use the new execution interface with the PaperBroker and Alpha Vantage integration.

## Overview

The execution interface provides a flexible architecture for live trading that supports:

1. **Swappable Brokers**: Easy switching between paper trading and live brokers
2. **Live Data Integration**: Real-time market data from Alpha Vantage
3. **Strategy Framework**: Simple interface for implementing trading strategies
4. **Safe Testing**: Paper broker for risk-free strategy testing

## Quick Start

### 1. Basic Paper Trading Setup

```python
import asyncio
from backtesting.brokers.paper import PaperBroker
from backtesting.data_providers.alpha_vantage import AlphaVantageDataProvider
from backtesting.execution.live_engine import LiveTradingEngine, SimpleTradingStrategy

async def main():
    # Create paper broker with $100,000 starting capital
    broker = PaperBroker("MY_ACCOUNT", initial_cash=100000.0)
    
    # Create data provider with your Alpha Vantage API key
    data_provider = AlphaVantageDataProvider("YOUR_API_KEY")
    
    # Create trading engine
    engine = LiveTradingEngine(
        broker=broker,
        data_provider=data_provider,
        symbols=["IBM", "AAPL"],
        update_interval=60  # Update every 60 seconds
    )
    
    # Create and start strategy
    strategy = SimpleTradingStrategy()
    await engine.start(strategy)

asyncio.run(main())
```

### 2. Switching to Live Broker

To switch from paper trading to live trading with Schwab, simply change the broker:

```python
from backtesting.brokers.schwab import SchwabBroker

# Replace PaperBroker with SchwabBroker
broker = SchwabBroker("ACCOUNT_ID", "CLIENT_ID", "CLIENT_SECRET")

# Everything else stays the same!
engine = LiveTradingEngine(broker, data_provider, symbols, update_interval)
```

## Components

### PaperBroker

The `PaperBroker` simulates trading without real money:

```python
from backtesting.brokers.paper import PaperBroker
from backtesting.brokers.base import BrokerOrder, OrderSide, OrderType

broker = PaperBroker("TEST_ACCOUNT", initial_cash=50000.0)
await broker.connect()

# Place a mock order
order = BrokerOrder(
    symbol="IBM",
    quantity=100,
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    price=150.0
)

order_id = await broker.place_order(order)
print(f"Order placed: {order_id}")

# Check account status
account_info = await broker.get_account_info()
print(f"Cash balance: ${account_info.cash_balance}")

positions = await broker.get_positions()
for pos in positions:
    print(f"{pos.symbol}: {pos.quantity} shares @ ${pos.average_price}")
```

Key features:
- ✅ Logs all orders with detailed information
- ✅ Simulates position tracking and P&L
- ✅ Manages cash balance realistically
- ✅ Provides same interface as live brokers

### Alpha Vantage Data Provider

The data provider fetches live market data:

```python
from backtesting.data_providers.alpha_vantage import AlphaVantageDataProvider

provider = AlphaVantageDataProvider("YOUR_API_KEY")

# Test connection
if provider.test_connection():
    print("✓ Connected to Alpha Vantage")

# Get real-time quote
async with provider as p:
    quote_data = await p.get_quote("IBM")
    parsed = p.parse_quote_data(quote_data)
    print(f"IBM: ${parsed['price']:.2f}")

# Get daily data
daily_data = await p.get_daily_data("IBM")
parsed_daily = p.parse_daily_data(daily_data)
```

Supported endpoints:
- `get_quote()` - Real-time quotes
- `get_daily_data()` - Daily OHLCV data
- `get_intraday_data()` - Intraday data
- `get_latest_price()` - Quick price lookup

### Live Trading Engine

The engine coordinates brokers, data, and strategies:

```python
from backtesting.execution.live_engine import LiveTradingEngine

engine = LiveTradingEngine(
    broker=broker,
    data_provider=data_provider,
    symbols=["IBM", "AAPL", "MSFT"],
    update_interval=30  # seconds
)

# The engine will:
# 1. Connect to broker and data provider
# 2. Fetch live data for all symbols
# 3. Call strategy with new data
# 4. Execute any orders returned by strategy
# 5. Repeat every update_interval seconds
```

### Custom Trading Strategies

Create your own strategy by implementing the `LiveStrategy` protocol:

```python
from backtesting.execution.live_engine import LiveStrategy
from backtesting.brokers.base import BrokerOrder, OrderSide, OrderType

class MyStrategy:
    def __init__(self):
        self.positions = {}
        
    def on_start(self):
        print("Strategy started")
        
    def on_stop(self):
        print("Strategy stopped")
        
    def on_data(self, symbol: str, data: dict) -> list[BrokerOrder]:
        orders = []
        price = data["price"]
        
        # Your trading logic here
        if self.should_buy(symbol, price):
            orders.append(BrokerOrder(
                symbol=symbol,
                quantity=100,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                price=price
            ))
            
        return orders
        
    def should_buy(self, symbol, price):
        # Your buy logic
        return False
```

## Running the Demo

To see everything in action:

```bash
cd /home/runner/work/fantastic-palm-tree/fantastic-palm-tree
python live_trading_demo.py
```

This will demonstrate:
1. Paper broker functionality
2. Alpha Vantage data retrieval  
3. Live trading engine with mock data
4. Complete order lifecycle

## Testing

Run the comprehensive test suite:

```bash
python test_execution_interface.py
```

Tests cover:
- PaperBroker order execution
- Data provider functionality
- Live trading engine integration
- Broker swappability

## Configuration

### Environment Variables

```bash
export ALPHA_VANTAGE_API_KEY="your_api_key_here"
export SCHWAB_CLIENT_ID="your_client_id"
export SCHWAB_CLIENT_SECRET="your_client_secret"
```

### Logging Configuration

```python
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or configure specific loggers
logging.getLogger("PaperBroker").setLevel(logging.DEBUG)
logging.getLogger("AlphaVantageDataProvider").setLevel(logging.INFO)
```

## Best Practices

### 1. Always Test with Paper Broker First

```python
# Test your strategy safely
paper_broker = PaperBroker("TEST", 100000)
# ... develop and test strategy

# Then switch to live trading
live_broker = SchwabBroker("LIVE_ACCOUNT", client_id, client_secret)
```

### 2. Handle API Rate Limits

```python
# Use reasonable update intervals
engine = LiveTradingEngine(
    broker=broker,
    data_provider=data_provider,
    symbols=symbols,
    update_interval=60  # Don't hammer the API
)
```

### 3. Implement Proper Error Handling

```python
class RobustStrategy:
    def on_data(self, symbol, data):
        try:
            # Your trading logic
            return self.generate_orders(symbol, data)
        except Exception as e:
            logger.error(f"Strategy error for {symbol}: {e}")
            return []  # Return empty list on error
```

### 4. Monitor Resource Usage

```python
# Check account status regularly
account_info = await engine.get_account_info()
print(f"Cash: ${account_info.cash_balance}")
print(f"Total: ${account_info.total_value}")

# Review order history
orders = await engine.get_orders()
print(f"Orders placed today: {len(orders)}")
```

## Troubleshooting

### Alpha Vantage API Issues

If you see connection errors:

1. Check your API key
2. Verify internet connectivity
3. Check Alpha Vantage rate limits
4. Use the mock provider for testing:

```python
from backtesting.data_providers.mock_alpha_vantage import MockAlphaVantageDataProvider
data_provider = MockAlphaVantageDataProvider("test_key")
```

### Paper Broker Issues

All paper broker operations are logged. Check logs for:
- Order execution details
- Cash balance changes  
- Position updates
- Error messages

### Live Trading Engine Issues

Common issues:
- Broker connection failures
- Data provider timeouts
- Strategy exceptions
- Network connectivity

Enable debug logging to see detailed execution flow:

```python
logging.getLogger("LiveTradingEngine").setLevel(logging.DEBUG)
```

## Production Deployment

When ready for live trading:

1. ✅ Test thoroughly with PaperBroker
2. ✅ Verify all API credentials
3. ✅ Implement proper monitoring
4. ✅ Set up alerts for failures
5. ✅ Use conservative position sizes initially
6. ✅ Monitor closely for first few days

```python
# Production setup
live_broker = SchwabBroker(account_id, client_id, client_secret)
data_provider = AlphaVantageDataProvider(api_key)

engine = LiveTradingEngine(
    broker=live_broker,
    data_provider=data_provider,  
    symbols=["IBM"],  # Start with one symbol
    update_interval=300  # 5 minutes for production
)

# Your well-tested strategy
strategy = MyProvenStrategy()
await engine.start(strategy)
```

## API Reference

See the individual module documentation for complete API details:

- `backtesting.brokers.paper.PaperBroker`
- `backtesting.brokers.schwab.SchwabBroker`  
- `backtesting.data_providers.alpha_vantage.AlphaVantageDataProvider`
- `backtesting.execution.live_engine.LiveTradingEngine`

The execution interface is now ready for both development and production use!