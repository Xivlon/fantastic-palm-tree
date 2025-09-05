"""
ATR Breakout Strategy - Reference Implementation

This module provides a complete reference implementation of an ATR-based breakout
trading strategy with trailing stops. It serves as a template for building
custom strategies within the fantastic-palm-tree framework.

The strategy works by:
1. Detecting price breakouts beyond ATR-based thresholds
2. Entering positions when breakouts occur
3. Managing risk with ATR-based trailing stops
4. Providing comprehensive metrics and logging

This implementation demonstrates:
- Integration with the modular architecture
- Proper configuration management
- Risk management integration
- Metrics and logging pipeline
- Type-safe result handling
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from ..config import ATRBreakoutConfig
from ..exceptions import NoPositionError, PositionExistsError
from ..indicators.atr import ATRCalculator
from ..logging import get_logger
from ..models.position import TradePosition
from ..results import BarProcessResult, ExitResult
from ..risk.trailing import TrailingStopEngine
from .base import BaseStrategy

logger = get_logger()


class PriceBuffer:
    """Circular buffer for tracking price history for breakout detection."""
    
    def __init__(self, size: int):
        self.size = size
        self.highs: list[float] = []
        self.lows: list[float] = []
        self.closes: list[float] = []
    
    def add_bar(self, high: float, low: float, close: float) -> None:
        """Add a new price bar to the buffer."""
        self.highs.append(high)
        self.lows.append(low)
        self.closes.append(close)
        
        # Keep only the last 'size' bars
        if len(self.highs) > self.size:
            self.highs.pop(0)
            self.lows.pop(0)
            self.closes.pop(0)
    
    def get_highest_high(self, lookback: int = None) -> float:
        """Get the highest high over the lookback period."""
        if not self.highs:
            return 0.0
        if lookback is None or lookback > len(self.highs):
            lookback = len(self.highs)
        return max(self.highs[-lookback:])
    
    def get_lowest_low(self, lookback: int = None) -> float:
        """Get the lowest low over the lookback period."""
        if not self.lows:
            return float('inf')
        if lookback is None or lookback > len(self.lows):
            lookback = len(self.lows)
        return min(self.lows[-lookback:])
    
    def has_enough_data(self, required: int) -> bool:
        """Check if buffer has enough data for analysis."""
        return len(self.highs) >= required


class ATRBreakoutStrategy(BaseStrategy):
    """
    ATR-based breakout strategy with trailing stops.
    
    This strategy identifies potential breakout opportunities by comparing
    current price action to recent highs/lows adjusted for volatility (ATR).
    When a breakout is detected, it enters a position and manages risk using
    ATR-based trailing stops.
    
    Key Features:
    - ATR-based breakout detection
    - Dynamic position sizing based on volatility
    - Integrated trailing stop management
    - Comprehensive logging and metrics
    - Configurable risk parameters
    """
    
    def __init__(
        self,
        config: ATRBreakoutConfig,
        commission_rate: float = 0.001,
        slippage: float = 0.01
    ):
        """
        Initialize the ATR breakout strategy.
        
        Args:
            config: Strategy configuration with breakout and risk parameters
            commission_rate: Commission rate as decimal (0.001 = 0.1%)
            slippage: Slippage as absolute value
        """
        self.config = config
        self.commission_rate = commission_rate
        self.slippage = slippage
        
        # Initialize components
        self.atr_calc = ATRCalculator(period=config.atr_period)
        self.price_buffer = PriceBuffer(size=config.breakout["lookback_period"] + 10)
        
        # Create a StrategyConfig for the trailing stop engine
        from ..config import StrategyConfig
        trailing_config = StrategyConfig(
            exits=config.exits,
            atr_period=config.atr_period
        )
        self.trailing_engine = TrailingStopEngine(trailing_config, self.atr_calc)
        
        # State
        self.position: Optional[TradePosition] = None
        self._realized_pnl: float = 0.0
        self._bar_count: int = 0
        
        logger.info(
            "ATR Breakout Strategy initialized",
            extra={
                "atr_period": config.atr_period,
                "breakout_multiplier": config.breakout["multiplier"],
                "lookback_period": config.breakout["lookback_period"],
                "commission_rate": commission_rate,
                "slippage": slippage,
            }
        )

    def process_bar(
        self, high: float, low: float, close: float, prev_close: float
    ) -> BarProcessResult:
        """
        Process a new price bar and detect breakout opportunities.
        
        Args:
            high: Bar high price
            low: Bar low price  
            close: Bar close price
            prev_close: Previous bar close price
            
        Returns:
            BarProcessResult with breakout analysis and any exit information
        """
        self._bar_count += 1
        
        # Update ATR indicator
        current_atr = self.atr_calc.add_bar(high, low, prev_close)
        
        # Check for new breakout opportunities BEFORE updating price buffer
        breakout_signal = None
        if not self.position and self._should_check_breakouts():
            # Check breakout using current bar against historical data
            breakout_signal = self._detect_breakout(high, low, close, current_atr)
        
        # Update price buffer AFTER breakout check
        self.price_buffer.add_bar(high, low, close)
        
        # Initialize result
        stop_hit = False
        exit_result = None
        stop_price = None
        
        # Check for position management first
        if self.position:
            # Update trailing stop
            stop_price = self.trailing_engine.update_trailing_stop(self.position, close)
            
            # Check if stop was hit
            stop_hit = self.trailing_engine.stop_hit(self.position, high, low)
            
            if stop_hit and self.position:
                exit_result = self.exit_position(
                    price=self.position.stop_price or close,
                    reason="trailing_stop"
                )
        
        # Execute breakout signal if detected
        if breakout_signal and not self.position:
            direction, entry_price = breakout_signal
            position_size = self._calculate_position_size(entry_price, current_atr)
            
            logger.debug(f"Breakout detected: {direction} at {entry_price:.2f}, size={position_size:.0f}")
            
            if position_size > 0:
                try:
                    self.enter_position(
                        price=entry_price,
                        size=position_size,
                        is_long=(direction == "long")
                    )
                    logger.info(
                        "Breakout signal detected",
                        extra={
                            "direction": direction,
                            "entry_price": entry_price,
                            "position_size": position_size,
                            "atr": current_atr,
                            "bar_count": self._bar_count,
                        }
                    )
                except PositionExistsError:
                    # This shouldn't happen but handle gracefully
                    logger.warning("Attempted to enter position when one already exists")
            else:
                logger.debug(f"Position size too small: {position_size}")

        # Get current stop price if position exists
        if self.position and not stop_hit:
            stop_price = self.position.stop_price

        return BarProcessResult(
            atr=current_atr,
            stop_hit=stop_hit,
            exit_result=exit_result,
            stop_price=stop_price
        )

    def _should_check_breakouts(self) -> bool:
        """Check if we have enough data to detect breakouts."""
        return (
            self.config.breakout["enabled"] and
            self.price_buffer.has_enough_data(self.config.breakout["lookback_period"]) and
            self.atr_calc.has_enough_samples(self.config.atr_period)
        )

    def _detect_breakout(
        self, high: float, low: float, close: float, atr: float
    ) -> Optional[tuple[str, float]]:
        """
        Detect if current price action constitutes a breakout.
        
        Returns:
            Tuple of (direction, entry_price) if breakout detected, None otherwise
        """
        if atr < self.config.breakout["min_atr_threshold"]:
            return None
            
        lookback = self.config.breakout["lookback_period"]
        multiplier = self.config.breakout["multiplier"]
        direction = self.config.breakout["direction"]
        
        # Get recent price levels (excluding current bar)
        recent_high = self.price_buffer.get_highest_high(lookback - 1)
        recent_low = self.price_buffer.get_lowest_low(lookback - 1)
        
        # Calculate breakout thresholds
        long_threshold = recent_high + (atr * multiplier)
        short_threshold = recent_low - (atr * multiplier)
        
        # Check for long breakout
        if direction in ("long", "both") and high > long_threshold:
            return ("long", long_threshold)
            
        # Check for short breakout
        if direction in ("short", "both") and low < short_threshold:
            return ("short", short_threshold)
            
        return None

    def _calculate_position_size(self, entry_price: float, atr: float) -> float:
        """
        Calculate position size based on risk management rules.
        
        Args:
            entry_price: Intended entry price
            atr: Current ATR value
            
        Returns:
            Position size in shares/units
        """
        # Calculate stop distance
        stop_distance = atr * self.config.stop_loss_atr_multiplier
        
        # Risk-based position sizing
        # Risk per trade = position_size * stop_distance
        # position_size = max_risk / stop_distance
        max_risk_amount = self.config.position_size * self.config.max_risk_per_trade
        
        if stop_distance > 0:
            risk_based_size = max_risk_amount / stop_distance
        else:
            risk_based_size = self.config.position_size
            
        # Use the smaller of default size or risk-based size
        return min(self.config.position_size, risk_based_size)

    def enter_position(self, price: float, size: float, is_long: bool = True) -> bool:
        """
        Enter a new trading position.
        
        Args:
            price: Entry price
            size: Position size
            is_long: True for long position, False for short
            
        Returns:
            True if position was successfully entered
            
        Raises:
            PositionExistsError: If a position already exists
        """
        if self.position is not None:
            raise PositionExistsError("A position already exists; exit before entering a new one.")
            
        # Calculate costs
        entry_atr = self.atr_calc.get_atr()
        effective_price = price + (self.slippage if is_long else -self.slippage)
        commission = abs(size * effective_price * self.commission_rate)
        
        # Create position
        self.position = TradePosition(
            entry_price=effective_price,
            size=size,
            entry_atr=entry_atr,
            is_long=is_long,
            timestamp=self._bar_count,
        )
        
        # Set initial stop loss
        stop_distance = entry_atr * self.config.stop_loss_atr_multiplier
        if is_long:
            self.position.stop_price = effective_price - stop_distance
        else:
            self.position.stop_price = effective_price + stop_distance
        
        # Deduct commission
        self._realized_pnl -= commission
        
        logger.debug(
            "Position entered",
            extra={
                "entry_price": effective_price,
                "size": size,
                "is_long": is_long,
                "entry_atr": entry_atr,
                "initial_stop": self.position.stop_price,
                "commission": commission,
                "bar_count": self._bar_count,
            }
        )
        
        return True

    def exit_position(self, price: float, reason: str = "manual") -> ExitResult:
        """
        Exit the current trading position.
        
        Args:
            price: Exit price
            reason: Reason for exit (e.g., "trailing_stop", "manual")
            
        Returns:
            ExitResult with trade details
            
        Raises:
            NoPositionError: If no position exists to exit
        """
        if not self.position:
            raise NoPositionError("No position to exit.")
            
        position = self.position
        effective_price = price + (-self.slippage if position.is_long else self.slippage)
        commission = abs(position.size * effective_price * self.commission_rate)

        # Calculate P&L
        if position.is_long:
            position_pnl = position.size * (effective_price - position.entry_price)
        else:
            position_pnl = position.size * (position.entry_price - effective_price)

        # Calculate R-multiple (risk-adjusted return)
        r_multiple = self._compute_r_multiple(position_pnl, position)
        
        # Update total P&L
        self._realized_pnl += position_pnl - commission

        # Create result
        exit_result = ExitResult(
            pnl=position_pnl,
            r_multiple=r_multiple,
            total_pnl=self._realized_pnl,
            commission=commission,
            reason=reason,
        )

        logger.debug(
            "Position exited",
            extra={
                **asdict(exit_result),
                "exit_price": effective_price,
                "bars_held": self._bar_count - position.timestamp,
            }
        )

        # Clear position
        self.position = None
        
        return exit_result

    def _compute_r_multiple(self, pnl: float, position: TradePosition) -> float:
        """
        Compute R-multiple for the trade.
        
        R-multiple represents how many times the initial risk the P&L represents.
        Positive R-multiple means profit, negative means loss.
        """
        if not position.entry_atr or position.entry_atr <= 0:
            return 0.0
            
        # Risk is based on initial stop distance
        initial_risk = position.size * position.entry_atr * self.config.stop_loss_atr_multiplier
        
        if initial_risk <= 0:
            return 0.0
            
        return pnl / initial_risk

    def get_position_info(self) -> Optional[dict]:
        """Get current position information for debugging/monitoring."""
        if not self.position:
            return None
            
        return {
            "entry_price": self.position.entry_price,
            "size": self.position.size,
            "entry_atr": self.position.entry_atr,
            "stop_price": self.position.stop_price,
            "is_long": self.position.is_long,
            "bars_held": self._bar_count - self.position.timestamp,
        }

    def get_realized_pnl(self) -> float:
        """Get total realized P&L."""
        return self._realized_pnl

    def get_stats(self) -> dict:
        """Get strategy statistics."""
        return {
            "total_bars_processed": self._bar_count,
            "realized_pnl": self._realized_pnl,
            "current_position": self.get_position_info(),
            "atr_samples": self.atr_calc.sample_count(),
            "current_atr": self.atr_calc.get_atr(),
        }