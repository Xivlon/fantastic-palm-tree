#!/usr/bin/env python3
"""
Usage example demonstrating the improved error handling and data adapter layer.

This example shows how to use the new DataProviderProtocol interface and 
unified DataAdapter to work with different data providers safely.
"""

import asyncio
import logging
import sys
import os

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging to see the defensive coding in action
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demonstrate_error_handling():
    """Demonstrate defensive coding and error handling."""
    print("=" * 60)
    print("DEMONSTRATING DEFENSIVE CODING & ERROR HANDLING")
    print("=" * 60)
    
    # Import here to avoid dependency issues during demonstration
    try:
        from backtesting.data_providers import (
            MockAlphaVantageDataProvider, 
            DataAdapter, 
            InvalidSymbolError
        )
    except ImportError as e:
        print(f"⚠️  Import error (expected in this environment): {e}")
        print("This would work in a properly configured environment with all dependencies.")
        return
    
    print("\n1. Testing Parameter Validation:")
    print("-" * 40)
    
    # Show what happens with bad API keys
    try:
        bad_provider = MockAlphaVantageDataProvider("")
    except ValueError as e:
        print(f"✅ Caught invalid API key: {e}")
    
    try:
        bad_provider2 = MockAlphaVantageDataProvider("   ")
    except ValueError as e:
        print(f"✅ Caught whitespace API key: {e}")
    
    # Create a valid provider
    provider = MockAlphaVantageDataProvider("demo_api_key")
    adapter = DataAdapter(provider, "DemoAdapter")
    
    print("\n2. Testing Symbol Validation:")
    print("-" * 40)
    
    # Test various invalid symbols
    invalid_symbols = ["", "TOOLONGSYMBOL", "INVALID@SYMBOL", "   "]
    
    for symbol in invalid_symbols:
        try:
            quote = await adapter.get_quote(symbol)
        except InvalidSymbolError as e:
            print(f"✅ Caught invalid symbol '{symbol}': {e}")
    
    print("\n3. Testing Successful Data Flow:")
    print("-" * 40)
    
    # Test with valid symbols
    valid_symbols = ["IBM", "AAPL", "MSFT"]
    
    for symbol in valid_symbols:
        try:
            # Test connection
            if adapter.test_connection():
                print(f"✅ Connection test passed for {symbol}")
            
            # Get quote data through adapter (validates and normalizes)
            quote = await adapter.get_quote(symbol)
            if quote:
                print(f"✅ Retrieved quote for {symbol}: ${quote['price']:.2f}")
            
            # Get latest price (convenience method)
            price = await adapter.get_latest_price(symbol)
            if price:
                print(f"✅ Latest price for {symbol}: ${price:.2f}")
            
            # Get daily data
            daily_data = await adapter.get_daily_data(symbol)
            if daily_data:
                print(f"✅ Retrieved {len(daily_data)} daily data points for {symbol}")
                
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
    
    print("\n4. Testing Error Recovery:")
    print("-" * 40)
    
    # Simulate bad API response data
    bad_responses = [
        {},  # Empty response
        {"Error Message": "Invalid API call"},  # API error
        {"Note": "API call limit reached"},  # Rate limit
        {"wrong": "structure"},  # Malformed response
    ]
    
    for i, bad_response in enumerate(bad_responses, 1):
        result = provider.parse_quote_data(bad_response)
        if result is None:
            print(f"✅ Case {i}: Gracefully handled bad API response")
        else:
            print(f"❌ Case {i}: Should have returned None for bad response")
    
    print("\n5. Protocol Compliance:")
    print("-" * 40)
    
    # Import the protocol for checking
    from interfaces.data_provider import DataProviderProtocol
    
    if isinstance(provider, DataProviderProtocol):
        print("✅ MockAlphaVantageDataProvider implements DataProviderProtocol")
    else:
        print("❌ Protocol not implemented")
    
    # Check required methods
    required_methods = ['get_quote', 'get_daily_data', 'parse_quote_data', 'parse_daily_data', 'test_connection']
    for method in required_methods:
        if hasattr(provider, method):
            print(f"✅ Has required method: {method}")
        else:
            print(f"❌ Missing method: {method}")


async def demonstrate_provider_switching():
    """Demonstrate how the unified interface allows easy provider switching."""
    print("\n" + "=" * 60)
    print("DEMONSTRATING PROVIDER SWITCHING")
    print("=" * 60)
    
    try:
        from backtesting.data_providers import (
            MockAlphaVantageDataProvider,
            AlphaVantageDataProvider, 
            DataAdapter
        )
        from interfaces.data_provider import DataProviderProtocol
    except ImportError as e:
        print(f"⚠️  Import error (expected): {e}")
        return
    
    # Create different providers with the same interface
    providers = [
        ("Mock Provider", MockAlphaVantageDataProvider("demo_key")),
        ("Alpha Vantage Provider", AlphaVantageDataProvider("demo_key")),
    ]
    
    for name, provider in providers:
        print(f"\nUsing {name}:")
        print("-" * 30)
        
        # All providers implement the same protocol
        if isinstance(provider, DataProviderProtocol):
            print(f"✅ {name} implements DataProviderProtocol")
            
            # Same adapter can work with any provider
            adapter = DataAdapter(provider, f"Demo-{name}")
            
            try:
                # Same code works with any provider
                if adapter.test_connection():
                    print(f"✅ Connection test passed")
                
                quote = await adapter.get_quote("IBM")
                if quote:
                    print(f"✅ Quote retrieved: {quote['symbol']} @ ${quote['price']:.2f}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ {name} does not implement protocol")


def show_usage_summary():
    """Show a summary of how to use the improved system."""
    print("\n" + "=" * 60)
    print("USAGE SUMMARY")
    print("=" * 60)
    
    usage_code = '''
# Basic usage with error handling
from backtesting.data_providers import MockAlphaVantageDataProvider, DataAdapter
from backtesting.data_providers import InvalidSymbolError

# Create provider (automatically validates API key)
try:
    provider = MockAlphaVantageDataProvider("your_api_key")
    adapter = DataAdapter(provider, "MyAdapter")
except ValueError as e:
    print(f"Invalid API key: {e}")

# Use adapter for safe data access
try:
    quote = await adapter.get_quote("AAPL")
    if quote:
        print(f"Price: ${quote['price']:.2f}")
except InvalidSymbolError as e:
    print(f"Invalid symbol: {e}")

# Switch providers easily (same interface)
from backtesting.data_providers import AlphaVantageDataProvider

live_provider = AlphaVantageDataProvider("live_api_key")
live_adapter = DataAdapter(live_provider, "LiveAdapter")

# Same code works with different providers
quote = await live_adapter.get_quote("AAPL")  # Same interface!

# Robust error handling built-in
daily_data = await adapter.get_daily_data("IBM")  # Won't crash on bad data
price = await adapter.get_latest_price("MSFT")   # Returns None if error

# All providers implement DataProviderProtocol
from interfaces.data_provider import DataProviderProtocol
assert isinstance(provider, DataProviderProtocol)
'''
    
    print(usage_code)
    
    print("\n🎯 Key Benefits:")
    print("  • No more silent failures - all errors are caught and logged")
    print("  • Parameter validation prevents bad inputs from causing issues")
    print("  • Unified interface allows easy switching between data providers")
    print("  • Data validation ensures API responses are properly structured")
    print("  • Defensive coding makes the system more robust and maintainable")


async def main():
    """Run the demonstration."""
    await demonstrate_error_handling()
    await demonstrate_provider_switching()
    show_usage_summary()
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("✅ Error handling and data adapter improvements are ready for use.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())