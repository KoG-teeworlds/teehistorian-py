# Quick Start

## Basic Usage

Here's a simple example to get you started with teehistorian-py:

```python
import teehistorian_py as th

# Read the teehistorian file
with open("demo.teehistorian", "rb") as f:
    data = f.read()

# Create parser
parser = th.Teehistorian(data)

# Iterate over chunks
for chunk in parser:
    print(chunk)
```

## Filtering Specific Events

You can filter for specific chunk types:

```python
import teehistorian_py as th

with open("demo.teehistorian", "rb") as f:
    data = f.read()

parser = th.Teehistorian(data)

# Track player joins and drops
for chunk in parser:
    if isinstance(chunk, th.Join):
        print(f"Player {chunk.client_id} joined the server")
    elif isinstance(chunk, th.Drop):
        print(f"Player {chunk.client_id} left: {chunk.reason}")
```

## Accessing Chunk Data

Each chunk type has specific attributes:

```python
import teehistorian_py as th

with open("demo.teehistorian", "rb") as f:
    data = f.read()

parser = th.Teehistorian(data)

for chunk in parser:
    if isinstance(chunk, th.PlayerNew):
        print(f"Player {chunk.client_id} spawned at ({chunk.x}, {chunk.y})")
    elif isinstance(chunk, th.ConsoleCommand):
        print(f"Player {chunk.client_id} executed: {chunk.command} {chunk.args}")
```

## Error Handling

Handle parsing errors gracefully:

```python
import teehistorian_py as th

try:
    with open("demo.teehistorian", "rb") as f:
        data = f.read()
    
    parser = th.Teehistorian(data)
    
    for chunk in parser:
        # Process chunks
        pass
        
except th.ValidationError as e:
    print(f"Invalid file format: {e}")
except th.ParseError as e:
    print(f"Parse error: {e}")
except th.TeehistorianError as e:
    print(f"General error: {e}")
```

## Next Steps

- Learn about all [chunk types](../guide/chunk-types.md)
- Explore [error handling](../guide/error-handling.md)
- Check the [API reference](../api/parser.md)
