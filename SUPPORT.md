# Support

Welcome to the Fantastic Palm Tree support community! We're here to help you succeed with algorithmic trading strategy development and backtesting.

## Getting Help

### 📖 Documentation First
Before asking for help, please check:
- **[README.md](README.md)**: Comprehensive framework documentation
- **[API Reference](README.md#api-reference)**: Detailed API documentation
- **[Examples](examples/)**: Working code examples and tutorials
- **[Architecture Documentation](Architecture.md)**: Framework design and internals

### 💬 GitHub Discussions (Recommended)
**Best for**: General questions, strategy discussions, sharing experiences

[🔗 Start a Discussion](https://github.com/Xivlon/fantastic-palm-tree/discussions)

**Discussion Categories:**
- **💡 Ideas**: Feature requests and enhancement proposals
- **🙋 Q&A**: Questions about usage, implementation, and best practices
- **📋 General**: Community discussions about algorithmic trading
- **🎉 Show and Tell**: Share your strategies and results (anonymized)
- **📦 Extensions**: Third-party extensions and integrations

### 🐛 GitHub Issues
**Best for**: Bug reports, specific technical problems, feature requests

[🔗 Create an Issue](https://github.com/Xivlon/fantastic-palm-tree/issues/new)

**When to Use Issues:**
- Reproducible bugs in the framework
- Documentation errors or missing information
- Performance problems with specific use cases
- Feature requests with detailed specifications

**Issue Templates:**
- **Bug Report**: For reporting framework bugs
- **Feature Request**: For requesting new functionality
- **Documentation**: For documentation improvements
- **Performance**: For performance-related issues

### 📧 Direct Contact
**Best for**: Security vulnerabilities, licensing questions, sensitive topics

- **Security Issues**: Follow our [Security Policy](SECURITY.md)
- **Business Inquiries**: Contact maintainers through GitHub profile
- **Licensing Questions**: Create a GitHub issue with "licensing" label

## Community Guidelines

### 📋 Before Asking for Help
1. **Search First**: Check existing discussions and issues
2. **Be Specific**: Provide clear, minimal examples of your problem
3. **Include Context**: Python version, OS, framework version, error messages
4. **Show Your Work**: What have you tried? What didn't work?

### 💻 Creating Good Questions
Include this information in your questions:

```
**Environment:**
- Python version: 3.11.5
- Framework version: 0.1.0
- Operating System: Ubuntu 22.04

**Problem Description:**
Clear description of what you're trying to do and what's happening instead.

**Code Example:**
```python
# Minimal, reproducible code example
from fantastic_palm_tree import Strategy

# Your code that demonstrates the problem
```

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened, including any error messages.

**Additional Context:**
Any other relevant information.
```

### 🎯 Response Expectations
- **Community discussions**: Responses typically within 24-48 hours
- **Bug reports**: Acknowledged within 2-3 business days
- **Security issues**: Acknowledged within 24 hours (see [Security Policy](SECURITY.md))
- **Feature requests**: Reviewed in monthly planning sessions

## Contributing Back

### 🤝 Ways to Help the Community
- **Answer Questions**: Help other users in discussions
- **Share Examples**: Contribute working strategy examples
- **Report Bugs**: Help us identify and fix issues
- **Improve Documentation**: Suggest or contribute documentation improvements
- **Code Contributions**: See our [Contributing Guide](CONTRIBUTING.md)

### 📚 Educational Resources
**Algorithmic Trading Learning:**
- [Quantitative Trading Strategies](https://github.com/topics/quantitative-trading)
- [Algorithmic Trading Books](https://github.com/wilsonfreitas/awesome-quant#books)
- [Financial Data Sources](https://github.com/wilsonfreitas/awesome-quant#data-sources)

**Python for Finance:**
- [Python for Finance Resources](https://github.com/topics/python-finance)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Financial Functions](https://numpy.org/doc/stable/reference/routines.financial.html)

## Frequently Asked Questions

### General Usage

**Q: How do I get started with my first strategy?**
A: Check the [Quick Start](README.md#quick-start) section in the README and explore the [examples](examples/) directory.

**Q: Can I use this for live trading?**
A: The framework includes paper trading and broker integration scaffolding, but you're responsible for testing and risk management in live environments.

**Q: What data sources are supported?**
A: The framework is designed to work with any OHLCV data source. See our [data integration examples](examples/data_integration/).

### Technical Support

**Q: Why are my backtests running slowly?**
A: Check the [Performance Best Practices](README.md#performance--best-practices) section for optimization tips.

**Q: How do I add custom indicators?**
A: See the [Extension Guide](README.md#extension-guide) for information on extending the framework.

**Q: Can I backtest multiple strategies simultaneously?**
A: Yes, see the [Advanced Features](README.md#advanced-features) documentation for parallel backtesting.

### Troubleshooting

**Q: I'm getting import errors**
A: Ensure you've installed the framework with `pip install -e .` and all dependencies with `pip install -r requirements.txt`

**Q: Tests are failing**
A: Run `python -m pytest tests/ -v` to see detailed test output. Check that all dependencies are installed.

**Q: Pre-commit hooks are failing**
A: Run `pre-commit run --all-files` to see specific linting issues and fix them.

## Community Standards

### 🌟 Our Commitment
We are committed to providing a welcoming, inclusive environment for everyone, regardless of background or experience level.

### 📜 Code of Conduct
All community interactions are governed by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read and follow these guidelines.

### 🚀 Response Quality
We strive to provide:
- **Helpful**: Clear, actionable guidance
- **Respectful**: Professional, courteous communication
- **Educational**: Explanations that help you learn
- **Timely**: Responses within reasonable timeframes

## Disclaimer

**⚠️ Important Trading Disclaimer**
This framework is for educational and research purposes. Always:
- Test strategies thoroughly before live trading
- Understand the risks of algorithmic trading
- Comply with applicable financial regulations
- Never risk more than you can afford to lose

See our full [Risk Disclaimers](docs/DISCLAIMERS.md) for more information.

---

**Thank you for being part of the Fantastic Palm Tree community!** 🌴

Your questions, feedback, and contributions help make this framework better for everyone.