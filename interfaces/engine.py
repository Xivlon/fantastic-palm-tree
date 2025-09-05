"""
Engine interface definition.

This module defines the minimal public interface for backtesting and
live trading engines that execute strategies.
"""

from typing import Protocol, Any, Dict, Optional, runtime_checkable
from abc import ABC, abstractmethod


@runtime_checkable
class EngineProtocol(Protocol):
    """
    Minimal protocol for trading engines.
    
    This protocol defines the essential interface for engines that execute
    trading strategies, whether for backtesting or live trading.
    
    Extension Guidelines:
    - Implement data feeding and order execution in `run`
    - Use dependency injection for strategy, data sources, and brokers
    - Support configurable execution parameters
    - Provide progress reporting for long-running operations
    
    Constraints:
    - Engine must be thread-safe for concurrent strategy execution
    - Must handle strategy errors gracefully without crashing
    - Should provide consistent behavior across different data sources
    - Must support clean shutdown and resource cleanup
    """
    
    def run(self, strategy: Any, **kwargs: Any) -> Any:
        """
        Execute a trading strategy.
        
        Core method that runs the trading strategy against market data,
        handling order execution, position management, and result collection.
        
        Args:
            strategy: Strategy object implementing StrategyProtocol
            **kwargs: Engine-specific configuration parameters
            
        Returns:
            Results object containing performance metrics and trade history
            
        Constraints:
            - Must call strategy lifecycle methods (on_start, on_data, on_finish)
            - Should handle data feed interruptions gracefully
            - Must track all orders and positions accurately
            - Should provide meaningful error messages on failure
        """
        ...
    
    def add_kill_switch(self, trigger: Any) -> None:
        """
        Add risk management trigger to halt execution.
        
        Allows registration of conditions that should immediately stop
        strategy execution to prevent excessive losses.
        
        Args:
            trigger: Callable that returns True when execution should stop
            
        Constraints:
            - Triggers must be checked on every data point
            - Must allow multiple triggers to be registered
            - Should log trigger activation for audit purposes
        """
        ...


class EngineABC(ABC):
    """
    Abstract base class for trading engines.
    
    Use this ABC when you need enforcement of engine implementation
    or want to provide common functionality across different engines.
    """
    
    def __init__(self):
        self.kill_switches: list = []
        self.is_running: bool = False
    
    @abstractmethod 
    def run(self, strategy: Any, **kwargs: Any) -> Any:
        """Execute a trading strategy."""
        pass
    
    def add_kill_switch(self, trigger: Any) -> None:
        """Add risk management trigger to halt execution."""
        self.kill_switches.append(trigger)
    
    def check_kill_switches(self, context: Dict[str, Any]) -> bool:
        """
        Check if any kill switch conditions are met.
        
        Args:
            context: Current state including portfolio, prices, etc.
            
        Returns:
            True if execution should be halted
        """
        for trigger in self.kill_switches:
            try:
                if trigger(context):
                    return True
            except Exception:
                # Don't let kill switch errors crash the engine
                continue
        return False