# Contributing to Fantastic Palm Tree

Thank you for your interest in contributing to Fantastic Palm Tree! This document provides guidelines for contributing to this advanced backtesting framework.

## Getting Started

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/fantastic-palm-tree.git
   cd fantastic-palm-tree
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Code Quality

We maintain high code quality standards:

- **Linting**: Use `ruff check .` to check for issues
- **Formatting**: Use `ruff format .` to format code
- **Type Checking**: Use `mypy fantastic_palm_tree/` for type validation
- **Testing**: Use `pytest` to run tests with coverage

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Python version
   - Package version
   - Minimal reproduction steps
   - Expected vs actual behavior

### Feature Requests

1. Check existing feature requests
2. Use the feature request template
3. Provide:
   - Use case description
   - Proposed solution
   - Alternative solutions considered

### Pull Requests

1. Create a feature branch from `main`
2. Make your changes following our coding standards
3. Add tests for new functionality
4. Update documentation if needed
5. Ensure all tests pass
6. Submit a pull request with a clear description

#### PR Requirements

- [ ] Tests pass locally
- [ ] Code is properly formatted
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] Type hints added for new code

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints for all new code
- Prefer dataclasses for data structures
- Use descriptive variable and function names

### Documentation

- Write docstrings for all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings when helpful
- Keep README.md updated

### Testing

- Write unit tests for new features
- Aim for 80%+ test coverage
- Use pytest fixtures for test setup
- Mock external dependencies

## Project Structure

```
fantastic-palm-tree/
├── fantastic_palm_tree/     # Core package
├── backtesting/            # Backtesting framework
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/              # Usage examples
└── README.md              # Main documentation
```

## Security

- Never commit sensitive data (API keys, passwords)
- Follow our security policy in SECURITY.md
- Report security vulnerabilities privately

## Questions?

- Open a discussion on GitHub
- Check existing documentation
- Review similar issues/PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.