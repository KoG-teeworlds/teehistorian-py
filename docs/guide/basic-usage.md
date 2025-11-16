# Basic Usage

## Creating a Parser

The recommended way to parse teehistorian files is using the `open()` function with a context manager:

```python
import teehistorian_py as th

# Recommended: use context manager
with th.open("demo.teehistorian") as parser:
    for chunk in parser:
        print(chunk)
```

Alternative methods:

```python
import teehistorian_py as th

# Method 1: Using parse()
parser = th.parse("demo.teehistorian")

# Method 2: From bytes directly
from pathlib import Path
data = Path("demo.teehistorian").read_bytes()
parser = th.Teehistorian(data)
```

## Iterating Over Chunks

The parser implements the iterator protocol, allowing you to loop over all chunks:

```python
for chunk in parser:
    print(f"Chunk type: {chunk.chunk_type()}")
    print(f"Chunk data: {chunk}")
```

## Using TeehistorianParser Alias

For backward compatibility, you can also use `TeehistorianParser`:

```python
# These are equivalent
parser1 = th.Teehistorian(data)
parser2 = th.TeehistorianParser(data)
```

## Converting Chunks to Dictionaries

All chunks can be converted to dictionaries for easier inspection:

```python
for chunk in parser:
    chunk_dict = chunk.to_dict()
    print(chunk_dict)
```

## Getting Parser Statistics

You can access the chunk count during iteration:

```python
parser = th.Teehistorian(data)

for chunk in parser:
    # Process chunk
    pass

print(f"Processed {parser.chunk_count} chunks")
```
