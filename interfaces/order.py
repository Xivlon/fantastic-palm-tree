"""
Order interface definition.

This module defines the minimal public interface for trading orders
that can be placed, modified, and executed in the trading system.
"""

from typing import Protocol, Optional, runtime_checkable
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime


class OrderSide(Enum):
    """Standard order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Standard order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(Enum):
    """Standard order status enumeration."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED" 
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


@runtime_checkable
class OrderProtocol(Protocol):
    """
    Minimal protocol for trading orders.
    
    This protocol defines the essential interface that trading orders
    must implement for consistent order management across the system.
    
    Extension Guidelines:
    - Always include symbol, quantity, side, and order_type
    - Use standard enums for side, type, and status
    - Implement proper state transitions (pending -> filled/canceled/rejected)
    - Track timing information for analysis
    
    Constraints:
    - Order state must be immutable once filled
    - Price and stop_price must be positive numbers when set
    - Quantity must be positive
    - State transitions must follow valid order lifecycle
    """
    
    symbol: str
    """Trading symbol identifier."""
    
    quantity: float
    """Order quantity (positive number)."""
    
    side: OrderSide
    """Order side (BUY or SELL)."""
    
    order_type: OrderType
    """Type of order (MARKET, LIMIT, etc.)."""
    
    status: OrderStatus
    """Current order status."""
    
    price: Optional[float]
    """Limit price for limit orders."""
    
    stop_price: Optional[float]
    """Stop price for stop orders."""
    
    timestamp: Optional[datetime]
    """Order creation timestamp."""
    
    fill_price: Optional[float] 
    """Price at which order was filled."""
    
    fill_timestamp: Optional[datetime]
    """Timestamp when order was filled."""
    
    def fill(self, price: float, timestamp: Optional[datetime] = None) -> None:
        """
        Mark order as filled at specified price.
        
        Args:
            price: Execution price
            timestamp: Fill timestamp (defaults to current time)
            
        Constraints:
            - Can only fill pending orders
            - Price must be positive
            - Must update status to FILLED
            - Must record fill_price and fill_timestamp
        """
        ...
    
    def cancel(self) -> None:
        """
        Cancel the order.
        
        Constraints:
            - Can only cancel pending orders
            - Must update status to CANCELED
            - Cannot be reversed once canceled
        """
        ...
    
    def reject(self, reason: Optional[str] = None) -> None:
        """
        Reject the order.
        
        Args:
            reason: Optional rejection reason
            
        Constraints:
            - Can only reject pending orders
            - Must update status to REJECTED
            - Should log rejection reason if provided
        """
        ...


class OrderABC(ABC):
    """
    Abstract base class for trading orders.
    
    Use this ABC when you need enforcement of order implementation
    or want to provide common functionality across order types.
    """
    
    def __init__(
        self,
        symbol: str,
        quantity: float,
        side: OrderSide,
        order_type: OrderType,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price is not None and price <= 0:
            raise ValueError("Price must be positive when specified")
        if stop_price is not None and stop_price <= 0:
            raise ValueError("Stop price must be positive when specified")
            
        self.symbol = symbol
        self.quantity = quantity
        self.side = side
        self.order_type = order_type
        self.price = price
        self.stop_price = stop_price
        self.status = OrderStatus.PENDING
        self.timestamp = datetime.now()
        self.fill_price: Optional[float] = None
        self.fill_timestamp: Optional[datetime] = None
    
    def fill(self, price: float, timestamp: Optional[datetime] = None) -> None:
        """Mark order as filled at specified price."""
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot fill order with status {self.status}")
        if price <= 0:
            raise ValueError("Fill price must be positive")
            
        self.status = OrderStatus.FILLED
        self.fill_price = price
        self.fill_timestamp = timestamp or datetime.now()
    
    def cancel(self) -> None:
        """Cancel the order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot cancel order with status {self.status}")
        self.status = OrderStatus.CANCELED
    
    def reject(self, reason: Optional[str] = None) -> None:
        """Reject the order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot reject order with status {self.status}")
        self.status = OrderStatus.REJECTED