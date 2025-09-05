"""Base interface for metric processors."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd
from datetime import datetime


class MetricProcessor(ABC):
    """Base class for metric processors in the pipeline."""
    
    def __init__(self, name: str):
        """Initialize the processor.
        
        Args:
            name: Name of the metric processor
        """
        self.name = name
        self._initialized = False
    
    @abstractmethod
    def initialize(self, initial_cash: float, **kwargs) -> None:
        """Initialize the processor with starting parameters.
        
        Args:
            initial_cash: Starting cash amount
            **kwargs: Additional initialization parameters
        """
        pass
    
    @abstractmethod
    def process_bar(self, timestamp: datetime, portfolio_value: float, 
                   bar_data: Dict[str, Any]) -> None:
        """Process data for a single bar/time period.
        
        Args:
            timestamp: Current timestamp
            portfolio_value: Current total portfolio value
            bar_data: Additional bar data (prices, volume, etc.)
        """
        pass
    
    @abstractmethod
    def process_trade(self, trade: Dict[str, Any]) -> None:
        """Process a completed trade.
        
        Args:
            trade: Trade data containing symbol, side, quantity, price, etc.
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics from this processor.
        
        Returns:
            Dictionary containing computed metrics
        """
        pass
    
    def reset(self) -> None:
        """Reset the processor to initial state."""
        self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if processor is initialized."""
        return self._initialized