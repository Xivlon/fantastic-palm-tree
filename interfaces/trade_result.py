"""
Trade result interface definition.

This module defines the minimal public interface for capturing
and analyzing individual trade results and outcomes.
"""

from typing import Protocol, Optional, runtime_checkable
from abc import ABC, abstractmethod
from datetime import datetime


@runtime_checkable
class TradeResultProtocol(Protocol):
    """
    Minimal protocol for trade results.
    
    This protocol defines the essential interface for capturing
    the outcome of individual trades, including entry/exit details,
    P&L, and risk metrics.
    
    Extension Guidelines:
    - Capture all essential trade details for analysis
    - Calculate risk-adjusted returns (R-multiples)
    - Track both gross and net P&L (including costs)
    - Support both completed and partial trades
    
    Constraints:
    - Entry and exit prices must be positive when set
    - Quantities must be positive
    - P&L calculations must be consistent with position direction
    - Risk metrics should be meaningful and comparable
    """
    
    symbol: str
    """Trading symbol identifier."""
    
    entry_price: float
    """Entry price for the trade."""
    
    exit_price: Optional[float]
    """Exit price for the trade (None if still open)."""
    
    quantity: float
    """Trade quantity (always positive)."""
    
    is_long: bool
    """True for long positions, False for short positions."""
    
    entry_time: datetime
    """Trade entry timestamp."""
    
    exit_time: Optional[datetime]
    """Trade exit timestamp (None if still open)."""
    
    def gross_pnl(self) -> float:
        """
        Calculate gross profit/loss before costs.
        
        Returns:
            Gross P&L amount (positive=profit, negative=loss)
            
        Constraints:
            - Must return 0 if trade is not closed (exit_price is None)
            - Must handle both long and short positions correctly
            - Should not include commissions or fees
        """
        ...
    
    def net_pnl(self) -> float:
        """
        Calculate net profit/loss after all costs.
        
        Returns:
            Net P&L amount including commissions and fees
            
        Constraints:
            - Must subtract all trading costs from gross P&L
            - Should return accurate net result for strategy analysis
        """
        ...
    
    def r_multiple(self, risk_amount: float) -> float:
        """
        Calculate R-multiple (risk-adjusted return).
        
        Args:
            risk_amount: Initial risk amount for the trade
            
        Returns:
            R-multiple (net P&L / risk amount)
            
        Constraints:
            - Risk amount must be positive
            - Should return meaningful metric for strategy evaluation
            - Must handle edge cases (zero risk) gracefully
        """
        ...
    
    def duration(self) -> Optional[float]:
        """
        Calculate trade duration in seconds.
        
        Returns:
            Trade duration in seconds, or None if trade is still open
            
        Constraints:
            - Must return None for open trades
            - Should handle timezone-aware datetimes correctly
        """
        ...


class TradeResultABC(ABC):
    """
    Abstract base class for trade results.
    
    Use this ABC when you need enforcement of trade result implementation
    or want to provide common functionality across result types.
    """
    
    def __init__(
        self,
        symbol: str,
        entry_price: float,
        quantity: float,
        is_long: bool,
        entry_time: Optional[datetime] = None,
        commission: float = 0.0,
    ):
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if commission < 0:
            raise ValueError("Commission cannot be negative")
            
        self.symbol = symbol
        self.entry_price = entry_price
        self.quantity = quantity
        self.is_long = is_long
        self.entry_time = entry_time or datetime.now()
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[datetime] = None
        self.commission = commission
    
    def close_trade(self, exit_price: float, exit_time: Optional[datetime] = None) -> None:
        """
        Close the trade at specified price and time.
        
        Args:
            exit_price: Exit price for the trade
            exit_time: Exit timestamp (defaults to current time)
            
        Constraints:
            - Exit price must be positive
            - Can only close open trades
        """
        if exit_price <= 0:
            raise ValueError("Exit price must be positive")
        if self.exit_price is not None:
            raise ValueError("Trade is already closed")
            
        self.exit_price = exit_price
        self.exit_time = exit_time or datetime.now()
    
    def gross_pnl(self) -> float:
        """Calculate gross profit/loss before costs."""
        if self.exit_price is None:
            return 0.0
            
        if self.is_long:
            return self.quantity * (self.exit_price - self.entry_price)
        else:
            return self.quantity * (self.entry_price - self.exit_price)
    
    def net_pnl(self) -> float:
        """Calculate net profit/loss after all costs."""
        return self.gross_pnl() - self.commission
    
    def r_multiple(self, risk_amount: float) -> float:
        """Calculate R-multiple (risk-adjusted return)."""
        if risk_amount <= 0:
            raise ValueError("Risk amount must be positive")
        return self.net_pnl() / risk_amount
    
    def duration(self) -> Optional[float]:
        """Calculate trade duration in seconds."""
        if self.exit_time is None:
            return None
        return (self.exit_time - self.entry_time).total_seconds()