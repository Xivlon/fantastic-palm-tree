"""
Unified data adapter for standardizing data flow across different providers.

This module provides a consistent interface for market data that can work
with multiple data providers (Alpha Vantage, Schwab, Yahoo Finance, etc.).
"""

import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime

from ..interfaces.data_provider import DataProviderProtocol


class DataAdapterError(Exception):
    """Base exception for data adapter errors."""
    pass


class InvalidSymbolError(DataAdapterError):
    """Raised when an invalid symbol is provided."""
    pass


class DataParsingError(DataAdapterError):
    """Raised when data parsing fails."""
    pass


class DataAdapter:
    """
    Unified data adapter that standardizes data flow across providers.
    
    This adapter provides a consistent interface for market data by wrapping
    different data providers and ensuring they all return data in the same format.
    It handles error conditions, parameter validation, and data normalization.
    """
    
    def __init__(self, provider: DataProviderProtocol, name: str = "DataAdapter"):
        """
        Initialize the data adapter.
        
        Args:
            provider: Data provider implementing DataProviderProtocol
            name: Name for this adapter instance (for logging)
        """
        self.provider = provider
        self.name = name
        
        # Setup logging
        self.logger = logging.getLogger(f"DataAdapter.{name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _validate_symbol(self, symbol: str) -> str:
        """
        Validate and normalize symbol parameter.
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            Normalized symbol
            
        Raises:
            InvalidSymbolError: If symbol is invalid
        """
        if not symbol:
            raise InvalidSymbolError("Symbol cannot be empty")
        
        if not isinstance(symbol, str):
            raise InvalidSymbolError("Symbol must be a string")
        
        symbol = symbol.strip().upper()
        
        if len(symbol) == 0:
            raise InvalidSymbolError("Symbol cannot be empty after trimming")
        
        if len(symbol) > 10:
            raise InvalidSymbolError("Symbol is too long (max 10 characters)")
        
        # Basic symbol validation - alphanumeric with dots and dashes
        if not all(c.isalnum() or c in '.-' for c in symbol):
            raise InvalidSymbolError("Symbol contains invalid characters")
        
        return symbol
    
    async def get_quote(self, symbol: str) -> Dict[str, Any] | None:
        """
        Get standardized quote data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'IBM')
            
        Returns:
            Standardized quote data dictionary, or None if error
            
        Raises:
            InvalidSymbolError: If symbol is invalid
        """
        try:
            normalized_symbol = self._validate_symbol(symbol)
            self.logger.debug(f"Getting quote for {normalized_symbol}")
            
            # Get raw data from provider
            raw_data = await self.provider.get_quote(normalized_symbol)
            if raw_data is None:
                self.logger.warning(f"No raw quote data returned for {normalized_symbol}")
                return None
            
            # Parse the data using provider's parser
            parsed_data = self.provider.parse_quote_data(raw_data)
            if parsed_data is None:
                self.logger.warning(f"Failed to parse quote data for {normalized_symbol}")
                return None
            
            # Validate parsed data format
            return self._validate_quote_data(parsed_data, normalized_symbol)
            
        except InvalidSymbolError:
            raise  # Re-raise validation errors
        except Exception as e:
            self.logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    async def get_daily_data(self, symbol: str) -> list[Dict[str, Any]]:
        """
        Get standardized daily data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'IBM')
            
        Returns:
            List of standardized daily data dictionaries
            
        Raises:
            InvalidSymbolError: If symbol is invalid
        """
        try:
            normalized_symbol = self._validate_symbol(symbol)
            self.logger.debug(f"Getting daily data for {normalized_symbol}")
            
            # Get raw data from provider
            raw_data = await self.provider.get_daily_data(normalized_symbol)
            if raw_data is None:
                self.logger.warning(f"No raw daily data returned for {normalized_symbol}")
                return []
            
            # Parse the data using provider's parser
            parsed_data = self.provider.parse_daily_data(raw_data)
            if not parsed_data:
                self.logger.warning(f"Failed to parse daily data for {normalized_symbol}")
                return []
            
            # Validate and normalize each data point
            validated_data = []
            for data_point in parsed_data:
                try:
                    validated_point = self._validate_daily_data_point(data_point, normalized_symbol)
                    if validated_point:
                        validated_data.append(validated_point)
                except Exception as e:
                    self.logger.warning(f"Skipping invalid data point for {normalized_symbol}: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(validated_data)} daily data points for {normalized_symbol}")
            return validated_data
            
        except InvalidSymbolError:
            raise  # Re-raise validation errors
        except Exception as e:
            self.logger.error(f"Error getting daily data for {symbol}: {e}")
            return []
    
    def _validate_quote_data(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any] | None:
        """
        Validate and normalize quote data format.
        
        Args:
            data: Parsed quote data from provider
            symbol: Symbol for logging purposes
            
        Returns:
            Validated quote data or None if invalid
        """
        try:
            required_fields = ['symbol', 'price', 'open', 'high', 'low', 'volume']
            for field in required_fields:
                if field not in data:
                    raise DataParsingError(f"Missing required field: {field}")
            
            # Validate numeric fields
            numeric_fields = ['price', 'open', 'high', 'low', 'volume']
            for field in numeric_fields:
                if not isinstance(data[field], (int, float)):
                    try:
                        data[field] = float(data[field])
                    except (ValueError, TypeError):
                        raise DataParsingError(f"Invalid {field}: {data[field]}")
                
                if data[field] < 0:
                    raise DataParsingError(f"Negative {field}: {data[field]}")
            
            # Ensure volume is integer
            data['volume'] = int(data['volume'])
            
            # Validate price relationships
            if not (data['low'] <= data['price'] <= data['high']):
                self.logger.warning(f"Price {data['price']} not between low {data['low']} and high {data['high']} for {symbol}")
            
            # Ensure timestamp exists
            if 'timestamp' not in data or data['timestamp'] is None:
                data['timestamp'] = datetime.now()
            
            return data
            
        except DataParsingError as e:
            self.logger.error(f"Quote data validation failed for {symbol}: {e}")
            return None
    
    def _validate_daily_data_point(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any] | None:
        """
        Validate and normalize a single daily data point.
        
        Args:
            data: Single daily data point from provider
            symbol: Symbol for logging purposes
            
        Returns:
            Validated data point or None if invalid
        """
        try:
            required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for field in required_fields:
                if field not in data:
                    raise DataParsingError(f"Missing required field: {field}")
            
            # Validate numeric fields
            numeric_fields = ['open', 'high', 'low', 'close', 'volume']
            for field in numeric_fields:
                if not isinstance(data[field], (int, float)):
                    try:
                        data[field] = float(data[field])
                    except (ValueError, TypeError):
                        raise DataParsingError(f"Invalid {field}: {data[field]}")
                
                if data[field] < 0:
                    raise DataParsingError(f"Negative {field}: {data[field]}")
            
            # Ensure volume is integer
            data['volume'] = int(data['volume'])
            
            # Validate OHLC relationships
            ohlc = [data['open'], data['high'], data['low'], data['close']]
            if not (data['low'] <= min(data['open'], data['close']) and 
                    data['high'] >= max(data['open'], data['close'])):
                self.logger.warning(f"Invalid OHLC relationships for {symbol}: {ohlc}")
            
            # Validate timestamp
            if not isinstance(data['timestamp'], datetime):
                self.logger.warning(f"Invalid timestamp type for {symbol}: {type(data['timestamp'])}")
            
            return data
            
        except DataParsingError as e:
            self.logger.error(f"Daily data point validation failed for {symbol}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test connection to the underlying data provider.
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            self.logger.debug("Testing provider connection")
            result = self.provider.test_connection()
            if result:
                self.logger.info("Provider connection test successful")
            else:
                self.logger.warning("Provider connection test failed")
            return result
        except Exception as e:
            self.logger.error(f"Provider connection test error: {e}")
            return False
    
    async def get_latest_price(self, symbol: str) -> float | None:
        """
        Convenience method to get just the latest price for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Latest price as float, or None if error
        """
        try:
            quote_data = await self.get_quote(symbol)
            if quote_data and 'price' in quote_data:
                return float(quote_data['price'])
            return None
        except Exception as e:
            self.logger.error(f"Error getting latest price for {symbol}: {e}")
            return None