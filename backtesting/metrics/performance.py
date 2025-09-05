from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    # Return metrics
    total_return: float
    annualized_return: float
    cumulative_return: float

    # Risk metrics
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int

    # Trade metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float

    # Risk-adjusted metrics
    calmar_ratio: float
    var_95: float  # Value at Risk (95%)
    cvar_95: float  # Conditional Value at Risk (95%)

    # Additional metrics
    beta: float | None = None
    alpha: float | None = None
    information_ratio: float | None = None
    tracking_error: float | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "Total Return (%)": self.total_return * 100,
            "Annualized Return (%)": self.annualized_return * 100,
            "Volatility (%)": self.volatility * 100,
            "Sharpe Ratio": self.sharpe_ratio,
            "Sortino Ratio": self.sortino_ratio,
            "Max Drawdown (%)": self.max_drawdown * 100,
            "Max DD Duration (days)": self.max_drawdown_duration,
            "Total Trades": self.total_trades,
            "Win Rate (%)": self.win_rate * 100,
            "Profit Factor": self.profit_factor,
            "Calmar Ratio": self.calmar_ratio,
            "VaR 95% (%)": self.var_95 * 100,
            "CVaR 95% (%)": self.cvar_95 * 100,
        }

    def __str__(self) -> str:
        """String representation."""
        lines = ["Performance Metrics:"]
        for key, value in self.to_dict().items():
            if isinstance(value, float):
                lines.append(f"  {key}: {value:.2f}")
            else:
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)
