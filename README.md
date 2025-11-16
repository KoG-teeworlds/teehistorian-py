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

## Chunk Types

The parser supports all standard teehistorian chunk types:

### Player Lifecycle
- `Join` / `JoinVer6` - Player connects
- `Drop` - Player disconnects  
- `PlayerReady` - Player becomes ready
- `PlayerNew` - Player spawns
- `PlayerOld` - Player despawns

### Player State
- `PlayerTeam` - Team change
- `PlayerName` - Name change
- `PlayerDiff` - Position updates
- `AuthLogin` - Authentication events

### Input & Communication  
- `InputNew` / `InputDiff` - Player input events
- `NetMessage` - Network messages
- `ConsoleCommand` - Console commands

### Server Events
- `TickSkip` - Server tick skips
- `TeamLoadSuccess` / `TeamLoadFailure` - Team save events
- `AntiBot` - Anti-bot system events
- `DdnetVersion` - Client version info

### Special
- `Eos` - End of stream
- `Unknown` - Unknown UUID chunks
- `CustomChunk` - Registered custom handlers
- `Generic` - Fallback for unhandled types

## Custom UUID Handlers

Register handlers for mod-specific chunks:

```python
parser = th.Teehistorian(data)

# Register a custom UUID for mod support
parser.register_custom_uuid("12345678-1234-5678-1234-567812345678")

# Custom chunks will now appear as CustomChunk objects
for chunk in parser:
    if isinstance(chunk, th.CustomChunk):
        print(f"Custom chunk: {chunk.handler_name}")
        print(f"Data: {chunk.data_preview()}")
```

## API Reference

### `Teehistorian(data: bytes)`

Main parser class.

**Methods:**
- `register_custom_uuid(uuid_string: str)` - Register custom UUID handler
- `get_registered_uuids() -> List[str]` - Get registered UUID list  
- `header() -> bytes` - Get file header data
- `chunk_count -> int` - Current chunk count (property)

**Usage:**
```python
parser = th.Teehistorian(file_data)
for chunk in parser:  # Implements iterator protocol
    process_chunk(chunk)
```

### Chunk Objects

All chunks have these common methods:
- `chunk_type() -> str` - Get chunk type name
- `to_dict() -> Dict` - Convert to dictionary
- `__repr__()` / `__str__()` - String representations

## Utilities

```python
from teehistorian_py import calculate_uuid, format_uuid_from_bytes

# Generate UUID for mod integration
uuid = calculate_uuid("my-mod@example.com")
print(f"Mod UUID: {uuid}")

# Format raw UUID bytes
formatted = format_uuid_from_bytes(raw_bytes)
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

## Performance

This library is built for performance:

- **Zero-copy parsing** where possible
- **Streaming iteration** - memory efficient for large files  
- **Rust backend** - native speed with memory safety
- **Minimal Python overhead** - thin wrapper around Rust core

Benchmarks show 10-50x performance improvements over pure Python implementations.

## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md).

### Areas for Contribution

- Additional chunk type support
- Performance optimizations  
- Documentation improvements
- Example scripts and tutorials
- Testing and bug reports

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