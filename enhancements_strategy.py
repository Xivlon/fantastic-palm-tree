"""
Enhanced Trading Strategy with Dynamic ATR Trailing Configuration

This module implements trading strategy enhancements with dynamic ATR trailing stops.
"""

import math
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class TradePosition:
    """Represents a trading position"""
    entry_price: float
    size: float
    entry_atr: float
    timestamp: int = 0
    stop_price: Optional[float] = None
    is_long: bool = True


@dataclass
class StrategyConfig:
    """Configuration for strategy behavior"""
    exits: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if 'trailing' not in self.exits:
            self.exits['trailing'] = {}
        
        trailing = self.exits['trailing']
        if 'use_dynamic_atr' not in trailing:
            trailing['use_dynamic_atr'] = False
        if 'dynamic_atr_min_samples' not in trailing:
            trailing['dynamic_atr_min_samples'] = 1
        if 'type' not in trailing:
            trailing['type'] = 'atr'
        if 'enabled' not in trailing:
            trailing['enabled'] = True


class ATRCalculator:
    """Calculate Average True Range"""
    
    def __init__(self, period: int = 14):
        self.period = period
        self.true_ranges: List[float] = []
    
    def add_bar(self, high: float, low: float, prev_close: float) -> float:
        """Add a new bar and calculate TR"""
        true_range = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        
        self.true_ranges.append(true_range)
        if len(self.true_ranges) > self.period:
            self.true_ranges.pop(0)
        
        return self.get_atr()
    
    def get_atr(self) -> float:
        """Get current ATR value"""
        if not self.true_ranges:
            return 0.0
        return sum(self.true_ranges) / len(self.true_ranges)
    
    def has_enough_samples(self, min_samples: int = 1) -> bool:
        """Check if we have enough samples for reliable ATR"""
        return len(self.true_ranges) >= min_samples


class EnhancedStrategy:
    """Enhanced trading strategy with dynamic ATR trailing stops"""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.atr_calculator = ATRCalculator()
        self.position: Optional[TradePosition] = None
        self.pnl = 0.0
        self.commission_rate = 0.0
        self.slippage = 0.0
        
    def set_fees(self, commission_rate: float = 0.0, slippage: float = 0.0):
        """Set commission and slippage rates"""
        self.commission_rate = commission_rate
        self.slippage = slippage
    
    def update_atr(self, high: float, low: float, prev_close: float) -> float:
        """Update ATR calculation with new bar data"""
        return self.atr_calculator.add_bar(high, low, prev_close)
    
    def enter_position(self, price: float, size: float, is_long: bool = True) -> bool:
        """Enter a new position"""
        if self.position is not None:
            return False
        
        entry_atr = self.atr_calculator.get_atr()
        effective_price = price + (self.slippage if is_long else -self.slippage)
        commission = abs(size * effective_price * self.commission_rate)
        
        self.position = TradePosition(
            entry_price=effective_price,
            size=size,
            entry_atr=entry_atr,
            is_long=is_long
        )
        
        # Deduct commission from PnL
        self.pnl -= commission
        return True
    
    def calculate_trailing_stop_distance(self) -> float:
        """Calculate trailing stop distance based on configuration"""
        if not self.position:
            return 0.0
        
        trailing_config = self.config.exits['trailing']
        
        # Check if trailing stops are enabled
        if not trailing_config.get('enabled', True):
            return 0.0
        
        if trailing_config['type'] != 'atr':
            return 0.0
        
        if trailing_config['use_dynamic_atr']:
            min_samples = trailing_config['dynamic_atr_min_samples']
            if self.atr_calculator.has_enough_samples(min_samples):
                # Use latest ATR average
                return self.atr_calculator.get_atr()
            else:
                # Use entry ATR
                return self.position.entry_atr
        else:
            # Use entry ATR
            return self.position.entry_atr
    
    def update_trailing_stop(self, current_price: float) -> Optional[float]:
        """Update trailing stop based on current price and ATR"""
        if not self.position:
            return None
        
        distance = self.calculate_trailing_stop_distance()
        if distance <= 0:
            return None
        
        if self.position.is_long:
            # For long positions, stop trails below current price
            new_stop = current_price - distance
            if self.position.stop_price is None or new_stop > self.position.stop_price:
                self.position.stop_price = new_stop
        else:
            # For short positions, stop trails above current price
            new_stop = current_price + distance
            if self.position.stop_price is None or new_stop < self.position.stop_price:
                self.position.stop_price = new_stop
        
        return self.position.stop_price
    
    def check_stop_hit(self, price: float) -> bool:
        """Check if stop loss has been hit"""
        if not self.position or self.position.stop_price is None:
            return False
        
        if self.position.is_long:
            return price <= self.position.stop_price
        else:
            return price >= self.position.stop_price
    
    def exit_position(self, price: float, reason: str = "manual") -> Dict[str, float]:
        """Exit the current position and calculate PnL"""
        if not self.position:
            return {"pnl": 0.0, "r_multiple": 0.0}
        
        effective_price = price + (-self.slippage if self.position.is_long else self.slippage)
        commission = abs(self.position.size * effective_price * self.commission_rate)
        
        # Calculate position PnL
        if self.position.is_long:
            position_pnl = self.position.size * (effective_price - self.position.entry_price)
        else:
            position_pnl = self.position.size * (self.position.entry_price - effective_price)
        
        # Calculate R multiple (profit/loss per share relative to risk per share)
        risk_per_share = self.position.entry_atr if self.position.entry_atr > 0 else 1.0
        price_change_per_share = position_pnl / self.position.size if self.position.size > 0 else 0.0
        r_multiple = price_change_per_share / risk_per_share if risk_per_share > 0 else 0.0
        
        # Update total PnL
        self.pnl += position_pnl - commission
        
        result = {
            "pnl": position_pnl,
            "r_multiple": r_multiple,
            "total_pnl": self.pnl,
            "commission": commission,
            "reason": reason
        }
        
        self.position = None
        return result
    
    def process_bar(self, high: float, low: float, close: float, prev_close: float) -> Dict[str, Any]:
        """Process a new price bar"""
        # Update ATR
        atr = self.update_atr(high, low, prev_close)
        
        result = {
            "atr": atr,
            "stop_hit": False,
            "exit_result": None
        }
        
        if self.position:
            # Update trailing stop
            stop_price = self.update_trailing_stop(close)
            result["stop_price"] = stop_price
            
            # Check if stop was hit during this bar
            if self.check_stop_hit(low if self.position.is_long else high):
                exit_price = self.position.stop_price
                result["exit_result"] = self.exit_position(exit_price, "stop_loss")
                result["stop_hit"] = True
        
        return result
    
    def get_position_info(self) -> Optional[Dict[str, Any]]:
        """Get current position information"""
        if not self.position:
            return None
        
        return {
            "entry_price": self.position.entry_price,
            "size": self.position.size,
            "entry_atr": self.position.entry_atr,
            "stop_price": self.position.stop_price,
            "is_long": self.position.is_long
        }
    
    def get_realized_pnl(self) -> float:
        """Get total realized PnL"""
        return self.pnl