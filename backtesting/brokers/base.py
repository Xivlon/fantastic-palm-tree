from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class BrokerOrder:
    """Represents an order in the broker system."""
    symbol: str
    quantity: int
    side: OrderSide
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_fill_price: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Position:
    """Represents a position in the broker account."""
    symbol: str
    quantity: int
    average_price: float
    market_value: float
    unrealized_pnl: float
    day_change: float
    day_change_percent: float


@dataclass
class AccountInfo:
    """Represents account information."""
    account_id: str
    total_value: float
    cash_balance: float
    buying_power: float
    day_trades_remaining: int
    positions: List[Position]


class BaseBroker(ABC):
    """Base broker interface."""
    
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.is_connected = False
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the broker API."""
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the broker API."""
        pass
        
    @abstractmethod
    async def get_account_info(self) -> AccountInfo:
        """Get account information."""
        pass
        
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get current positions."""
        pass
        
    @abstractmethod
    async def place_order(self, order: BrokerOrder) -> str:
        """Place an order. Returns order ID."""
        pass
        
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        pass
        
    @abstractmethod
    async def get_order_status(self, order_id: str) -> BrokerOrder:
        """Get order status."""
        pass
        
    @abstractmethod
    async def get_orders(self, symbol: Optional[str] = None) -> List[BrokerOrder]:
        """Get orders, optionally filtered by symbol."""
        pass
        
    @abstractmethod
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol."""
        pass
        
    @abstractmethod
    async def get_historical_data(self, symbol: str, period: str = "1d", 
                                 interval: str = "1m") -> List[Dict[str, Any]]:
        """Get historical market data."""
        pass