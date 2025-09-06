#!/usr/bin/env python3
"""
Test script specifically for the improved Alpha Vantage and Mock data providers.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise for test

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the specific implementations
try:
    from backtesting.data_providers.alpha_vantage import AlphaVantageDataProvider
    from backtesting.data_providers.mock_alpha_vantage import MockAlphaVantageDataProvider
    from backtesting.data_providers.adapter import DataAdapter, InvalidSymbolError
    from interfaces.data_provider import DataProviderProtocol
    
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_OK = False


async def test_api_key_validation():
    """Test API key validation."""
    print("Testing API key validation...")
    
    # Test AlphaVantage provider
    try:
        AlphaVantageDataProvider("")
        print("❌ AlphaVantage should reject empty API key")
        return False
    except ValueError:
        print("✅ AlphaVantage correctly rejects empty API key")
    
    try:
        AlphaVantageDataProvider("   ")
        print("❌ AlphaVantage should reject whitespace API key")
        return False
    except ValueError:
        print("✅ AlphaVantage correctly rejects whitespace API key")
    
    # Test Mock provider
    try:
        MockAlphaVantageDataProvider("")
        print("❌ Mock should reject empty API key")
        return False
    except ValueError:
        print("✅ Mock correctly rejects empty API key")
    
    # Test valid keys
    try:
        provider1 = AlphaVantageDataProvider("valid_key")
        provider2 = MockAlphaVantageDataProvider("valid_key")
        print("✅ Both providers accept valid API keys")
    except Exception as e:
        print(f"❌ Should accept valid API keys: {e}")
        return False
    
    return True


async def test_symbol_validation():
    """Test symbol validation."""
    print("\nTesting symbol validation...")
    
    provider = MockAlphaVantageDataProvider("test_key")
    
    # Test invalid symbols through the provider's _validate_symbol method
    invalid_symbols = ["", "   ", "TOOLONGSYMBOL123", "INVALID@SYMBOL"]
    
    for symbol in invalid_symbols:
        try:
            provider._validate_symbol(symbol)
            print(f"❌ Should reject invalid symbol: '{symbol}'")
            return False
        except ValueError:
            print(f"✅ Correctly rejected invalid symbol: '{symbol}'")
    
    # Test valid symbol
    try:
        normalized = provider._validate_symbol("  ibm  ")
        if normalized == "IBM":
            print("✅ Correctly normalized valid symbol")
        else:
            print(f"❌ Symbol normalization failed: {normalized}")
            return False
    except Exception as e:
        print(f"❌ Should accept valid symbol: {e}")
        return False
    
    return True


async def test_mock_provider():
    """Test mock provider functionality."""
    print("\nTesting mock provider...")
    
    provider = MockAlphaVantageDataProvider("test_key")
    
    # Test connection
    if not provider.test_connection():
        print("❌ Mock connection test failed")
        return False
    print("✅ Mock connection test passed")
    
    # Test quote data
    try:
        async with provider:
            quote_data = await provider.get_quote("IBM")
            if quote_data and "Global Quote" in quote_data:
                print("✅ Mock quote data generation works")
                
                # Test parsing
                parsed = provider.parse_quote_data(quote_data)
                if parsed and "symbol" in parsed and "price" in parsed:
                    print("✅ Mock quote data parsing works")
                else:
                    print("❌ Mock quote data parsing failed")
                    return False
            else:
                print("❌ Mock quote data generation failed")
                return False
    except Exception as e:
        print(f"❌ Mock quote test failed: {e}")
        return False
    
    # Test daily data
    try:
        async with provider:
            daily_data = await provider.get_daily_data("IBM")
            if daily_data and "Time Series (Daily)" in daily_data:
                print("✅ Mock daily data generation works")
                
                # Test parsing
                parsed = provider.parse_daily_data(daily_data)
                if parsed and len(parsed) > 0:
                    print("✅ Mock daily data parsing works")
                else:
                    print("❌ Mock daily data parsing failed")
                    return False
            else:
                print("❌ Mock daily data generation failed")
                return False
    except Exception as e:
        print(f"❌ Mock daily test failed: {e}")
        return False
    
    return True


async def test_data_adapter():
    """Test the unified data adapter."""
    print("\nTesting data adapter...")
    
    provider = MockAlphaVantageDataProvider("test_key")
    adapter = DataAdapter(provider, "TestAdapter")
    
    # Test connection
    if not adapter.test_connection():
        print("❌ Adapter connection test failed")
        return False
    print("✅ Adapter connection test passed")
    
    # Test symbol validation through adapter
    try:
        await adapter.get_quote("")
        print("❌ Adapter should reject empty symbol")
        return False
    except InvalidSymbolError:
        print("✅ Adapter correctly rejects empty symbol")
    
    # Test quote retrieval
    try:
        quote = await adapter.get_quote("IBM")
        if quote and "price" in quote and isinstance(quote["price"], float):
            print("✅ Adapter quote retrieval works")
        else:
            print("❌ Adapter quote retrieval failed")
            return False
    except Exception as e:
        print(f"❌ Adapter quote test failed: {e}")
        return False
    
    # Test daily data retrieval
    try:
        daily_data = await adapter.get_daily_data("IBM")
        if daily_data and len(daily_data) > 0:
            print("✅ Adapter daily data retrieval works")
        else:
            print("❌ Adapter daily data retrieval failed")
            return False
    except Exception as e:
        print(f"❌ Adapter daily test failed: {e}")
        return False
    
    # Test latest price convenience method
    try:
        price = await adapter.get_latest_price("IBM")
        if isinstance(price, float) and price > 0:
            print("✅ Adapter latest price method works")
        else:
            print("❌ Adapter latest price method failed")
            return False
    except Exception as e:
        print(f"❌ Adapter latest price test failed: {e}")
        return False
    
    return True


async def test_error_handling():
    """Test error handling with bad data."""
    print("\nTesting error handling...")
    
    provider = MockAlphaVantageDataProvider("test_key")
    
    # Test with malformed data
    bad_data_cases = [
        None,
        {},
        {"wrong": "structure"},
        {"Global Quote": "not a dict"},
        {"Global Quote": {"missing": "fields"}},
    ]
    
    for i, bad_data in enumerate(bad_data_cases):
        result = provider.parse_quote_data(bad_data)
        if result is None:
            print(f"✅ Correctly handled bad quote data case {i+1}")
        else:
            print(f"❌ Should return None for bad quote data case {i+1}")
            return False
    
    # Test daily data parsing with bad data
    for i, bad_data in enumerate(bad_data_cases):
        result = provider.parse_daily_data(bad_data)
        if result == []:
            print(f"✅ Correctly handled bad daily data case {i+1}")
        else:
            print(f"❌ Should return empty list for bad daily data case {i+1}")
            return False
    
    return True


async def test_protocol_compliance():
    """Test protocol compliance."""
    print("\nTesting protocol compliance...")
    
    providers = [
        AlphaVantageDataProvider("test_key"),
        MockAlphaVantageDataProvider("test_key")
    ]
    
    for provider in providers:
        provider_name = provider.__class__.__name__
        if isinstance(provider, DataProviderProtocol):
            print(f"✅ {provider_name} implements DataProviderProtocol")
        else:
            print(f"❌ {provider_name} does not implement DataProviderProtocol")
            return False
    
    return True


async def main():
    """Run all tests."""
    print("=" * 70)
    print("TESTING IMPROVED DATA PROVIDERS & ERROR HANDLING")
    print("=" * 70)
    
    if not IMPORTS_OK:
        print("❌ Cannot run tests due to import errors")
        return False
    
    tests = [
        test_api_key_validation,
        test_symbol_validation,
        test_mock_provider,
        test_data_adapter,
        test_error_handling,
        test_protocol_compliance,
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
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Error handling and data adapter improvements are working correctly.")
        print("✅ Defensive coding has been successfully implemented.")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the failures above.")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)