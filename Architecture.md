# Architecture Documentation

## Overview

Fantastic Palm Tree is a comprehensive, modular backtesting framework designed with a clean architectural foundation that emphasizes separation of concerns, type safety, and extensibility. The framework is built around a modular design that separates strategy logic, risk management, technical indicators, configuration, and backtesting infrastructure into focused, testable components.

## Design Principles

### 1. Modular Architecture
- **Single Responsibility**: Each module has a clearly defined purpose
- **Loose Coupling**: Modules interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together
- **Dependency Injection**: Dependencies are injected rather than hard-coded

### 2. Type Safety
- **Strongly Typed**: All data structures use typed dataclasses
- **Interface Contracts**: Abstract base classes define clear interfaces
- **Runtime Validation**: Configuration validation catches errors early
- **Type Hints**: Full type annotation throughout the codebase

### 3. Extensibility
- **Plugin Architecture**: Easy to add new strategies, indicators, and risk modules
- **Configuration-Driven**: Behavior controlled through configuration
- **Strategy Pattern**: Multiple implementations of core interfaces
- **Template Method**: Base classes provide extension points

### 4. Testability
- **Isolated Components**: Each module can be tested independently
- **Mock-Friendly**: Interfaces designed for easy mocking
- **State Management**: Clear state boundaries for predictable testing
- **Focused Tests**: Each test validates specific behaviors

## Core Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  demo_modular_architecture.py │ example_usage.py           │
├─────────────────────────────────────────────────────────────┤
│                    Strategy Framework                       │
├─────────────────────────────────────────────────────────────┤
│  fantastic_palm_tree/         │ backtesting/               │
│  ├── strategy/                │ ├── core/                  │
│  ├── risk/                    │ ├── metrics/               │
│  ├── indicators/              │ ├── sweep/                 │
│  ├── models/                  │ ├── killswitch/            │
│  ├── config.py                │ └── brokers/               │
│  ├── results.py               │                            │
│  ├── exceptions.py            │                            │
│  └── logging.py               │                            │
└─────────────────────────────────────────────────────────────┘
```

### Module Dependencies

```
fantastic_palm_tree/
├── strategy/enhanced.py ─┬─→ config.py
│                         ├─→ models/position.py
│                         ├─→ results.py
│                         ├─→ risk/trailing.py
│                         ├─→ indicators/atr.py
│                         └─→ exceptions.py
│
├── risk/trailing.py ─────┬─→ config.py
│                         ├─→ models/position.py
│                         └─→ indicators/atr.py
│
├── indicators/atr.py ────→ (no dependencies)
├── models/position.py ───→ (no dependencies)  
├── config.py ───────────→ exceptions.py
├── results.py ──────────→ (no dependencies)
├── exceptions.py ───────→ (no dependencies)
└── logging.py ──────────→ (no dependencies)
```

## Detailed Module Architecture

### 1. Strategy Module (`fantastic_palm_tree/strategy/`)

**Purpose**: Implements trading strategy logic with a clean interface.

**Key Components**:
- `BaseStrategy` (Abstract): Defines the strategy interface contract
- `EnhancedStrategy` (Concrete): Implementation with ATR-based trailing stops

**Design Patterns**:
- **Template Method**: BaseStrategy defines the interface, implementations provide specifics
- **Strategy Pattern**: Multiple strategy implementations can coexist
- **Dependency Injection**: Configuration and calculators injected via constructor

**Interface**:
```python
class BaseStrategy(ABC):
    @abstractmethod
    def enter_position(self, price: float, size: float, is_long: bool) -> bool
    
    @abstractmethod
    def exit_position(self, price: float, reason: str) -> ExitResult
    
    @abstractmethod
    def process_bar(self, high: float, low: float, close: float, prev_close: float) -> BarProcessResult
