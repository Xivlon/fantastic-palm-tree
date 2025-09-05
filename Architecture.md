# Architecture Documentation

## Overview

Fantastic Palm Tree is a comprehensive backtesting framework built with a modular architecture that emphasizes clean separation of concerns, extensibility, and type safety. The framework provides advanced metrics, parameter sweeping capabilities, risk management, and integration scaffolds for production trading.

## Core Modules

### 1. Engine Module (`backtesting/core/engine.py`)

**Purpose**: Orchestrates the backtesting execution lifecycle, coordinates between strategy, data feed, broker, and metrics collection.

**Responsibilities**:
- Manages the main execution loop for backtesting
- Coordinates data flow between modules
- Handles portfolio state management
- Aggregates results from multiple components

**Key Interfaces**:
```python
class BacktestResults:
    """Container for backtest results with equity curves, trades, and orders."""
    
class BacktestEngine:
    """Main engine for coordinating backtest execution."""
```

**Extension Points**:
- Custom result aggregation strategies
- Alternative execution models (parallel, distributed)
- Performance optimizations for different data scales

### 2. Strategy Module (`fantastic_palm_tree/strategy/`)

**Purpose**: Contains trading logic, decision-making algorithms, and strategy implementations.

**Responsibilities**:
- Implements trading signals and position management
- Manages strategy configuration and validation
- Provides base interfaces for custom strategy development
- Handles position lifecycle (entry, management, exit)

**Key Interfaces**:
```python
class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
class EnhancedStrategy(BaseStrategy):
    """Reference implementation with advanced features."""
```

**Module Structure**:
- `base.py`: Abstract strategy interfaces and protocols
- `enhanced.py`: Full-featured strategy implementation
- `__init__.py`: Public strategy exports

**Extension Points**:
- Custom strategy implementations via `BaseStrategy`
- Plugin architecture for strategy components
- Dynamic strategy loading and hot-swapping

### 3. Metrics Module (`backtesting/metrics/`)

**Purpose**: Calculates performance metrics, risk measures, and generates analytical reports.

**Responsibilities**:
- Computes standard performance metrics (returns, Sharpe ratio, drawdown)
- Calculates risk metrics (VaR, CVaR, volatility)
- Generates comprehensive trading reports
- Provides statistical analysis of trading results

**Key Interfaces**:
```python
class PerformanceMetrics:
    """Container for performance and risk metrics."""
    
class MetricsCalculator:
    """Engine for computing various trading metrics."""
```

**Module Structure**:
- `performance.py`: Return and performance calculations
- `risk.py`: Risk metrics and analysis
- `calculator.py`: Core calculation engine
- `reports.py`: Report generation and formatting

**Extension Points**:
- Custom metric definitions
- Alternative risk models
- Pluggable report formats (PDF, HTML, JSON)

### 4. Execution Module (Embedded in Engine/Broker)

**Purpose**: Handles order management, trade execution, and fill simulation.

**Responsibilities**:
- Order lifecycle management (creation, modification, cancellation)
- Trade execution simulation with realistic fills
- Slippage and commission modeling
- Order routing and execution policies

**Key Interfaces**:
```python
class BrokerOrder:
    """Represents an order in the broker system."""
    
class OrderStatus(Enum):
    """Order status enumeration."""
```

**Integration Points**:
- Embedded within `BacktestEngine` for simulation
- Integrated with `Broker` modules for live trading
- Connected to `Portfolio` for position tracking

**Extension Points**:
- Custom execution algorithms
- Advanced slippage models
- Market microstructure simulation

### 5. Data Feed Module (`backtesting/core/data.py`)

**Purpose**: Manages market data ingestion, preprocessing, and streaming.

**Responsibilities**:
- Market data ingestion from various sources
- Data preprocessing and validation
- Streaming data to strategy components
- Historical data management and caching

**Key Interfaces**:
```python
class DataHandler:
    """Handles market data for backtesting."""
    
class Bar:
    """Represents a price bar/candle."""
```

**Extension Points**:
- Multiple data source adapters
- Real-time data streaming for live trading
- Custom data preprocessing pipelines
- Alternative data integration (sentiment, fundamental)

