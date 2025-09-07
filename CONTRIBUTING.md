# Contributing to Fantastic Palm Tree

We welcome contributions to the Fantastic Palm Tree trading and backtesting framework! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Security](#security)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/fantastic-palm-tree.git
   cd fantastic-palm-tree
   ```
3. Set up the development environment (see [Development Setup](#development-setup))

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher (for frontend components)
- Git

### Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pre-commit install

# Install frontend dependencies
npm install
```

### Running Tests

```bash
# Run Python tests
pytest

# Run tests with coverage
pytest --cov=fantastic_palm_tree --cov-report=html

# Run specific test categories
pytest -k "test_strategy"
pytest -m slow  # For slow/integration tests

# Run frontend tests
npm test
```

### Code Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy fantastic_palm_tree/

# Run all quality checks
ruff check . && ruff format --check . && mypy fantastic_palm_tree/
```

## Making Changes

### Creating a Branch

Create a descriptive branch name:
```bash
git checkout -b feature/add-risk-management
git checkout -b fix/trailing-stop-calculation
git checkout -b docs/update-installation-guide
```

### Commit Messages

Use clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters or less
- Reference issues and pull requests when applicable

Examples:
```
Add trailing stop loss functionality

Implement ATR-based trailing stops with configurable activation
and distance parameters. Closes #123.

- Add TrailingStopManager class
- Integrate with existing position management
- Add comprehensive test coverage
- Update documentation
```

## Testing

### Test Requirements

- All new features must include tests
- Bug fixes must include regression tests
- Maintain or improve code coverage
- Tests should be fast and reliable

### Test Categories

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Performance tests**: Test performance-critical paths

### Writing Tests

```python
import pytest
from fantastic_palm_tree.strategy import EnhancedStrategy

def test_trailing_stop_activation():
    """Test that trailing stops activate at the correct R-multiple."""
    strategy = EnhancedStrategy(config={
        'trailing': {
            'activation_r_multiple': 2.0
        }
    })
    # Test implementation...
```

## Submitting Changes

### Before Submitting

1. Ensure all tests pass
2. Run code quality checks
3. Update documentation if needed
4. Add entry to CHANGELOG.md for significant changes
5. Rebase your branch on the latest main

### Pull Request Process

1. **Create Pull Request**: Submit a pull request to the main repository
2. **Fill Template**: Use the provided PR template
3. **Link Issues**: Reference related issues using keywords (fixes #123)
4. **Request Review**: Tag appropriate reviewers
5. **Address Feedback**: Respond to review comments promptly
6. **Update Branch**: Keep your branch up-to-date with main

### Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] No merge conflicts
- [ ] PR description clearly explains changes

## Code Style

### Python Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Maximum line length: 88 characters (Black default)
- Use descriptive variable and function names
- Add docstrings for all public functions and classes

```python
def calculate_position_size(
    account_balance: float,
    risk_percentage: float,
    stop_distance: float,
    price: float
) -> int:
    """Calculate position size based on risk management rules.
    
    Args:
        account_balance: Current account balance
        risk_percentage: Risk as percentage of account (0.0-1.0)
        stop_distance: Distance to stop loss in price units
        price: Current asset price
        
    Returns:
        Position size in shares
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Implementation...
```

### TypeScript/JavaScript Style

- Use TypeScript for all new frontend code
- Follow ESLint configuration
- Use meaningful component and variable names
- Add JSDoc comments for complex functions

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Keep documentation up-to-date with code changes
- Use proper Markdown formatting

## Security

### Reporting Security Issues

Please refer to our [Security Policy](SECURITY.md) for reporting security vulnerabilities.

### Security Guidelines

- Never commit secrets, API keys, or credentials
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices
- Keep dependencies up-to-date

## Getting Help

### Resources

- [Project Documentation](README.md)
- [API Reference](docs/api-reference.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Examples](examples/)

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Request Comments**: Code-specific discussions

### Maintainer Response Times

- We aim to respond to issues within 48 hours
- Pull requests are typically reviewed within 1 week
- Security issues are prioritized and addressed immediately

## Recognition

Contributors are recognized in:
- CHANGELOG.md for significant contributions
- README.md contributors section
- Release notes for major features

## License

By contributing to Fantastic Palm Tree, you agree that your contributions will be licensed under the [MIT License](LICENSE).

Thank you for contributing to Fantastic Palm Tree! 🌴