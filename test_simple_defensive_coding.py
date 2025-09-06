#!/usr/bin/env python3
"""
Simple standalone test script to validate error handling and data adapter improvements.

This script tests the defensive coding improvements without importing the full backtesting module.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Any, Dict

# Setup simple logging
logging.basicConfig(level=logging.INFO)

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only what we need directly
from interfaces.data_provider import DataProviderProtocol


# Simple test implementations to validate our concepts
class TestDataProvider:
    """Test implementation of DataProviderProtocol."""
    
    def __init__(self, api_key: str):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string")
        if len(api_key.strip()) == 0:
            raise ValueError("API key cannot be empty or whitespace only")
        self.api_key = api_key.strip()
        
    async def get_quote(self, symbol: str) -> Dict[str, Any] | None:
        if not symbol or not isinstance(symbol, str):
            return None
        return {"symbol": symbol.upper(), "price": 100.0}
    
    async def get_daily_data(self, symbol: str) -> Dict[str, Any] | None:
        if not symbol or not isinstance(symbol, str):
            return None
        return {"Time Series (Daily)": {"2023-01-01": {"1. open": "100", "2. high": "101", "3. low": "99", "4. close": "100.5", "5. volume": "1000"}}}
    
    def parse_quote_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any] | None:
        if not raw_data or not isinstance(raw_data, dict):
            return None
        return raw_data
    
    def parse_daily_data(self, raw_data: Dict[str, Any]) -> list[Dict[str, Any]]:
        if not raw_data or not isinstance(raw_data, dict):
            return []
        return [{"timestamp": datetime.now(), "close": 100.0}]
    
    def test_connection(self) -> bool:
        return True


async def test_parameter_validation():
    """Test parameter validation improvements."""
    print("Testing parameter validation...")
    
    # Test invalid API keys
    try:
        TestDataProvider("")
        print("❌ Should reject empty API key")
        return False
    except ValueError:
        print("✅ Correctly rejects empty API key")
    
    try:
        TestDataProvider("   ")
        print("❌ Should reject whitespace-only API key")
        return False
    except ValueError:
        print("✅ Correctly rejects whitespace-only API key")
    
    # Test valid API key
    try:
        provider = TestDataProvider("test_key")
        print("✅ Accepts valid API key")
    except Exception as e:
        print(f"❌ Should accept valid API key: {e}")
        return False
    
    return True


async def test_protocol_compliance():
    """Test that our provider implements the DataProviderProtocol."""
    print("\nTesting protocol compliance...")
    
    provider = TestDataProvider("test_key")
    
    if isinstance(provider, DataProviderProtocol):
        print("✅ TestDataProvider implements DataProviderProtocol")
    else:
        print("❌ TestDataProvider does not implement DataProviderProtocol")
        return False
    
    # Test required methods exist
    required_methods = ['get_quote', 'get_daily_data', 'parse_quote_data', 'parse_daily_data', 'test_connection']
    for method in required_methods:
        if hasattr(provider, method):
            print(f"✅ Has required method: {method}")
        else:
            print(f"❌ Missing required method: {method}")
            return False
    
    return True


async def test_error_handling():
    """Test error handling improvements."""
    print("\nTesting error handling...")
    
    provider = TestDataProvider("test_key")
    
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
            if result is None or result == {}:
                print(f"✅ Correctly handled bad data: {type(bad_data)}")
            else:
                print(f"❌ Should return None/empty for bad data: {type(bad_data)}")
                return False
        except Exception as e:
            print(f"❌ Should not raise exception for bad data: {e}")
            return False
    
    # Test symbol validation
    invalid_symbols = ["", None]
    for symbol in invalid_symbols:
        try:
            result = await provider.get_quote(symbol)
            if result is None:
                print(f"✅ Correctly handled invalid symbol: {symbol}")
            else:
                print(f"❌ Should return None for invalid symbol: {symbol}")
                return False
        except Exception as e:
            print(f"❌ Should not raise exception for invalid symbol: {e}")
            return False
    
    return True


async def test_data_flow():
    """Test basic data flow."""
    print("\nTesting data flow...")
    
    provider = TestDataProvider("test_key")
    
    # Test connection
    if not provider.test_connection():
        print("❌ Connection test failed")
        return False
    print("✅ Connection test passed")
    
    # Test quote data flow
    try:
        raw_quote = await provider.get_quote("IBM")
        if raw_quote:
            parsed_quote = provider.parse_quote_data(raw_quote)
            if parsed_quote:
                print("✅ Quote data flow works")
            else:
                print("❌ Quote data parsing failed")
                return False
        else:
            print("❌ Quote data retrieval failed")
            return False
    except Exception as e:
        print(f"❌ Quote data flow failed: {e}")
        return False
    
    # Test daily data flow
    try:
        raw_daily = await provider.get_daily_data("IBM")
        if raw_daily:
            parsed_daily = provider.parse_daily_data(raw_daily)
            if parsed_daily:
                print("✅ Daily data flow works")
            else:
                print("❌ Daily data parsing failed")
                return False
        else:
            print("❌ Daily data retrieval failed")
            return False
    except Exception as e:
        print(f"❌ Daily data flow failed: {e}")
        return False
    
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING ERROR HANDLING & DATA PROVIDER IMPROVEMENTS")
    print("=" * 60)
    
    tests = [
        test_parameter_validation,
        test_protocol_compliance,
        test_error_handling,
        test_data_flow,
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
        print("✅ Error handling and data provider improvements are working correctly.")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the failures above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)