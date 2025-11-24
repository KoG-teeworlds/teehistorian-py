# teehistorian-py

High-performance Python bindings for parsing teehistorian files, written in Rust using PyO3.

## Features

- **Fast**: Written in Rust for maximum performance
- **Pythonic**: Clean Python API with type hints and context managers
- **Memory Efficient**: Zero-copy parsing where possible
- **Type Safe**: Strong typing for all chunk types
- **Easy to Use**: Simple iterator-based interface
- **Full Read/Write Support**: Parse existing files and create new ones

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

## Writing Files

```python
import teehistorian_py as th

# Create a new teehistorian file (modern way with context manager)
with th.create(server_name="My Server") as writer:
    writer.write(th.Join(0))
    writer.write(th.PlayerName(0, "Alice"))
    writer.write(th.PlayerNew(0, 100, 200))
    writer.save("recording.teehistorian")
    # EOS chunk is automatically written when exiting context

# Method chaining for fluent API
writer = (th.create()
    .set_header("server_name", "My Server")
    .write(th.Join(0))
    .write(th.PlayerName(0, "Player")))
```

## Installation

```bash
pip install teehistorian-py
```

## Documentation

- [Installation Guide](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [Writing Guide](getting-started/writing.md)
- [API Reference](api/parser.md)
- [Writer API](api/writer.md)

## Links

- [GitHub Repository](https://github.com/KoG-teeworlds/teehistorian-py)
- [PyPI Package](https://pypi.org/project/teehistorian-py/)
- [Issue Tracker](https://github.com/KoG-teeworlds/teehistorian-py/issues)

## License

This project is licensed under the AGPLv3 License - see the LICENSE file for details.
