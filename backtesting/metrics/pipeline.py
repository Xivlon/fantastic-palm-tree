"""MetricsPipeline for processing and aggregating per-trade and per-bar results."""

from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

from .processors.base import MetricProcessor
from .processors.equity import EquityCurveProcessor
from .processors.drawdown import DrawdownProcessor
from .processors.trades import TradeListProcessor
from .performance import PerformanceMetrics


class MetricsPipeline:
    """Pipeline for processing and aggregating trading metrics in real-time."""
    
    def __init__(self, processors: Optional[List[MetricProcessor]] = None):
        """Initialize the metrics pipeline.
        
        Args:
            processors: List of metric processors. If None, default processors are used.
        """
        if processors is None:
            # Default core processors
            self._processors = [
                EquityCurveProcessor(),
                DrawdownProcessor(),
                TradeListProcessor()
            ]
        else:
            self._processors = processors
        
        self._processor_map = {p.name: p for p in self._processors}
        self._initialized = False
    
    def add_processor(self, processor: MetricProcessor) -> None:
        """Add a processor to the pipeline.
        
        Args:
            processor: Metric processor to add
        """
        if processor.name in self._processor_map:
            raise ValueError(f"Processor with name '{processor.name}' already exists")
        
        self._processors.append(processor)
        self._processor_map[processor.name] = processor
        
        # Initialize if pipeline is already initialized
        if self._initialized:
            processor.initialize(self._initial_cash)
    
    def remove_processor(self, name: str) -> bool:
        """Remove a processor from the pipeline.
        
        Args:
            name: Name of the processor to remove
            
        Returns:
            True if processor was removed, False if not found
        """
        if name not in self._processor_map:
            return False
        
        processor = self._processor_map[name]
        self._processors.remove(processor)
        del self._processor_map[name]
        return True
    
    def get_processor(self, name: str) -> Optional[MetricProcessor]:
        """Get a processor by name.
        
        Args:
            name: Name of the processor
            
        Returns:
            The processor if found, None otherwise
        """
        return self._processor_map.get(name)
    
    def initialize(self, initial_cash: float, **kwargs) -> None:
        """Initialize all processors in the pipeline.
        
        Args:
            initial_cash: Starting cash amount
            **kwargs: Additional initialization parameters
        """
        self._initial_cash = initial_cash
        
        for processor in self._processors:
            processor.initialize(initial_cash, **kwargs)
        
        self._initialized = True
    
    def process_bar(self, timestamp: datetime, portfolio_value: float, 
                   bar_data: Optional[Dict[str, Any]] = None) -> None:
        """Process data for a single bar across all processors.
        
        Args:
            timestamp: Current timestamp
            portfolio_value: Current total portfolio value
            bar_data: Additional bar data (prices, volume, etc.)
        """
        if not self._initialized:
            raise RuntimeError("MetricsPipeline not initialized")
        
        if bar_data is None:
            bar_data = {}
        
        for processor in self._processors:
            processor.process_bar(timestamp, portfolio_value, bar_data)
    
    def process_trade(self, trade: Dict[str, Any]) -> None:
        """Process a completed trade across all processors.
        
        Args:
            trade: Trade data containing symbol, side, quantity, price, pnl, etc.
        """
        if not self._initialized:
            raise RuntimeError("MetricsPipeline not initialized")
        
        for processor in self._processors:
            processor.process_trade(trade)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics from all processors.
        
        Returns:
            Dictionary mapping processor names to their metrics
        """
        return {processor.name: processor.get_metrics() for processor in self._processors}
    
    def get_processor_metrics(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metrics from a specific processor.
        
        Args:
            name: Name of the processor
            
        Returns:
            Metrics dictionary if processor found, None otherwise
        """
        processor = self._processor_map.get(name)
        return processor.get_metrics() if processor else None
    
    def get_equity_curve(self) -> pd.DataFrame:
        """Get the equity curve data.
        
        Returns:
            DataFrame with equity curve data
        """
        equity_processor = self.get_processor("equity_curve")
        if equity_processor:
            metrics = equity_processor.get_metrics()
            return metrics.get("equity_curve", pd.DataFrame())
        return pd.DataFrame()
    
    def get_trades(self) -> pd.DataFrame:
        """Get the trades data.
        
        Returns:
            DataFrame with all trades
        """
        trade_processor = self.get_processor("trade_list")
        if trade_processor:
            metrics = trade_processor.get_metrics()
            return metrics.get("trades_df", pd.DataFrame())
        return pd.DataFrame()
    
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get a summary of key metrics across all processors.
        
        Returns:
            Dictionary containing key summary metrics
        """
        summary = {}
        
        # Equity metrics
        equity_metrics = self.get_processor_metrics("equity_curve")
        if equity_metrics:
            summary.update({
                "total_return": equity_metrics.get("total_return", 0.0),
                "current_value": equity_metrics.get("current_value", 0.0),
                "initial_value": equity_metrics.get("initial_value", 0.0)
            })
        
        # Drawdown metrics
        drawdown_metrics = self.get_processor_metrics("drawdown")
        if drawdown_metrics:
            summary.update({
                "max_drawdown": drawdown_metrics.get("max_drawdown", 0.0),
                "max_drawdown_duration": drawdown_metrics.get("max_drawdown_duration", 0),
                "current_drawdown": drawdown_metrics.get("current_drawdown", 0.0)
            })
        
        # Trade metrics
        trade_metrics = self.get_processor_metrics("trade_list")
        if trade_metrics:
            summary.update({
                "total_trades": trade_metrics.get("total_trades", 0),
                "winning_trades": trade_metrics.get("winning_trades", 0),
                "losing_trades": trade_metrics.get("losing_trades", 0),
                "win_rate": trade_metrics.get("win_rate", 0.0),
                "profit_factor": trade_metrics.get("profit_factor", 0.0),
                "total_pnl": trade_metrics.get("total_pnl", 0.0)
            })
        
        return summary
    
    def to_performance_metrics(self, benchmark: Optional[pd.Series] = None,
                             risk_free_rate: float = 0.02) -> PerformanceMetrics:
        """Convert pipeline metrics to PerformanceMetrics for compatibility.
        
        Args:
            benchmark: Optional benchmark series for beta/alpha calculation
            risk_free_rate: Risk-free rate for calculations
            
        Returns:
            PerformanceMetrics object
        """
        # Get basic metrics from processors
        equity_metrics = self.get_processor_metrics("equity_curve") or {}
        drawdown_metrics = self.get_processor_metrics("drawdown") or {}
        trade_metrics = self.get_processor_metrics("trade_list") or {}
        
        # Get equity curve for return calculations
        equity_curve = equity_metrics.get("equity_curve", pd.DataFrame())
        
        if equity_curve.empty:
            # Return empty metrics
            return PerformanceMetrics(
                total_return=0, annualized_return=0, cumulative_return=0,
                volatility=0, sharpe_ratio=0, sortino_ratio=0,
                max_drawdown=0, max_drawdown_duration=0,
                total_trades=0, winning_trades=0, losing_trades=0,
                win_rate=0, avg_win=0, avg_loss=0, profit_factor=0,
                calmar_ratio=0, var_95=0, cvar_95=0
            )
        
        # Calculate advanced metrics from equity curve
        returns = equity_curve['equity'].pct_change().dropna()
        
        # Time-based calculations
        days = len(equity_curve)
        years = days / 252 if days > 0 else 1
        
        total_return = equity_metrics.get("total_return", 0.0)
        annualized_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        # Risk metrics
        volatility = returns.std() * (252 ** 0.5) if len(returns) > 1 else 0
        
        # Sharpe ratio
        if len(returns) > 1 and returns.std() != 0:
            excess_returns = returns - risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * (252 ** 0.5)
        else:
            sharpe_ratio = 0
        
        # Sortino ratio
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() * (252 ** 0.5) if len(negative_returns) > 1 else 0
        sortino_ratio = (annualized_return - risk_free_rate) / downside_std if downside_std != 0 else 0
        
        # Calmar ratio
        max_drawdown = abs(drawdown_metrics.get("max_drawdown", 0.0))
        calmar_ratio = annualized_return / max_drawdown if max_drawdown != 0 else 0
        
        # VaR and CVaR
        import numpy as np
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
        cvar_95 = returns[returns <= var_95].mean() if len(returns) > 0 and len(returns[returns <= var_95]) > 0 else 0
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            cumulative_return=total_return,  # Same as total return for this implementation
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=drawdown_metrics.get("max_drawdown", 0.0),
            max_drawdown_duration=drawdown_metrics.get("max_drawdown_duration", 0),
            total_trades=trade_metrics.get("total_trades", 0),
            winning_trades=trade_metrics.get("winning_trades", 0),
            losing_trades=trade_metrics.get("losing_trades", 0),
            win_rate=trade_metrics.get("win_rate", 0.0),
            avg_win=trade_metrics.get("avg_win", 0.0),
            avg_loss=trade_metrics.get("avg_loss", 0.0),
            profit_factor=trade_metrics.get("profit_factor", 0.0),
            calmar_ratio=calmar_ratio,
            var_95=var_95,
            cvar_95=cvar_95
        )
    
    def reset(self) -> None:
        """Reset all processors in the pipeline."""
        for processor in self._processors:
            processor.reset()
        self._initialized = False
    
    @property
    def processor_names(self) -> List[str]:
        """Get names of all processors in the pipeline."""
        return list(self._processor_map.keys())
    
    @property
    def is_initialized(self) -> bool:
        """Check if pipeline is initialized."""
        return self._initialized