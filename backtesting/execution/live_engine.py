"""Live trading engine for real-time execution."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Protocol, Optional

from ..brokers.base import BaseBroker, BrokerOrder, OrderSide, OrderType
from ..data_providers.alpha_vantage import AlphaVantageDataProvider
from ..metrics.live_aggregator import LiveMetricsAggregator


class LiveStrategy(Protocol):
    """Protocol for live trading strategies."""
    
    def on_data(self, symbol: str, data: dict[str, Any]) -> list[BrokerOrder]:
        """Process new market data and return orders to place."""
        ...

    def on_start(self) -> None:
        """Called when live trading starts."""
        ...

    def on_stop(self) -> None:
        """Called when live trading stops."""
        ...


class LiveTradingEngine:
    """Engine for live trading with real brokers and live data."""

    def __init__(
        self,
        broker: BaseBroker,
        data_provider: AlphaVantageDataProvider,
        symbols: list[str],
        update_interval: int = 60,  # seconds
        enable_metrics: bool = True,
    ):
        self.broker = broker
        self.data_provider = data_provider
        self.symbols = symbols
        self.update_interval = update_interval
        self.is_running = False
        self.strategy: LiveStrategy | None = None
        
        # Metrics tracking
        self.metrics_aggregator: Optional[LiveMetricsAggregator] = None
        if enable_metrics:
            self.metrics_aggregator = LiveMetricsAggregator(broker, update_interval)
        
        # Setup logging
        self.logger = logging.getLogger("LiveTradingEngine")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def start(self, strategy: LiveStrategy) -> None:
        """Start live trading with the given strategy."""
        if self.is_running:
            self.logger.warning("Engine is already running")
            return

        self.strategy = strategy
        self.is_running = True
        
        self.logger.info("Starting live trading engine")
        self.logger.info(f"Symbols: {', '.join(self.symbols)}")
        self.logger.info(f"Update interval: {self.update_interval} seconds")
        
        # Connect to broker
        if not await self.broker.connect():
            self.logger.error("Failed to connect to broker")
            self.is_running = False
            return

        # Test data provider connection
        if not self.data_provider.test_connection():
            self.logger.error("Failed to connect to data provider")
            self.is_running = False
            return

        # Initialize strategy
        self.strategy.on_start()
        
        # Start main trading loop
        await self._trading_loop()

    async def stop(self) -> None:
        """Stop live trading."""
        if not self.is_running:
            return

        self.logger.info("Stopping live trading engine")
        self.is_running = False
        
        if self.strategy:
            self.strategy.on_stop()
            
        await self.broker.disconnect()

    async def _trading_loop(self) -> None:
        """Main trading loop."""
        while self.is_running:
            try:
                # Update market prices in broker if it supports it
                if hasattr(self.broker, 'update_market_prices'):
                    prices = {}
                    for symbol in self.symbols:
                        quote_data = await self.data_provider.get_quote(symbol)
                        if quote_data:
                            parsed_quote = self.data_provider.parse_quote_data(quote_data)
                            if parsed_quote and 'price' in parsed_quote:
                                prices[symbol] = parsed_quote['price']
                    
                    if prices:
                        self.broker.update_market_prices(prices)
                
                # Update metrics if enabled
                if self.metrics_aggregator:
                    await self.metrics_aggregator.update_metrics()
                
                # Get latest data for all symbols
                for symbol in self.symbols:
                    if not self.is_running:
                        break
                        
                    # Get current quote
                    quote_data = await self.data_provider.get_quote(symbol)
                    if quote_data:
                        parsed_quote = self.data_provider.parse_quote_data(quote_data)
                        if parsed_quote and self.strategy:
                            # Process data with strategy
                            orders = self.strategy.on_data(symbol, parsed_quote)
                            
                            # Execute orders
                            for order in orders:
                                await self._execute_order(order)
                    
                    # Small delay between symbols to avoid rate limits
                    await asyncio.sleep(1)
                
                # Wait for next update cycle
                if self.is_running:
                    self.logger.info(f"Waiting {self.update_interval} seconds for next update")
                    await asyncio.sleep(self.update_interval)
                    
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, stopping...")
                break
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(self.update_interval)

    async def _execute_order(self, order: BrokerOrder) -> None:
        """Execute an order through the broker."""
        try:
            order_id = await self.broker.place_order(order)
            if order_id:
                self.logger.info(f"Order placed successfully: {order_id}")
            else:
                self.logger.error("Failed to place order")
        except Exception as e:
            self.logger.error(f"Error executing order: {e}")

    async def get_account_info(self) -> Any:
        """Get current account information."""
        return await self.broker.get_account_info()

    async def get_positions(self) -> Any:
        """Get current positions."""
        return await self.broker.get_positions()

    async def get_orders(self, symbol: str | None = None) -> Any:
        """Get order history."""
        return await self.broker.get_orders(symbol)
    
    def get_current_metrics(self) -> dict[str, Any]:
        """Get current performance metrics."""
        if self.metrics_aggregator:
            return self.metrics_aggregator.get_current_metrics()
        return {}
    
    def get_equity_curve(self) -> Any:
        """Get equity curve data."""
        if self.metrics_aggregator:
            return self.metrics_aggregator.get_equity_curve()
        return None
    
    def export_results(self, output_dir: str = "live_trading_results") -> dict[str, str]:
        """Export trading results to CSV files."""
        files_created = {}
        
        # Export broker data if it supports CSV export
        if hasattr(self.broker, 'export_to_csv'):
            broker_files = self.broker.export_to_csv(output_dir)
            files_created.update(broker_files)
        
        # Export metrics data
        if self.metrics_aggregator:
            metrics_files = self.metrics_aggregator.export_to_csv(output_dir)
            files_created.update(metrics_files)
        
        self.logger.info(f"Exported trading results to {len(files_created)} files")
        return files_created


class SimpleTradingStrategy:
    """Simple example trading strategy for testing."""

    def __init__(self, buy_threshold: float = 0.01, sell_threshold: float = 0.02):
        self.buy_threshold = buy_threshold  # Buy if price drops by this percentage
        self.sell_threshold = sell_threshold  # Sell if price rises by this percentage
        self.previous_prices: dict[str, float] = {}
        self.positions: dict[str, int] = {}  # Track positions
        
        # Setup logging
        self.logger = logging.getLogger("SimpleTradingStrategy")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def on_start(self) -> None:
        """Called when live trading starts."""
        self.logger.info("Simple trading strategy started")

    def on_stop(self) -> None:
        """Called when live trading stops."""
        self.logger.info("Simple trading strategy stopped")

    def on_data(self, symbol: str, data: dict[str, Any]) -> list[BrokerOrder]:
        """Process new market data and return orders to place."""
        current_price = data["price"]
        orders = []
        
        if symbol in self.previous_prices:
            previous_price = self.previous_prices[symbol]
            price_change = (current_price - previous_price) / previous_price
            
            self.logger.info(
                f"{symbol}: {previous_price:.2f} -> {current_price:.2f} "
                f"({price_change:.2%})"
            )
            
            # Check for buy signal (price dropped significantly)
            if price_change <= -self.buy_threshold and self.positions.get(symbol, 0) == 0:
                self.logger.info(f"BUY SIGNAL for {symbol}: Price dropped {price_change:.2%}")
                order = BrokerOrder(
                    symbol=symbol,
                    quantity=10,  # Fixed quantity for demo
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    price=current_price,
                )
                orders.append(order)
                self.positions[symbol] = 10
                
            # Check for sell signal (price rose significantly and we have position)
            elif price_change >= self.sell_threshold and self.positions.get(symbol, 0) > 0:
                self.logger.info(f"SELL SIGNAL for {symbol}: Price rose {price_change:.2%}")
                order = BrokerOrder(
                    symbol=symbol,
                    quantity=self.positions[symbol],
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    price=current_price,
                )
                orders.append(order)
                self.positions[symbol] = 0
        
        # Update price history
        self.previous_prices[symbol] = current_price
        
        return orders