import numpy as np
import pandas as pd

from ..core.engine import BacktestResults
from .performance import PerformanceMetrics


class MetricsCalculator:
    """Calculate comprehensive performance metrics from backtest results."""

    @staticmethod
    def calculate(
        results: BacktestResults,
        benchmark: pd.Series | None = None,
        risk_free_rate: float = 0.02,
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics.

        Args:
            results: BacktestResults object
            benchmark: Optional benchmark series for beta/alpha calculation
            risk_free_rate: Risk-free rate for Sharpe ratio calculation

        Returns:
            PerformanceMetrics object
        """
        equity_curve = results.get_equity_curve()
        trades_df = results.get_trades()

        if equity_curve.empty:
            return MetricsCalculator._empty_metrics()

        # Calculate returns
        returns = equity_curve["equity"].pct_change().dropna()

        # Basic metrics
        total_return = (
            equity_curve["equity"].iloc[-1] / equity_curve["equity"].iloc[0]
        ) - 1
        cumulative_return = (
            equity_curve["equity"].iloc[-1] / results.portfolio.initial_cash - 1
        )

        # Annualized return
        days = len(equity_curve)
        years = days / 252  # Assuming 252 trading days per year
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        # Volatility
        volatility = returns.std() * np.sqrt(252)  # Annualized

        # Sharpe ratio
        excess_returns = returns - risk_free_rate / 252
        sharpe_ratio = (
            excess_returns.mean() / excess_returns.std() * np.sqrt(252)
            if excess_returns.std() != 0
            else 0
        )

        # Sortino ratio
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() * np.sqrt(252)
        sortino_ratio = (
            (annualized_return - risk_free_rate) / downside_std
            if downside_std != 0
            else 0
        )

        # Drawdown metrics
        max_drawdown, max_dd_duration = MetricsCalculator._calculate_drawdown_metrics(
            equity_curve["equity"]
        )

        # Trade metrics
        trade_metrics = MetricsCalculator._calculate_trade_metrics(trades_df)

        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # VaR and CVaR
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()

        # Benchmark metrics (if provided)
        beta, alpha, information_ratio, tracking_error = None, None, None, None
        if benchmark is not None:
            beta, alpha, information_ratio, tracking_error = (
                MetricsCalculator._calculate_benchmark_metrics(
                    returns, benchmark, risk_free_rate
                )
            )

        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            cumulative_return=cumulative_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            total_trades=trade_metrics["total_trades"],
            winning_trades=trade_metrics["winning_trades"],
            losing_trades=trade_metrics["losing_trades"],
            win_rate=trade_metrics["win_rate"],
            avg_win=trade_metrics["avg_win"],
            avg_loss=trade_metrics["avg_loss"],
            profit_factor=trade_metrics["profit_factor"],
            calmar_ratio=calmar_ratio,
            var_95=var_95,
            cvar_95=cvar_95,
            beta=beta,
            alpha=alpha,
            information_ratio=information_ratio,
            tracking_error=tracking_error,
        )

    @staticmethod
    def _calculate_drawdown_metrics(equity: pd.Series) -> tuple[float, int]:
        """Calculate maximum drawdown and duration."""
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        max_drawdown = drawdown.min()

        # Calculate max drawdown duration
        max_duration = 0
        current_duration = 0

        for dd in drawdown:
            if dd < 0:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0

        return max_drawdown, max_duration

    @staticmethod
    def _calculate_trade_metrics(trades_df: pd.DataFrame) -> dict:
        """Calculate trade-based metrics."""
        if trades_df.empty:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "profit_factor": 0,
            }

        # Group trades by symbol and calculate P&L for round trips
        # This is simplified - in practice you'd want more sophisticated trade matching
        total_trades = len(trades_df)

        # For simplicity, assume each trade pair (buy/sell) is a round trip
        total_trades // 2

        # Calculate basic trade stats (this is a simplified version)
        wins = trades_df[trades_df["side"] == "sell"]["value"].sum()
        losses = trades_df[trades_df["side"] == "buy"]["value"].sum()

        winning_trades = len(trades_df[(trades_df["side"] == "sell")])
        losing_trades = len(trades_df[(trades_df["side"] == "buy")])

        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        avg_win = wins / winning_trades if winning_trades > 0 else 0
        avg_loss = losses / losing_trades if losing_trades > 0 else 0
        profit_factor = wins / abs(losses) if losses != 0 else 0

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
        }

    @staticmethod
    def _calculate_benchmark_metrics(
        returns: pd.Series, benchmark: pd.Series, risk_free_rate: float
    ) -> tuple[float, float, float, float]:
        """Calculate benchmark-relative metrics."""
        # Align returns and benchmark
        aligned_data = pd.concat([returns, benchmark], axis=1, join="inner").dropna()
        if aligned_data.empty:
            return 0, 0, 0, 0

        strategy_returns = aligned_data.iloc[:, 0]
        benchmark_returns = aligned_data.iloc[:, 1]

        # Beta
        covariance = np.cov(strategy_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 0

        # Alpha
        strategy_mean = strategy_returns.mean() * 252
        benchmark_mean = benchmark_returns.mean() * 252
        alpha = strategy_mean - (
            risk_free_rate + beta * (benchmark_mean - risk_free_rate)
        )

        # Information ratio and tracking error
        excess_returns = strategy_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = (
            excess_returns.mean() / excess_returns.std() * np.sqrt(252)
            if excess_returns.std() != 0
            else 0
        )

        return beta, alpha, information_ratio, tracking_error

    @staticmethod
    def _empty_metrics() -> PerformanceMetrics:
        """Return empty metrics for failed backtests."""
        return PerformanceMetrics(
            total_return=0,
            annualized_return=0,
            cumulative_return=0,
            volatility=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            max_drawdown=0,
            max_drawdown_duration=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            avg_win=0,
            avg_loss=0,
            profit_factor=0,
            calmar_ratio=0,
            var_95=0,
            cvar_95=0,
        )
