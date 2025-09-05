"""Trade list processor for tracking individual trades."""

from typing import Any, Dict, List
import pandas as pd
from datetime import datetime
from .base import MetricProcessor


class TradeListProcessor(MetricProcessor):
    """Processor for maintaining a list of completed trades."""
    
    def __init__(self):
        super().__init__("trade_list")
        self._trades: List[Dict[str, Any]] = []
        self._trade_count = 0
        self._winning_trades = 0
        self._losing_trades = 0
        self._total_pnl = 0.0
        self._gross_wins = 0.0
        self._gross_losses = 0.0
    
    def initialize(self, initial_cash: float, **kwargs) -> None:
        """Initialize the trade list processor.
        
        Args:
            initial_cash: Starting cash amount (not used for trade tracking)
        """
        self._trades = []
        self._trade_count = 0
        self._winning_trades = 0
        self._losing_trades = 0
        self._total_pnl = 0.0
        self._gross_wins = 0.0
        self._gross_losses = 0.0
        self._initialized = True
    
    def process_bar(self, timestamp: datetime, portfolio_value: float, 
                   bar_data: Dict[str, Any]) -> None:
        """Process a bar (trade list updates on trade basis).
        
        Args:
            timestamp: Current timestamp
            portfolio_value: Current total portfolio value
            bar_data: Additional bar data (not used for trade tracking)
        """
        # Trade list is updated per trade, not per bar
        pass
    
    def process_trade(self, trade: Dict[str, Any]) -> None:
        """Process a completed trade.
        
        Args:
            trade: Trade data containing symbol, side, quantity, price, pnl, etc.
        """
        if not self._initialized:
            raise RuntimeError("TradeListProcessor not initialized")
        
        # Add trade to list
        trade_copy = trade.copy()
        trade_copy['trade_id'] = self._trade_count
        self._trades.append(trade_copy)
        self._trade_count += 1
        
        # Update statistics
        pnl = trade.get('pnl', 0.0)
        self._total_pnl += pnl
        
        if pnl > 0:
            self._winning_trades += 1
            self._gross_wins += pnl
        elif pnl < 0:
            self._losing_trades += 1
            self._gross_losses += abs(pnl)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get trade list metrics.
        
        Returns:
            Dictionary containing trade list and summary statistics
        """
        if not self._trades:
            return {
                "trades_df": pd.DataFrame(),
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "total_pnl": 0.0
            }
        
        # Create DataFrame
        trades_df = pd.DataFrame(self._trades)
        
        # Calculate metrics
        win_rate = self._winning_trades / self._trade_count if self._trade_count > 0 else 0.0
        avg_win = self._gross_wins / self._winning_trades if self._winning_trades > 0 else 0.0
        avg_loss = self._gross_losses / self._losing_trades if self._losing_trades > 0 else 0.0
        profit_factor = self._gross_wins / self._gross_losses if self._gross_losses > 0 else float('inf')
        
        return {
            "trades_df": trades_df,
            "total_trades": self._trade_count,
            "winning_trades": self._winning_trades,
            "losing_trades": self._losing_trades,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "total_pnl": self._total_pnl,
            "gross_wins": self._gross_wins,
            "gross_losses": self._gross_losses
        }
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as a DataFrame.
        
        Returns:
            DataFrame containing all trades
        """
        if not self._trades:
            return pd.DataFrame()
        return pd.DataFrame(self._trades)
    
    def reset(self) -> None:
        """Reset the processor."""
        super().reset()
        self._trades = []
        self._trade_count = 0
        self._winning_trades = 0
        self._losing_trades = 0
        self._total_pnl = 0.0
        self._gross_wins = 0.0
        self._gross_losses = 0.0