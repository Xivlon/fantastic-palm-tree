"""Mock data provider for testing when Alpha Vantage is not accessible."""

import asyncio
import logging
import random
from datetime import datetime
from typing import Any


class MockAlphaVantageDataProvider:
    """Mock data provider that simulates Alpha Vantage API responses."""

    def __init__(self, api_key: str):
        # Validate API key (even for mock)
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string")
        if len(api_key.strip()) == 0:
            raise ValueError("API key cannot be empty or whitespace only")
        
        self.api_key = api_key.strip()
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
        
        self.logger.info("MockAlphaVantageDataProvider initialized successfully")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    def _validate_symbol(self, symbol: str) -> str:
        """Validate and normalize symbol parameter."""
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        if not isinstance(symbol, str):
            raise ValueError("Symbol must be a string")
        
        normalized = symbol.strip().upper()
        if len(normalized) == 0:
            raise ValueError("Symbol cannot be empty after trimming")
        if len(normalized) > 10:
            raise ValueError("Symbol is too long (max 10 characters)")
        
        # Basic validation for alphanumeric with dots and dashes
        if not all(c.isalnum() or c in '.-' for c in normalized):
            raise ValueError("Symbol contains invalid characters")
        
        return normalized

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
        try:
            normalized_symbol = self._validate_symbol(symbol)
        except ValueError as e:
            self.logger.error(f"Invalid symbol '{symbol}': {e}")
            return {}
        
        try:
            # Simulate API delay
            await asyncio.sleep(0.1)
            
            price = self._generate_price(normalized_symbol)
            open_price = price * random.uniform(0.99, 1.01)
            high_price = max(price, open_price) * random.uniform(1.0, 1.02)
            low_price = min(price, open_price) * random.uniform(0.98, 1.0)
            volume = random.randint(100000, 5000000)
            previous_close = price * random.uniform(0.98, 1.02)
            change = price - previous_close
            change_percent = f"{(change / previous_close * 100):+.2f}%"
            
            self.logger.info(f"Generated mock quote for {normalized_symbol}: ${price:.2f}")
            
            return {
                "Global Quote": {
                    "01. symbol": normalized_symbol,
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
        except Exception as e:
            self.logger.error(f"Error generating mock quote for {normalized_symbol}: {e}")
            return {}

    def parse_quote_data(self, raw_data: dict[str, Any]) -> dict[str, Any] | None:
        """Parse quote data from mock response."""
        if not raw_data or not isinstance(raw_data, dict):
            self.logger.error("Invalid raw data: not a dictionary")
            return None
        
        quote_key = "Global Quote"
        if quote_key not in raw_data:
            self.logger.error("No quote data found in response")
            return None
            
        quote = raw_data[quote_key]
        if not isinstance(quote, dict):
            self.logger.error("Quote data is not a dictionary")
            return None
            
        try:
            # Validate required fields exist
            required_fields = [
                "01. symbol", "05. price", "02. open", "03. high", "04. low",
                "06. volume", "07. latest trading day", "08. previous close",
                "09. change", "10. change percent"
            ]
            for field in required_fields:
                if field not in quote:
                    raise ValueError(f"Missing field: {field}")
            
            # Parse and validate numeric values
            try:
                price = float(quote["05. price"])
                open_price = float(quote["02. open"])
                high_price = float(quote["03. high"])
                low_price = float(quote["04. low"])
                volume = int(quote["06. volume"])
                previous_close = float(quote["08. previous close"])
                change = float(quote["09. change"])
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid numeric data: {e}")
            
            # Validate price ranges
            if any(price_val <= 0 for price_val in [price, open_price, high_price, low_price, previous_close]):
                self.logger.warning("Non-positive prices detected")
            
            if volume < 0:
                self.logger.warning(f"Negative volume detected: {volume}")
            
            # Parse change percent (remove % sign)
            change_percent_str = quote["10. change percent"].rstrip("%")
            
            return {
                "symbol": quote["01. symbol"],
                "price": price,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "volume": volume,
                "latest_trading_day": quote["07. latest trading day"],
                "previous_close": previous_close,
                "change": change,
                "change_percent": change_percent_str,
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
        try:
            normalized_symbol = self._validate_symbol(symbol)
        except ValueError as e:
            self.logger.error(f"Invalid symbol '{symbol}': {e}")
            return {}
        
        try:
            await asyncio.sleep(0.1)
            
            # Generate some mock daily data
            time_series = {}
            base_price = self.base_prices.get(normalized_symbol, 100.0)
            
            for i in range(10):  # Last 10 days
                date = datetime.now().date()
                date_str = date.strftime("%Y-%m-%d")
                
                # Generate OHLCV data with realistic relationships
                open_price = base_price * random.uniform(0.98, 1.02)
                close_price = open_price * random.uniform(0.97, 1.03)
                high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
                low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
                volume = random.randint(500000, 10000000)
                
                # Ensure prices are positive
                if any(price <= 0 for price in [open_price, close_price, high_price, low_price]):
                    self.logger.warning(f"Generated non-positive price for {normalized_symbol} on {date_str}")
                    continue
                
                time_series[date_str] = {
                    "1. open": f"{open_price:.4f}",
                    "2. high": f"{high_price:.4f}",
                    "3. low": f"{low_price:.4f}",
                    "4. close": f"{close_price:.4f}",
                    "5. volume": str(volume),
                }
                
                base_price = close_price  # For next day
            
            self.logger.info(f"Generated mock daily data for {normalized_symbol}")
            
            return {
                "Meta Data": {
                    "1. Information": "Daily Prices (open, high, low, close) and Volumes",
                    "2. Symbol": normalized_symbol,
                    "3. Last Refreshed": datetime.now().strftime("%Y-%m-%d"),
                    "4. Output Size": "Compact",
                    "5. Time Zone": "US/Eastern"
                },
                "Time Series (Daily)": time_series
            }
        except Exception as e:
            self.logger.error(f"Error generating mock daily data for {normalized_symbol}: {e}")
            return {}

    def parse_daily_data(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse daily data from mock response."""
        if not raw_data or not isinstance(raw_data, dict):
            self.logger.error("Invalid raw data: not a dictionary")
            return []
            
        time_series_key = "Time Series (Daily)"
        if time_series_key not in raw_data:
            self.logger.error("No time series data found in response")
            return []
        
        time_series = raw_data[time_series_key]
        if not isinstance(time_series, dict):
            self.logger.error("Time series data is not a dictionary")
            return []
            
        parsed_data = []
        
        for date_str, values in time_series.items():
            try:
                if not isinstance(values, dict):
                    self.logger.warning(f"Skipping invalid data for {date_str}: not a dictionary")
                    continue
                
                # Validate required fields exist
                required_fields = ["1. open", "2. high", "3. low", "4. close", "5. volume"]
                for field in required_fields:
                    if field not in values:
                        raise ValueError(f"Missing field: {field}")
                
                # Parse and validate timestamp
                try:
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError as e:
                    self.logger.warning(f"Invalid date format {date_str}: {e}")
                    continue
                
                # Parse and validate numeric values
                try:
                    open_price = float(values["1. open"])
                    high_price = float(values["2. high"])
                    low_price = float(values["3. low"])
                    close_price = float(values["4. close"])
                    volume = int(values["5. volume"])
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Invalid numeric data for {date_str}: {e}")
                    continue
                
                # Validate price ranges
                if any(price <= 0 for price in [open_price, high_price, low_price, close_price]):
                    self.logger.warning(f"Non-positive prices for {date_str}")
                    continue
                
                if volume < 0:
                    self.logger.warning(f"Negative volume for {date_str}: {volume}")
                    continue
                
                parsed_data.append({
                    "timestamp": timestamp,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                })
                
            except Exception as e:
                self.logger.error(f"Error parsing data for {date_str}: {e}")
                continue
                
        # Sort by timestamp (newest first)
        parsed_data.sort(key=lambda x: x["timestamp"], reverse=True)
        self.logger.info(f"Successfully parsed {len(parsed_data)} daily data points")
        return parsed_data