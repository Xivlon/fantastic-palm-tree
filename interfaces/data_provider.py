"""
Data provider interface definition.

This module defines the minimal public interface that data providers
should implement for consistent interaction with the trading system.
"""

from typing import Protocol, Any, Dict, Optional, runtime_checkable
from abc import ABC, abstractmethod


@runtime_checkable
class DataProviderProtocol(Protocol):
    """
    Minimal protocol for market data providers.
    
    This protocol defines the essential interface that any data provider
    must implement to work with the trading system. Providers can be
    implemented as classes or objects that satisfy this protocol.
    
    Extension Guidelines:
    - Implement data fetching in async methods
    - Use consistent data parsing with parse_* methods
    - Provide connection testing via test_connection
    - Handle rate limits and API errors gracefully
    
    Constraints:
    - All methods should handle network errors gracefully
    - Data parsing should validate API responses before processing
    - Providers should not raise exceptions for invalid symbols
    - Connection testing should not affect rate limits
    """
    
    async def get_quote(self, symbol: str) -> Dict[str, Any] | None:
        """
        Get real-time quote for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'IBM')
            
        Returns:
            Raw quote data dictionary from API, or None if error
            
        Constraints:
            - Must validate symbol parameter
            - Should handle API rate limits gracefully
            - Must return consistent data structure
        """
        ...
    
    async def get_daily_data(self, symbol: str) -> Dict[str, Any] | None:
        """
        Get daily time series data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'IBM')
            
        Returns:
            Raw daily data dictionary from API, or None if error
            
        Constraints:
            - Must validate symbol parameter
            - Should include at least OHLCV data
            - Must handle missing data gracefully
        """
        ...
    
    def parse_quote_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Parse quote data from API response.
        
        Args:
            raw_data: Raw response from API
            
        Returns:
            Standardized quote data dictionary, or None if parsing fails
            
        Expected output format:
            {
                'symbol': str,
                'price': float,
                'open': float,
                'high': float,
                'low': float,
                'volume': int,
                'timestamp': datetime,
                'change': float,
                'change_percent': str
            }
            
        Constraints:
            - Must validate input data structure
            - Should handle missing fields gracefully
            - Must return None for unparseable data
        """
        ...
    
    def parse_daily_data(self, raw_data: Dict[str, Any]) -> list[Dict[str, Any]]:
        """
        Parse daily data from API response.
        
        Args:
            raw_data: Raw response from API
            
        Returns:
            List of daily data dictionaries in standardized format
            
        Expected output format for each item:
            {
                'timestamp': datetime,
                'open': float,
                'high': float,
                'low': float,
                'close': float,
                'volume': int
            }
            
        Constraints:
            - Must validate input data structure
            - Should handle missing fields gracefully
            - Must return empty list for unparseable data
        """
        ...
    
    def test_connection(self) -> bool:
        """
        Test connection to data provider API.
        
        Returns:
            True if connection is working, False otherwise
            
        Constraints:
            - Should not count against API rate limits if possible
            - Must handle network timeouts gracefully
            - Should complete quickly (< 10 seconds)
        """
        ...


class DataProviderABC(ABC):
    """
    Abstract base class for market data providers.
    
    Use this ABC when you need enforcement of data provider implementation
    or want to provide common functionality across providers.
    
    This provides the same interface as DataProviderProtocol but with
    stronger typing and enforcement through inheritance.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._validate_api_key(api_key)
    
    def _validate_api_key(self, api_key: str) -> None:
        """Validate API key parameter."""
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string")
        if len(api_key.strip()) == 0:
            raise ValueError("API key cannot be empty or whitespace only")
    
    @abstractmethod
    async def get_quote(self, symbol: str) -> Dict[str, Any] | None:
        """Get real-time quote for a symbol."""
        pass
    
    @abstractmethod
    async def get_daily_data(self, symbol: str) -> Dict[str, Any] | None:
        """Get daily time series data for a symbol."""
        pass
    
    @abstractmethod
    def parse_quote_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Parse quote data from API response."""
        pass
    
    @abstractmethod
    def parse_daily_data(self, raw_data: Dict[str, Any]) -> list[Dict[str, Any]]:
        """Parse daily data from API response."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to data provider API."""
        pass