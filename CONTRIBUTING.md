# Contributing to Fantastic Palm Tree

Thank you for your interest in contributing to the Fantastic Palm Tree backtesting framework! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues
- Use the GitHub issue tracker to report bugs or request features
- Provide clear, reproducible steps for bug reports
- Include system information (Python version, OS, dependencies)

### Pull Requests
1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes with clear commit messages
4. Add or update tests as needed
5. Ensure all tests pass
6. Submit a pull request with a clear description

### Development Setup
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/fantastic-palm-tree.git
cd fantastic-palm-tree

# Install development dependencies
pip install -e .
pip install -r requirements.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
python -m pytest tests/ -v
```

## Workflow and Branching Model

### Branching Strategy
We follow a simplified Git Flow model:

- **`main`**: Production-ready code, protected branch
- **`develop`**: Integration branch for features (if needed for major releases)
- **Feature branches**: `feature/short-description` or `fix/issue-number`
- **Release branches**: `release/v1.0.0` (for major releases)
- **Hotfix branches**: `hotfix/critical-fix-description`

### Workflow
1. **Create Feature Branch**: Branch from `main` for most work
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**: Implement your feature with tests
3. **Regular Commits**: Make small, logical commits
4. **Push and PR**: Push branch and create pull request to `main`
5. **Code Review**: Address review feedback
6. **Merge**: Squash and merge after approval

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear, semantic commit messages:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, missing semi-colons, etc)
- **refactor**: Code refactoring without feature changes
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Changes to build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files

### Examples
```bash
git commit -m "feat(strategy): add ATR breakout strategy implementation"
git commit -m "fix(risk): resolve trailing stop calculation bug"
git commit -m "docs: update installation instructions"
git commit -m "test(integration): add end-to-end backtesting tests"
```

### Scope Guidelines
Common scopes for this project:
- `strategy`: Strategy-related changes
- `risk`: Risk management features
- `data`: Data handling and models
- `api`: API and interface changes
- `docs`: Documentation
- `ci`: Continuous integration
- `deps`: Dependency updates

## Code Style and Quality

### Python Code Style
We use automated tools to maintain consistent code quality:

- **Formatter**: [Ruff](https://github.com/astral-sh/ruff) for code formatting
- **Linter**: Ruff for linting and import sorting
- **Type Checker**: [mypy](http://mypy-lang.org/) for static type checking
- **Security**: [bandit](https://github.com/PyCQA/bandit) for security linting

### Code Style Guidelines

#### General Python Standards
- Follow [PEP 8](https://pep8.org/) style guide
- Maximum line length: 88 characters (Black default)
- Use type hints for all public functions and class methods
- Write comprehensive docstrings using Google style
- Prefer composition over inheritance
- Use descriptive variable and function names

#### Type Hints
```python
from typing import List, Optional, Union
from decimal import Decimal
from datetime import datetime

def calculate_position_size(
    portfolio_value: Decimal,
    risk_percentage: float,
    stop_loss_distance: float
) -> Decimal:
    """Calculate position size based on risk management rules."""
    # Implementation here
```

#### Docstring Style
```python
def backtest_strategy(
    strategy: Strategy,
    data: pd.DataFrame,
    start_date: datetime,
    end_date: datetime
) -> BacktestResult:
    """Run a backtest for the given strategy.
    
    Args:
        strategy: The trading strategy to test
        data: Historical market data
        start_date: Start date for backtesting
        end_date: End date for backtesting
        
    Returns:
        Complete backtest results with metrics
        
    Raises:
        ValueError: If date range is invalid
        DataError: If market data is insufficient
    """
```

#### Error Handling
- Use specific exception types
- Include helpful error messages
- Handle edge cases gracefully
- Use logging for debugging information

### Testing Standards
- **Minimum Coverage**: 80% code coverage
- **Test Types**: Unit tests, integration tests, property-based tests
- **Test Structure**: Arrange-Act-Assert pattern
- **Naming**: `test_function_name_expected_behavior`
- **Fixtures**: Use pytest fixtures for test data

```python
def test_atr_calculation_with_valid_data():
    """Test ATR calculation with valid historical data."""
    # Arrange
    data = create_sample_ohlc_data()
    period = 14
    
    # Act
    atr_values = calculate_atr(data, period)
    
    # Assert
    assert len(atr_values) == len(data) - period + 1
    assert all(atr > 0 for atr in atr_values)
```

## Development Tools

### Required Tools
Install these tools for development:

```bash
# Core development dependencies
pip install -e ".[dev]"

# Pre-commit hooks (automatic code formatting and linting)
pre-commit install
```

### Pre-commit Hooks
We use pre-commit hooks to automatically format and lint code:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
```

### Running Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check . --fix

# Type checking
mypy fantastic_palm_tree/

# Security scanning
bandit -r fantastic_palm_tree/

# Run all pre-commit hooks
pre-commit run --all-files

# Run tests with coverage
pytest tests/ --cov=fantastic_palm_tree --cov-report=html
```

### IDE Configuration

#### VS Code
Recommended extensions and settings:
```json
{
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.linting.flake8Enabled": false,
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true
}
```

#### PyCharm
- Enable mypy plugin
- Configure Black as external tool
- Set up pytest as test runner
- Enable PEP 8 inspections

### Testing Guidelines
- Write tests for new features
- Maintain or improve test coverage
- Test across different market conditions
- Include edge case testing
- Use property-based testing for mathematical functions

## Code of Conduct
This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Security
For security-related issues, see our [Security Policy](SECURITY.md).

## Getting Help
- Check existing documentation and issues first
- Use GitHub Discussions for questions
- Tag maintainers for urgent issues

Thank you for contributing!