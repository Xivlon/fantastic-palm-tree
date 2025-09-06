"""Paper broker implementation for testing and simulation."""

import logging
from datetime import datetime
from typing import Any

from .base import (
    AccountInfo,
    BaseBroker,
    BrokerOrder,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
)


class PaperBroker(BaseBroker):
    """Paper trading broker that logs orders instead of executing them."""

    def __init__(self, account_id: str, initial_cash: float = 100000.0):
        super().__init__(account_id)
        self.initial_cash = initial_cash
        self.cash_balance = initial_cash
        self.positions: dict[str, Position] = {}
        self.orders: list[BrokerOrder] = []
        self.order_counter = 0
        
        # Setup logging
        self.logger = logging.getLogger(f"PaperBroker-{account_id}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def connect(self) -> bool:
        """Connect to the paper broker (always succeeds)."""
        self.is_connected = True
        self.logger.info(f"Paper broker connected for account {self.account_id}")
        return True

    async def disconnect(self) -> None:
        """Disconnect from the paper broker."""
        self.is_connected = False
        self.logger.info(f"Paper broker disconnected for account {self.account_id}")

    async def get_account_info(self) -> AccountInfo:
        """Get account information."""
        total_value = self.cash_balance
        for position in self.positions.values():
            total_value += position.market_value
            
        return AccountInfo(
            account_id=self.account_id,
            total_value=total_value,
            cash_balance=self.cash_balance,
            buying_power=self.cash_balance,
            day_trades_remaining=3,  # Mock value
            positions=list(self.positions.values()),
        )

    async def get_positions(self) -> list[Position]:
        """Get current positions."""
        return list(self.positions.values())

    async def place_order(self, order: BrokerOrder) -> str:
        """Place an order (logs the order)."""
        self.order_counter += 1
        order_id = f"PAPER_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.order_counter:04d}"
        
        # Update order with ID and status
        order.order_id = order_id
        order.status = OrderStatus.FILLED  # For simplicity, instantly fill orders
        order.filled_quantity = order.quantity
        order.average_fill_price = order.price or 100.0  # Default price if not specified
        
        # Log the order
        self.logger.info(
            f"ORDER PLACED: {order.side.value} {order.quantity} {order.symbol} "
            f"@ ${order.average_fill_price:.2f} (Order ID: {order_id})"
        )
        
        # Simulate filling the order by updating positions and cash
        self._simulate_fill(order)
        
        # Store the order
        self.orders.append(order)
        
        return order_id

    def _simulate_fill(self, order: BrokerOrder) -> None:
        """Simulate filling an order by updating positions and cash."""
        fill_price = order.average_fill_price or 100.0
        total_cost = order.quantity * fill_price
        
        if order.side == OrderSide.BUY:
            # Check if we have enough cash
            if total_cost > self.cash_balance:
                self.logger.warning(
                    f"Insufficient cash for order {order.order_id}. "
                    f"Required: ${total_cost:.2f}, Available: ${self.cash_balance:.2f}"
                )
                order.status = OrderStatus.REJECTED
                return
                
            # Deduct cash
            self.cash_balance -= total_cost
            
            # Update or create position
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                total_value = (pos.quantity * pos.average_price) + total_cost
                new_quantity = pos.quantity + order.quantity
                pos.average_price = total_value / new_quantity
                pos.quantity = new_quantity
                pos.market_value = new_quantity * fill_price
                pos.unrealized_pnl = (fill_price - pos.average_price) * new_quantity
            else:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    average_price=fill_price,
                    market_value=order.quantity * fill_price,
                    unrealized_pnl=0.0,
                    day_change=0.0,
                    day_change_percent=0.0,
                )
                
        elif order.side == OrderSide.SELL:
            # Check if we have the position
            if order.symbol not in self.positions:
                self.logger.warning(
                    f"No position found for {order.symbol} to sell (Order: {order.order_id})"
                )
                order.status = OrderStatus.REJECTED
                return
                
            pos = self.positions[order.symbol]
            if pos.quantity < order.quantity:
                self.logger.warning(
                    f"Insufficient shares to sell {order.symbol}. "
                    f"Required: {order.quantity}, Available: {pos.quantity}"
                )
                order.status = OrderStatus.REJECTED
                return
                
            # Add cash from sale
            self.cash_balance += total_cost
            
            # Update position
            pos.quantity -= order.quantity
            if pos.quantity == 0:
                # Close position
                del self.positions[order.symbol]
            else:
                pos.market_value = pos.quantity * fill_price
                pos.unrealized_pnl = (fill_price - pos.average_price) * pos.quantity

        self.logger.info(
            f"ORDER FILLED: {order.side.value} {order.quantity} {order.symbol} "
            f"@ ${fill_price:.2f}. Cash balance: ${self.cash_balance:.2f}"
        )

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        for order in self.orders:
            if order.order_id == order_id and order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CANCELED
                self.logger.info(f"ORDER CANCELED: {order_id}")
                return True
        
        self.logger.warning(f"Could not cancel order {order_id} (not found or already filled)")
        return False

    async def get_order_status(self, order_id: str) -> BrokerOrder | None:
        """Get order status."""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    async def get_orders(self, symbol: str | None = None) -> list[BrokerOrder]:
        """Get orders, optionally filtered by symbol."""
        if symbol is None:
            return self.orders.copy()
        return [order for order in self.orders if order.symbol == symbol]

    async def get_quote(self, symbol: str) -> dict[str, Any] | None:
        """Get real-time quote for a symbol (mock implementation)."""
        # For paper trading, we'll return a mock quote
        # In a real implementation, this would connect to a data provider
        self.logger.info(f"QUOTE REQUEST: {symbol} (returning mock data)")
        return {
            "symbol": symbol,
            "price": 100.0,  # Mock price
            "bid": 99.95,
            "ask": 100.05,
            "volume": 1000000,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_historical_data(
        self, symbol: str, period: str = "1d", interval: str = "1m"
    ) -> list[dict[str, Any]]:
        """Get historical market data (mock implementation)."""
        self.logger.info(
            f"HISTORICAL DATA REQUEST: {symbol}, period={period}, interval={interval}"
        )
        # Return mock historical data
        base_time = datetime.now()
        return [
            {
                "timestamp": base_time.isoformat(),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.5,
                "volume": 100000,
            }
        ]

    def update_market_prices(self, prices: dict[str, float]) -> None:
        """Update market prices for positions (for P&L calculation)."""
        for symbol, price in prices.items():
            if symbol in self.positions:
                pos = self.positions[symbol]
                old_market_value = pos.market_value
                pos.market_value = pos.quantity * price
                pos.unrealized_pnl = (price - pos.average_price) * pos.quantity
                pos.day_change = pos.market_value - old_market_value
                if old_market_value != 0:
                    pos.day_change_percent = (pos.day_change / old_market_value) * 100
                else:
                    pos.day_change_percent = 0.0