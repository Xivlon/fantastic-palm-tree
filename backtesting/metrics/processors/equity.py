"""Equity curve processor for tracking portfolio value over time."""

from typing import Any, Dict, List, Tuple
import pandas as pd
from datetime import datetime
from .base import MetricProcessor


class EquityCurveProcessor(MetricProcessor):
    """Processor for tracking equity curve over time."""
    
    def __init__(self):
        super().__init__("equity_curve")
        self._equity_data: List[Tuple[datetime, float]] = []
        self._initial_cash = 0.0
    
    def initialize(self, initial_cash: float, **kwargs) -> None:
        """Initialize with starting cash.
        
        Args:
            initial_cash: Starting cash amount
        """
        self._initial_cash = initial_cash
        self._equity_data = [(datetime.now(), initial_cash)]
        self._initialized = True
    
    def process_bar(self, timestamp: datetime, portfolio_value: float, 
                   bar_data: Dict[str, Any]) -> None:
        """Process a bar by recording the portfolio value.
        
        Args:
            timestamp: Current timestamp
            portfolio_value: Current total portfolio value
            bar_data: Additional bar data (not used for equity curve)
        """
        if not self._initialized:
            raise RuntimeError("EquityCurveProcessor not initialized")
        
        self._equity_data.append((timestamp, portfolio_value))
    
    def process_trade(self, trade: Dict[str, Any]) -> None:
        """Process a trade (equity curve updates on bar basis, not trade basis).
        
        Args:
            trade: Trade data (not used for equity curve)
        """
        # Equity curve is updated per bar, not per trade
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get equity curve metrics.
        
        Returns:
            Dictionary containing equity curve data and basic metrics
        """
        if not self._equity_data:
            return {"equity_curve": pd.DataFrame(), "total_return": 0.0}
        
        # Create DataFrame
        timestamps, values = zip(*self._equity_data)
        equity_df = pd.DataFrame({
            'timestamp': timestamps,
            'equity': values
        }).set_index('timestamp')
        
        # Calculate basic metrics
        total_return = (values[-1] / values[0]) - 1 if values[0] != 0 else 0.0
        
        return {
            "equity_curve": equity_df,
            "total_return": total_return,
            "current_value": values[-1] if values else self._initial_cash,
            "initial_value": self._initial_cash
        }
    
    def get_equity_series(self) -> pd.Series:
        """Get equity as a pandas Series.
        
        Returns:
            Equity values as a time-indexed Series
        """
        if not self._equity_data:
            return pd.Series(dtype=float)
        
        timestamps, values = zip(*self._equity_data)
        return pd.Series(values, index=timestamps, name='equity')
    
    def reset(self) -> None:
        """Reset the processor."""
        super().reset()
        self._equity_data = []
        self._initial_cash = 0.0