"""Tests for the MetricsPipeline."""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from backtesting.metrics.pipeline import MetricsPipeline
from backtesting.metrics.processors import EquityCurveProcessor, DrawdownProcessor, TradeListProcessor


class TestMetricsPipeline:
    """Test cases for MetricsPipeline."""
    
    def test_pipeline_initialization(self):
        """Test basic pipeline initialization."""
        pipeline = MetricsPipeline()
        
        # Check default processors are added
        assert len(pipeline.processor_names) == 3
        assert "equity_curve" in pipeline.processor_names
        assert "drawdown" in pipeline.processor_names
        assert "trade_list" in pipeline.processor_names
        assert not pipeline.is_initialized
        
        # Initialize
        pipeline.initialize(100000.0)
        assert pipeline.is_initialized
    
    def test_custom_processors(self):
        """Test pipeline with custom processors."""
        equity_processor = EquityCurveProcessor()
        pipeline = MetricsPipeline(processors=[equity_processor])
        
        assert len(pipeline.processor_names) == 1
        assert "equity_curve" in pipeline.processor_names
    
    def test_add_remove_processors(self):
        """Test adding and removing processors."""
        pipeline = MetricsPipeline()
        pipeline.initialize(100000.0)
        
        # Add a new processor
        new_processor = EquityCurveProcessor()
        new_processor.name = "custom_equity"
        pipeline.add_processor(new_processor)
        
        assert "custom_equity" in pipeline.processor_names
        assert pipeline.get_processor("custom_equity") is not None
        
        # Remove processor
        assert pipeline.remove_processor("custom_equity")
        assert "custom_equity" not in pipeline.processor_names
        assert not pipeline.remove_processor("nonexistent")
    
    def test_equity_curve_processing(self):
        """Test equity curve processing."""
        pipeline = MetricsPipeline()
        pipeline.initialize(100000.0)
        
        # Process some bars
        base_time = datetime(2024, 1, 1)
        pipeline.process_bar(base_time, 100000.0)
        pipeline.process_bar(base_time + timedelta(days=1), 105000.0)
        pipeline.process_bar(base_time + timedelta(days=2), 98000.0)
        
        # Get equity curve
        equity_curve = pipeline.get_equity_curve()
        assert len(equity_curve) == 4  # Including initialization
        assert equity_curve['equity'].iloc[-1] == 98000.0
        
        # Get summary metrics
        summary = pipeline.get_summary_metrics()
        assert summary['current_value'] == 98000.0
        assert summary['initial_value'] == 100000.0
        assert abs(summary['total_return'] - (-0.02)) < 1e-10  # -2% with floating point tolerance
    
    def test_drawdown_processing(self):
        """Test drawdown processing."""
        pipeline = MetricsPipeline()
        pipeline.initialize(100000.0)
        
        # Simulate equity changes
        base_time = datetime(2024, 1, 1)
        pipeline.process_bar(base_time, 100000.0)
        pipeline.process_bar(base_time + timedelta(days=1), 110000.0)  # New peak
        pipeline.process_bar(base_time + timedelta(days=2), 105000.0)  # Drawdown
        pipeline.process_bar(base_time + timedelta(days=3), 95000.0)   # Larger drawdown
        pipeline.process_bar(base_time + timedelta(days=4), 115000.0)  # Recovery to new peak
        
        # Check drawdown metrics
        summary = pipeline.get_summary_metrics()
        assert summary['max_drawdown'] < 0  # Should be negative
        assert abs(summary['max_drawdown']) > 0.13  # Should be > 13% (95k from 110k peak)
    
    def test_trade_processing(self):
        """Test trade processing."""
        pipeline = MetricsPipeline()
        pipeline.initialize(100000.0)
        
        # Process some trades
        trades = [
            {'symbol': 'AAPL', 'side': 'buy', 'quantity': 100, 'price': 150.0, 'pnl': 500.0},
            {'symbol': 'MSFT', 'side': 'sell', 'quantity': 50, 'price': 300.0, 'pnl': -200.0},
            {'symbol': 'GOOGL', 'side': 'buy', 'quantity': 25, 'price': 2500.0, 'pnl': 1000.0}
        ]
        
        for trade in trades:
            pipeline.process_trade(trade)
        
        # Check trade metrics
        summary = pipeline.get_summary_metrics()
        assert summary['total_trades'] == 3
        assert summary['winning_trades'] == 2
        assert summary['losing_trades'] == 1
        assert summary['win_rate'] == 2/3
        assert summary['total_pnl'] == 1300.0
        
        # Get trades dataframe
        trades_df = pipeline.get_trades()
        assert len(trades_df) == 3
        assert 'trade_id' in trades_df.columns
    
    def test_performance_metrics_conversion(self):
        """Test conversion to PerformanceMetrics."""
        pipeline = MetricsPipeline()
        pipeline.initialize(100000.0)
        
        # Add some data
        base_time = datetime(2024, 1, 1)
        pipeline.process_bar(base_time, 100000.0)
        pipeline.process_bar(base_time + timedelta(days=1), 105000.0)
        pipeline.process_bar(base_time + timedelta(days=2), 110000.0)
        
        # Add a trade
        pipeline.process_trade({
            'symbol': 'AAPL', 'side': 'buy', 'quantity': 100, 
            'price': 150.0, 'pnl': 500.0
        })
        
        # Convert to PerformanceMetrics
        metrics = pipeline.to_performance_metrics()
        
        assert metrics.total_return == 0.1  # 10%
        assert metrics.total_trades == 1
        assert metrics.winning_trades == 1
        assert metrics.losing_trades == 0
    
    def test_pipeline_reset(self):
        """Test pipeline reset functionality."""
        pipeline = MetricsPipeline()
        pipeline.initialize(100000.0)
        
        # Add some data
        pipeline.process_bar(datetime.now(), 105000.0)
        pipeline.process_trade({'symbol': 'AAPL', 'pnl': 500.0})
        
        # Verify data exists
        assert pipeline.get_summary_metrics()['current_value'] == 105000.0
        assert pipeline.get_summary_metrics()['total_trades'] == 1
        
        # Reset
        pipeline.reset()
        assert not pipeline.is_initialized
        
        # Re-initialize and verify clean state
        pipeline.initialize(100000.0)
        summary = pipeline.get_summary_metrics()
        assert summary['current_value'] == 100000.0
        assert summary['total_trades'] == 0


if __name__ == "__main__":
    # Run basic smoke test
    test = TestMetricsPipeline()
    test.test_pipeline_initialization()
    test.test_equity_curve_processing()
    test.test_trade_processing()
    print("Basic tests passed!")