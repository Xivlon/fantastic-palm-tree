"""
Example usage of the Fantastic Palm Tree backtesting framework.

This script demonstrates:
1. Creating a simple moving average crossover strategy
2. Running a backtest with kill switches
3. Parameter optimization
4. Metrics calculation and reporting
"""

from datetime import datetime

import numpy as np
import pandas as pd

from backtesting import (
    BacktestEngine,
    GridSearchOptimizer,
    MetricsCalculator,
    ParameterSpace,
    Strategy,
    create_default_kill_switches,
)


class MovingAverageCrossoverStrategy(Strategy):
    """Simple moving average crossover strategy."""

    def __init__(self, name="MA Crossover"):
        super().__init__(name)
        self.short_window = 10
        self.long_window = 30
        self.position = 0  # 0 = no position, 1 = long, -1 = short

    def set_params(self, **params):
        """Set strategy parameters."""
        super().set_params(**params)
        self.short_window = params.get("short_window", self.short_window)
        self.long_window = params.get("long_window", self.long_window)

    def on_data(self, timestamp, data):
        """Strategy logic - called for each data point."""
        # Get symbol data (assuming we're trading AAPL)
        symbol = "AAPL"
        if symbol not in data:
            return

        symbol_data = data[symbol]
        current_price = symbol_data.get("close")
        if current_price is None:
            return

        # Get historical data for moving averages
        if self.data_handler:
            hist_data = self.data_handler.get_historical_data(
                symbol, max(self.short_window, self.long_window) + 5
            )

            if len(hist_data) < self.long_window:
                return  # Not enough data

            # Calculate moving averages
            short_ma = hist_data["close"].rolling(self.short_window).mean().iloc[-1]
            long_ma = hist_data["close"].rolling(self.long_window).mean().iloc[-1]

            # Trading logic
            if self.position <= 0 and short_ma > long_ma:
                # Buy signal
                if self.position == -1:
                    # Close short position first
                    self.sell(symbol, 100)
                # Open long position
                self.buy(symbol, 100)
                self.position = 1

            elif self.position >= 0 and short_ma < long_ma:
                # Sell signal
                if self.position == 1:
                    # Close long position first
                    self.sell(symbol, 100)
                # Open short position (if allowed)
                # self.sell(symbol, 100)  # Uncomment for short selling
                self.position = -1


def create_sample_data():
    """Create sample market data for demonstration."""
    # Generate sample price data
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")

    # Simulate price movement
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices = [100.0]  # Starting price

    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))

    # Create DataFrame with OHLCV data
    data = pd.DataFrame(
        {
            "AAPL_open": [p * np.random.uniform(0.99, 1.01) for p in prices],
            "AAPL_high": [p * np.random.uniform(1.00, 1.03) for p in prices],
            "AAPL_low": [p * np.random.uniform(0.97, 1.00) for p in prices],
            "AAPL_close": prices,
            "AAPL_volume": np.random.randint(1000000, 10000000, len(dates)),
        },
        index=dates,
    )

    return data


def run_simple_backtest():
    """Run a simple backtest with kill switches."""
    print("=" * 60)
    print("SIMPLE BACKTEST EXAMPLE")
    print("=" * 60)

    # Create sample data
    data = create_sample_data()
    print(f"Created sample data: {len(data)} days")

    # Create strategy
    strategy = MovingAverageCrossoverStrategy()
    strategy.set_params(short_window=10, long_window=30)

    # Create backtest engine with kill switches
    engine = BacktestEngine(initial_cash=100000)
    kill_switches = create_default_kill_switches(
        max_drawdown=0.15,  # 15% max drawdown
        max_loss=20000,  # $20k max loss
        max_volatility=0.40,  # 40% max volatility
    )

    # Add kill switch triggers to engine
    for trigger in kill_switches.triggers:
        engine.add_kill_switch_trigger(
            lambda portfolio, prices, trigger=trigger: trigger.check(
                portfolio, prices, datetime.now()
            )
        )

    # Run backtest
    print("Running backtest...")
    results = engine.run(strategy, data, verbose=True)

    # Calculate metrics
    print("\nCalculating metrics...")
    metrics = MetricsCalculator.calculate(results)
    print(metrics)

    # Check if kill switch was activated
    if engine.kill_switch_active:
        print("\n⚠️  KILL SWITCH ACTIVATED")

    return results, metrics


