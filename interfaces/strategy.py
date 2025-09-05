"""
Strategy interface definition.

This module defines the minimal public interface that trading strategies
should implement for consistent interaction with the trading system.
"""

from typing import Protocol, Any, Dict, Optional, runtime_checkable
from abc import ABC, abstractmethod


@runtime_checkable
class StrategyProtocol(Protocol):
    """
    Minimal protocol for trading strategies.
    
    This protocol defines the essential interface that any trading strategy
    must implement to work with the trading system. Strategies can be
    implemented as classes or objects that satisfy this protocol.
    
    Extension Guidelines:
    - Implement signal generation in `on_data`
    - Use `on_start` for strategy initialization 
    - Use `on_finish` for cleanup and finalization
    - Keep strategy state minimal and well-defined
    
    Constraints:
    - `on_data` must be thread-safe if used in multi-threaded environments
    - Strategy should not directly access market data outside of provided callbacks
    - All parameters should be configurable via `set_params`
    """
    
    name: str
    """Strategy identifier name."""
    
    def on_data(self, timestamp: str, data: Dict[str, Any]) -> None:
        """
        Process new market data and generate trading signals.
        
        This is the core method where strategy logic is implemented.
        Strategies should analyze the provided data and make trading
        decisions by calling appropriate broker/portfolio methods.
        
        Args:
            timestamp: Current market timestamp (ISO format recommended)
            data: Market data dictionary containing OHLCV and derived indicators
            
        Constraints:
            - Must not block for extended periods
            - Should handle missing/invalid data gracefully
            - Must not raise exceptions that could halt the trading system
        """
        ...
    
    def on_start(self) -> None:
        """
        Initialize strategy before trading begins.
        
        Called once at the beginning of a trading session or backtest.
        Use this method to set up initial state, load historical data,
        or perform any required initialization.
        
        Constraints:
            - Should complete quickly to avoid delaying system startup
            - Must not access live market data directly
        """
        ...
    
    def on_finish(self) -> None:
        """
        Cleanup strategy after trading ends.
        
        Called once at the end of a trading session or backtest.
        Use this method to close positions, save state, or perform
        any required cleanup operations.
        
        Constraints:
            - Should handle cleanup gracefully even if strategy failed
            - Must not prevent system shutdown
        """
        ...
    
    def set_params(self, **params: Any) -> None:
        """
        Configure strategy parameters.
        
        Allows dynamic configuration of strategy parameters without
        reconstructing the strategy object. Parameters should be
        validated and applied immediately.
        
        Args:
            **params: Arbitrary strategy parameters
            
        Constraints:
            - Invalid parameters should raise ValueError with clear message
            - Parameters should take effect immediately or on next data point
            - Parameter changes should be logged for audit purposes
        """
        ...


class StrategyABC(ABC):
    """
    Abstract base class for trading strategies.
    
    Use this ABC when you need enforcement of strategy implementation
    or want to provide common functionality across strategies.
    
    This provides the same interface as StrategyProtocol but with
    stronger typing and enforcement through inheritance.
    """
    
    def __init__(self, name: str = "Strategy"):
        self.name = name
        self.params: Dict[str, Any] = {}
    
    @abstractmethod
    def on_data(self, timestamp: str, data: Dict[str, Any]) -> None:
        """Process new market data and generate trading signals."""
        pass
    
    def on_start(self) -> None:
        """Initialize strategy before trading begins."""
        pass
    
    def on_finish(self) -> None:
        """Cleanup strategy after trading ends."""
        pass
    
    def set_params(self, **params: Any) -> None:
        """Configure strategy parameters."""
        self.params.update(params)