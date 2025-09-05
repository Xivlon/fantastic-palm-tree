# MetricsPipeline Documentation

## Overview

The MetricsPipeline is a flexible and extensible abstraction for processing and aggregating per-trade and per-bar trading results in real-time. It allows for modular metric calculations and easy addition of new metrics.

## Architecture

### Core Components

1. **MetricsPipeline**: Main coordinator that manages metric processors
2. **MetricProcessor**: Base interface for individual metric processors  
3. **Core Processors**: Built-in processors for equity curve, drawdown, and trade list

### Built-in Processors

#### EquityCurveProcessor
Tracks portfolio value over time and provides basic return calculations.

**Metrics Provided:**
- `equity_curve`: DataFrame with timestamp and equity columns
- `total_return`: Overall return since start
- `current_value`: Current portfolio value
- `initial_value`: Starting portfolio value

#### DrawdownProcessor  
Calculates drawdown metrics in real-time as new data comes in.

**Metrics Provided:**
- `max_drawdown`: Maximum drawdown experienced (negative value)
- `max_drawdown_duration`: Maximum number of periods in drawdown
- `current_drawdown`: Current drawdown from peak
- `current_drawdown_duration`: Current periods in drawdown
- `drawdown_series`: Full drawdown time series

#### TradeListProcessor
Maintains a list of completed trades and calculates trade-based statistics.

**Metrics Provided:**
- `trades_df`: DataFrame with all trade data
- `total_trades`: Total number of trades
- `winning_trades`: Number of profitable trades
- `losing_trades`: Number of losing trades
- `win_rate`: Percentage of winning trades
- `avg_win`: Average profit per winning trade
- `avg_loss`: Average loss per losing trade
- `profit_factor`: Ratio of gross wins to gross losses
- `total_pnl`: Total profit and loss

## Usage

### Basic Usage

```python
from backtesting.metrics.pipeline import MetricsPipeline
from datetime import datetime

# Create pipeline with default processors
pipeline = MetricsPipeline()

# Initialize with starting cash
pipeline.initialize(100000.0)

# Process bars (called for each time period)
pipeline.process_bar(datetime.now(), 105000.0)

# Process trades (called when trades are completed)
pipeline.process_trade({
    'symbol': 'AAPL',
    'side': 'buy', 
    'quantity': 100,
    'price': 150.0,
    'pnl': 500.0
})

# Get summary metrics
summary = pipeline.get_summary_metrics()
print(f"Total Return: {summary['total_return']:.2%}")
print(f"Max Drawdown: {summary['max_drawdown']:.2%}")
print(f"Total Trades: {summary['total_trades']}")
```

### Integration with BacktestEngine

The pipeline can be integrated into the backtesting engine to provide real-time metrics:

```python
# In your backtest loop
for timestamp, portfolio_value in equity_data:
    pipeline.process_bar(timestamp, portfolio_value)

for trade in completed_trades:
    pipeline.process_trade(trade)

# Get final metrics
final_metrics = pipeline.to_performance_metrics()
```

### Extensibility - Adding Custom Processors

You can easily add custom metric processors by extending the `MetricProcessor` base class:

```python
from backtesting.metrics.processors.base import MetricProcessor

class SharpeRatioProcessor(MetricProcessor):
    def __init__(self, risk_free_rate=0.02):
        super().__init__("sharpe_ratio")
        self.risk_free_rate = risk_free_rate
        self._returns = []
    
    def initialize(self, initial_cash: float, **kwargs):
        self._returns = []
        self._initialized = True
    
    def process_bar(self, timestamp, portfolio_value, bar_data):
        # Calculate daily return and update Sharpe ratio
        if hasattr(self, '_prev_value'):
            daily_return = (portfolio_value - self._prev_value) / self._prev_value
            self._returns.append(daily_return)
        self._prev_value = portfolio_value
    
    def process_trade(self, trade):
        pass  # Sharpe ratio is calculated from returns, not trades
    
    def get_metrics(self):
        if len(self._returns) < 2:
            return {"sharpe_ratio": 0.0}
        
        import numpy as np
        returns = np.array(self._returns)
        excess_returns = returns - (self.risk_free_rate / 252)
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
        return {"sharpe_ratio": sharpe}

# Add to pipeline
pipeline = MetricsPipeline()
pipeline.add_processor(SharpeRatioProcessor())
```

## Compatibility

### MetricsCalculator Integration

The pipeline maintains compatibility with the existing `MetricsCalculator` by providing a conversion method:

```python
# Convert pipeline metrics to PerformanceMetrics object
performance_metrics = pipeline.to_performance_metrics()

# This returns the same PerformanceMetrics object that MetricsCalculator produces
print(performance_metrics.sharpe_ratio)
print(performance_metrics.max_drawdown)
```

### Data Access

The pipeline provides convenient methods to access data in familiar formats:

```python
# Get equity curve as DataFrame (same format as BacktestResults.get_equity_curve())
equity_df = pipeline.get_equity_curve()

# Get trades as DataFrame (same format as BacktestResults.get_trades())
trades_df = pipeline.get_trades()
```

## Advanced Features

### Processor Management

```python
# Add processors dynamically
pipeline.add_processor(CustomProcessor())

# Remove processors
pipeline.remove_processor("processor_name")

# Get specific processor
processor = pipeline.get_processor("equity_curve")

# List all processors
print(pipeline.processor_names)
```

### Custom Initialization

```python
# Pass custom parameters to processors during initialization
pipeline.initialize(
    initial_cash=100000.0,
    custom_param="value"
)
```

### Resetting State

```python
# Reset all processors to clean state
pipeline.reset()

# Re-initialize for new backtest
pipeline.initialize(new_cash_amount)
```

## Performance Considerations

- Processors are designed for real-time calculation with minimal overhead
- Memory usage scales with the number of bars and trades processed
- For very long backtests, consider periodically saving and clearing historical data

## Thread Safety

The current implementation is not thread-safe. For multi-threaded usage, implement appropriate locking mechanisms around pipeline operations.

## Future Extensions

The pipeline architecture easily supports additional processors for:

- **SharpeRatioProcessor**: Real-time Sharpe ratio calculation
- **SortinoRatioProcessor**: Sortino ratio with downside deviation
- **VaRProcessor**: Value at Risk calculations
- **CalmarRatioProcessor**: Calmar ratio (return/max drawdown)
- **BenchmarkProcessor**: Benchmark comparison metrics (alpha, beta, tracking error)
- **RiskMetricsProcessor**: Advanced risk metrics (volatility, skewness, kurtosis)

## Example: Complete Integration

See `examples/metrics_pipeline_extension.py` for a complete example showing:
- Custom processor implementation
- Pipeline integration
- Real-time metric calculation
- Compatibility with existing code