def run_parameter_optimization():
    """Run parameter optimization example."""
    print("\n" + "=" * 60)
    print("PARAMETER OPTIMIZATION EXAMPLE")
    print("=" * 60)

    # Create sample data
    data = create_sample_data()

    # Define parameter space
    param_space = ParameterSpace()
    param_space.add_parameter("short_window", [5, 10, 15, 20])
    param_space.add_parameter("long_window", [25, 30, 35, 40])

    print(f"Parameter space size: {param_space.size()} combinations")

    # Create optimizer
    engine = BacktestEngine(initial_cash=100000)
    optimizer = GridSearchOptimizer(
        engine=engine,
        strategy_class=MovingAverageCrossoverStrategy,
        max_workers=2,  # Use 2 workers for parallel processing
    )

    # Run optimization
    print("Running parameter optimization...")
    optimization_results = optimizer.optimize(data, param_space, verbose=True)

    # Print results
    print("\nOptimization Results:")
    print(optimization_results.summary())

    # Get top results
    top_results = optimization_results.get_top_n_results(3)
    print("\nTop 3 parameter combinations:")
    for i, result in enumerate(top_results, 1):
        print(f"{i}. Parameters: {result['parameters']}")
        print(f"   Sharpe Ratio: {result['objective_value']:.3f}")
        if result["metrics"]:
            print(f"   Total Return: {result['metrics'].total_return:.2%}")
            print(f"   Max Drawdown: {result['metrics'].max_drawdown:.2%}")
        print()

    return optimization_results


async def broker_integration_example():
    """Example of broker integration (requires actual Schwab credentials)."""
    print("\n" + "=" * 60)
    print("BROKER INTEGRATION EXAMPLE")
    print("=" * 60)

    # This is just a scaffold example - would need real credentials
    from backtesting.brokers import SchwabBroker

    # Initialize broker (would need real credentials)
    SchwabBroker(
        account_id="123456789",
        client_id="your_client_id",
        client_secret="your_client_secret",
    )

    print("Schwab broker initialized (scaffold)")
    print("In a real implementation, you would:")
    print("1. Set up OAuth authentication")
    print("2. Connect to the API")
    print("3. Get account information")
    print("4. Place orders")
    print("5. Monitor positions")

    # Example of what the API calls would look like:
    """
    # Connect to broker
    await broker.connect()

    # Get account info
    account_info = await broker.get_account_info()
    print(f"Account Value: ${account_info.total_value:,.2f}")

    # Get current positions
    positions = await broker.get_positions()
    for pos in positions:
        print(f"{pos.symbol}: {pos.quantity} shares @ ${pos.average_price:.2f}")

    # Place an order
    from backtesting.brokers.base import BrokerOrder, OrderType, OrderSide
    order = BrokerOrder(
        symbol="AAPL",
        quantity=100,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET
    )
    order_id = await broker.place_order(order)
    print(f"Order placed: {order_id}")

    # Disconnect
    await broker.disconnect()
    """


def main():
    """Main example function."""
    print("Fantastic Palm Tree Backtesting Framework")
    print("Advanced Backtesting with Kill Switches and Parameter Optimization")
    print()

    # Run simple backtest
    results, metrics = run_simple_backtest()

    # Run parameter optimization
    run_parameter_optimization()

    # Show broker integration example
    import asyncio

    asyncio.run(broker_integration_example())

    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETED")
    print("=" * 60)
    print("This framework provides:")
    print("✓ Advanced backtest architecture")
    print("✓ Comprehensive performance metrics")
    print("✓ Parameter sweep optimization")
    print("✓ Kill-switch risk management")
    print("✓ Schwab broker integration scaffold")


if __name__ == "__main__":
    main()
