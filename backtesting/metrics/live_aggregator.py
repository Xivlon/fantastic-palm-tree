"""Live trading metrics aggregator for real-time performance tracking."""

import logging
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..brokers.base import BaseBroker


class LiveMetricsAggregator:
    """Aggregates and tracks metrics during live trading sessions."""
    
    def __init__(self, broker: BaseBroker, update_interval: int = 60):
        self.broker = broker
        self.update_interval = update_interval
        self.metrics_history: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        
        # Setup logging
        self.logger = logging.getLogger("LiveMetricsAggregator")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    async def update_metrics(self) -> Dict[str, Any]:
        """Update and calculate current metrics."""
        # Get current account info and positions
        account_info = await self.broker.get_account_info()
        positions = await self.broker.get_positions()
        orders = await self.broker.get_orders()
        
        # Calculate current metrics
        current_metrics = {
            'timestamp': datetime.now(),
            'cash_balance': account_info.cash_balance,
            'total_value': account_info.total_value,
            'unrealized_pnl': sum(pos.unrealized_pnl for pos in positions),
            'realized_pnl': account_info.total_value - account_info.cash_balance - sum(pos.market_value - pos.unrealized_pnl for pos in positions),
            'positions_count': len(positions),
            'orders_count': len([o for o in orders if o.status.name == 'PENDING']),
            'total_orders': len(orders)
        }
        
        # Add to history
        self.metrics_history.append(current_metrics)
        
        # Calculate performance metrics if we have enough data
        if len(self.metrics_history) > 1:
            performance_metrics = self._calculate_performance_metrics()
            current_metrics.update(performance_metrics)
        
        self.logger.info(f"Updated metrics: Total Value=${current_metrics['total_value']:,.2f}, "
                        f"Unrealized P&L=${current_metrics['unrealized_pnl']:,.2f}")
        
        return current_metrics
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics from history."""
        if len(self.metrics_history) < 2:
            return {}
        
        df = pd.DataFrame(self.metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Calculate returns
        returns = df['total_value'].pct_change().dropna()
        
        if len(returns) == 0:
            return {}
        
        # Basic performance metrics
        initial_value = df['total_value'].iloc[0]
        current_value = df['total_value'].iloc[-1]
        total_return = (current_value - initial_value) / initial_value
        
        # Risk metrics
        if len(returns) > 1:
            # Annualized metrics (assuming we update every minute for live trading)
            periods_per_year = 525600  # Minutes in a year
            update_periods_per_year = periods_per_year / self.update_interval
            
            mean_return = returns.mean()
            volatility = returns.std()
            
            # Annualized Sharpe ratio (assuming 0% risk-free rate for simplicity)
            sharpe_ratio = (mean_return * update_periods_per_year) / (volatility * (update_periods_per_year ** 0.5)) if volatility > 0 else 0
            
            # Drawdown calculation
            peak = df['total_value'].expanding().max()
            drawdown = (df['total_value'] - peak) / peak
            max_drawdown = drawdown.min()
            current_drawdown = drawdown.iloc[-1]
            
            # Sortino ratio (downside deviation)
            negative_returns = returns[returns < 0]
            downside_deviation = negative_returns.std() if len(negative_returns) > 0 else 0
            sortino_ratio = (mean_return * update_periods_per_year) / (downside_deviation * (update_periods_per_year ** 0.5)) if downside_deviation > 0 else 0
        else:
            sharpe_ratio = 0
            sortino_ratio = 0
            max_drawdown = 0
            current_drawdown = 0
            volatility = 0
        
        # Calculate session duration
        session_duration = (df.index[-1] - df.index[0]).total_seconds() / 3600  # Hours
        
        return {
            'total_return': total_return,
            'total_return_percent': total_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'max_drawdown_percent': max_drawdown * 100,
            'current_drawdown': current_drawdown,
            'current_drawdown_percent': current_drawdown * 100,
            'session_duration_hours': session_duration,
            'average_return_per_hour': total_return / session_duration if session_duration > 0 else 0
        }
    
    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve as DataFrame."""
        if not self.metrics_history:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df[['timestamp', 'total_value', 'unrealized_pnl', 'cash_balance']].copy()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the latest metrics."""
        if not self.metrics_history:
            return {}
        return self.metrics_history[-1].copy()
    
    def export_to_csv(self, output_dir: str = "live_trading_results") -> Dict[str, str]:
        """Export live trading metrics to CSV files."""
        if not self.metrics_history:
            return {}
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files_created = {}
        
        # Export metrics history (equity curve and performance)
        metrics_df = pd.DataFrame(self.metrics_history)
        metrics_file = output_path / f"live_metrics_{timestamp}.csv"
        metrics_df.to_csv(metrics_file, index=False)
        files_created['live_metrics'] = str(metrics_file)
        
        # Export current performance summary
        if len(self.metrics_history) > 1:
            latest_metrics = self.metrics_history[-1]
            summary_data = {
                'session_start': self.start_time,
                'session_end': latest_metrics['timestamp'],
                'duration_hours': (latest_metrics['timestamp'] - self.start_time).total_seconds() / 3600,
                **{k: v for k, v in latest_metrics.items() if k != 'timestamp'}
            }
            summary_df = pd.DataFrame([summary_data])
            summary_file = output_path / f"session_summary_{timestamp}.csv"
            summary_df.to_csv(summary_file, index=False)
            files_created['session_summary'] = str(summary_file)
        
        self.logger.info(f"Exported live trading metrics to {len(files_created)} files")
        return files_created
    
    def reset(self) -> None:
        """Reset the aggregator for a new session."""
        self.metrics_history.clear()
        self.start_time = datetime.now()
        self.logger.info("Metrics aggregator reset for new session")