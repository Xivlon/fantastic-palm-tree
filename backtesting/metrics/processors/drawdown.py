"""Drawdown processor for tracking portfolio drawdowns."""

from typing import Any, Dict
import pandas as pd
import numpy as np
from datetime import datetime
from .base import MetricProcessor


class DrawdownProcessor(MetricProcessor):
    """Processor for calculating drawdown metrics."""
    
    def __init__(self):
        super().__init__("drawdown")
        self._equity_values = []
        self._timestamps = []
        self._current_peak = 0.0
        self._max_drawdown = 0.0
        self._max_drawdown_duration = 0
        self._current_drawdown_start = None
        self._current_drawdown_duration = 0
    
    def initialize(self, initial_cash: float, **kwargs) -> None:
        """Initialize with starting cash.
        
        Args:
            initial_cash: Starting cash amount
        """
        self._current_peak = initial_cash
        self._equity_values = [initial_cash]
        self._timestamps = [datetime.now()]
        self._initialized = True
    
    def process_bar(self, timestamp: datetime, portfolio_value: float, 
                   bar_data: Dict[str, Any]) -> None:
        """Process a bar to update drawdown calculations.
        
        Args:
            timestamp: Current timestamp
            portfolio_value: Current total portfolio value
            bar_data: Additional bar data (not used)
        """
        if not self._initialized:
            raise RuntimeError("DrawdownProcessor not initialized")
        
        self._equity_values.append(portfolio_value)
        self._timestamps.append(timestamp)
        
        # Update peak
        if portfolio_value > self._current_peak:
            self._current_peak = portfolio_value
            # End current drawdown period if we were in one
            if self._current_drawdown_start is not None:
                self._max_drawdown_duration = max(
                    self._max_drawdown_duration, 
                    self._current_drawdown_duration
                )
                self._current_drawdown_start = None
                self._current_drawdown_duration = 0
        else:
            # Calculate current drawdown
            current_drawdown = (portfolio_value - self._current_peak) / self._current_peak
            
            # Update max drawdown
            if current_drawdown < self._max_drawdown:
                self._max_drawdown = current_drawdown
            
            # Track drawdown duration
            if self._current_drawdown_start is None:
                self._current_drawdown_start = timestamp
                self._current_drawdown_duration = 1
            else:
                self._current_drawdown_duration += 1
    
    def process_trade(self, trade: Dict[str, Any]) -> None:
        """Process a trade (drawdown updates on bar basis).
        
        Args:
            trade: Trade data (not used for drawdown calculation)
        """
        # Drawdown is calculated per bar, not per trade
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get drawdown metrics.
        
        Returns:
            Dictionary containing drawdown metrics
        """
        if len(self._equity_values) < 2:
            return {
                "max_drawdown": 0.0,
                "max_drawdown_duration": 0,
                "current_drawdown": 0.0,
                "current_drawdown_duration": 0,
                "drawdown_series": pd.Series(dtype=float)
            }
        
        # Calculate full drawdown series
        equity_series = pd.Series(self._equity_values, index=self._timestamps)
        peak_series = equity_series.expanding().max()
        drawdown_series = (equity_series - peak_series) / peak_series
        
        # Current drawdown info
        current_value = self._equity_values[-1]
        current_drawdown = (current_value - self._current_peak) / self._current_peak
        
        # If we're still in a drawdown, use current duration
        current_dd_duration = self._current_drawdown_duration
        if self._current_drawdown_start is None:
            current_dd_duration = 0
        
        return {
            "max_drawdown": self._max_drawdown,
            "max_drawdown_duration": max(self._max_drawdown_duration, current_dd_duration),
            "current_drawdown": current_drawdown,
            "current_drawdown_duration": current_dd_duration,
            "drawdown_series": drawdown_series
        }
    
    def reset(self) -> None:
        """Reset the processor."""
        super().reset()
        self._equity_values = []
        self._timestamps = []
        self._current_peak = 0.0
        self._max_drawdown = 0.0
        self._max_drawdown_duration = 0
        self._current_drawdown_start = None
        self._current_drawdown_duration = 0