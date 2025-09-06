"""Mock data provider for testing when Alpha Vantage is not accessible."""

import asyncio
import logging
import random
from datetime import datetime
from typing import Any


class MockAlphaVantageDataProvider:
    """Mock data provider that simulates Alpha Vantage API responses."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_prices = {"IBM": 150.0, "AAPL": 175.0, "MSFT": 300.0}
        self.price_history = {}
        
        # Setup logging
        self.logger = logging.getLogger("MockAlphaVantageDataProvider")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    def _generate_price(self, symbol: str) -> float:
        """Generate a realistic price with some random movement."""
        base_price = self.base_prices.get(symbol, 100.0)
        
        if symbol not in self.price_history:
            self.price_history[symbol] = base_price
        
        # Add some random movement (-2% to +2%)
        change_percent = random.uniform(-0.02, 0.02)
        new_price = self.price_history[symbol] * (1 + change_percent)
        
        # Keep price within reasonable bounds
        min_price = base_price * 0.8
        max_price = base_price * 1.2
        new_price = max(min_price, min(max_price, new_price))
        
        self.price_history[symbol] = new_price
        return new_price

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Get mock quote data."""
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        price = self._generate_price(symbol)
        open_price = price * random.uniform(0.99, 1.01)
        high_price = max(price, open_price) * random.uniform(1.0, 1.02)
        low_price = min(price, open_price) * random.uniform(0.98, 1.0)
        volume = random.randint(100000, 5000000)
        previous_close = price * random.uniform(0.98, 1.02)
        change = price - previous_close
        change_percent = f"{(change / previous_close * 100):+.2f}%"
        
        self.logger.info(f"Generated mock quote for {symbol}: ${price:.2f}")
        
        return {
            "Global Quote": {
                "01. symbol": symbol,
                "02. open": f"{open_price:.4f}",
                "03. high": f"{high_price:.4f}",
                "04. low": f"{low_price:.4f}",
                "05. price": f"{price:.4f}",
                "06. volume": str(volume),
                "07. latest trading day": datetime.now().strftime("%Y-%m-%d"),
                "08. previous close": f"{previous_close:.4f}",
                "09. change": f"{change:.4f}",
                "10. change percent": change_percent,
            }
        }

    def parse_quote_data(self, raw_data: dict[str, Any]) -> dict[str, Any] | None:
        """Parse quote data from mock response."""
        quote_key = "Global Quote"
        if quote_key not in raw_data:
            self.logger.error("No quote data found in response")
            return None
            
        quote = raw_data[quote_key]
        try:
            return {
                "symbol": quote["01. symbol"],
                "price": float(quote["05. price"]),
                "open": float(quote["02. open"]),
                "high": float(quote["03. high"]),
                "low": float(quote["04. low"]),
                "volume": int(quote["06. volume"]),
                "latest_trading_day": quote["07. latest trading day"],
                "previous_close": float(quote["08. previous close"]),
                "change": float(quote["09. change"]),
                "change_percent": quote["10. change percent"].rstrip("%"),
                "timestamp": datetime.now(),
            }
        except (KeyError, ValueError) as e:
            self.logger.error(f"Error parsing quote data: {e}")
            return None

    def test_connection(self) -> bool:
        """Test connection (always returns True for mock)."""
        self.logger.info("Mock Alpha Vantage API connection test successful")
        return True

    async def get_daily_data(self, symbol: str) -> dict[str, Any]:
        """Get mock daily data."""
        await asyncio.sleep(0.1)
        
        # Generate some mock daily data
        time_series = {}
        base_price = self.base_prices.get(symbol, 100.0)
        
        for i in range(10):  # Last 10 days
            date = datetime.now().date()
            date_str = date.strftime("%Y-%m-%d")
            
            # Generate OHLCV data
            open_price = base_price * random.uniform(0.98, 1.02)
            close_price = open_price * random.uniform(0.97, 1.03)
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
            low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
            volume = random.randint(500000, 10000000)
            
            time_series[date_str] = {
                "1. open": f"{open_price:.4f}",
                "2. high": f"{high_price:.4f}",
                "3. low": f"{low_price:.4f}",
                "4. close": f"{close_price:.4f}",
                "5. volume": str(volume),
            }
            
            base_price = close_price  # For next day
        
        return {
            "Meta Data": {
                "1. Information": "Daily Prices (open, high, low, close) and Volumes",
                "2. Symbol": symbol,
                "3. Last Refreshed": datetime.now().strftime("%Y-%m-%d"),
                "4. Output Size": "Compact",
                "5. Time Zone": "US/Eastern"
            },
            "Time Series (Daily)": time_series
        }