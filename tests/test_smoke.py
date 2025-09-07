"""
Smoke tests to verify basic functionality and imports.

These tests ensure core modules can be imported and basic functionality works.
"""
import pytest


def test_core_imports():
    """Test that core modules can be imported without errors."""
    # Test core strategy imports
    from fantastic_palm_tree.strategy.base import BaseStrategy
    from fantastic_palm_tree.strategy.enhanced import EnhancedStrategy
    assert BaseStrategy is not None
    assert EnhancedStrategy is not None
    
    # Test configuration imports
    from fantastic_palm_tree.config import StrategyConfig
    assert StrategyConfig is not None
    
    # Test exception imports
    from fantastic_palm_tree.exceptions import NoPositionError, PositionExistsError
    assert NoPositionError is not None
    assert PositionExistsError is not None


def test_basic_configuration():
    """Test that basic configuration works."""
    from fantastic_palm_tree.config import StrategyConfig
    
    config = StrategyConfig()
    assert config.atr_period == 14
    assert config.trailing["enabled"] is True
    assert config.trailing["type"] == "atr"


def test_basic_strategy_creation():
    """Test that basic strategy can be created."""
    from fantastic_palm_tree.strategy.enhanced import EnhancedStrategy
    from fantastic_palm_tree.config import StrategyConfig
    
    config = StrategyConfig()
    strategy = EnhancedStrategy(config)
    
    assert strategy.config is not None
    assert strategy.position is None
    assert strategy.trailing is not None
    assert strategy.atr_calc is not None


if __name__ == "__main__":
    # Allow running smoke tests standalone
    test_core_imports()
    test_basic_configuration()
    test_basic_strategy_creation()
    print("✅ All smoke tests passed!")