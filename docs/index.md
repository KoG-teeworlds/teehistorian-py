# teehistorian-py

High-performance Python bindings for parsing teehistorian files, written in Rust using PyO3.

## Features

- **Fast**: Written in Rust for maximum performance
- **Pythonic**: Clean Python API with type hints
- **Memory Efficient**: Zero-copy parsing where possible
- **Type Safe**: Strong typing for all chunk types
- **Easy to Use**: Simple iterator-based interface

## Quick Example

```python
import teehistorian_py as th

# Parse a teehistorian file (modern way)
with th.open("demo.teehistorian") as parser:
    for chunk in parser:
        if isinstance(chunk, th.Join):
            print(f"Player {chunk.client_id} joined")
        elif isinstance(chunk, th.Drop):
            print(f"Player {chunk.client_id} left: {chunk.reason}")
```

Or with Python 3.10+ match statement:

```python
import teehistorian_py as th

for chunk in th.parse("demo.teehistorian"):
    match chunk:
        case th.Join(client_id=cid):
            print(f"Player {cid} joined")
        case th.Drop(client_id=cid, reason=reason):
            print(f"Player {cid} left: {reason}")
```

## Installation

```bash
pip install teehistorian-py
```

## Documentation

- [Installation Guide](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [API Reference](api/parser.md)

## Links

- [GitHub Repository](https://github.com/KoG-teeworlds/teehistorian-py)
- [PyPI Package](https://pypi.org/project/teehistorian-py/)
- [Issue Tracker](https://github.com/KoG-teeworlds/teehistorian-py/issues)

## License

This project is licensed under the AGPLv3 License - see the LICENSE file for details.
