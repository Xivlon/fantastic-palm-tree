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

# Run tests
python -m pytest tests/ -v
```

### Code Standards
- Follow existing code style and patterns
- Add type hints for new code
- Include docstrings for public methods
- Keep changes minimal and focused
- Update documentation when needed

### Testing
- Write tests for new features
- Maintain or improve test coverage
- Test across different market conditions
- Include edge case testing

## Code of Conduct
This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Security
For security-related issues, see our [Security Policy](SECURITY.md).

## Getting Help
- Check existing documentation and issues first
- Use GitHub Discussions for questions
- Tag maintainers for urgent issues

Thank you for contributing!