### 6. Broker Module (`backtesting/brokers/`)

**Purpose**: Provides interfaces to trading venues and handles order execution.

**Responsibilities**:
- Broker API integration (currently supports Schwab)
- Order submission and management
- Account information retrieval
- Position and balance tracking

**Key Interfaces**:
```python
class BrokerInterface(ABC):
    """Abstract interface for broker operations."""
    
class SchwabBroker(BrokerInterface):
    """Charles Schwab API integration."""
```

**Module Structure**:
- `base.py`: Abstract broker interfaces
- `schwab.py`: Schwab-specific implementation
- `auth.py`: Authentication and token management

**Extension Points**:
- Additional broker integrations (Interactive Brokers, Alpaca, etc.)
- Custom authentication mechanisms
- Paper trading simulators

### 7. Risk Module (`fantastic_palm_tree/risk/`)

**Purpose**: Implements risk management algorithms and safety mechanisms.

**Responsibilities**:
- Trailing stop loss management
- Kill-switch mechanisms for emergency stops
- Position sizing and capital allocation
- Risk limit monitoring and enforcement

**Key Interfaces**:
```python
class TrailingStopEngine:
    """Configurable trailing stop logic."""
    
class KillSwitchManager:
    """Risk protection and emergency stop mechanisms."""
```

**Module Structure**:
- `trailing.py`: Trailing stop implementations
- `../killswitch/`: Emergency stop mechanisms and triggers

**Extension Points**:
- Custom trailing stop algorithms
- Additional risk triggers (volatility, correlation)
- Portfolio-level risk management

## Module Boundaries and Interfaces

### Data Flow Architecture

```
Data Feed → Strategy → Engine → Broker
     ↓         ↓        ↓       ↓
  Metrics ← Portfolio ← Risk ← Execution
```

### Interface Contracts

#### Strategy ↔ Engine
- **Input**: Market data (OHLCV bars)
- **Output**: Trading signals and position updates
- **Protocol**: `BarProcessResult` dataclass with typed fields

#### Engine ↔ Broker
- **Input**: Order requests and portfolio queries
- **Output**: Fill confirmations and position updates
- **Protocol**: `BrokerOrder` and `Fill` dataclasses

#### Risk ↔ Strategy
- **Input**: Position state and market conditions
- **Output**: Risk adjustments and stop prices
- **Protocol**: `TradePosition` model with risk parameters

#### Metrics ↔ Engine
- **Input**: Trade history and portfolio snapshots
- **Output**: Performance analytics and reports
- **Protocol**: `PerformanceMetrics` and `EquityPoint` dataclasses

## Public API Surface

The public API is defined in `src/fantastic_palm_tree/__init__.py` and re-exports stable interfaces:

```python
from .strategy.base import Strategy, Bar
from .engine.base import Engine
from .orders import Order, OrderSide, OrderType
from .position import Position
from .results import TradeResult
from .metrics.base import MetricsPipeline, Metric, EquityPoint
```

### Stability Guarantees

- **Protocol Interfaces**: Abstract base classes maintain backward compatibility
- **Dataclass Schemas**: Field additions are non-breaking, removals require deprecation
- **Configuration**: New fields added with sensible defaults
- **Exception Hierarchy**: Custom exceptions maintain inheritance relationships

### Versioning Strategy

- **Major Versions**: Breaking changes to public interfaces
- **Minor Versions**: New features and non-breaking additions
- **Patch Versions**: Bug fixes and performance improvements

## Future Extension Points

### 1. Strategy System
- **Multi-asset Strategies**: Framework for cross-asset trading strategies
- **Signal Composition**: Combining multiple signal sources with weights
- **Dynamic Rebalancing**: Time-based and threshold-based portfolio rebalancing

### 2. Data Infrastructure
- **Alternative Data**: Integration points for sentiment, fundamental, and social data
- **Real-time Processing**: Streaming data pipeline for live trading
- **Data Quality**: Validation and cleansing frameworks

### 3. Risk Management
- **Portfolio Risk**: Cross-position risk analysis and hedging
- **Regime Detection**: Market regime identification and adaptation
- **Stress Testing**: Scenario analysis and Monte Carlo simulation

