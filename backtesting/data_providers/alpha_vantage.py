"""Alpha Vantage data provider for live market data."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

import aiohttp
import requests


class AlphaVantageDataProvider:
    """Data provider for Alpha Vantage API."""

    def __init__(self, api_key: str):
        # Validate API key
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string")
        if len(api_key.strip()) == 0:
            raise ValueError("API key cannot be empty or whitespace only")
        
        self.api_key = api_key.strip()
        self.base_url = "https://www.alphavantage.co/query"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Setup logging
        self.logger = logging.getLogger("AlphaVantageDataProvider")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        self.logger.info("AlphaVantageDataProvider initialized successfully")

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

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

    async def get_daily_data(self, symbol: str) -> dict[str, Any] | None:
        """Get daily time series data for a symbol."""
        try:
            normalized_symbol = self._validate_symbol(symbol)
        except ValueError as e:
            self.logger.error(f"Invalid symbol '{symbol}': {e}")
            return None
        
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": normalized_symbol,
            "apikey": self.api_key,
        }
        
        try:
            if self.session:
                async with self.session.get(self.base_url, params=params, timeout=30) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            # Check for API errors immediately
                            if "Error Message" in data:
                                self.logger.error(f"API Error for {normalized_symbol}: {data['Error Message']}")
                                return None
                            if "Note" in data:
                                self.logger.warning(f"API Note for {normalized_symbol}: {data['Note']}")
                                return None
                            self.logger.info(f"Retrieved daily data for {normalized_symbol}")
                            return data
                        except Exception as json_error:
                            self.logger.error(f"JSON parsing error for {normalized_symbol}: {json_error}")
                            return None
                    else:
                        self.logger.error(f"Error fetching data for {normalized_symbol}: HTTP {response.status}")
                        return None
            else:
                # Fallback to synchronous request
                response = requests.get(self.base_url, params=params, timeout=30)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Check for API errors immediately
                        if "Error Message" in data:
                            self.logger.error(f"API Error for {normalized_symbol}: {data['Error Message']}")
                            return None
                        if "Note" in data:
                            self.logger.warning(f"API Note for {normalized_symbol}: {data['Note']}")
                            return None
                        self.logger.info(f"Retrieved daily data for {normalized_symbol}")
                        return data
                    except Exception as json_error:
                        self.logger.error(f"JSON parsing error for {normalized_symbol}: {json_error}")
                        return None
                else:
                    self.logger.error(f"Error fetching data for {normalized_symbol}: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Exception fetching data for {normalized_symbol}: {e}")
            return None

    async def get_intraday_data(self, symbol: str, interval: str = "5min") -> dict[str, Any] | None:
        """Get intraday time series data for a symbol."""
        try:
            normalized_symbol = self._validate_symbol(symbol)
        except ValueError as e:
            self.logger.error(f"Invalid symbol '{symbol}': {e}")
            return None
        
        # Validate interval parameter
        valid_intervals = ["1min", "5min", "15min", "30min", "60min"]
        if interval not in valid_intervals:
            self.logger.error(f"Invalid interval '{interval}'. Must be one of: {valid_intervals}")
            return None
        
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": normalized_symbol,
            "interval": interval,
            "apikey": self.api_key,
        }
        
        try:
            if self.session:
                async with self.session.get(self.base_url, params=params, timeout=30) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            # Check for API errors immediately
                            if "Error Message" in data:
                                self.logger.error(f"API Error for {normalized_symbol}: {data['Error Message']}")
                                return None
                            if "Note" in data:
                                self.logger.warning(f"API Note for {normalized_symbol}: {data['Note']}")
                                return None
                            self.logger.info(f"Retrieved intraday data for {normalized_symbol} ({interval})")
                            return data
                        except Exception as json_error:
                            self.logger.error(f"JSON parsing error for {normalized_symbol}: {json_error}")
                            return None
                    else:
                        self.logger.error(f"Error fetching intraday data for {normalized_symbol}: HTTP {response.status}")
                        return None
            else:
                # Fallback to synchronous request
                response = requests.get(self.base_url, params=params, timeout=30)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Check for API errors immediately
                        if "Error Message" in data:
                            self.logger.error(f"API Error for {normalized_symbol}: {data['Error Message']}")
                            return None
                        if "Note" in data:
                            self.logger.warning(f"API Note for {normalized_symbol}: {data['Note']}")
                            return None
                        self.logger.info(f"Retrieved intraday data for {normalized_symbol} ({interval})")
                        return data
                    except Exception as json_error:
                        self.logger.error(f"JSON parsing error for {normalized_symbol}: {json_error}")
                        return None
                else:
                    self.logger.error(f"Error fetching intraday data for {normalized_symbol}: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Exception fetching intraday data for {normalized_symbol}: {e}")
            return None

    async def get_quote(self, symbol: str) -> dict[str, Any] | None:
        """Get real-time quote for a symbol."""
        try:
            normalized_symbol = self._validate_symbol(symbol)
        except ValueError as e:
            self.logger.error(f"Invalid symbol '{symbol}': {e}")
            return None
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": normalized_symbol,
            "apikey": self.api_key,
        }
        
        try:
            if self.session:
                async with self.session.get(self.base_url, params=params, timeout=30) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            # Check for API errors immediately
                            if "Error Message" in data:
                                self.logger.error(f"API Error for {normalized_symbol}: {data['Error Message']}")
                                return None
                            if "Note" in data:
                                self.logger.warning(f"API Note for {normalized_symbol}: {data['Note']}")
                                return None
                            self.logger.info(f"Retrieved quote for {normalized_symbol}")
                            return data
                        except Exception as json_error:
                            self.logger.error(f"JSON parsing error for {normalized_symbol}: {json_error}")
                            return None
                    else:
                        self.logger.error(f"Error fetching quote for {normalized_symbol}: HTTP {response.status}")
                        return None
            else:
                # Fallback to synchronous request
                response = requests.get(self.base_url, params=params, timeout=30)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Check for API errors immediately
                        if "Error Message" in data:
                            self.logger.error(f"API Error for {normalized_symbol}: {data['Error Message']}")
                            return None
                        if "Note" in data:
                            self.logger.warning(f"API Note for {normalized_symbol}: {data['Note']}")
                            return None
                        self.logger.info(f"Retrieved quote for {normalized_symbol}")
                        return data
                    except Exception as json_error:
                        self.logger.error(f"JSON parsing error for {normalized_symbol}: {json_error}")
                        return None
                else:
                    self.logger.error(f"Error fetching quote for {normalized_symbol}: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Exception fetching quote for {normalized_symbol}: {e}")
            return None

    def parse_daily_data(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse daily data from Alpha Vantage response."""
        if not raw_data or not isinstance(raw_data, dict):
            self.logger.error("Invalid raw data: not a dictionary")
            return []
        
        if "Error Message" in raw_data:
            self.logger.error(f"API Error: {raw_data['Error Message']}")
            return []
            
        if "Note" in raw_data:
            self.logger.warning(f"API Note: {raw_data['Note']}")
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
                
                # Validate OHLC relationships
                if not (low_price <= min(open_price, close_price) and 
                        high_price >= max(open_price, close_price)):
                    self.logger.warning(f"Invalid OHLC relationships for {date_str}")
                    # Don't skip - just log warning
                
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
                
        # Sort by timestamp (newest first by default from Alpha Vantage)
        parsed_data.sort(key=lambda x: x["timestamp"], reverse=True)
        self.logger.info(f"Successfully parsed {len(parsed_data)} daily data points")
        return parsed_data

    def parse_quote_data(self, raw_data: dict[str, Any]) -> dict[str, Any] | None:
        """Parse quote data from Alpha Vantage response."""
        if not raw_data or not isinstance(raw_data, dict):
            self.logger.error("Invalid raw data: not a dictionary")
            return None
        
        if "Error Message" in raw_data:
            self.logger.error(f"API Error: {raw_data['Error Message']}")
            return None
            
        if "Note" in raw_data:
            self.logger.warning(f"API Note: {raw_data['Note']}")
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
            
            # Validate OHLC relationships
            if not (low_price <= price <= high_price):
                self.logger.warning(f"Price {price} not between low {low_price} and high {high_price}")
            
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

    async def get_latest_price(self, symbol: str) -> float | None:
        """Get the latest price for a symbol (convenience method)."""
        quote_data = await self.get_quote(symbol)
        if quote_data:
            parsed_quote = self.parse_quote_data(quote_data)
            if parsed_quote:
                return parsed_quote["price"]
        return None

    def test_connection(self) -> bool:
        """Test connection to Alpha Vantage API."""
        try:
            response = requests.get(
                self.base_url,
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": "IBM",
                    "apikey": self.api_key,
                },
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                if "Error Message" not in data and "Note" not in data:
                    self.logger.info("Alpha Vantage API connection test successful")
                    return True
                else:
                    self.logger.error(f"API Error: {data.get('Error Message', data.get('Note', 'Unknown error'))}")
                    return False
            else:
                self.logger.error(f"HTTP Error: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False