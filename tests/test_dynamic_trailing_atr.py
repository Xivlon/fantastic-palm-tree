"""
Test dynamic ATR trailing behavior

This test verifies that the dynamic ATR trailing stop functionality works correctly,
testing both the use of dynamic ATR and fallback to entry ATR when insufficient samples.
"""

import os
import sys
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhancements_strategy import EnhancedStrategy, StrategyConfig


class TestDynamicTrailingATR(unittest.TestCase):
    """Test cases for dynamic ATR trailing stop behavior"""

    def setUp(self):
        """Set up test environment"""
        # Create strategy config with dynamic ATR enabled
        config = StrategyConfig()
        config.exits["trailing"]["enabled"] = True
        config.exits["trailing"]["use_dynamic_atr"] = True
        config.exits["trailing"]["dynamic_atr_min_samples"] = 3
        config.exits["trailing"]["type"] = "atr"

        self.strategy = EnhancedStrategy(config)
        self.strategy.set_fees(commission_rate=0.0, slippage=0.0)

    def test_dynamic_atr_with_sufficient_samples(self):
        """Test that dynamic ATR is used when enough samples are available"""
        # Establish initial ATR with multiple bars
        self.strategy.update_atr(high=101.0, low=99.0, prev_close=100.0)  # TR = 2.0
        self.strategy.update_atr(high=102.0, low=100.0, prev_close=101.0)  # TR = 2.0
        self.strategy.update_atr(high=103.0, low=101.0, prev_close=102.0)  # TR = 2.0
        # ATR = 2.0

        # Enter position
        self.strategy.enter_position(price=100.0, size=1000.0, is_long=True)
        position_info = self.strategy.get_position_info()
        entry_atr = position_info["entry_atr"]
        self.assertEqual(entry_atr, 2.0, "Entry ATR should be 2.0")

        # Add more bars with different ATR to create dynamic change
        # These bars will have smaller true ranges, lowering the ATR
        self.strategy.update_atr(high=103.5, low=102.5, prev_close=103.0)  # TR = 1.0
        self.strategy.update_atr(high=104.0, low=103.0, prev_close=103.5)  # TR = 1.0
        # Now ATR should be (2+2+2+1+1)/5 = 1.6

        # Calculate trailing stop distance - should use new dynamic ATR
        distance = self.strategy.calculate_trailing_stop_distance()
        expected_dynamic_atr = 1.6
        self.assertAlmostEqual(
            distance,
            expected_dynamic_atr,
            places=1,
            msg="Should use dynamic ATR when enough samples available",
        )
        self.assertNotEqual(
            distance, entry_atr, "Should not use entry ATR when dynamic is available"
        )

    def test_fallback_to_entry_atr_insufficient_samples(self):
        """Test that entry ATR is used when insufficient samples for dynamic ATR"""
        # Create config with higher minimum samples requirement
        config = StrategyConfig()
        config.exits["trailing"]["enabled"] = True
        config.exits["trailing"]["use_dynamic_atr"] = True
        config.exits["trailing"]["dynamic_atr_min_samples"] = 10  # Require 10 samples
        config.exits["trailing"]["type"] = "atr"

        strategy = EnhancedStrategy(config)
        strategy.set_fees(commission_rate=0.0, slippage=0.0)

        # Establish initial ATR with only 2 bars (less than required 10)
        strategy.update_atr(high=101.0, low=99.0, prev_close=100.0)  # TR = 2.0
        strategy.update_atr(high=102.0, low=100.0, prev_close=101.0)  # TR = 2.0
        # ATR = 2.0

        # Enter position
        strategy.enter_position(price=100.0, size=1000.0, is_long=True)
        position_info = strategy.get_position_info()
        entry_atr = position_info["entry_atr"]

        # Add one more bar with different TR
        strategy.update_atr(high=104.0, low=100.0, prev_close=102.0)  # TR = 4.0
        # New ATR = (2+2+4)/3 = 2.67, but we still don't have 10 samples

        # Calculate trailing stop distance - should use entry ATR due to insufficient samples
        distance = strategy.calculate_trailing_stop_distance()
        self.assertEqual(
            distance,
            entry_atr,
            "Should use entry ATR when insufficient samples for dynamic ATR",
        )

    def test_dynamic_atr_trailing_stop_update(self):
        """Test that trailing stops update correctly with dynamic ATR"""
        # Setup with low minimum samples for dynamic ATR
        config = StrategyConfig()
        config.exits["trailing"]["enabled"] = True
        config.exits["trailing"]["use_dynamic_atr"] = True
        config.exits["trailing"]["dynamic_atr_min_samples"] = 2
        config.exits["trailing"]["type"] = "atr"

        strategy = EnhancedStrategy(config)
        strategy.set_fees(commission_rate=0.0, slippage=0.0)

        # Establish ATR
        strategy.update_atr(high=101.0, low=99.0, prev_close=100.0)  # TR = 2.0
        strategy.update_atr(high=102.0, low=100.0, prev_close=101.0)  # TR = 2.0
        # ATR = 2.0

        # Enter long position
        strategy.enter_position(price=100.0, size=1000.0, is_long=True)

        # Price moves up, update trailing stop
        current_price = 105.0
        stop_price = strategy.update_trailing_stop(current_price)
        expected_stop = current_price - 2.0  # 105 - 2 = 103
        self.assertEqual(
            stop_price, expected_stop, "Initial trailing stop should use ATR of 2.0"
        )

        # Add bars that change the ATR
        strategy.update_atr(high=105.5, low=104.5, prev_close=105.0)  # TR = 1.0
        # New ATR = (2+2+1)/3 = 1.67

        # Price moves up more, trailing stop should use new dynamic ATR
        current_price = 107.0
        stop_price = strategy.update_trailing_stop(current_price)
        new_atr = strategy.atr_calculator.get_atr()
        expected_stop = current_price - new_atr  # 107 - 1.67 = 105.33
        self.assertAlmostEqual(
            stop_price,
            expected_stop,
            places=2,
            msg="Trailing stop should use updated dynamic ATR",
        )

    def test_static_atr_vs_dynamic_atr_behavior(self):
        """Test the difference between static (entry) ATR and dynamic ATR behavior"""
        # Test static ATR behavior
        static_config = StrategyConfig()
        static_config.exits["trailing"]["enabled"] = True
        static_config.exits["trailing"]["use_dynamic_atr"] = False
        static_config.exits["trailing"]["type"] = "atr"

        static_strategy = EnhancedStrategy(static_config)
        static_strategy.set_fees(commission_rate=0.0, slippage=0.0)

        # Test dynamic ATR behavior
        dynamic_config = StrategyConfig()
        dynamic_config.exits["trailing"]["enabled"] = True
        dynamic_config.exits["trailing"]["use_dynamic_atr"] = True
        dynamic_config.exits["trailing"]["dynamic_atr_min_samples"] = 2
        dynamic_config.exits["trailing"]["type"] = "atr"

        dynamic_strategy = EnhancedStrategy(dynamic_config)
        dynamic_strategy.set_fees(commission_rate=0.0, slippage=0.0)

        # Setup same initial conditions for both
        for strategy in [static_strategy, dynamic_strategy]:
            strategy.update_atr(high=101.0, low=99.0, prev_close=100.0)  # TR = 2.0
            strategy.update_atr(high=102.0, low=100.0, prev_close=101.0)  # TR = 2.0
            strategy.enter_position(price=100.0, size=1000.0, is_long=True)

        # Add bars that change ATR
        for strategy in [static_strategy, dynamic_strategy]:
            strategy.update_atr(high=102.5, low=101.5, prev_close=102.0)  # TR = 1.0

        # Calculate distances
        static_distance = static_strategy.calculate_trailing_stop_distance()
        dynamic_distance = dynamic_strategy.calculate_trailing_stop_distance()

        # Static should use entry ATR (2.0), dynamic should use current ATR (1.67)
        self.assertEqual(static_distance, 2.0, "Static strategy should use entry ATR")
        self.assertAlmostEqual(
            dynamic_distance,
            5.0 / 3.0,
            places=2,
            msg="Dynamic strategy should use updated ATR",
        )
        self.assertNotEqual(
            static_distance,
            dynamic_distance,
            "Static and dynamic strategies should behave differently",
        )

    def test_min_samples_configuration(self):
        """Test that the dynamic_atr_min_samples configuration works correctly"""
        # Test with min_samples = 1
        config1 = StrategyConfig()
        config1.exits["trailing"]["use_dynamic_atr"] = True
        config1.exits["trailing"]["dynamic_atr_min_samples"] = 1

        strategy1 = EnhancedStrategy(config1)
        strategy1.update_atr(high=101.0, low=99.0, prev_close=100.0)  # 1 sample
        self.assertTrue(strategy1.atr_calculator.has_enough_samples(1))

        # Test with min_samples = 5
        config5 = StrategyConfig()
        config5.exits["trailing"]["use_dynamic_atr"] = True
        config5.exits["trailing"]["dynamic_atr_min_samples"] = 5

        strategy5 = EnhancedStrategy(config5)
        for _i in range(3):  # Only 3 samples
            strategy5.update_atr(high=101.0, low=99.0, prev_close=100.0)
        self.assertFalse(strategy5.atr_calculator.has_enough_samples(5))


if __name__ == "__main__":
    unittest.main()
