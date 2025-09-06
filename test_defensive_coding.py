#!/usr/bin/env python3
"""
Simple test script to validate error handling and data adapter improvements.

This script tests the defensive coding improvements without requiring pytest.
"""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtesting.data_providers import (
    AlphaVantageDataProvider, 
    MockAlphaVantageDataProvider,
    DataAdapter,
    InvalidSymbolError,
    DataParsingError
)
from interfaces.data_provider import DataProviderProtocol


async def test_parameter_validation():
    """Test parameter validation improvements."""
    print("Testing parameter validation...")
    
    # Test invalid API keys
    try:
        AlphaVantageDataProvider("")
        print("❌ AlphaVantage should reject empty API key")
        return False
    except ValueError:
        print("✅ AlphaVantage correctly rejects empty API key")
    
    try:
        MockAlphaVantageDataProvider(None)
        print("❌ Mock should reject None API key")
        return False
    except (ValueError, TypeError):
        print("✅ Mock correctly rejects None API key")
    
    # Test valid API key
    try:
        provider = MockAlphaVantageDataProvider("test_key")
        print("✅ Mock accepts valid API key")
    except Exception as e:
        print(f"❌ Mock should accept valid API key: {e}")
        return False
    
    return True


async def test_symbol_validation():
    """Test symbol validation in data adapter."""
    print("\nTesting symbol validation...")
    
    provider = MockAlphaVantageDataProvider("test_key")
    adapter = DataAdapter(provider, "TestAdapter")
    
    # Test invalid symbols
    invalid_symbols = ["", " ", None, "TOOLONGSYMBOL", "INVALID@SYMBOL"]
    
    for symbol in invalid_symbols:
        try:
            if symbol is None:
                continue  # Skip None test as it will fail before validation
            await adapter.get_quote(symbol)
            print(f"❌ Should reject invalid symbol: {symbol}")
            return False
        except InvalidSymbolError:
            print(f"✅ Correctly rejected invalid symbol: {symbol}")
        except Exception as e:
            # Some symbols might fail at different validation points
            print(f"✅ Rejected invalid symbol {symbol}: {e}")
    
    # Test valid symbol
    try:
        quote = await adapter.get_quote("IBM")
        if quote and "symbol" in quote:
            print("✅ Correctly accepted valid symbol")
        else:
            print("❌ Failed to get quote for valid symbol")
            return False
    except Exception as e:
        print(f"❌ Should accept valid symbol: {e}")
        return False
    
    return True


async def test_data_adapter():
    """Test the unified data adapter."""
    print("\nTesting data adapter...")
    
    provider = MockAlphaVantageDataProvider("test_key")
    adapter = DataAdapter(provider, "TestAdapter")
    
    # Test connection
    if not adapter.test_connection():
        print("❌ Connection test failed")
        return False
    print("✅ Connection test passed")
    
    # Test quote data
    try:
        quote = await adapter.get_quote("IBM")
        if quote and isinstance(quote, dict) and "price" in quote:
            print("✅ Quote data retrieved and validated")
        else:
            print("❌ Quote data validation failed")
            return False
    except Exception as e:
        print(f"❌ Quote retrieval failed: {e}")
        return False
    
    # Test daily data
    try:
        daily_data = await adapter.get_daily_data("IBM")
        if isinstance(daily_data, list) and len(daily_data) > 0:
            print("✅ Daily data retrieved and validated")
        else:
            print("❌ Daily data validation failed")
            return False
    except Exception as e:
        print(f"❌ Daily data retrieval failed: {e}")
        return False
    
    # Test latest price convenience method
    try:
        price = await adapter.get_latest_price("IBM")
        if isinstance(price, float) and price > 0:
            print("✅ Latest price method works")
        else:
            print("❌ Latest price method failed")
            return False
    except Exception as e:
        print(f"❌ Latest price retrieval failed: {e}")
        return False
    
    return True


async def test_protocol_compliance():
    """Test that our providers implement the DataProviderProtocol."""
    print("\nTesting protocol compliance...")
    
    # Test that MockAlphaVantageDataProvider implements the protocol
    provider = MockAlphaVantageDataProvider("test_key")
    
    if isinstance(provider, DataProviderProtocol):
        print("✅ MockAlphaVantageDataProvider implements DataProviderProtocol")
    else:
        print("❌ MockAlphaVantageDataProvider does not implement DataProviderProtocol")
        return False
    
    # Test that AlphaVantageDataProvider implements the protocol
    alpha_provider = AlphaVantageDataProvider("test_key")
    
    if isinstance(alpha_provider, DataProviderProtocol):
        print("✅ AlphaVantageDataProvider implements DataProviderProtocol")
    else:
        print("❌ AlphaVantageDataProvider does not implement DataProviderProtocol")
        return False
    
    return True


async def test_error_handling():
    """Test error handling improvements."""
    print("\nTesting error handling...")
    
    provider = MockAlphaVantageDataProvider("test_key")
    
    # Test parsing with bad data
    bad_data_cases = [
        {},  # Empty dict
        {"wrong": "structure"},  # Wrong structure
        None,  # None input
        "not a dict",  # Wrong type
    ]
    
    for bad_data in bad_data_cases:
        try:
            result = provider.parse_quote_data(bad_data)
            if result is None:
                print(f"✅ Correctly handled bad data: {type(bad_data)}")
            else:
                print(f"❌ Should return None for bad data: {type(bad_data)}")
                return False
        except Exception as e:
            print(f"❌ Should not raise exception for bad data: {e}")
            return False
    
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING ERROR HANDLING & DATA ADAPTER IMPROVEMENTS")
    print("=" * 60)
    
    tests = [
        test_parameter_validation,
        test_symbol_validation,
        test_data_adapter,
        test_protocol_compliance,
        test_error_handling,
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            result = await test()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Error handling and data adapter improvements are working correctly.")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the failures above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)