```

**Key Features**:
- **Immutable Operations**: Each bar processing returns new result objects
- **Type Safety**: All results are strongly typed dataclasses
- **Error Handling**: Clear exceptions for invalid state transitions
- **Stateful Management**: Maintains position state with clear lifecycle

### 2. Risk Management Module (`fantastic_palm_tree/risk/`)

**Purpose**: Handles risk management logic, particularly trailing stop functionality.

**Key Components**:
- `TrailingStopEngine`: Manages trailing stop distance calculation and updates

**Design Patterns**:
- **Strategy Pattern**: Different trailing stop algorithms (ATR, percentage, etc.)
- **Composition**: Used by strategy rather than inheritance
- **Stateless Operations**: All methods are pure functions or clearly modify passed objects

**Interface**:
```python
class TrailingStopEngine:
    def compute_distance(self, position: TradePosition | None) -> float
    def update_trailing_stop(self, position: TradePosition, current_price: float) -> float | None
    @staticmethod
    def stop_hit(position: TradePosition, bar_high: float, bar_low: float) -> bool
```

**Key Features**:
- **Configurable Behavior**: Algorithm behavior controlled by configuration
- **Dynamic ATR**: Supports both static and dynamic ATR trailing
- **Position-Aware**: Logic adapts to long/short positions automatically
- **Extensible**: Easy to add new trailing stop algorithms

### 3. Technical Indicators Module (`fantastic_palm_tree/indicators/`)

**Purpose**: Provides technical analysis calculations.

**Key Components**:
- `ATRCalculator`: Rolling Average True Range calculation

**Design Patterns**:
- **Accumulator Pattern**: Maintains rolling window of data
- **Simple Interface**: Single responsibility for each indicator
- **Stateful Calculator**: Maintains internal state for rolling calculations

**Interface**:
```python
class ATRCalculator:
    def add_bar(self, high: float, low: float, prev_close: float) -> float
    def get_atr(self) -> float
    def has_enough_samples(self, min_samples: int) -> bool
```

**Key Features**:
- **Rolling Window**: Efficiently maintains fixed-size data window
- **Sample Validation**: Tracks whether enough data exists for reliable calculations
- **Arithmetic Mean**: Currently uses simple average (extensible to Wilder's smoothing)

### 4. Data Models Module (`fantastic_palm_tree/models/`)

**Purpose**: Defines core data structures and business entities.

**Key Components**:
- `TradePosition`: Represents an active trading position

**Design Patterns**:
- **Data Transfer Object**: Pure data containers with minimal logic
- **Immutable Data**: Dataclasses provide immutable-by-default structures
- **Rich Objects**: Methods provide calculated properties (e.g., unrealized PnL)

**Interface**:
```python
@dataclass
class TradePosition:
    entry_price: float
    size: float
    entry_atr: float
    is_long: bool
    timestamp: int = 0
    stop_price: float | None = None
    
    def unrealized_pnl(self, mark_price: float) -> float
```

**Key Features**:
- **Type Safety**: All fields are strongly typed
- **Business Logic**: Contains position-specific calculations
- **Mutable State**: Stop price can be updated by risk management
- **Direction Agnostic**: Handles both long and short positions

### 5. Results Module (`fantastic_palm_tree/results.py`)

**Purpose**: Defines result data structures for operations.

**Key Components**:
- `ExitResult`: Results from position exit operations
- `BarProcessResult`: Results from processing market data

**Design Patterns**:
- **Result Object**: Encapsulates operation outcomes
- **Composite Data**: Aggregates related information
- **Optional Fields**: Uses Optional types for conditional data

**Interface**:
```python
@dataclass
class ExitResult:
    pnl: float
    r_multiple: float
    total_pnl: float
    commission: float
    reason: str

@dataclass  
class BarProcessResult:
    atr: float
    stop_hit: bool
    exit_result: ExitResult | None
    stop_price: float | None = None
