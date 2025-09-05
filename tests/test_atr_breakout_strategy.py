"""
Test cases for ATR Breakout Strategy

This test suite validates the ATR breakout strategy implementation,
covering configuration, breakout detection, position management,
and integration with the metrics pipeline.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fantastic_palm_tree.strategy.atr_breakout import ATRBreakoutStrategy, PriceBuffer
from fantastic_palm_tree.config import ATRBreakoutConfig
from fantastic_palm_tree.results import BarProcessResult, ExitResult
from fantastic_palm_tree.exceptions import PositionExistsError, NoPositionError


class TestPriceBuffer(unittest.TestCase):
    """Test the PriceBuffer utility class."""
    
    def setUp(self):
        self.buffer = PriceBuffer(size=5)
    
    def test_add_bars(self):
        """Test adding price bars to buffer."""
        self.buffer.add_bar(100.0, 99.0, 99.5)
        self.buffer.add_bar(101.0, 99.5, 100.5)
        
        self.assertEqual(len(self.buffer.highs), 2)
        self.assertEqual(len(self.buffer.lows), 2)
        self.assertEqual(len(self.buffer.closes), 2)
    
    def test_buffer_size_limit(self):
        """Test that buffer maintains size limit."""
        # Add more bars than the size limit
        for i in range(7):
            self.buffer.add_bar(100.0 + i, 99.0 + i, 99.5 + i)
        
        # Should only keep the last 5
        self.assertEqual(len(self.buffer.highs), 5)
        self.assertEqual(self.buffer.highs[0], 102.0)  # First kept bar
        self.assertEqual(self.buffer.highs[-1], 106.0)  # Last bar
    
    def test_get_highest_high(self):
        """Test getting highest high over lookback period."""
        self.buffer.add_bar(100.0, 99.0, 99.5)
        self.buffer.add_bar(102.0, 99.5, 101.5)  # Highest
        self.buffer.add_bar(101.0, 100.0, 100.5)
        
        self.assertEqual(self.buffer.get_highest_high(), 102.0)
        self.assertEqual(self.buffer.get_highest_high(2), 102.0)
        self.assertEqual(self.buffer.get_highest_high(1), 101.0)
    
    def test_get_lowest_low(self):
        """Test getting lowest low over lookback period."""
        self.buffer.add_bar(100.0, 99.0, 99.5)  # Lowest
        self.buffer.add_bar(102.0, 99.5, 101.5)
        self.buffer.add_bar(101.0, 100.0, 100.5)
        
        self.assertEqual(self.buffer.get_lowest_low(), 99.0)
        self.assertEqual(self.buffer.get_lowest_low(2), 99.5)
        self.assertEqual(self.buffer.get_lowest_low(1), 100.0)
    
    def test_has_enough_data(self):
        """Test checking if buffer has enough data."""
        self.assertFalse(self.buffer.has_enough_data(1))
        
        self.buffer.add_bar(100.0, 99.0, 99.5)
        self.assertTrue(self.buffer.has_enough_data(1))
        self.assertFalse(self.buffer.has_enough_data(2))


class TestATRBreakoutConfig(unittest.TestCase):
    """Test ATR breakout configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ATRBreakoutConfig()
        
        self.assertEqual(config.atr_period, 14)
        self.assertEqual(config.position_size, 1000.0)
        self.assertEqual(config.max_risk_per_trade, 0.01)
        self.assertEqual(config.stop_loss_atr_multiplier, 2.0)
        
        # Check default breakout settings
        self.assertEqual(config.breakout["multiplier"], 2.0)
        self.assertEqual(config.breakout["lookback_period"], 20)
        self.assertEqual(config.breakout["direction"], "both")
        
        # Check default trailing settings
        self.assertTrue(config.exits["trailing"]["enabled"])
        self.assertEqual(config.exits["trailing"]["type"], "atr")
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ATRBreakoutConfig(
            atr_period=21,
            position_size=5000.0,
            breakout={
                "multiplier": 1.5,
                "direction": "long",
                "lookback_period": 30
            }
        )
        
        self.assertEqual(config.atr_period, 21)
        self.assertEqual(config.position_size, 5000.0)
        self.assertEqual(config.breakout["multiplier"], 1.5)
        self.assertEqual(config.breakout["direction"], "long")
        self.assertEqual(config.breakout["lookback_period"], 30)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Invalid direction
        with self.assertRaises(Exception):
            ATRBreakoutConfig(breakout={"direction": "invalid"})
        
        # Invalid risk
        with self.assertRaises(Exception):
            ATRBreakoutConfig(max_risk_per_trade=1.5)
        
        # Invalid multiplier
        with self.assertRaises(Exception):
            ATRBreakoutConfig(breakout={"multiplier": -1.0})


