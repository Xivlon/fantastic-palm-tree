"""
Position interface definition.

This module defines the minimal public interface for position tracking
and management in the trading system.
"""

from typing import Protocol, Optional, runtime_checkable
from abc import ABC, abstractmethod


@runtime_checkable
class PositionProtocol(Protocol):
    """
    Minimal protocol for trading positions.
    
    This protocol defines the essential interface for tracking open
    positions, calculating P&L, and managing position state.
    
    Extension Guidelines:
    - Track entry price, size, and direction consistently
    - Calculate unrealized P&L based on current market price
    - Support partial position closures
    - Maintain position history for analysis
    
    Constraints:
    - Position size can be positive (long) or negative (short)
    - Entry price must be positive
    - P&L calculations must be accurate for both long and short positions
    - Position must track total cost basis correctly
    """
    
    symbol: str
    """Trading symbol identifier."""
    
    size: float
    """Current position size (positive=long, negative=short, zero=no position)."""
    
    entry_price: float
    """Average entry price for the position."""
    
    def unrealized_pnl(self, current_price: float) -> float:
        """
        Calculate unrealized profit/loss at current market price.
        
        Args:
            current_price: Current market price for the symbol
            
        Returns:
            Unrealized P&L amount (positive=profit, negative=loss)
            
        Constraints:
            - Must handle both long and short positions correctly
            - Should return 0 if position size is 0
            - Current price must be positive
        """
        ...
    
    def update_position(self, quantity: float, price: float) -> None:
        """
        Update position with new trade execution.
        
        Args:
            quantity: Trade quantity (positive=buy, negative=sell)
            price: Execution price
            
        Constraints:
            - Must update size and average entry price correctly
            - Price must be positive
            - Should handle position increases, decreases, and reversals
            - Must maintain accurate cost basis
        """
        ...
    
    def close_position(self, price: float) -> float:
        """
        Close the entire position at specified price.
        
        Args:
            price: Closing price
            
        Returns:
            Realized P&L from position closure
            
        Constraints:
            - Must zero out position size
            - Price must be positive
            - Should return accurate realized P&L
            - Position should be marked as closed
        """
        ...


class PositionABC(ABC):
    """
    Abstract base class for trading positions.
    
    Use this ABC when you need enforcement of position implementation
    or want to provide common functionality across position types.
    """
    
    def __init__(self, symbol: str, size: float = 0.0, entry_price: float = 0.0):
        if entry_price < 0:
            raise ValueError("Entry price cannot be negative")
            
        self.symbol = symbol
        self.size = size
        self.entry_price = entry_price
        self._total_cost = size * entry_price
    
    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized profit/loss at current market price."""
        if current_price <= 0:
            raise ValueError("Current price must be positive")
        if self.size == 0:
            return 0.0
        return self.size * (current_price - self.entry_price)
    
    def update_position(self, quantity: float, price: float) -> None:
        """Update position with new trade execution."""
        if price <= 0:
            raise ValueError("Price must be positive")
            
        new_size = self.size + quantity
        
        if new_size == 0:
            # Position closed
            self.size = 0.0
            self.entry_price = 0.0
            self._total_cost = 0.0
        elif (self.size > 0 and new_size > 0) or (self.size < 0 and new_size < 0):
            # Adding to existing position
            self._total_cost += quantity * price
            self.size = new_size
            self.entry_price = abs(self._total_cost / self.size)
        elif (self.size > 0 and new_size < 0) or (self.size < 0 and new_size > 0):
            # Position reversal
            self.size = new_size
            self.entry_price = price
            self._total_cost = new_size * price
        else:
            # Partial close
            self.size = new_size
            self._total_cost = new_size * self.entry_price
    
    def close_position(self, price: float) -> float:
        """Close the entire position at specified price."""
        if price <= 0:
            raise ValueError("Price must be positive")
            
        realized_pnl = self.unrealized_pnl(price)
        self.size = 0.0
        self.entry_price = 0.0
        self._total_cost = 0.0
        return realized_pnl