```

**Key Features**:
- **Comprehensive Information**: Contains all relevant operation data
- **Type Safety**: Strongly typed fields prevent runtime errors
- **Optional Results**: Handles cases where operations don't produce results
- **Immutable Results**: Results are snapshots, not mutable state

### 6. Configuration Module (`fantastic_palm_tree/config.py`)

**Purpose**: Manages framework configuration with validation.

**Key Components**:
- `StrategyConfig`: Main configuration dataclass with validation

**Design Patterns**:
- **Configuration Object**: Centralized configuration management
- **Default Values**: Sensible defaults with override capability
- **Validation**: Post-initialization validation catches errors early
- **Nested Configuration**: Hierarchical configuration structure

**Interface**:
```python
@dataclass
class StrategyConfig:
    exits: dict[str, Any] = field(default_factory=dict)
    atr_period: int = 14
    
    def __post_init__(self) -> None
    def _validate(self) -> None
    
    @property
    def trailing(self) -> dict[str, Any]
```

**Key Features**:
- **Default Merging**: Automatically merges user config with defaults
- **Validation**: Validates configuration consistency at creation
- **Type Safety**: Configuration errors caught at startup
- **Extensible**: Easy to add new configuration sections

### 7. Exception Handling (`fantastic_palm_tree/exceptions.py`)

**Purpose**: Defines framework-specific exceptions with clear hierarchy.

**Key Components**:
- `StrategyError`: Base exception for all strategy-related errors
- `InvalidConfigError`: Configuration validation errors
- `PositionExistsError`: Attempting to enter position when one exists  
- `NoPositionError`: Attempting operations without an active position

**Design Patterns**:
- **Exception Hierarchy**: Clear inheritance structure
- **Specific Exceptions**: Each error type has specific meaning
- **Fail Fast**: Configuration errors caught at initialization

**Key Features**:
- **Clear Semantics**: Each exception type has specific meaning
- **Early Detection**: Configuration errors caught at startup
- **Debugging Support**: Exception names clearly indicate the problem
- **Client Handling**: Clients can catch specific exception types

### 8. Logging Module (`fantastic_palm_tree/logging.py`)

**Purpose**: Provides structured logging throughout the framework.

**Design Patterns**:
- **Singleton Pattern**: Single logger instance shared across modules
- **Factory Pattern**: Logger creation abstracted behind function
- **Structured Logging**: Consistent format across all modules

**Key Features**:
- **Centralized**: Single logger configuration for entire framework
- **Structured**: Consistent message format and metadata
- **Level Control**: Configurable logging levels
- **Framework-Aware**: Specific to framework needs

## Backtesting Infrastructure

### Architecture Overview

The backtesting system provides a comprehensive infrastructure for testing strategies with realistic market conditions, performance analysis, and parameter optimization.

### Core Modules

#### 1. Backtesting Engine (`backtesting/core/`)

**Purpose**: Core backtesting execution engine.

**Key Components**:
- `BacktestEngine`: Main execution engine
- `DataHandler`: Market data management
- `Portfolio`: Position and cash management
- `Order`: Order management and execution

**Design Patterns**:
- **Event-Driven**: Processes market events sequentially
- **State Machine**: Clear state transitions for orders/positions
- **Observer Pattern**: Portfolio observes order executions

#### 2. Metrics System (`backtesting/metrics/`)

**Purpose**: Performance and risk analysis.

**Key Components**:
- `MetricsCalculator`: Comprehensive performance metrics
- `PerformanceMetrics`: Standardized performance data structure
- `RiskMetrics`: Risk-specific calculations
- `Reports`: Formatted output generation

**Key Features**:
- **Standard Metrics**: Sharpe ratio, Sortino ratio, maximum drawdown
- **Risk Analysis**: VaR, volatility, correlation analysis
- **Benchmark Comparison**: Performance vs. benchmark calculations
- **Custom Metrics**: Extensible for strategy-specific metrics

#### 3. Parameter Optimization (`backtesting/sweep/`)

**Purpose**: Parameter space exploration and optimization.

**Key Components**:
- `ParameterSpace`: Define parameter ranges and combinations
- `GridSearch`: Exhaustive parameter combination testing
- `Optimizer`: Optimization algorithms (grid search, genetic, etc.)
- `Results`: Parameter sweep result analysis

**Design Patterns**:
- **Iterator Pattern**: Iterate through parameter combinations
- **Strategy Pattern**: Multiple optimization algorithms
- **Factory Pattern**: Create parameter combinations

#### 4. Risk Management (`backtesting/killswitch/`)

**Purpose**: Risk monitoring and emergency controls.

**Key Components**:
- `KillSwitchManager`: Central risk monitoring
- `Triggers`: Specific risk condition triggers
- `RiskMonitor`: Real-time risk monitoring

**Key Features**:
- **Real-Time Monitoring**: Continuous risk assessment
- **Multiple Triggers**: Drawdown, daily loss, position limits
- **Emergency Stop**: Immediate trading halt capabilities
- **Configurable Thresholds**: User-defined risk limits

#### 5. Broker Integration (`backtesting/brokers/`)

**Purpose**: Real broker integration for live trading.

**Key Components**:
- `BaseBroker`: Abstract broker interface
- `SchwabBroker`: Charles Schwab integration
- `Auth`: Authentication management

**Design Patterns**:
- **Adapter Pattern**: Uniform interface across different brokers
- **Async/Await**: Non-blocking broker communications
- **Factory Pattern**: Broker instance creation

## Data Flow Architecture

### Strategy Execution Flow

```
Market Data Input
       ↓
