# teehistorian-py

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![PyPI version](https://badge.fury.io/py/teehistorian-py.svg)](https://badge.fury.io/py/teehistorian-py)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://kog-teeworlds.github.io/teehistorian-py/)
[![codecov](https://codecov.io/gh/KoG-teeworlds/teehistorian-py/branch/main/graph/badge.svg)](https://codecov.io/gh/KoG-teeworlds/teehistorian-py)
[![CI](https://github.com/KoG-teeworlds/teehistorian-py/workflows/Build%20and%20Publish/badge.svg)](https://github.com/KoG-teeworlds/teehistorian-py/actions)

High-performance Python bindings for parsing Teeworlds/DDNet teehistorian files. Built with Rust for speed and memory safety.

📚 **[Documentation](https://kog-teeworlds.github.io/teehistorian-py/)** | 🐛 **[Issue Tracker](https://github.com/KoG-teeworlds/teehistorian-py/issues)** | 📦 **[PyPI](https://pypi.org/project/teehistorian-py/)**

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

# Parse a teehistorian file (modern Pythonic way)
with th.open("server.teehistorian") as parser:
    for chunk in parser:
        if isinstance(chunk, th.Join):
            print(f"Player {chunk.client_id} joined")
        elif isinstance(chunk, th.Drop):
            print(f"Player {chunk.client_id} left: {chunk.reason}")
        elif isinstance(chunk, th.PlayerName):
            print(f"Player {chunk.client_id} is now called '{chunk.name}'")
```

Or with Python 3.10+ match statement:

```python
import teehistorian_py as th

with th.open("server.teehistorian") as parser:
    for chunk in parser:
        match chunk:
            case th.Join(client_id=cid):
                print(f"Player {cid} joined")
            case th.Drop(client_id=cid, reason=reason):
                print(f"Player {cid} left: {reason}")
            case th.PlayerName(client_id=cid, name=name):
                print(f"Player {cid} is now called '{name}'")
```

See the **[full documentation](https://kog-teeworlds.github.io/teehistorian-py/)** for more examples and advanced usage.

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
