from datetime import datetime

import pandas as pd

from .data import DataHandler
from .portfolio import Portfolio
from .strategy import Strategy


class BacktestResults:
    """Container for backtest results."""

    def __init__(
        self,
        portfolio: Portfolio,
        strategy: Strategy,
        start_time: datetime,
        end_time: datetime,
    ):
        self.portfolio = portfolio
        self.strategy = strategy
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time

    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve as DataFrame."""
        if not self.portfolio.equity_curve:
            return pd.DataFrame()

        timestamps, values = zip(*self.portfolio.equity_curve, strict=False)
        return pd.DataFrame({"timestamp": timestamps, "equity": values}).set_index(
            "timestamp"
        )

    def get_trades(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        if not self.portfolio.trades:
            return pd.DataFrame()
        return pd.DataFrame(self.portfolio.trades)

    def get_orders(self) -> pd.DataFrame:
        """Get all orders as DataFrame."""
        if not self.portfolio.orders:
            return pd.DataFrame()

        orders_data = []
        for order in self.portfolio.orders:
            orders_data.append(
                {
                    "symbol": order.symbol,
                    "quantity": order.quantity,
                    "side": order.side,
                    "order_type": order.order_type.value,
                    "price": order.price,
                    "status": order.status.value,
                    "timestamp": order.timestamp,
                    "fill_price": order.fill_price,
                    "fill_timestamp": order.fill_timestamp,
                }
            )
        return pd.DataFrame(orders_data)


class BacktestEngine:
    """Main backtesting engine."""

    def __init__(self, initial_cash: float = 100000.0):
        self.initial_cash = initial_cash
        self.kill_switch_active = False
        self.kill_switch_triggers: list[callable] = []

    def add_kill_switch_trigger(self, trigger_func: callable) -> None:
        """Add a kill switch trigger function.

        Args:
            trigger_func: Function that takes (portfolio, current_prices) and returns bool
        """
        self.kill_switch_triggers.append(trigger_func)

    def check_kill_switch(
        self, portfolio: Portfolio, current_prices: dict[str, float]
    ) -> bool:
        """Check if any kill switch triggers are activated."""
        for trigger in self.kill_switch_triggers:
            if trigger(portfolio, current_prices):
                self.kill_switch_active = True
                return True
        return False

    def run(
        self, strategy: Strategy, data: pd.DataFrame, verbose: bool = False
    ) -> BacktestResults:
        """Run a backtest.

        Args:
            strategy: Strategy to test
            data: Market data DataFrame
            verbose: Print progress information

        Returns:
            BacktestResults object
        """
        start_time = datetime.now()

        # Initialize components
        portfolio = Portfolio(self.initial_cash)
        data_handler = DataHandler(data)

        # Setup strategy
        strategy.set_portfolio(portfolio)
        strategy.set_data_handler(data_handler)
        strategy.on_start()

        if verbose:
            print(f"Starting backtest for {strategy.name}")
            print(f"Initial cash: ${self.initial_cash:,.2f}")
            print(f"Data points: {len(data)}")

        step_count = 0

        # Main backtest loop
        while data_handler.has_data():
            current_data = data_handler.get_current_data()
            timestamp = current_data.get("timestamp")

            # Get current prices for all symbols
            current_prices = {}
            for symbol in data_handler.symbols:
                price = data_handler.get_price(symbol, "close")
                if price is not None:
                    current_prices[symbol] = price

            # Check kill switch
            if self.check_kill_switch(portfolio, current_prices):
                if verbose:
                    print(f"Kill switch activated at {timestamp}")
                break

            # Execute pending orders (simplified market orders)
            for order in portfolio.get_pending_orders():
                if order.symbol in current_prices:
                    execution_price = current_prices[order.symbol]

                    # For limit orders, check if price condition is met
                    if order.price is not None:
                        if order.side == "buy" and execution_price > order.price:
                            continue
                        if order.side == "sell" and execution_price < order.price:
                            continue

                    portfolio.execute_order(order, execution_price)

            # Update equity curve
            portfolio.update_equity_curve(timestamp, current_prices)

            # Call strategy
            strategy.on_data(timestamp, current_data)

            # Move to next data point
            data_handler.next()
            step_count += 1

            if verbose and step_count % 1000 == 0:
                total_value = portfolio.get_total_value(current_prices)
                print(f"Step {step_count}: Portfolio value: ${total_value:,.2f}")

        # Finish strategy
        strategy.on_finish()

        end_time = datetime.now()

        if verbose:
            final_value = portfolio.get_total_value(current_prices)
            total_return = (final_value - self.initial_cash) / self.initial_cash * 100
            print(f"Backtest completed in {end_time - start_time}")
            print(f"Final portfolio value: ${final_value:,.2f}")
            print(f"Total return: {total_return:.2f}%")
            print(f"Total trades: {len(portfolio.trades)}")

        return BacktestResults(portfolio, strategy, start_time, end_time)
