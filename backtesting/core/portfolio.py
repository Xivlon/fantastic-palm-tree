from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .order import Order, OrderType, OrderStatus


class Position:
    """Represents a position in a security."""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0
        self.average_price = 0.0
        self.total_cost = 0.0
        
    def add_shares(self, quantity: int, price: float) -> None:
        """Add shares to the position."""
        if self.quantity == 0:
            self.average_price = price
            self.total_cost = quantity * price
        else:
            new_total_cost = self.total_cost + (quantity * price)
            new_quantity = self.quantity + quantity
            self.average_price = new_total_cost / new_quantity if new_quantity != 0 else 0
            self.total_cost = new_total_cost
        self.quantity += quantity
        
    def remove_shares(self, quantity: int) -> float:
        """Remove shares from the position. Returns realized P&L."""
        if quantity > self.quantity:
            raise ValueError(f"Cannot sell {quantity} shares, only have {self.quantity}")
            
        realized_pnl = 0.0
        if self.quantity > 0:
            cost_per_share = self.total_cost / self.quantity
            realized_pnl = quantity * (0 - cost_per_share)  # Will be calculated with actual sell price
            self.total_cost -= quantity * cost_per_share
            
        self.quantity -= quantity
        return realized_pnl
        
    def market_value(self, current_price: float) -> float:
        """Calculate current market value."""
        return self.quantity * current_price
        
    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L."""
        return self.market_value(current_price) - self.total_cost


class Portfolio:
    """Manages portfolio positions and cash."""
    
    def __init__(self, initial_cash: float = 100000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trades: List[Dict] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        
    def get_position(self, symbol: str) -> Position:
        """Get position for a symbol."""
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)
        return self.positions[symbol]
        
    def buy(self, symbol: str, quantity: int, price: Optional[float] = None) -> Order:
        """Place a buy order."""
        order = Order(
            symbol=symbol,
            quantity=quantity,
            order_type=OrderType.MARKET if price is None else OrderType.LIMIT,
            side='buy',
            price=price
        )
        self.orders.append(order)
        return order
        
    def sell(self, symbol: str, quantity: int, price: Optional[float] = None) -> Order:
        """Place a sell order."""
        order = Order(
            symbol=symbol,
            quantity=quantity,
            order_type=OrderType.MARKET if price is None else OrderType.LIMIT,
            side='sell',
            price=price
        )
        self.orders.append(order)
        return order
        
    def execute_order(self, order: Order, execution_price: float) -> None:
        """Execute an order at given price."""
        total_cost = order.quantity * execution_price
        
        if order.side == 'buy':
            if self.cash >= total_cost:
                self.cash -= total_cost
                position = self.get_position(order.symbol)
                position.add_shares(order.quantity, execution_price)
                order.fill(execution_price)
                
                self.trades.append({
                    'timestamp': order.fill_timestamp,
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': order.quantity,
                    'price': execution_price,
                    'value': total_cost
                })
            else:
                order.reject()
                
        elif order.side == 'sell':
            position = self.get_position(order.symbol)
            if position.quantity >= order.quantity:
                self.cash += total_cost
                position.remove_shares(order.quantity)
                order.fill(execution_price)
                
                self.trades.append({
                    'timestamp': order.fill_timestamp,
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': order.quantity,
                    'price': execution_price,
                    'value': total_cost
                })
            else:
                order.reject()
                
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value."""
        total = self.cash
        for symbol, position in self.positions.items():
            if symbol in current_prices and position.quantity > 0:
                total += position.market_value(current_prices[symbol])
        return total
        
    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders."""
        return [order for order in self.orders if order.status == OrderStatus.PENDING]
        
    def update_equity_curve(self, timestamp: datetime, current_prices: Dict[str, float]) -> None:
        """Update the equity curve with current portfolio value."""
        total_value = self.get_total_value(current_prices)
        self.equity_curve.append((timestamp, total_value))