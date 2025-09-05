"""
Test realized PnL and R multiple calculations

This test verifies R multiple behavior with deterministic ATR and prices,
ensuring no trailing or partial interference, with slippage and commission set to zero.
Expected: realized PnL=1250 and R multiple=1.25
"""

import os
import sys
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhancements_strategy import EnhancedStrategy, StrategyConfig


class TestRealizedRMultiple(unittest.TestCase):
    """Test cases for realized PnL and R multiple calculations"""

    def setUp(self):
        """Set up test environment"""
        # Create strategy config with no dynamic ATR to avoid trailing interference
        config = StrategyConfig()
        config.exits["trailing"]["use_dynamic_atr"] = False
        config.exits["trailing"]["type"] = "atr"

        self.strategy = EnhancedStrategy(config)
        # Set slippage and commission to zero as required
        self.strategy.set_fees(commission_rate=0.0, slippage=0.0)

    def test_r_multiple_calculation_with_deterministic_atr(self):
        """
        Test R multiple behavior with deterministic ATR and prices.
        Expected: realized PnL=1250 and R multiple=1.25
        """
        # Setup deterministic ATR by providing specific price bars
        # We need to establish an ATR value of 1.0 to achieve R multiple = 1.25

        # Initial bar to establish ATR
        # High=100.5, Low=99.5, PrevClose=100 -> TR = max(1, 0.5, 0.5) = 1.0
        self.strategy.update_atr(high=100.5, low=99.5, prev_close=100.0)

        # Second bar to get a stable ATR
        # High=101.5, Low=100.5, PrevClose=100.5 -> TR = max(1, 1, 0) = 1.0
        # ATR = (1.0 + 1.0) / 2 = 1.0
        atr = self.strategy.update_atr(high=101.5, low=100.5, prev_close=100.5)

        # Verify ATR is deterministic
        self.assertEqual(atr, 1.0, "ATR should be 1.0 for deterministic calculation")

        # Enter position with specific parameters to achieve target PnL and R multiple
        # Position size: 1000 shares
        # Entry price: 100.0
        # ATR: 1.0
        # Risk per share: 1.0 (ATR)
        # Price change needed for R multiple 1.25: 1.25 * 1.0 = 1.25

        entry_price = 100.0
        position_size = 1000.0

        success = self.strategy.enter_position(
            price=entry_price, size=position_size, is_long=True
        )
        self.assertTrue(success, "Position entry should succeed")

        # Verify position was created correctly
        position_info = self.strategy.get_position_info()
        self.assertIsNotNone(position_info)
        self.assertEqual(position_info["entry_price"], entry_price)
        self.assertEqual(position_info["size"], position_size)
        self.assertEqual(position_info["entry_atr"], 1.0)

        # Exit position at price that gives PnL = 1250
        # PnL = size * (exit_price - entry_price)
        # 1250 = 1000 * (exit_price - 100)
        # exit_price = 101.25
        exit_price = 101.25

        exit_result = self.strategy.exit_position(price=exit_price, reason="manual")

        # Verify PnL is exactly 1250
        self.assertEqual(
            exit_result["pnl"], 1250.0, "Realized PnL should be exactly 1250"
        )

        # Verify R multiple is exactly 1.25
        # R multiple = (price change per share) / (risk per share) = 1.25 / 1.0 = 1.25

        expected_r_multiple = 1.25
        self.assertEqual(
            exit_result["r_multiple"],
            expected_r_multiple,
            f"R multiple should be exactly {expected_r_multiple}",
        )

        # Verify total realized PnL
        total_pnl = self.strategy.get_realized_pnl()
        self.assertEqual(total_pnl, 1250.0, "Total realized PnL should be exactly 1250")

        # Verify no commission was charged (should be 0)
        self.assertEqual(exit_result["commission"], 0.0, "Commission should be 0")

    def test_no_trailing_interference(self):
        """Test that trailing stops don't interfere with the R multiple calculation"""
        # Setup with trailing disabled
        config = StrategyConfig()
        config.exits["trailing"]["enabled"] = False
        config.exits["trailing"]["use_dynamic_atr"] = False
        strategy = EnhancedStrategy(config)
        strategy.set_fees(commission_rate=0.0, slippage=0.0)

        # Establish ATR
        strategy.update_atr(high=100.5, low=99.5, prev_close=100.0)
        strategy.update_atr(high=101.5, low=100.5, prev_close=100.5)

        # Enter position
        strategy.enter_position(price=100.0, size=1000.0, is_long=True)

        # Process several bars that could trigger trailing stops if enabled
        strategy.process_bar(high=105.0, low=103.0, close=104.0, prev_close=102.0)
        strategy.process_bar(high=106.0, low=104.0, close=105.0, prev_close=104.0)
        strategy.process_bar(high=107.0, low=105.0, close=106.0, prev_close=105.0)

        # Position should still be open (no trailing stop interference)
        position_info = strategy.get_position_info()
        self.assertIsNotNone(position_info, "Position should still be open")

        # Manual exit should still work correctly
        exit_result = strategy.exit_position(price=101.25, reason="manual")
        self.assertEqual(exit_result["pnl"], 1250.0)

    def test_partial_fill_interference_prevention(self):
        """Test that partial fills don't interfere with calculations"""
        # This test ensures we're using full position sizes, not partial fills
        config = StrategyConfig()
        strategy = EnhancedStrategy(config)
        strategy.set_fees(commission_rate=0.0, slippage=0.0)

        # Establish ATR
        strategy.update_atr(high=100.5, low=99.5, prev_close=100.0)
        strategy.update_atr(high=101.5, low=100.5, prev_close=100.5)

        # Enter full position (no partial fills)
        full_size = 1000.0
        strategy.enter_position(price=100.0, size=full_size, is_long=True)

        position_info = strategy.get_position_info()
        self.assertEqual(
            position_info["size"], full_size, "Full position size should be maintained"
        )

        # Exit full position (no partial exits)
        exit_result = strategy.exit_position(price=101.25, reason="manual")
        self.assertEqual(
            exit_result["pnl"], 1250.0, "Full position PnL should be correct"
        )

        # Verify position is completely closed
        position_info = strategy.get_position_info()
        self.assertIsNone(position_info, "Position should be completely closed")


if __name__ == "__main__":
    unittest.main()
