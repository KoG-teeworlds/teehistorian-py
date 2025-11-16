# Basic Usage

## Creating a Parser

The `Teehistorian` class is the main entry point for parsing teehistorian files:

```python
import teehistorian_py as th

# Read the file
with open("demo.teehistorian", "rb") as f:
    data = f.read()

# Create the parser
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
