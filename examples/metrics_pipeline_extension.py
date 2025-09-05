"""Example of extending MetricsPipeline with custom processors."""

import numpy as np
import pandas as pd
from typing import Any, Dict
from datetime import datetime

from backtesting.metrics.processors.base import MetricProcessor
from backtesting.metrics.pipeline import MetricsPipeline


class SharpeRatioProcessor(MetricProcessor):
    """Processor for calculating Sharpe ratio in real-time."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        super().__init__("sharpe_ratio")
        self.risk_free_rate = risk_free_rate
        self._returns = []
        self._current_sharpe = 0.0
    
    def initialize(self, initial_cash: float, **kwargs) -> None:
        """Initialize the Sharpe ratio processor."""
        self._returns = []
        self._current_sharpe = 0.0
        self._initialized = True
    
    def process_bar(self, timestamp: datetime, portfolio_value: float, 
                   bar_data: Dict[str, Any]) -> None:
        """Process a bar to update Sharpe ratio calculation."""
        if not self._initialized:
            raise RuntimeError("SharpeRatioProcessor not initialized")
        
        # Calculate return from previous value
        if len(self._returns) > 0 or hasattr(self, '_prev_value'):
            prev_value = getattr(self, '_prev_value', portfolio_value)
            if prev_value > 0:
                daily_return = (portfolio_value - prev_value) / prev_value
                self._returns.append(daily_return)
                
                # Calculate rolling Sharpe ratio
                self._calculate_sharpe()
        
        self._prev_value = portfolio_value
    
    def process_trade(self, trade: Dict[str, Any]) -> None:
        """Process a trade (Sharpe ratio is calculated on bar basis)."""
        pass
    
    def _calculate_sharpe(self) -> None:
        """Calculate current Sharpe ratio."""
        if len(self._returns) < 2:
            self._current_sharpe = 0.0
            return
        
        returns_array = np.array(self._returns)
        daily_rf_rate = self.risk_free_rate / 252
        
        excess_returns = returns_array - daily_rf_rate
        mean_excess = np.mean(excess_returns)
        std_excess = np.std(excess_returns, ddof=1)
        
        if std_excess > 0:
            self._current_sharpe = mean_excess / std_excess * np.sqrt(252)
        else:
            self._current_sharpe = 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Sharpe ratio metrics."""
        return {
            "sharpe_ratio": self._current_sharpe,
            "total_returns": len(self._returns),
            "returns_data": self._returns.copy()
        }
    
    def reset(self) -> None:
        """Reset the processor."""
        super().reset()
        self._returns = []
        self._current_sharpe = 0.0
        if hasattr(self, '_prev_value'):
            delattr(self, '_prev_value')


class SortinoRatioProcessor(MetricProcessor):
    """Processor for calculating Sortino ratio in real-time."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        super().__init__("sortino_ratio")
        self.risk_free_rate = risk_free_rate
        self._returns = []
        self._current_sortino = 0.0
    
    def initialize(self, initial_cash: float, **kwargs) -> None:
        """Initialize the Sortino ratio processor."""
        self._returns = []
        self._current_sortino = 0.0
        self._initialized = True
    
    def process_bar(self, timestamp: datetime, portfolio_value: float, 
                   bar_data: Dict[str, Any]) -> None:
        """Process a bar to update Sortino ratio calculation."""
        if not self._initialized:
            raise RuntimeError("SortinoRatioProcessor not initialized")
        
        # Calculate return from previous value
        if len(self._returns) > 0 or hasattr(self, '_prev_value'):
            prev_value = getattr(self, '_prev_value', portfolio_value)
            if prev_value > 0:
                daily_return = (portfolio_value - prev_value) / prev_value
                self._returns.append(daily_return)
                
                # Calculate rolling Sortino ratio
                self._calculate_sortino()
        
        self._prev_value = portfolio_value
    
    def process_trade(self, trade: Dict[str, Any]) -> None:
        """Process a trade (Sortino ratio is calculated on bar basis)."""
        pass
    
    def _calculate_sortino(self) -> None:
        """Calculate current Sortino ratio."""
        if len(self._returns) < 2:
            self._current_sortino = 0.0
            return
        
        returns_array = np.array(self._returns)
        daily_rf_rate = self.risk_free_rate / 252
        
        # Only consider negative returns for downside deviation
        negative_returns = returns_array[returns_array < daily_rf_rate]
        
        if len(negative_returns) == 0:
            # No negative returns, infinite Sortino ratio (capped for practical purposes)
            self._current_sortino = 10.0
            return
        
        mean_return = np.mean(returns_array)
        downside_std = np.std(negative_returns - daily_rf_rate, ddof=1)
        
        if downside_std > 0:
            self._current_sortino = (mean_return - daily_rf_rate) / downside_std * np.sqrt(252)
        else:
            self._current_sortino = 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Sortino ratio metrics."""
        return {
            "sortino_ratio": self._current_sortino,
            "total_returns": len(self._returns),
            "negative_returns_count": len([r for r in self._returns if r < 0])
        }
    
    def reset(self) -> None:
        """Reset the processor."""
        super().reset()
        self._returns = []
        self._current_sortino = 0.0
        if hasattr(self, '_prev_value'):
            delattr(self, '_prev_value')


def example_extended_pipeline():
    """Example of using MetricsPipeline with custom processors."""
    print("=== Extended MetricsPipeline Example ===")
    
    # Create pipeline with default processors
    pipeline = MetricsPipeline()
    
    # Add custom processors
    sharpe_processor = SharpeRatioProcessor(risk_free_rate=0.02)
    sortino_processor = SortinoRatioProcessor(risk_free_rate=0.02)
    
    pipeline.add_processor(sharpe_processor)
    pipeline.add_processor(sortino_processor)
    
    print(f"Pipeline processors: {pipeline.processor_names}")
    
    # Initialize
    pipeline.initialize(100000.0)
    
    # Simulate some market data
    values = [100000, 102000, 99000, 105000, 97000, 110000, 108000, 115000]
    base_time = datetime(2024, 1, 1)
    
    for i, value in enumerate(values):
        timestamp = datetime(2024, 1, 1 + i)
        pipeline.process_bar(timestamp, value)
        
        # Add some trades
        if i % 2 == 0 and i > 0:
            pnl = (value - values[i-1]) * 0.8  # Simulate trade PnL
            pipeline.process_trade({
                'symbol': f'STOCK_{i}',
                'side': 'buy' if pnl > 0 else 'sell',
                'quantity': 100,
                'price': value / 1000,
                'pnl': pnl
            })
    
    # Get all metrics
    all_metrics = pipeline.get_all_metrics()
    
    print("\n=== Summary Metrics ===")
    summary = pipeline.get_summary_metrics()
    for key, value in summary.items():
        print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")
    
    print("\n=== Custom Processor Metrics ===")
    sharpe_metrics = pipeline.get_processor_metrics("sharpe_ratio")
    print(f"Sharpe Ratio: {sharpe_metrics['sharpe_ratio']:.4f}")
    
    sortino_metrics = pipeline.get_processor_metrics("sortino_ratio")
    print(f"Sortino Ratio: {sortino_metrics['sortino_ratio']:.4f}")
    
    print("\n=== PerformanceMetrics Compatibility ===")
    perf_metrics = pipeline.to_performance_metrics()
    print(f"Total Return: {perf_metrics.total_return:.4f}")
    print(f"Max Drawdown: {perf_metrics.max_drawdown:.4f}")
    print(f"Win Rate: {perf_metrics.win_rate:.4f}")
    
    return pipeline


if __name__ == "__main__":
    example_extended_pipeline()