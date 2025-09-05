from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class RiskMetrics:
    """Container for risk-specific metrics."""

    value_at_risk_95: float
    conditional_var_95: float
    maximum_drawdown: float
    volatility: float
    downside_deviation: float
    beta: float | None = None

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "VaR 95%": self.value_at_risk_95 * 100,
            "CVaR 95%": self.conditional_var_95 * 100,
            "Max Drawdown": self.maximum_drawdown * 100,
            "Volatility": self.volatility * 100,
            "Downside Deviation": self.downside_deviation * 100,
            "Beta": self.beta or 0.0,
        }


class RiskCalculator:
    """Calculate various risk metrics."""

    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk."""
        return np.percentile(returns, (1 - confidence_level) * 100)

    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)."""
        var = RiskCalculator.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()

    @staticmethod
    def calculate_maximum_drawdown(equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown."""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()

    @staticmethod
    def calculate_downside_deviation(
        returns: pd.Series, target_return: float = 0
    ) -> float:
        """Calculate downside deviation."""
        downside_returns = returns[returns < target_return] - target_return
        return np.sqrt(np.mean(downside_returns**2))

    @staticmethod
    def calculate_rolling_var(
        returns: pd.Series, window: int = 252, confidence_level: float = 0.95
    ) -> pd.Series:
        """Calculate rolling Value at Risk."""
        return returns.rolling(window).quantile(1 - confidence_level)

    @staticmethod
    def calculate_stress_scenarios(returns: pd.Series) -> dict[str, float]:
        """Calculate returns under various stress scenarios."""
        scenarios = {
            "worst_day": returns.min(),
            "worst_week": returns.rolling(5).sum().min(),
            "worst_month": returns.rolling(21).sum().min(),
            "worst_quarter": returns.rolling(63).sum().min(),
            "tail_expectation_1pct": returns[returns <= returns.quantile(0.01)].mean(),
            "tail_expectation_5pct": returns[returns <= returns.quantile(0.05)].mean(),
        }
        return scenarios
