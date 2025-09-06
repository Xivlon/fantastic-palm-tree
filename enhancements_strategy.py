"""
Enhanced Trading Strategy with Dynamic ATR Trailing Configuration

This module implements trading strategy enhancements with dynamic ATR trailing stops.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TradePosition:
    """Represents a trading position"""

    entry_price: float
    size: float
    entry_atr: float
    timestamp: int = 0
    stop_price: float | None = None
    is_long: bool = True


@dataclass
class StrategyConfig:
    """Configuration for strategy behavior"""

    exits: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if "trailing" not in self.exits:
            self.exits["trailing"] = {}

        trailing = self.exits["trailing"]
        if "use_dynamic_atr" not in trailing:
            trailing["use_dynamic_atr"] = False
        if "dynamic_atr_min_samples" not in trailing:
            trailing["dynamic_atr_min_samples"] = 1
        if "type" not in trailing:
            trailing["type"] = "atr"
        if "enabled" not in trailing:
            trailing["enabled"] = True


class ATRCalculator:
    """Calculate Average True Range"""

    def __init__(self, period: int = 14):
        self.period = period
        self.true_ranges: list[float] = []

    def add_bar(self, high: float, low: float, prev_close: float) -> float:
        """Add a new bar and calculate TR"""
        true_range = max(high - low, abs(high - prev_close), abs(low - prev_close))

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
        self.position: TradePosition | None = None
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
            entry_price=effective_price, size=size, entry_atr=entry_atr, is_long=is_long
        )

        # Deduct commission from PnL
        self.pnl -= commission
        return True

    def calculate_trailing_stop_distance(self) -> float:
        """Calculate trailing stop distance based on configuration"""
        if not self.position:
            return 0.0

        trailing_config = self.config.exits["trailing"]

        # Check if trailing stops are enabled
        if not trailing_config.get("enabled", True):
            return 0.0

        if trailing_config["type"] != "atr":
            return 0.0

        if trailing_config["use_dynamic_atr"]:
            min_samples = trailing_config["dynamic_atr_min_samples"]
            if self.atr_calculator.has_enough_samples(min_samples):
                # Use latest ATR average
                return self.atr_calculator.get_atr()
            else:
                # Use entry ATR
                return self.position.entry_atr
        else:
            # Use entry ATR
            return self.position.entry_atr

    def update_trailing_stop(self, current_price: float) -> float | None:
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

    def exit_position(self, price: float, reason: str = "manual") -> dict[str, float]:
        """Exit the current position and calculate PnL"""
        if not self.position:
            return {"pnl": 0.0, "r_multiple": 0.0}

        effective_price = price + (
            -self.slippage if self.position.is_long else self.slippage
        )
        commission = abs(self.position.size * effective_price * self.commission_rate)

        # Calculate position PnL
        if self.position.is_long:
            position_pnl = self.position.size * (
                effective_price - self.position.entry_price
            )
        else:
            position_pnl = self.position.size * (
                self.position.entry_price - effective_price
            )

        # Calculate R multiple (profit/loss per share relative to risk per share)
        risk_per_share = self.position.entry_atr if self.position.entry_atr > 0 else 1.0
        price_change_per_share = (
            position_pnl / self.position.size if self.position.size > 0 else 0.0
        )
        r_multiple = (
            price_change_per_share / risk_per_share if risk_per_share > 0 else 0.0
        )

        # Update total PnL
        self.pnl += position_pnl - commission

        result = {
            "pnl": position_pnl,
            "r_multiple": r_multiple,
            "total_pnl": self.pnl,
            "commission": commission,
            "reason": reason,
        }

        self.position = None
        return result

    def process_bar(
        self, high: float, low: float, close: float, prev_close: float
    ) -> dict[str, Any]:
        """Process a new price bar"""
        # Update ATR
        atr = self.update_atr(high, low, prev_close)

        result = {"atr": atr, "stop_hit": False, "exit_result": None}

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

    def get_position_info(self) -> dict[str, Any] | None:
        """Get current position information"""
        if not self.position:
            return None

        return {
            "entry_price": self.position.entry_price,
            "size": self.position.size,
            "entry_atr": self.position.entry_atr,
            "stop_price": self.position.stop_price,
            "is_long": self.position.is_long,
        }

    def get_realized_pnl(self) -> float:
        """Get total realized PnL"""
        return self.pnl


# Additional classes needed for test compatibility


@dataclass
class Position:
    """Position tracking for broker interface"""

    symbol: str
    qty: float
    avg_price: float


@dataclass
class Fill:
    """Represents a trade execution fill"""

    symbol: str
    side: str  # "BUY" or "SELL"
    qty: float
    price: float
    commission: float = 0.0  # Commission charged for this fill


@dataclass
class Bar:
    """Represents a price bar/candle"""

    symbol: str
    datetime: Any  # datetime object
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass 
class Order:
    """Represents a trading order"""
    
    symbol: str
    side: str  # "BUY" or "SELL"
    qty: float
    order_type: str = "MARKET"  # "MARKET", "LIMIT", "STOP"
    price: float | None = None
    

class SlippageModel:
    """Base class for slippage models"""
    
    def calculate_slippage(self, order: Order, market_price: float, volume: float = 0) -> float:
        """Calculate slippage for an order. Returns adjustment to price."""
        return 0.0


class FixedSlippageModel(SlippageModel):
    """Fixed slippage model - constant dollar amount per share"""
    
    def __init__(self, slippage_amount: float = 0.01):
        self.slippage_amount = slippage_amount
    
    def calculate_slippage(self, order: Order, market_price: float, volume: float = 0) -> float:
        # Positive slippage for buys (pay more), negative for sells (receive less)
        return self.slippage_amount if order.side == "BUY" else -self.slippage_amount


class PercentageSlippageModel(SlippageModel):
    """Percentage-based slippage model"""
    
    def __init__(self, slippage_bps: float = 10):  # basis points
        self.slippage_bps = slippage_bps
    
    def calculate_slippage(self, order: Order, market_price: float, volume: float = 0) -> float:
        slippage_rate = self.slippage_bps / 10000  # Convert bps to decimal
        slippage = market_price * slippage_rate
        return slippage if order.side == "BUY" else -slippage


class VolumeBasedSlippageModel(SlippageModel):
    """Volume-dependent slippage model with tiered structure"""
    
    def __init__(self, tiers: list[dict]):
        """
        tiers: List of dicts with keys 'adv_threshold' and 'bps'
        e.g., [{"adv_threshold": 0, "bps": 5}, {"adv_threshold": 1000000, "bps": 10}]
        """
        self.tiers = sorted(tiers, key=lambda x: x['adv_threshold'])
    
    def calculate_slippage(self, order: Order, market_price: float, volume: float = 0) -> float:
        # Find appropriate tier based on volume
        slippage_bps = 0
        for tier in reversed(self.tiers):
            if volume >= tier['adv_threshold']:
                slippage_bps = tier['bps']
                break
        
        if slippage_bps == 0:
            return 0.0
            
        slippage_rate = slippage_bps / 10000
        slippage = market_price * slippage_rate
        return slippage if order.side == "BUY" else -slippage


class CommissionModel:
    """Base class for commission models"""
    
    def calculate_commission(self, order: Order, fill_price: float) -> float:
        """Calculate commission for an order. Returns commission amount."""
        return 0.0


class PerShareCommissionModel(CommissionModel):
    """Per-share commission model"""
    
    def __init__(self, per_share: float = 0.005, min_commission: float = 1.0):
        self.per_share = per_share
        self.min_commission = min_commission
    
    def calculate_commission(self, order: Order, fill_price: float) -> float:
        commission = order.qty * self.per_share
        return max(commission, self.min_commission)


class PercentageCommissionModel(CommissionModel):
    """Percentage-based commission model"""
    
    def __init__(self, rate: float = 0.001, min_commission: float = 1.0):  # 0.1% default
        self.rate = rate
        self.min_commission = min_commission
    
    def calculate_commission(self, order: Order, fill_price: float) -> float:
        commission = order.qty * fill_price * self.rate
        return max(commission, self.min_commission)


class TieredCommissionModel(CommissionModel):
    """Tiered commission model based on trade size"""
    
    def __init__(self, tiers: list[dict]):
        """
        tiers: List of dicts with keys 'threshold' and 'rate'
        e.g., [{"threshold": 0, "rate": 0.001}, {"threshold": 10000, "rate": 0.0005}]
        """
        self.tiers = sorted(tiers, key=lambda x: x['threshold'])
    
    def calculate_commission(self, order: Order, fill_price: float) -> float:
        trade_value = order.qty * fill_price
        
        # Find appropriate tier
        rate = 0.001  # default
        for tier in reversed(self.tiers):
            if trade_value >= tier['threshold']:
                rate = tier['rate']
                break
        
        return trade_value * rate


class ExecutionEngine:
    """Handles realistic order execution with slippage, commissions, and delays"""
    
    def __init__(self, 
                 slippage_model: SlippageModel | None = None,
                 commission_model: CommissionModel | None = None,
                 execution_delay_ms: int = 0,
                 spread_bps: float = 0):
        self.slippage_model = slippage_model or FixedSlippageModel(0.0)
        self.commission_model = commission_model or PerShareCommissionModel(0.0, 0.0)
        self.execution_delay_ms = execution_delay_ms
        self.spread_bps = spread_bps
    
    def execute_order(self, order: Order, market_price: float, volume: float = 0) -> Fill:
        """Execute an order with realistic slippage, spreads, and commissions"""
        
        # Apply bid-ask spread
        spread = market_price * (self.spread_bps / 10000)
        if order.side == "BUY":
            # Buy at ask (higher price)
            base_price = market_price + (spread / 2)
        else:
            # Sell at bid (lower price)  
            base_price = market_price - (spread / 2)
        
        # Apply slippage
        slippage = self.slippage_model.calculate_slippage(order, base_price, volume)
        fill_price = base_price + slippage
        
        # Calculate commission
        commission = self.commission_model.calculate_commission(order, fill_price)
        
        # Create fill with commission
        fill = Fill(
            symbol=order.symbol,
            side=order.side,
            qty=order.qty,
            price=fill_price,
            commission=commission
        )
        
        return fill


def create_slippage_model(config: dict) -> SlippageModel:
    """Factory function to create slippage model from configuration"""
    if 'tiers' in config and config['tiers']:
        return VolumeBasedSlippageModel(config['tiers'])
    elif 'bps' in config:
        return PercentageSlippageModel(config['bps'])
    elif 'amount' in config:
        return FixedSlippageModel(config['amount'])
    else:
        # Default to no slippage
        return FixedSlippageModel(0.0)


def create_commission_model(config: dict) -> CommissionModel:
    """Factory function to create commission model from configuration"""
    if 'per_share' in config:
        min_commission = config.get('min_commission', 0.0)
        return PerShareCommissionModel(config['per_share'], min_commission)
    elif 'rate' in config:
        min_commission = config.get('min_commission', 0.0)
        return PercentageCommissionModel(config['rate'], min_commission)
    elif 'tiers' in config:
        return TieredCommissionModel(config['tiers'])
    else:
        # Default to no commission
        return PerShareCommissionModel(0.0, 0.0)


class BrokerInterface:
    """Abstract interface for broker operations with realistic execution"""

    def __init__(self, starting_equity: float = 100_000):
        self._equity = starting_equity
        self._positions: dict[str, Position] = {}
        self._execution_engine: ExecutionEngine | None = None

    def set_execution_engine(self, execution_engine: ExecutionEngine) -> None:
        """Set the execution engine for realistic order processing"""
        self._execution_engine = execution_engine

    @property
    def equity(self) -> float:
        return self._equity

    def get_position(self, symbol: str) -> Position | None:
        return self._positions.get(symbol)

    def open_positions(self) -> list[Position]:
        return list(self._positions.values())

    def execute(self, orders, slippage_model=None, commission_model=None) -> list[Fill]:
        """Execute orders with realistic slippage and commissions"""
        fills = []
        
        # For now, still return empty list as actual execution happens in strategy
        # But this provides the interface for future enhancement
        return fills
    
    def execute_order_realistic(self, order: Order, market_price: float, volume: float = 0) -> Fill:
        """Execute a single order with realistic execution modeling"""
        if self._execution_engine:
            return self._execution_engine.execute_order(order, market_price, volume)
        else:
            # Fallback to perfect execution
            return Fill(
                symbol=order.symbol,
                side=order.side,
                qty=order.qty,
                price=market_price,
                commission=0.0
            )

    def flatten_all(self) -> None:
        self._positions.clear()


class MetricsTracker:
    """Tracks trading metrics and open trades"""

    def __init__(self):
        self._open_trades: dict[str, Any] = {}

    def get_open_trade(self, symbol: str) -> Any | None:
        return self._open_trades.get(symbol)


class ATRTracker:
    """Tracks ATR values"""

    def __init__(self):
        self.tr_values: dict[str, Any] = {}


class EnhancementsContext:
    """Main context for enhanced trading strategy"""

    def __init__(self, config: dict[str, Any], broker: BrokerInterface, indicator_fn):
        self.config = config
        self.broker = broker
        self.indicator_fn = indicator_fn
        self.metrics_tracker = MetricsTracker()
        self.atr_tracker = ATRTracker()

    def on_bar_start(self, bar: Bar, broker: BrokerInterface) -> None:
        """Called at the start of each bar"""
        pass

    def process_symbol(
        self, symbol: str, bar: Bar, broker: BrokerInterface, adv_lookup
    ) -> list[Fill]:
        """Process a symbol for the given bar"""
        return []