### 4. Execution
- **Smart Routing**: Intelligent order routing across venues
- **Execution Algorithms**: TWAP, VWAP, and custom execution strategies
- **Market Making**: Bid-ask spread capture strategies

### 5. Analytics
- **Machine Learning**: Integration with ML frameworks for predictive analytics
- **Attribution Analysis**: Performance attribution to various factors
- **Optimization**: Parameter optimization using advanced algorithms

## Naming Conventions

### Module Organization
- **Package Names**: `snake_case` (e.g., `fantastic_palm_tree`)
- **Module Names**: `snake_case` (e.g., `trailing_stop.py`)
- **Subpackages**: Logical grouping by functionality

### Class Naming
- **Abstract Base Classes**: `Base` prefix (e.g., `BaseStrategy`)
- **Interfaces**: `Interface` suffix (e.g., `BrokerInterface`)
- **Implementations**: Descriptive names (e.g., `EnhancedStrategy`)
- **Data Classes**: Descriptive nouns (e.g., `TradePosition`, `BarProcessResult`)

### Function and Method Naming
- **Public Methods**: `snake_case` with clear action verbs
- **Private Methods**: Leading underscore `_private_method`
- **Property Accessors**: Noun-based names for state access

### Configuration
- **Config Keys**: `snake_case` with hierarchical structure
- **Environment Variables**: `UPPER_CASE` with module prefixes
- **Default Values**: Explicit constants with `DEFAULT_` prefix

### File Organization
```
fantastic_palm_tree/
├── strategy/           # Strategy implementations
├── risk/              # Risk management
├── indicators/        # Technical indicators
├── models/           # Data models and schemas
├── config.py         # Configuration management
├── results.py        # Result data classes
└── exceptions.py     # Custom exception hierarchy
```

## Constraints and Invariants

### System Invariants

#### 1. Data Consistency
- **Temporal Ordering**: Market data must be chronologically ordered
- **Price Validity**: All prices must be positive, non-zero values
- **Position Integrity**: Position size and stop prices must be consistent with market reality

#### 2. State Management
- **Position Lifecycle**: Positions can only be modified or closed, never retroactively created
- **Order Atomicity**: Order operations are atomic - either fully succeed or fully fail
- **Configuration Immutability**: Strategy configuration cannot change during execution

#### 3. Type Safety
- **Dataclass Integrity**: All result objects use strongly-typed dataclasses
- **Interface Compliance**: All implementations must satisfy their interface contracts
- **Error Propagation**: Exceptions must be properly typed and handled

### What Must Not Be Assumed

#### 1. Data Availability
- **Market Hours**: Do not assume continuous data - handle gaps and market closures
- **Data Quality**: Always validate input data for completeness and sanity
- **Latency**: Do not assume zero-latency data delivery in live trading

#### 2. Execution Guarantees
- **Fill Assumptions**: Orders may be partially filled or rejected
- **Price Execution**: Actual fill prices may differ from expected due to slippage
- **Timing**: Order execution timing is not guaranteed in live markets

#### 3. System Resources
- **Memory Limits**: Large datasets may not fit in memory
- **Computing Resources**: Parallel execution capabilities may be limited
- **Network Reliability**: Broker connections may be unstable

#### 4. Market Conditions
- **Liquidity**: Instruments may become illiquid
- **Volatility**: Market conditions can change rapidly
- **Circuit Breakers**: Markets may halt trading

### Design Principles

#### 1. Modularity
- Each module has a single, well-defined responsibility
- Interfaces are stable and implementation-agnostic
- Dependencies flow in one direction to avoid circular references

#### 2. Extensibility
- New functionality can be added without modifying existing code
- Plugin architecture supports custom implementations
- Configuration-driven behavior reduces code changes

#### 3. Reliability
- Graceful degradation under adverse conditions
- Comprehensive error handling and logging
- Fail-fast principle for invalid configurations

#### 4. Performance
- Lazy evaluation where appropriate
- Efficient data structures for time-series operations
- Configurable performance trade-offs

This architecture provides a solid foundation for backtesting and live trading while maintaining flexibility for future enhancements and customizations.