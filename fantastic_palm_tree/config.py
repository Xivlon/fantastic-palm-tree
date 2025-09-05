from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .exceptions import InvalidConfigError

DEFAULT_TRAILING = {
    "enabled": True,
    "type": "atr",  # future: 'percent', 'vol_contraction', etc.
    "use_dynamic_atr": False,
    "dynamic_atr_min_samples": 1,
}

DEFAULT_BREAKOUT = {
    "enabled": True,
    "multiplier": 2.0,  # ATR multiplier for breakout detection
    "lookback_period": 20,  # Period to look back for high/low
    "direction": "both",  # "long", "short", or "both"
    "min_atr_threshold": 0.01,  # Minimum ATR value to consider for breakouts
}


@dataclass
class StrategyConfig:
    exits: dict[str, Any] = field(default_factory=dict)
    atr_period: int = 14

    def __post_init__(self) -> None:
        trailing = self.exits.setdefault("trailing", {})
        for k, v in DEFAULT_TRAILING.items():
            trailing.setdefault(k, v)
        self._validate()

    def _validate(self) -> None:
        trailing = self.exits["trailing"]
        if trailing["type"] not in {"atr"}:
            raise InvalidConfigError(f"Unsupported trailing.type={trailing['type']}")
        min_samples = trailing["dynamic_atr_min_samples"]
        if not isinstance(min_samples, int) or min_samples < 1:
            raise InvalidConfigError("dynamic_atr_min_samples must be positive int")

    @property
    def trailing(self) -> dict[str, Any]:
        return self.exits["trailing"]


@dataclass
class ATRBreakoutConfig:
    """Configuration for ATR breakout strategy parameters."""
    
    # Core ATR settings
    atr_period: int = 14
    
    # Breakout detection settings
    breakout: dict[str, Any] = field(default_factory=dict)
    
    # Exit/trailing stop settings
    exits: dict[str, Any] = field(default_factory=dict)
    
    # Position sizing
    position_size: float = 1000.0  # Default position size
    max_position_pct: float = 0.02  # Max 2% of portfolio per position
    
    # Risk management
    max_risk_per_trade: float = 0.01  # Max 1% risk per trade
    stop_loss_atr_multiplier: float = 2.0  # Initial stop loss distance
    
    def __post_init__(self) -> None:
        # Set breakout defaults
        breakout = self.breakout
        for k, v in DEFAULT_BREAKOUT.items():
            breakout.setdefault(k, v)
            
        # Set trailing defaults
        trailing = self.exits.setdefault("trailing", {})
        for k, v in DEFAULT_TRAILING.items():
            trailing.setdefault(k, v)
            
        self._validate()

    def _validate(self) -> None:
        # Validate breakout settings
        breakout = self.breakout
        if breakout["direction"] not in {"long", "short", "both"}:
            raise InvalidConfigError(f"Invalid breakout direction: {breakout['direction']}")
        if breakout["multiplier"] <= 0:
            raise InvalidConfigError("Breakout multiplier must be positive")
        if breakout["lookback_period"] <= 0:
            raise InvalidConfigError("Lookback period must be positive")
            
        # Validate trailing settings
        trailing = self.exits["trailing"]
        if trailing["type"] not in {"atr"}:
            raise InvalidConfigError(f"Unsupported trailing.type={trailing['type']}")
        min_samples = trailing["dynamic_atr_min_samples"]
        if not isinstance(min_samples, int) or min_samples < 1:
            raise InvalidConfigError("dynamic_atr_min_samples must be positive int")
            
        # Validate risk settings
        if self.max_risk_per_trade <= 0 or self.max_risk_per_trade > 1:
            raise InvalidConfigError("max_risk_per_trade must be between 0 and 1")
        if self.stop_loss_atr_multiplier <= 0:
            raise InvalidConfigError("stop_loss_atr_multiplier must be positive")
