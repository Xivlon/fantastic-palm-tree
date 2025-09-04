import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json

from .base import BaseBroker, BrokerOrder, Position, AccountInfo, OrderStatus, OrderType, OrderSide
from .auth import SchwabAuth


class SchwabBroker(BaseBroker):
    """Schwab broker implementation."""
    
    def __init__(self, account_id: str, client_id: str, client_secret: str):
        super().__init__(account_id)
        self.auth = SchwabAuth(client_id, client_secret)
        self.base_url = "https://api.schwabapi.com/trader/v1"
        self.market_data_url = "https://api.schwabapi.com/marketdata/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
    async def connect(self) -> bool:
        """Connect to Schwab API."""
        try:
            # Create session
            self.session = aiohttp.ClientSession()
            
            # Ensure we have valid authentication
            if not await self.auth.ensure_valid_token():
                self.logger.error("Failed to authenticate with Schwab API")
                return False
                
            # Test connection with account info
            account_info = await self.get_account_info()
            if account_info:
                self.is_connected = True
                self.logger.info(f"Connected to Schwab API for account {self.account_id}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to connect to Schwab API: {e}")
            return False
            
    async def disconnect(self) -> None:
        """Disconnect from Schwab API."""
        if self.session:
            await self.session.close()
            self.session = None
        self.is_connected = False
        self.logger.info("Disconnected from Schwab API")
        
    async def _make_request(self, method: str, endpoint: str, 
                           params: Optional[Dict] = None,
                           data: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to Schwab API."""
        if not self.session:
            raise RuntimeError("Not connected to Schwab API")
            
        if not await self.auth.ensure_valid_token():
            raise RuntimeError("Unable to authenticate with Schwab API")
            
        url = f"{self.base_url}{endpoint}"
        headers = self.auth.get_auth_headers()
        
        try:
            async with self.session.request(
                method, url, headers=headers, params=params, json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    # Try to refresh token and retry once
                    if await self.auth.refresh_access_token():
                        headers = self.auth.get_auth_headers()
                        async with self.session.request(
                            method, url, headers=headers, params=params, json=data
                        ) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                            else:
                                error_text = await retry_response.text()
                                self.logger.error(f"API request failed after retry: {retry_response.status} - {error_text}")
                                return None
                    else:
                        self.logger.error("Failed to refresh token")
                        return None
                else:
                    error_text = await response.text()
                    self.logger.error(f"API request failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"API request error: {e}")
            return None
            
    async def get_account_info(self) -> Optional[AccountInfo]:
        """Get account information."""
        endpoint = f"/accounts/{self.account_id}"
        params = {"fields": "positions"}
        
        response = await self._make_request("GET", endpoint, params=params)
        if not response:
            return None
            
        try:
            account_data = response.get("securitiesAccount", {})
            
            # Parse positions
            positions = []
            for pos_data in account_data.get("positions", []):
                instrument = pos_data.get("instrument", {})
                symbol = instrument.get("symbol", "")
                
                position = Position(
                    symbol=symbol,
                    quantity=int(pos_data.get("longQuantity", 0)),
                    average_price=float(pos_data.get("averagePrice", 0)),
                    market_value=float(pos_data.get("marketValue", 0)),
                    unrealized_pnl=float(pos_data.get("currentDayProfitLoss", 0)),
                    day_change=float(pos_data.get("currentDayProfitLoss", 0)),
                    day_change_percent=float(pos_data.get("currentDayProfitLossPercentage", 0))
                )
                positions.append(position)
                
            # Parse account balances
            initial_balances = account_data.get("initialBalances", {})
            current_balances = account_data.get("currentBalances", {})
            
            return AccountInfo(
                account_id=self.account_id,
                total_value=float(current_balances.get("liquidationValue", 0)),
                cash_balance=float(current_balances.get("cashBalance", 0)),
                buying_power=float(current_balances.get("buyingPower", 0)),
                day_trades_remaining=int(account_data.get("roundTrips", 0)),
                positions=positions
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse account info: {e}")
            return None
            
    async def get_positions(self) -> List[Position]:
        """Get current positions."""
        account_info = await self.get_account_info()
        return account_info.positions if account_info else []
        
    async def place_order(self, order: BrokerOrder) -> Optional[str]:
        """Place an order."""
        endpoint = f"/accounts/{self.account_id}/orders"
        
        # Build order payload
        order_data = {
            "orderType": order.order_type.value,
            "session": "NORMAL",
            "duration": order.time_in_force,
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [{
                "instruction": order.side.value,
                "quantity": order.quantity,
                "instrument": {
                    "symbol": order.symbol,
                    "assetType": "EQUITY"  # Assuming equity for now
                }
            }]
        }
        
        # Add price for limit orders
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            order_data["price"] = order.price
            
        # Add stop price for stop orders
        if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
            order_data["stopPrice"] = order.stop_price
            
        response = await self._make_request("POST", endpoint, data=order_data)
        
        # Schwab returns order ID in Location header, but for simplicity
        # we'll return a success indicator
        if response is not None:
            # Generate a mock order ID since this is a scaffold
            order_id = f"SCHWAB_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{order.symbol}"
            return order_id
        return None
        
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        endpoint = f"/accounts/{self.account_id}/orders/{order_id}"
        
        response = await self._make_request("DELETE", endpoint)
        return response is not None
        
    async def get_order_status(self, order_id: str) -> Optional[BrokerOrder]:
        """Get order status."""
        endpoint = f"/accounts/{self.account_id}/orders/{order_id}"
        
        response = await self._make_request("GET", endpoint)
        if not response:
            return None
            
        # This is a simplified parser - real implementation would be more complex
        try:
            order_data = response
            leg = order_data.get("orderLegCollection", [{}])[0]
            instrument = leg.get("instrument", {})
            
            return BrokerOrder(
                symbol=instrument.get("symbol", ""),
                quantity=int(leg.get("quantity", 0)),
                side=OrderSide(leg.get("instruction", "BUY")),
                order_type=OrderType(order_data.get("orderType", "MARKET")),
                price=order_data.get("price"),
                order_id=order_id,
                status=OrderStatus(order_data.get("status", "PENDING")),
                filled_quantity=int(order_data.get("filledQuantity", 0)),
                average_fill_price=order_data.get("averageFilledPrice")
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse order status: {e}")
            return None
            
    async def get_orders(self, symbol: Optional[str] = None) -> List[BrokerOrder]:
        """Get orders, optionally filtered by symbol."""
        endpoint = f"/accounts/{self.account_id}/orders"
        
        response = await self._make_request("GET", endpoint)
        if not response:
            return []
            
        orders = []
        for order_data in response:
            try:
                leg = order_data.get("orderLegCollection", [{}])[0]
                instrument = leg.get("instrument", {})
                order_symbol = instrument.get("symbol", "")
                
                # Filter by symbol if specified
                if symbol and order_symbol != symbol:
                    continue
                    
                order = BrokerOrder(
                    symbol=order_symbol,
                    quantity=int(leg.get("quantity", 0)),
                    side=OrderSide(leg.get("instruction", "BUY")),
                    order_type=OrderType(order_data.get("orderType", "MARKET")),
                    price=order_data.get("price"),
                    order_id=str(order_data.get("orderId", "")),
                    status=OrderStatus(order_data.get("status", "PENDING")),
                    filled_quantity=int(order_data.get("filledQuantity", 0)),
                    average_fill_price=order_data.get("averageFilledPrice")
                )
                orders.append(order)
                
            except Exception as e:
                self.logger.error(f"Failed to parse order: {e}")
                continue
                
        return orders
        
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a symbol."""
        # Use market data endpoint
        url = f"{self.market_data_url}/quotes"
        params = {"symbols": symbol}
        headers = self.auth.get_auth_headers()
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get(symbol, {})
                else:
                    error_text = await response.text()
                    self.logger.error(f"Quote request failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Quote request error: {e}")
            return None
            
    async def get_historical_data(self, symbol: str, period: str = "1d", 
                                 interval: str = "1m") -> List[Dict[str, Any]]:
        """Get historical market data."""
        # This would use Schwab's price history endpoint
        url = f"{self.market_data_url}/pricehistory"
        params = {
            "symbol": symbol,
            "period": period,
            "frequency": interval
        }
        headers = self.auth.get_auth_headers()
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("candles", [])
                else:
                    error_text = await response.text()
                    self.logger.error(f"Historical data request failed: {response.status} - {error_text}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Historical data request error: {e}")
            return []