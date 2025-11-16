# Contributing

Thank you for your interest in contributing to teehistorian-py!

## Development Setup

1. Fork and clone the repository
2. Install Rust and Python dependencies
3. Set up the development environment:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install maturin pytest pytest-cov black isort mypy

# Build the extension
maturin develop
```

## Running Tests

```bash
# Run Python tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=teehistorian_py --cov-report=html
```

## Code Quality

```bash
# Format Rust code
cargo fmt

# Lint Rust code
cargo clippy -- -D warnings

# Format Python code
black .
isort .

# Type check Python code
mypy .
```

## Making Changes

1. Create a new branch for your feature
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Run code formatters and linters
6. Submit a pull request

## Pull Request Guidelines

- Write clear commit messages
- Include tests for new features
- Update documentation as needed
- Ensure CI passes
- Keep changes focused and atomic

## Reporting Issues

Use the [GitHub issue tracker](https://github.com/KoG-teeworlds/teehistorian-py/issues) to report bugs or suggest features.

Include:
- Clear description of the issue
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
