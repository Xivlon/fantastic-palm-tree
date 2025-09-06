# Error Handling & Data Adapter Improvements

This document describes the defensive coding and data adapter layer improvements implemented to address the requirements for robust error handling and formalized data dependencies.

## Overview

The improvements focus on two main areas:
1. **Defensive Coding**: Enhanced error handling, parameter validation, and logging to prevent silent failures
2. **Data Adapter Layer**: Unified interface for data providers to formalize data flow and enable easy provider switching

## Key Improvements

### 1. DataProviderProtocol Interface

A standardized protocol interface has been created to ensure all data providers implement consistent methods:

```python
from interfaces.data_provider import DataProviderProtocol

# All data providers now implement this protocol
class MyDataProvider:
    async def get_quote(self, symbol: str) -> Dict[str, Any] | None: ...
    async def get_daily_data(self, symbol: str) -> Dict[str, Any] | None: ...
    def parse_quote_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any] | None: ...
    def parse_daily_data(self, raw_data: Dict[str, Any]) -> list[Dict[str, Any]]: ...
    def test_connection(self) -> bool: ...
```

### 2. Enhanced Error Handling

#### Parameter Validation
- **API Key Validation**: All providers validate API keys on initialization
- **Symbol Validation**: Symbols are normalized and validated (length, characters, format)
- **Input Sanitization**: All user inputs are validated before processing

```python
# Before: Silent failure possible
provider = AlphaVantageDataProvider("")  # Would work but fail later

# After: Immediate validation
try:
    provider = AlphaVantageDataProvider("")  # Raises ValueError immediately
except ValueError as e:
    print(f"Invalid API key: {e}")
```

#### API Response Validation
- **Structure Validation**: API responses are validated before parsing
- **Data Type Checking**: Numeric fields are validated and converted safely
- **Error Response Handling**: API errors are caught and logged appropriately

```python
# Enhanced parsing with validation
def parse_quote_data(self, raw_data: dict[str, Any]) -> dict[str, Any] | None:
    if not raw_data or not isinstance(raw_data, dict):
        self.logger.error("Invalid raw data: not a dictionary")
        return None
    
    if "Error Message" in raw_data:
        self.logger.error(f"API Error: {raw_data['Error Message']}")
        return None
    
    # ... additional validation
```

#### Network Error Handling
- **Timeout Configuration**: All network requests have timeouts
- **Graceful Degradation**: Network failures don't crash the system
- **Retry Logic**: Authentication errors trigger token refresh attempts

### 3. Unified Data Adapter Layer

The `DataAdapter` class provides a consistent interface across all data providers:

```python
from backtesting.data_providers import DataAdapter, MockAlphaVantageDataProvider

# Create adapter with any provider
provider = MockAlphaVantageDataProvider("api_key")
adapter = DataAdapter(provider, "MyAdapter")

# Consistent interface regardless of underlying provider
quote = await adapter.get_quote("AAPL")
daily_data = await adapter.get_daily_data("IBM")
price = await adapter.get_latest_price("MSFT")
```

#### Benefits of the Adapter Layer
- **Data Validation**: Ensures data integrity (positive prices, valid OHLC relationships)
- **Error Normalization**: Consistent error handling across all providers
- **Easy Provider Switching**: Change providers without changing client code
- **Enhanced Logging**: Centralized logging with detailed error information

### 4. Custom Exception Handling

Specific exceptions provide better error handling:

```python
from backtesting.data_providers import InvalidSymbolError, DataParsingError

try:
    quote = await adapter.get_quote("INVALID@SYMBOL")
except InvalidSymbolError as e:
    print(f"Symbol validation failed: {e}")
except DataParsingError as e:
    print(f"Data parsing failed: {e}")
```

## Implementation Details

### Enhanced AlphaVantageDataProvider

```python
class AlphaVantageDataProvider:
    def __init__(self, api_key: str):
        # Validate API key immediately
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string")
        if len(api_key.strip()) == 0:
            raise ValueError("API key cannot be empty or whitespace only")
        
        self.api_key = api_key.strip()
        # ... setup logging
    
    def _validate_symbol(self, symbol: str) -> str:
        """Validate and normalize symbol parameter."""
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        
        normalized = symbol.strip().upper()
        if len(normalized) == 0:
            raise ValueError("Symbol cannot be empty after trimming")
        if len(normalized) > 10:
            raise ValueError("Symbol is too long (max 10 characters)")
        
        # Character validation
        if not all(c.isalnum() or c in '.-' for c in normalized):
            raise ValueError("Symbol contains invalid characters")
        
        return normalized
    
    async def get_quote(self, symbol: str) -> dict[str, Any] | None:
        try:
            normalized_symbol = self._validate_symbol(symbol)
        except ValueError as e:
            self.logger.error(f"Invalid symbol '{symbol}': {e}")
            return None
        
        # ... make request with timeout and error handling
```

### Data Validation in Adapter