class TestATRBreakoutStrategy(unittest.TestCase):
    """Test ATR breakout strategy implementation."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = ATRBreakoutConfig(
            atr_period=5,  # Short period for faster testing
            breakout={
                "multiplier": 1.0,
                "lookback_period": 10,
                "direction": "both",
                "min_atr_threshold": 0.1
            },
            position_size=1000.0,
            max_risk_per_trade=0.02
        )
        self.strategy = ATRBreakoutStrategy(self.config)
    
    def test_initialization(self):
        """Test strategy initialization."""
        self.assertIsNotNone(self.strategy.atr_calc)
        self.assertIsNotNone(self.strategy.price_buffer)
        self.assertIsNotNone(self.strategy.trailing_engine)
        self.assertIsNone(self.strategy.position)
        self.assertEqual(self.strategy._realized_pnl, 0.0)
        self.assertEqual(self.strategy._bar_count, 0)
    
    def test_process_bar_basic(self):
        """Test basic bar processing."""
        result = self.strategy.process_bar(100.0, 99.0, 99.5, 99.0)
        
        self.assertIsInstance(result, BarProcessResult)
        self.assertGreater(result.atr, 0)
        self.assertFalse(result.stop_hit)
        self.assertIsNone(result.exit_result)
        self.assertEqual(self.strategy._bar_count, 1)
    
    def test_breakout_detection(self):
        """Test breakout detection logic."""
        # Build up price history
        for i in range(15):
            self.strategy.process_bar(100.0, 99.0, 99.5, 99.0)
        
        # Test long breakout
        atr = self.strategy.atr_calc.get_atr()
        recent_high = self.strategy.price_buffer.get_highest_high(9)  # lookback - 1
        
        # Strong breakout should be detected
        breakout_high = recent_high + (atr * 1.2)
        breakout = self.strategy._detect_breakout(breakout_high, 99.0, breakout_high - 0.1, atr)
        
        self.assertIsNotNone(breakout)
        self.assertEqual(breakout[0], "long")
        
        # Weak move should not be detected
        weak_high = recent_high + (atr * 0.5)
        no_breakout = self.strategy._detect_breakout(weak_high, 99.0, weak_high - 0.1, atr)
        self.assertIsNone(no_breakout)
    
    def test_position_entry_and_exit(self):
        """Test position entry and exit."""
        # Build up history first
        for i in range(15):
            self.strategy.process_bar(100.0, 99.0, 99.5, 99.0)
        
        # Test position entry
        success = self.strategy.enter_position(100.0, 500.0, is_long=True)
        self.assertTrue(success)
        self.assertIsNotNone(self.strategy.position)
        
        # Test position exists error
        with self.assertRaises(PositionExistsError):
            self.strategy.enter_position(101.0, 500.0)
        
        # Test position exit
        exit_result = self.strategy.exit_position(102.0, reason="test")
        self.assertIsInstance(exit_result, ExitResult)
        self.assertIsNone(self.strategy.position)
        
        # Test no position error
        with self.assertRaises(NoPositionError):
            self.strategy.exit_position(103.0)
    
    def test_position_sizing(self):
        """Test position sizing calculation."""
        # Set up ATR
        for i in range(10):
            self.strategy.process_bar(100.0, 99.0, 99.5, 99.0)
        
        atr = self.strategy.atr_calc.get_atr()
        entry_price = 100.0
        
        position_size = self.strategy._calculate_position_size(entry_price, atr)
        
        # Should be positive and reasonable
        self.assertGreater(position_size, 0)
        self.assertLessEqual(position_size, self.config.position_size)
    
    def test_full_breakout_trade(self):
        """Test a complete breakout trade scenario."""
        # Build up base price pattern
        base_bars = [(100.0, 99.0, 99.5, 99.0)] * 15
        for high, low, close, prev_close in base_bars:
            self.strategy.process_bar(high, low, close, prev_close)
        
        # Ensure no position initially
        self.assertIsNone(self.strategy.position)
        
        # Create a breakout scenario
        breakout_result = self.strategy.process_bar(105.0, 102.0, 104.0, 99.5)
        
        # Should have detected breakout and entered position
        self.assertIsNotNone(self.strategy.position)
        self.assertTrue(self.strategy.position.is_long)
        
        # Continue with some upward movement
        cont_result = self.strategy.process_bar(106.0, 104.5, 105.5, 104.0)
        self.assertIsNotNone(self.strategy.position)
        self.assertFalse(cont_result.stop_hit)
        
        # Create a pullback that should hit trailing stop
        pullback_result = self.strategy.process_bar(104.0, 100.0, 101.0, 105.5)
        
        # Position should be exited by trailing stop
        self.assertTrue(pullback_result.stop_hit or self.strategy.position is None)
        if pullback_result.exit_result:
            self.assertIsInstance(pullback_result.exit_result, ExitResult)
    
    def test_risk_management(self):
        """Test risk management features."""
        # Build history
        for i in range(15):
            self.strategy.process_bar(100.0, 99.0, 99.5, 99.0)
        
        # Enter position
        self.strategy.enter_position(100.0, 1000.0, is_long=True)
        
        # Check that stop loss is set
        self.assertIsNotNone(self.strategy.position.stop_price)
        self.assertLess(self.strategy.position.stop_price, 100.0)  # Stop below entry for long
        
        # Check initial risk calculation
        entry_atr = self.strategy.position.entry_atr
        expected_stop_distance = entry_atr * self.config.stop_loss_atr_multiplier
        actual_stop_distance = abs(self.strategy.position.entry_price - self.strategy.position.stop_price)
        
        self.assertAlmostEqual(actual_stop_distance, expected_stop_distance, places=2)
    
    def test_metrics_and_stats(self):
        """Test metrics and statistics tracking."""
        # Process some bars
        for i in range(10):
            self.strategy.process_bar(100.0 + i, 99.0 + i, 99.5 + i, 99.0 + i - 1 if i > 0 else 99.0)
        
        stats = self.strategy.get_stats()
        
        self.assertEqual(stats["total_bars_processed"], 10)
        self.assertEqual(stats["realized_pnl"], 0.0)  # No trades yet
        self.assertGreater(stats["atr_samples"], 0)
        self.assertGreater(stats["current_atr"], 0)
        self.assertIsNone(stats["current_position"])
        
        # After entering position
        self.strategy.enter_position(110.0, 500.0)
        stats = self.strategy.get_stats()
        self.assertIsNotNone(stats["current_position"])


class TestIntegrationWithCoreEngine(unittest.TestCase):
    """Test integration with core engine and metrics pipeline."""
    
    def test_result_dataclass_integration(self):
        """Test that results use proper dataclasses."""
        config = ATRBreakoutConfig()
        strategy = ATRBreakoutStrategy(config)
        
        # Process a bar
        result = strategy.process_bar(100.0, 99.0, 99.5, 99.0)
        
        # Verify result type and attributes
        self.assertIsInstance(result, BarProcessResult)
        self.assertTrue(hasattr(result, 'atr'))
        self.assertTrue(hasattr(result, 'stop_hit'))
        self.assertTrue(hasattr(result, 'exit_result'))
        self.assertTrue(hasattr(result, 'stop_price'))
    
    def test_configuration_inheritance(self):
        """Test that configuration properly inherits defaults."""
        config = ATRBreakoutConfig()
        
        # Should have all required fields
        self.assertTrue(hasattr(config, 'breakout'))
        self.assertTrue(hasattr(config, 'exits'))
        self.assertTrue(hasattr(config, 'atr_period'))
        
        # Breakout config should have defaults
        self.assertIn('enabled', config.breakout)
        self.assertIn('multiplier', config.breakout)
        self.assertIn('direction', config.breakout)
        
        # Trailing config should have defaults
        self.assertIn('trailing', config.exits)
        self.assertIn('enabled', config.exits['trailing'])


if __name__ == '__main__':
    unittest.main()