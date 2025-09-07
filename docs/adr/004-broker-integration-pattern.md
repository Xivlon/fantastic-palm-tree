# ADR-004: Broker Integration Pattern

## Status
Accepted

## Context
The framework needed to support multiple broker integrations for live trading while maintaining:
- Consistent interface across brokers
- Asynchronous operations for performance
- Proper authentication and error handling
- Easy testing with paper trading
- Extensibility for new brokers

## Decision
We adopted an adapter pattern with async/await for broker integration:

1. **Abstract Base Class**: Common interface for all brokers
2. **Async Operations**: Non-blocking broker communications
3. **Authentication Layer**: Separate authentication handling
4. **Paper Trading**: Mock implementation for testing

### Design Pattern
```python
class BaseBroker(ABC):
    @abstractmethod
    async def place_order(self, order: Order) -> OrderResult:
        pass
    
    @abstractmethod
    async def get_positions(self) -> list[Position]:
        pass

class SchwabBroker(BaseBroker):
    def __init__(self, auth: SchwabAuth):
        self.auth = auth
    
    async def place_order(self, order: Order) -> OrderResult:
        # Implementation specific to Schwab API
        pass
```

### Authentication Strategy
- OAuth2 flow with token refresh
- Secure token storage
- Environment variable configuration
- Automatic token renewal

## Consequences

### Positive
- Uniform interface across different brokers
- Non-blocking operations improve performance
- Easy to add new broker implementations
- Paper trading enables safe testing
- Proper separation of concerns

### Negative
- Async complexity requires careful error handling
- Authentication setup can be complex
- Network errors need robust handling

### Mitigation
- Comprehensive error handling and retry logic
- Clear documentation for broker setup
- Paper trading for development and testing
- Connection health monitoring