```python
class DataAdapter:
    def _validate_quote_data(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any] | None:
        """Validate and normalize quote data format."""
        try:
            required_fields = ['symbol', 'price', 'open', 'high', 'low', 'volume']
            for field in required_fields:
                if field not in data:
                    raise DataParsingError(f"Missing required field: {field}")
            
            # Validate numeric fields
            for field in ['price', 'open', 'high', 'low', 'volume']:
                if not isinstance(data[field], (int, float)):
                    data[field] = float(data[field])
                if data[field] < 0:
                    raise DataParsingError(f"Negative {field}: {data[field]}")
            
            # Validate price relationships
            if not (data['low'] <= data['price'] <= data['high']):
                self.logger.warning(f"Price relationships invalid for {symbol}")
            
            return data
        except DataParsingError as e:
            self.logger.error(f"Quote validation failed for {symbol}: {e}")
            return None
```

## Usage Examples

### Basic Usage with Error Handling

```python
import asyncio
from backtesting.data_providers import MockAlphaVantageDataProvider, DataAdapter
from backtesting.data_providers import InvalidSymbolError

async def safe_data_access():
    # Provider with validation
    try:
        provider = MockAlphaVantageDataProvider("your_api_key")
        adapter = DataAdapter(provider, "MyAdapter")
    except ValueError as e:
        print(f"Configuration error: {e}")
        return
    
    # Test connection first
    if not adapter.test_connection():
        print("Connection failed")
        return
    
    # Safe data access
    try:
        quote = await adapter.get_quote("AAPL")
        if quote:
            print(f"AAPL: ${quote['price']:.2f}")
        else:
            print("No quote data available")
    except InvalidSymbolError as e:
        print(f"Invalid symbol: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(safe_data_access())
```

### Provider Switching

```python
# Easy provider switching with same interface
providers = [
    MockAlphaVantageDataProvider("demo_key"),
    AlphaVantageDataProvider("live_key"),
]

for provider in providers:
    adapter = DataAdapter(provider, f"Adapter-{provider.__class__.__name__}")
    
    # Same code works with any provider
    quote = await adapter.get_quote("IBM")
    if quote:
        print(f"IBM price from {provider.__class__.__name__}: ${quote['price']:.2f}")
```

### Error Recovery

```python
# Robust error handling prevents crashes
symbols = ["AAPL", "INVALID@SYMBOL", "IBM", ""]

for symbol in symbols:
    try:
        quote = await adapter.get_quote(symbol)
        if quote:
            print(f"{symbol}: ${quote['price']:.2f}")
        else:
            print(f"{symbol}: No data available")
    except InvalidSymbolError:
        print(f"{symbol}: Invalid symbol format")
    # System continues running despite errors
```

## Testing

Comprehensive tests validate the defensive coding improvements:

```bash
# Run the test suite
python test_defensive_improvements.py

# Expected output:
# ✅ Parameter validation prevents bad inputs
# ✅ Error handling prevents silent failures  
# ✅ Data parsing validates API responses
# ✅ Symbol normalization works correctly
```

## Migration Guide

### From Previous Implementation

```python
# Before: Basic implementation
provider = AlphaVantageDataProvider("key")
data = await provider.get_quote("AAPL")  # Could fail silently

# After: Defensive implementation  
try:
    provider = AlphaVantageDataProvider("key")  # Validates immediately
    adapter = DataAdapter(provider, "MyAdapter")
    data = await adapter.get_quote("AAPL")  # Robust error handling
except ValueError as e:
    print(f"Configuration error: {e}")
except InvalidSymbolError as e:
    print(f"Symbol error: {e}")
```

### Adding New Data Providers

```python
from interfaces.data_provider import DataProviderProtocol

class MyCustomDataProvider:
    """Custom provider implementing the standard protocol."""
    
    def __init__(self, api_key: str):
        # Validate parameters
        if not api_key:
            raise ValueError("API key required")
        self.api_key = api_key
    
    async def get_quote(self, symbol: str) -> Dict[str, Any] | None:
        # Implement with error handling
        pass
    
    # ... implement other required methods
    
# Use with adapter immediately
adapter = DataAdapter(MyCustomDataProvider("key"), "Custom")
```

## Benefits Summary

### Error Handling & Logging
- ✅ **No Silent Failures**: All errors are caught, logged, and handled appropriately
- ✅ **Parameter Validation**: Invalid inputs are caught immediately with clear error messages
- ✅ **API Error Handling**: Malformed API responses don't crash the system
- ✅ **Enhanced Logging**: Detailed logging helps with debugging and monitoring

### Data Dependency Formalization  
- ✅ **Standardized Interface**: All data providers implement DataProviderProtocol
- ✅ **Unified Data Flow**: DataAdapter provides consistent interface regardless of provider
- ✅ **Easy Provider Switching**: Change data sources without changing client code
- ✅ **Data Validation**: Ensures data integrity across all providers

### Robustness & Maintainability
- ✅ **Defensive Coding**: System gracefully handles unexpected conditions
- ✅ **Clear Error Messages**: Problems are easy to diagnose and fix
- ✅ **Protocol Compliance**: Type checking ensures correct implementation
- ✅ **Future-Proof Design**: Easy to add new providers or extend functionality

The improvements ensure the trading system is robust, maintainable, and resistant to the types of silent failures that can occur with external APIs and user input validation.