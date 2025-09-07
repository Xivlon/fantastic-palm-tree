# ADR-003: Configuration System Design

## Status
Accepted

## Context
The framework needed a flexible configuration system that could:
- Support different strategy configurations
- Provide sensible defaults
- Validate configuration consistency
- Allow hierarchical configuration
- Enable environment-specific overrides

## Decision
We implemented a configuration system based on:

1. **Dataclass-based Configuration**: Type-safe configuration objects
2. **Default Merging**: Automatic merging of user config with defaults
3. **Post-initialization Validation**: Configuration validation at creation time
4. **Nested Configuration**: Hierarchical structure for complex settings

### Design
```python
@dataclass
class StrategyConfig:
    exits: dict[str, Any] = field(default_factory=dict)
    atr_period: int = 14
    
    def __post_init__(self) -> None:
        self._merge_defaults()
        self._validate()
    
    @property
    def trailing(self) -> dict[str, Any]:
        return self.exits.get("trailing", {})
```

### Configuration Hierarchy
- **System Defaults**: Framework-level defaults
- **Strategy Defaults**: Strategy-specific defaults  
- **User Configuration**: User-provided overrides
- **Environment Variables**: Runtime overrides

## Consequences

### Positive
- Type-safe configuration with IDE support
- Early validation prevents runtime configuration errors
- Flexible override system for different environments
- Self-documenting through type hints and defaults
- Extensible for new configuration options

### Negative
- More complex than simple dictionary configuration
- Requires understanding of dataclass patterns
- Validation logic needs maintenance

### Mitigation
- Comprehensive documentation with examples
- Clear error messages for validation failures
- Configuration templates for common use cases