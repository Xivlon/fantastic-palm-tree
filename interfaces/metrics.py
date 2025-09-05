"""
Metrics aggregator interface definition.

This module defines the minimal public interface for collecting,
calculating, and reporting trading performance metrics.
"""

from typing import Protocol, Dict, Any, List, Optional, runtime_checkable
from abc import ABC, abstractmethod


@runtime_checkable
class MetricsAggregatorProtocol(Protocol):
    """
    Minimal protocol for metrics aggregation.
    
    This protocol defines the essential interface for collecting
    trade data and calculating comprehensive performance metrics
    for strategy evaluation and comparison.
    
    Extension Guidelines:
    - Support incremental metric updates as trades complete
    - Calculate both return-based and risk-adjusted metrics  
    - Provide metrics at multiple time scales (daily, monthly, total)
    - Support benchmark comparison and relative metrics
    
    Constraints:
    - Metrics should be calculated consistently across strategies
    - Must handle edge cases (no trades, all losing trades, etc.)
    - Should provide meaningful defaults for missing data
    - Calculations must be mathematically correct and industry-standard
    """
    
    def add_trade_result(self, trade_result: Any) -> None:
        """
        Add a completed trade result to the aggregator.
        
        Args:
            trade_result: Trade result object implementing TradeResultProtocol
            
        Constraints:
            - Should only accept completed trades (with exit data)
            - Must update all relevant metrics incrementally
            - Should validate trade result data integrity
        """
        ...
    
    def add_equity_point(self, timestamp: str, equity_value: float) -> None:
        """
        Add an equity curve data point.
        
        Args:
            timestamp: Timestamp for the equity value
            equity_value: Portfolio equity value at the timestamp
            
        Constraints:
            - Timestamps should be in chronological order
            - Equity values must be positive
            - Should support high-frequency updates
        """
        ...
    
    def calculate_metrics(self, benchmark: Optional[Any] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            benchmark: Optional benchmark data for relative metrics
            
        Returns:
            Dictionary containing calculated metrics
            
        Constraints:
            - Must return consistent metric names and formats
            - Should handle missing data gracefully
            - Must include both absolute and risk-adjusted metrics
            - Should provide benchmark-relative metrics when available
        """
        ...
    
    def get_equity_curve(self) -> List[Dict[str, Any]]:
        """
        Get equity curve as time series data.
        
        Returns:
            List of dictionaries with timestamp and equity value
            
        Constraints:
            - Data should be in chronological order
            - Should include all recorded equity points
            - Format should be consistent for charting/analysis
        """
        ...
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """
        Get trade history as structured data.
        
        Returns:
            List of trade dictionaries with all trade details
            
        Constraints:
            - Should include all recorded trades
            - Format should be consistent for analysis
            - Must include essential trade metrics (P&L, duration, etc.)
        """
        ...
    
    def reset(self) -> None:
        """
        Reset aggregator to initial state.
        
        Constraints:
            - Must clear all accumulated data
            - Should reset to initial state for reuse
            - Must not affect ongoing calculations if called during processing
        """
        ...


class MetricsAggregatorABC(ABC):
    """
    Abstract base class for metrics aggregators.
    
    Use this ABC when you need enforcement of aggregator implementation
    or want to provide common functionality across aggregator types.
    """
    
    def __init__(self):
        self.trade_results: List[Any] = []
        self.equity_curve: List[Dict[str, Any]] = []
        self._cached_metrics: Optional[Dict[str, Any]] = None
    
    def add_trade_result(self, trade_result: Any) -> None:
        """Add a completed trade result to the aggregator."""
        # Validate trade is completed
        if not hasattr(trade_result, 'exit_price') or trade_result.exit_price is None:
            raise ValueError("Trade result must be completed (have exit_price)")
            
        self.trade_results.append(trade_result)
        self._cached_metrics = None  # Invalidate cache
    
    def add_equity_point(self, timestamp: str, equity_value: float) -> None:
        """Add an equity curve data point."""
        if equity_value <= 0:
            raise ValueError("Equity value must be positive")
            
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': equity_value
        })
        self._cached_metrics = None  # Invalidate cache
    
    @abstractmethod
    def calculate_metrics(self, benchmark: Optional[Any] = None) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        pass
    
    def get_equity_curve(self) -> List[Dict[str, Any]]:
        """Get equity curve as time series data."""
        return self.equity_curve.copy()
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history as structured data."""
        trade_history = []
        for trade in self.trade_results:
            trade_dict = {
                'symbol': trade.symbol,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'quantity': trade.quantity,
                'is_long': trade.is_long,
                'entry_time': trade.entry_time,
                'exit_time': trade.exit_time,
                'gross_pnl': trade.gross_pnl(),
                'net_pnl': trade.net_pnl(),
            }
            
            # Add duration if available
            duration = trade.duration()
            if duration is not None:
                trade_dict['duration_seconds'] = duration
                
            trade_history.append(trade_dict)
            
        return trade_history
    
    def reset(self) -> None:
        """Reset aggregator to initial state."""
        self.trade_results.clear()
        self.equity_curve.clear()
        self._cached_metrics = None
    
    def _calculate_basic_metrics(self) -> Dict[str, Any]:
        """Calculate basic metrics that are common across implementations."""
        if not self.trade_results:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
            }
        
        total_trades = len(self.trade_results)
        winning_trades = sum(1 for trade in self.trade_results if trade.net_pnl() > 0)
        losing_trades = sum(1 for trade in self.trade_results if trade.net_pnl() < 0)
        
        total_pnl = sum(trade.net_pnl() for trade in self.trade_results)
        total_wins = sum(trade.net_pnl() for trade in self.trade_results if trade.net_pnl() > 0)
        total_losses = sum(trade.net_pnl() for trade in self.trade_results if trade.net_pnl() < 0)
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        avg_win = total_wins / winning_trades if winning_trades > 0 else 0.0
        avg_loss = total_losses / losing_trades if losing_trades > 0 else 0.0
        profit_factor = abs(total_wins / total_losses) if total_losses != 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
        }