from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .data import DataHandler
from .portfolio import Portfolio


class Strategy(ABC):
    """Base strategy class for backtesting.
    
    All strategies should inherit from this class and implement the required methods.
    """
    
    def __init__(self, name: str = "Strategy"):
        self.name = name
        self.portfolio: Optional[Portfolio] = None
        self.data_handler: Optional[DataHandler] = None
        self.params: Dict[str, Any] = {}
        
    def set_portfolio(self, portfolio: Portfolio) -> None:
        """Set the portfolio for this strategy."""
        self.portfolio = portfolio
        
    def set_data_handler(self, data_handler: DataHandler) -> None:
        """Set the data handler for this strategy."""
        self.data_handler = data_handler
        
    def set_params(self, **params: Any) -> None:
        """Set strategy parameters."""
        self.params.update(params)
        
    @abstractmethod
    def on_data(self, timestamp: str, data: Dict[str, Any]) -> None:
        """Called when new data arrives.
        
        Args:
            timestamp: Current timestamp
            data: Market data for current timestamp
        """
        pass
        
    def on_start(self) -> None:
        """Called when backtest starts. Override for initialization logic."""
        pass
        
    def on_finish(self) -> None:
        """Called when backtest finishes. Override for cleanup logic."""
        pass
        
    def buy(self, symbol: str, quantity: int, price: Optional[float] = None) -> None:
        """Place a buy order."""
        if self.portfolio:
            self.portfolio.buy(symbol, quantity, price)
            
    def sell(self, symbol: str, quantity: int, price: Optional[float] = None) -> None:
        """Place a sell order."""
        if self.portfolio:
            self.portfolio.sell(symbol, quantity, price)