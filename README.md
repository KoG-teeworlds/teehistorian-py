# teehistorian-py

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![PyPI version](https://badge.fury.io/py/teehistorian-py.svg)](https://badge.fury.io/py/teehistorian-py)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

High-performance Python bindings for parsing Teeworlds/DDNet teehistorian files. Built with Rust for speed and memory safety.

## Features

- 🚀 **Fast**: Rust-powered parsing with minimal Python overhead
- 🔒 **Memory Safe**: No buffer overflows or memory leaks
- 📦 **Simple API**: Clean Python interface for easy integration  
- 🧩 **Extensible**: Support for custom UUID handlers for mods
- 🎯 **Complete**: Covers all standard teehistorian chunk types

## Installation

```bash
pip install teehistorian-py
```

## Quick Start

```python
import teehistorian_py as th

# Parse a teehistorian file
with open("server.teehistorian", "rb") as f:
    data = f.read()

parser = th.Teehistorian(data)

# Iterate through all chunks
for chunk in parser:
    if isinstance(chunk, th.Join):
        print(f"Player {chunk.client_id} joined")
    elif isinstance(chunk, th.Drop):
        print(f"Player {chunk.client_id} left: {chunk.reason}")
    elif isinstance(chunk, th.PlayerName):
        print(f"Player {chunk.client_id} is now called '{chunk.name}'")
```

## Development

### Building from Source

```bash
# Install development dependencies
pip install maturin

# Build extension module
maturin develop --release

# Run tests
pytest tests/
```

### Requirements

- Python 3.8+
- Rust 1.70+ (for building from source)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Credits

- Built on top of the excellent [teehistorian](https://crates.io/crates/teehistorian) Rust crate
- Part of the [KoG-teeworlds](https://github.com/KoG-teeworlds) ecosystem

## Related Projects

- [teehistorian](https://github.com/heinrich5991/teehistorian) - Original Rust implementation
- [Teeworlds](https://teeworlds.com/) - The game that generates these files
- [DDNet](https://ddnet.tw/) - Popular Teeworlds modification

---

**Need help?** Open an issue or check our [documentation](https://github.com/KoG-teeworlds/teehistorian-py).
