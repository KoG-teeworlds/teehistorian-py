# Quick Start

## Basic Usage

Here's a simple example to get you started with teehistorian-py:

```python
import teehistorian_py as th

# Parse from file path with context manager (recommended)
with th.open("demo.teehistorian") as parser:
    for chunk in parser:
        print(chunk)
```

Without context manager:

```python
import teehistorian_py as th

# Parse from file path
parser = th.parse("demo.teehistorian")

# Iterate over chunks
for chunk in parser:
    print(chunk)
```

Or using `pathlib`:

```python
from pathlib import Path
import teehistorian_py as th

# Works with Path objects too
parser = th.parse(Path("demo.teehistorian"))

for chunk in parser:
    print(chunk)
```

If you already have bytes in memory:

```python
import teehistorian_py as th

# Parse from bytes directly
data = Path("demo.teehistorian").read_bytes()
parser = th.Teehistorian(data)

for chunk in parser:
    print(chunk)
```

## Filtering Specific Events

You can filter for specific chunk types using `isinstance`:

```python
import teehistorian_py as th

# Track player joins and drops
for chunk in th.parse("demo.teehistorian"):
    if isinstance(chunk, th.Join):
        print(f"Player {chunk.client_id} joined the server")
    elif isinstance(chunk, th.Drop):
        print(f"Player {chunk.client_id} left: {chunk.reason}")
```

Or use Python 3.10+ match statement for cleaner code:

```python
import teehistorian_py as th

for chunk in th.parse("demo.teehistorian"):
    match chunk:
        case th.Join(client_id=cid):
            print(f"Player {cid} joined the server")
        case th.Drop(client_id=cid, reason=reason):
            print(f"Player {cid} left: {reason}")
        case th.PlayerNew(client_id=cid, x=x, y=y):
            print(f"Player {cid} spawned at ({x}, {y})")
```

## Accessing Chunk Data

Each chunk type has specific attributes:

```python
import teehistorian_py as th

for chunk in th.parse("demo.teehistorian"):
    if isinstance(chunk, th.PlayerNew):
        print(f"Player {chunk.client_id} spawned at ({chunk.x}, {chunk.y})")
    elif isinstance(chunk, th.ConsoleCommand):
        print(f"Player {chunk.client_id} executed: {chunk.command} {chunk.args}")
```

All chunks support conversion to dictionaries:

```python
import teehistorian_py as th

for chunk in th.parse("demo.teehistorian"):
    # Convert to dict for inspection or JSON serialization
    chunk_dict = chunk.to_dict()
    print(chunk_dict)
```

## Error Handling

Handle parsing errors gracefully:

```python
import teehistorian_py as th

try:
    for chunk in th.parse("demo.teehistorian"):
        # Process chunks
        pass
        
except FileNotFoundError as e:
    print(f"File not found: {e}")
except th.ValidationError as e:
    print(f"Invalid file format: {e}")
except th.ParseError as e:
    print(f"Parse error: {e}")
except th.TeehistorianError as e:
    print(f"General error: {e}")
```

Or handle multiple files with error recovery:

```python
import teehistorian_py as th
from pathlib import Path

def parse_all_files(directory: Path):
    """Parse all teehistorian files in a directory."""
    for path in directory.glob("*.teehistorian"):
        try:
            parser = th.parse(path)
            yield from parser
        except th.TeehistorianError as e:
            print(f"Error parsing {path}: {e}")
            continue

# Usage
for chunk in parse_all_files(Path("replays")):
    print(chunk)
```

## Next Steps

- Learn about all [chunk types](../guide/chunk-types.md)
- Explore [error handling](../guide/error-handling.md)
- Check the [API reference](../api/parser.md)