1. Bar Processing (EnhancedStrategy.process_bar)
       ↓
2. ATR Update (ATRCalculator.add_bar)
       ↓
3. Position Check (Has active position?)
       ↓
4. Risk Management (TrailingStopEngine.update_trailing_stop)
       ↓
5. Stop Hit Check (TrailingStopEngine.stop_hit)
       ↓
6. Exit Position (if stop hit)
       ↓
7. Return BarProcessResult
```

### Configuration Flow

```
User Configuration
       ↓
1. StrategyConfig.__init__
       ↓
2. Default Merging (__post_init__)
       ↓
3. Validation (_validate())
       ↓
4. Strategy Creation (EnhancedStrategy.__init__)
       ↓
5. Component Initialization
   ├── ATRCalculator(config.atr_period)
   └── TrailingStopEngine(config, atr_calc)
```

### Error Handling Flow

```
Error Occurrence
       ↓
1. Exception Type Determination
       ↓
2. Specific Exception Raised
   ├── InvalidConfigError (config issues)
   ├── PositionExistsError (state violations)
   └── NoPositionError (missing position)
       ↓
3. Client Error Handling
       ↓
4. Logging (if appropriate)
```

## Extension Points

### Adding New Strategy Types

1. **Inherit from BaseStrategy**: Implement required abstract methods
2. **Define Configuration**: Add strategy-specific configuration options
3. **Implement Core Logic**: Entry/exit logic and bar processing
4. **Add Tests**: Unit tests for strategy behavior

### Adding New Technical Indicators

1. **Create Calculator Class**: Similar interface to ATRCalculator
2. **Implement Core Methods**: add_bar(), get_value(), has_enough_samples()
3. **Integration**: Use in strategy or risk management modules
4. **Configuration**: Add configuration options if needed

### Adding New Risk Management Types

1. **Extend TrailingStopEngine**: Add new trailing stop algorithms
2. **Configuration Support**: Add configuration options for new types
3. **Interface Consistency**: Maintain existing interface contracts
4. **Testing**: Comprehensive unit tests for new algorithms

### Adding New Broker Integrations

1. **Inherit from BaseBroker**: Implement abstract broker interface
2. **Authentication**: Implement broker-specific authentication
3. **Order Management**: Map framework orders to broker API
4. **Error Handling**: Handle broker-specific errors appropriately

## Performance Considerations

### Memory Management

- **Rolling Windows**: Indicators use fixed-size windows to limit memory
- **Result Objects**: Lightweight dataclasses for minimal overhead
- **State Management**: Minimal state kept in strategy objects
- **Garbage Collection**: No circular references or memory leaks

### Computational Efficiency

- **Incremental Calculations**: ATR and other indicators update incrementally
- **Lazy Evaluation**: Calculations performed only when needed
- **Minimal Copying**: Objects passed by reference where safe
- **Efficient Data Structures**: Appropriate data structures for each use case

### Scalability

- **Stateless Components**: Most components can be parallelized
- **Event-Driven**: Natural fit for high-frequency processing
- **Modular Design**: Components can be optimized independently
- **Configuration-Driven**: Behavior tuning without code changes

## Testing Strategy

### Unit Testing

- **Isolated Components**: Each module tested independently
- **Mock Dependencies**: External dependencies mocked for isolation
- **Edge Cases**: Comprehensive testing of boundary conditions
- **State Testing**: Verify state transitions and invariants

### Integration Testing

- **Component Integration**: Test module interactions
- **End-to-End**: Full strategy execution workflows
- **Configuration Testing**: Various configuration combinations
- **Error Scenarios**: Error handling and recovery

### Performance Testing

- **Benchmark Testing**: Performance regression detection
- **Memory Testing**: Memory usage and leak detection
- **Scalability Testing**: Performance with large datasets
- **Profiling**: Identify bottlenecks and optimization opportunities

## Migration and Compatibility

### Backward Compatibility

- **Legacy Interface**: `enhancements_strategy.py` maintains old interface
- **Gradual Migration**: Step-by-step migration path documented
- **Bridge Pattern**: Legacy interface delegates to new implementation
- **Deprecation Warnings**: Clear migration timeline

### Future Evolution

- **Interface Stability**: Core interfaces designed for stability
- **Extension Points**: New features added through extension points
- **Configuration Evolution**: Backward-compatible configuration updates
- **Documentation**: Migration guides for breaking changes

## Security Considerations

### Input Validation

- **Configuration Validation**: All configuration validated at startup
- **Data Validation**: Market data validated for consistency
- **Parameter Bounds**: Trading parameters within reasonable bounds
- **Error Handling**: Graceful handling of invalid inputs

### State Protection

- **Immutable Results**: Result objects cannot be modified after creation
- **State Encapsulation**: Internal state properly encapsulated
- **Access Control**: Clear public/private interface boundaries
- **Exception Safety**: Strong exception safety guarantees

## Monitoring and Observability

### Logging Strategy

- **Structured Logging**: Consistent format across all components
- **Appropriate Levels**: DEBUG, INFO, WARNING, ERROR levels used appropriately
- **Context Information**: Relevant context included in log messages
- **Performance Impact**: Minimal performance impact from logging

### Metrics and Monitoring

- **Performance Metrics**: Built-in performance tracking
- **Error Metrics**: Error rates and types tracked
- **Business Metrics**: Trading-specific metrics (PnL, positions, etc.)
- **Real-Time Monitoring**: Live monitoring capabilities for production

## Conclusion

The Fantastic Palm Tree framework provides a robust, extensible architecture for algorithmic trading strategy development and backtesting. The modular design ensures that components can be developed, tested, and optimized independently while maintaining clear interfaces and contracts.

Key architectural strengths:

1. **Modularity**: Clean separation of concerns enables focused development
2. **Type Safety**: Strong typing prevents runtime errors and improves developer experience  
3. **Extensibility**: Well-defined extension points support new features
4. **Testability**: Isolated components and clear interfaces enable comprehensive testing
5. **Performance**: Efficient algorithms and data structures support high-frequency use
6. **Maintainability**: Clear code organization and documentation support long-term maintenance

The framework is designed to scale from simple backtesting scenarios to complex production trading systems while maintaining code quality and reliability throughout the evolution process.