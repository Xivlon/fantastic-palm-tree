from collections.abc import Callable
from datetime import datetime

from ..core.portfolio import Portfolio
from .triggers import KillSwitchTrigger


class KillSwitchManager:
    """Manages multiple kill switch triggers."""

    def __init__(self):
        self.triggers: list[KillSwitchTrigger] = []
        self.activated_triggers: list[KillSwitchTrigger] = []
        self.is_active = False
        self.activation_callbacks: list[Callable] = []

    def add_trigger(self, trigger: KillSwitchTrigger) -> None:
        """Add a kill switch trigger."""
        self.triggers.append(trigger)

    def add_activation_callback(self, callback: Callable) -> None:
        """Add callback function to be called when kill switch activates."""
        self.activation_callbacks.append(callback)

    def check_triggers(
        self,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> bool:
        """Check all triggers and return True if any are activated."""
        if self.is_active:
            return True

        for trigger in self.triggers:
            if trigger.check(portfolio, current_prices, timestamp):
                if trigger not in self.activated_triggers:
                    self.activated_triggers.append(trigger)
                    self._on_trigger_activated(
                        trigger, portfolio, current_prices, timestamp
                    )

        # Kill switch is active if any trigger is activated
        self.is_active = len(self.activated_triggers) > 0
        return self.is_active

    def _on_trigger_activated(
        self,
        trigger: KillSwitchTrigger,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> None:
        """Handle trigger activation."""
        print(f"KILL SWITCH ACTIVATED: {trigger.name}")
        print(f"Time: {timestamp}")
        print(f"Reason: {trigger.activation_reason}")
        print(f"Portfolio Value: ${portfolio.get_total_value(current_prices):,.2f}")

        # Call activation callbacks
        for callback in self.activation_callbacks:
            try:
                callback(trigger, portfolio, current_prices, timestamp)
            except Exception as e:
                print(f"Error in kill switch callback: {e}")

    def reset_all_triggers(self) -> None:
        """Reset all triggers."""
        for trigger in self.triggers:
            trigger.reset()
        self.activated_triggers.clear()
        self.is_active = False

    def get_activation_summary(self) -> dict:
        """Get summary of activated triggers."""
        if not self.activated_triggers:
            return {"is_active": False, "triggers": []}

        trigger_summaries = []
        for trigger in self.activated_triggers:
            trigger_summaries.append(
                {
                    "name": trigger.name,
                    "activation_time": trigger.activation_time,
                    "reason": trigger.activation_reason,
                }
            )

        return {
            "is_active": self.is_active,
            "triggers": trigger_summaries,
            "first_activation": min(t.activation_time for t in self.activated_triggers),
            "trigger_count": len(self.activated_triggers),
        }

    def get_status_report(self) -> str:
        """Get human-readable status report."""
        if not self.is_active:
            return f"Kill switch: INACTIVE ({len(self.triggers)} triggers monitored)"

        report = ["KILL SWITCH: ACTIVE"]
        report.append(f"Activated triggers: {len(self.activated_triggers)}")

        for trigger in self.activated_triggers:
            report.append(f"  - {trigger.name}: {trigger.activation_reason}")
            report.append(f"    Activated at: {trigger.activation_time}")

        return "\n".join(report)


def create_default_kill_switches(
    max_drawdown: float = 0.20, max_loss: float = 50000, max_volatility: float = 0.50
) -> KillSwitchManager:
    """Create a kill switch manager with common triggers.

    Args:
        max_drawdown: Maximum drawdown percentage (0.20 = 20%)
        max_loss: Maximum loss in dollars
        max_volatility: Maximum annualized volatility (0.50 = 50%)

    Returns:
        KillSwitchManager with default triggers
    """
    from .triggers import DrawdownTrigger, LossTrigger, VolatilityTrigger

    manager = KillSwitchManager()

    # Add common triggers
    manager.add_trigger(DrawdownTrigger(max_drawdown))
    manager.add_trigger(LossTrigger(max_loss))
    manager.add_trigger(VolatilityTrigger(max_volatility))

    return manager
