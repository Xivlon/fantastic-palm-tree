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
        self.api_key = api_key
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

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def get_daily_data(self, symbol: str) -> dict[str, Any] | None:
        """Get daily time series data for a symbol."""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key,
        }
        
        try:
            if self.session:
                async with self.session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"Retrieved daily data for {symbol}")
                        return data
                    else:
                        self.logger.error(f"Error fetching data for {symbol}: HTTP {response.status}")
                        return None
            else:
                # Fallback to synchronous request
                response = requests.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(f"Retrieved daily data for {symbol}")
                    return data
                else:
                    self.logger.error(f"Error fetching data for {symbol}: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Exception fetching data for {symbol}: {e}")
            return None

    async def get_intraday_data(self, symbol: str, interval: str = "5min") -> dict[str, Any] | None:
        """Get intraday time series data for a symbol."""
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
        }
        
        try:
            if self.session:
                async with self.session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"Retrieved intraday data for {symbol} ({interval})")
                        return data
                    else:
                        self.logger.error(f"Error fetching intraday data for {symbol}: HTTP {response.status}")
                        return None
            else:
                # Fallback to synchronous request
                response = requests.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(f"Retrieved intraday data for {symbol} ({interval})")
                    return data
                else:
                    self.logger.error(f"Error fetching intraday data for {symbol}: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Exception fetching intraday data for {symbol}: {e}")
            return None

    async def get_quote(self, symbol: str) -> dict[str, Any] | None:
        """Get real-time quote for a symbol."""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key,
        }
        
        try:
            if self.session:
                async with self.session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"Retrieved quote for {symbol}")
                        return data
                    else:
                        self.logger.error(f"Error fetching quote for {symbol}: HTTP {response.status}")
                        return None
            else:
                # Fallback to synchronous request
                response = requests.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(f"Retrieved quote for {symbol}")
                    return data
                else:
                    self.logger.error(f"Error fetching quote for {symbol}: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Exception fetching quote for {symbol}: {e}")
            return None

    def parse_daily_data(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse daily data from Alpha Vantage response."""
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
        parsed_data = []
        
        for date_str, values in time_series.items():
            try:
                parsed_data.append({
                    "timestamp": datetime.strptime(date_str, "%Y-%m-%d"),
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"]),
                })
            except (KeyError, ValueError) as e:
                self.logger.error(f"Error parsing data for {date_str}: {e}")
                continue
                
        # Sort by timestamp (newest first by default from Alpha Vantage)
        parsed_data.sort(key=lambda x: x["timestamp"], reverse=True)
        return parsed_data

    def parse_quote_data(self, raw_data: dict[str, Any]) -> dict[str, Any] | None:
        """Parse quote data from Alpha Vantage response."""
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