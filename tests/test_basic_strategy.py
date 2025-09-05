"""
Test basic strategy functionality to improve coverage.
"""
import pytest
from fantastic_palm_tree import StrategyConfig, EnhancedStrategy
from fantastic_palm_tree.exceptions import NoPositionError, PositionExistsError


def test_strategy_creation():
    """Test basic strategy creation and configuration."""
    config = StrategyConfig()
    strategy = EnhancedStrategy(config)
    
    assert strategy.config is not None
    assert strategy.position is None
    assert strategy.trailing is not None
    assert strategy.atr_calc is not None


def test_strategy_config_validation():
    """Test strategy configuration validation."""
    config = StrategyConfig()
    
    # Test default configuration
    assert config.atr_period == 14
    assert config.trailing["enabled"] is True
    assert config.trailing["type"] == "atr"
    

def test_position_management():
    """Test basic position management."""
    config = StrategyConfig()
    strategy = EnhancedStrategy(config)
    
    # Should have no position initially
    assert strategy.position is None
    
    # Enter a position
    strategy.enter_position(price=100.0, size=1000, is_long=True)
    assert strategy.position is not None
    assert strategy.position.entry_price == 100.0
    assert strategy.position.size == 1000
    assert strategy.position.is_long is True
    
    # Try to enter another position (should raise error)
    with pytest.raises(PositionExistsError):
        strategy.enter_position(price=101.0, size=500, is_long=True)
    
    # Exit the position
    strategy.exit_position(price=105.0)
    assert strategy.position is None
    
    # Try to exit when no position (should raise error)
    with pytest.raises(NoPositionError):
        strategy.exit_position(price=105.0)


def test_atr_calculation():
    """Test ATR calculation functionality."""
    config = StrategyConfig()
    strategy = EnhancedStrategy(config)
    
    # Update ATR with some bars
    strategy.update_atr(high=102, low=98, prev_close=100)
    strategy.update_atr(high=104, low=99, prev_close=102)
    
    # Should have valid ATR after updates
    assert strategy.atr_calc.get_atr() > 0


def test_bar_processing():
    """Test basic bar processing functionality."""
    config = StrategyConfig()
    strategy = EnhancedStrategy(config)
    
    # Process a bar without position
    result = strategy.process_bar(high=102, low=98, close=100, prev_close=99)
    
    assert result.atr > 0
    assert result.stop_hit is False
    assert result.exit_result is None