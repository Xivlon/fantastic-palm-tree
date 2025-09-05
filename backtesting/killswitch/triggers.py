from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import numpy as np

from ..core.portfolio import Portfolio


class KillSwitchTrigger(ABC):
    """Base class for kill switch triggers."""

    def __init__(self, name: str):
        self.name = name
        self.activated = False
        self.activation_time: datetime | None = None
        self.activation_reason: str | None = None

    @abstractmethod
    def check(
        self,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> bool:
        """Check if trigger condition is met."""
        pass

    def activate(self, reason: str, timestamp: datetime) -> None:
        """Activate the trigger."""
        self.activated = True
        self.activation_time = timestamp
        self.activation_reason = reason

    def reset(self) -> None:
        """Reset the trigger."""
        self.activated = False
        self.activation_time = None
        self.activation_reason = None


class DrawdownTrigger(KillSwitchTrigger):
    """Trigger based on maximum drawdown."""

    def __init__(self, max_drawdown: float = 0.20, name: str = "DrawdownTrigger"):
        super().__init__(name)
        self.max_drawdown = max_drawdown
        self.equity_history: list[tuple] = []

    def check(
        self,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> bool:
        """Check if drawdown exceeds threshold."""
        if self.activated:
            return True

        current_value = portfolio.get_total_value(current_prices)
        self.equity_history.append((timestamp, current_value))

        if len(self.equity_history) < 2:
            return False

        # Calculate drawdown
        values = [val for _, val in self.equity_history]
        peak = max(values)
        current_drawdown = (peak - current_value) / peak

        if current_drawdown >= self.max_drawdown:
            reason = (
                f"Drawdown {current_drawdown:.2%} exceeds limit {self.max_drawdown:.2%}"
            )
            self.activate(reason, timestamp)
            return True

        return False


class VolatilityTrigger(KillSwitchTrigger):
    """Trigger based on portfolio volatility."""

    def __init__(
        self,
        max_volatility: float = 0.50,
        lookback_days: int = 30,
        name: str = "VolatilityTrigger",
    ):
        super().__init__(name)
        self.max_volatility = max_volatility
        self.lookback_days = lookback_days
        self.return_history: list[tuple] = []

    def check(
        self,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> bool:
        """Check if volatility exceeds threshold."""
        if self.activated:
            return True

        current_value = portfolio.get_total_value(current_prices)

        # Calculate return if we have previous value
        if self.return_history:
            prev_value = self.return_history[-1][1]
            if prev_value > 0:
                daily_return = (current_value - prev_value) / prev_value
                self.return_history.append((timestamp, current_value, daily_return))
        else:
            self.return_history.append((timestamp, current_value, 0.0))

        # Keep only recent history
        cutoff_date = timestamp - timedelta(days=self.lookback_days)
        self.return_history = [
            (t, v, r) for t, v, r in self.return_history if t >= cutoff_date
        ]

        if len(self.return_history) < 10:  # Need minimum observations
            return False

        # Calculate volatility
        returns = [r for _, _, r in self.return_history[1:]]  # Skip first with 0 return
        volatility = np.std(returns) * np.sqrt(252)  # Annualized

        if volatility >= self.max_volatility:
            reason = (
                f"Volatility {volatility:.2%} exceeds limit {self.max_volatility:.2%}"
            )
            self.activate(reason, timestamp)
            return True

        return False


class LossTrigger(KillSwitchTrigger):
    """Trigger based on absolute loss amount."""

    def __init__(self, max_loss: float, name: str = "LossTrigger"):
        super().__init__(name)
        self.max_loss = max_loss

    def check(
        self,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> bool:
        """Check if loss exceeds threshold."""
        if self.activated:
            return True

        current_value = portfolio.get_total_value(current_prices)
        loss = portfolio.initial_cash - current_value

        if loss >= self.max_loss:
            reason = f"Loss ${loss:,.2f} exceeds limit ${self.max_loss:,.2f}"
            self.activate(reason, timestamp)
            return True

        return False


class TimeBasedTrigger(KillSwitchTrigger):
    """Trigger based on time conditions."""

    def __init__(
        self,
        start_time: str = "09:30",
        end_time: str = "16:00",
        trading_days_only: bool = True,
        name: str = "TimeBasedTrigger",
    ):
        super().__init__(name)
        self.start_time = datetime.strptime(start_time, "%H:%M").time()
        self.end_time = datetime.strptime(end_time, "%H:%M").time()
        self.trading_days_only = trading_days_only

    def check(
        self,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> bool:
        """Check if outside trading hours."""
        if self.activated:
            return True

        current_time = timestamp.time()

        # Check if outside trading hours
        if current_time < self.start_time or current_time > self.end_time:
            reason = f"Outside trading hours {self.start_time}-{self.end_time}"
            self.activate(reason, timestamp)
            return True

        # Check if weekend (if trading_days_only)
        if self.trading_days_only and timestamp.weekday() >= 5:
            reason = "Weekend - non-trading day"
            self.activate(reason, timestamp)
            return True

        return False


class VaRTrigger(KillSwitchTrigger):
    """Trigger based on Value at Risk breach."""

    def __init__(
        self,
        var_limit: float = 0.05,
        confidence: float = 0.95,
        lookback_days: int = 252,
        name: str = "VaRTrigger",
    ):
        super().__init__(name)
        self.var_limit = var_limit
        self.confidence = confidence
        self.lookback_days = lookback_days
        self.return_history: list[tuple] = []

    def check(
        self,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> bool:
        """Check if current loss exceeds VaR estimate."""
        if self.activated:
            return True

        current_value = portfolio.get_total_value(current_prices)

        # Calculate return if we have previous value
        if self.return_history:
            prev_value = self.return_history[-1][1]
            if prev_value > 0:
                daily_return = (current_value - prev_value) / prev_value
                self.return_history.append((timestamp, current_value, daily_return))
        else:
            self.return_history.append((timestamp, current_value, 0.0))

        # Keep only recent history
        cutoff_date = timestamp - timedelta(days=self.lookback_days)
        self.return_history = [
            (t, v, r) for t, v, r in self.return_history if t >= cutoff_date
        ]

        if len(self.return_history) < 30:  # Need minimum observations
            return False

        # Calculate VaR
        returns = [r for _, _, r in self.return_history[1:]]  # Skip first with 0 return
        var_estimate = np.percentile(returns, (1 - self.confidence) * 100)

        # Check if today's loss exceeds VaR
        if len(returns) > 0:
            current_return = returns[-1]
            if current_return <= var_estimate and abs(current_return) > self.var_limit:
                reason = f"Return {current_return:.2%} exceeds VaR estimate {var_estimate:.2%}"
                self.activate(reason, timestamp)
                return True

        return False
