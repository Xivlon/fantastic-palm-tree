from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class OrderType(Enum):
    """Order types supported by the system."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    """Order status values."""
    PENDING = "pending"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a trading order."""
    symbol: str
    quantity: int
    order_type: OrderType
    side: str  # 'buy' or 'sell'
    price: Optional[float] = None
    stop_price: Optional[float] = None
    timestamp: Optional[datetime] = None
    status: OrderStatus = OrderStatus.PENDING
    fill_price: Optional[float] = None
    fill_timestamp: Optional[datetime] = None
    order_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
            
    def fill(self, price: float, timestamp: Optional[datetime] = None) -> None:
        """Mark order as filled."""
        self.status = OrderStatus.FILLED
        self.fill_price = price
        self.fill_timestamp = timestamp or datetime.now()
        
    def cancel(self) -> None:
        """Cancel the order."""
        self.status = OrderStatus.CANCELED
        
    def reject(self) -> None:
        """Reject the order."""
        self.status = OrderStatus.REJECTED