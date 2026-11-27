# Parser API

## Teehistorian

**The main parser class for teehistorian files.**

### Constructor

```python
Teehistorian(data: bytes) -> Teehistorian
```

Creates a new teehistorian parser from raw bytes.

**Parameters:**
- `data` (bytes): Raw teehistorian file data

**Returns:**
- `Teehistorian`: A new parser instance

**Raises:**
- `ValidationError`: If the data is empty or too short
- `ParseError`: If the file format is invalid

**Example:**
```python
with open("demo.teehistorian", "rb") as f:
    data = f.read()

parser = th.Teehistorian(data)
```

### File-backed streaming

```python
parser = Teehistorian.from_file("demo.teehistorian")
```

`from_file` opens the recording without loading it into a Python `bytes` object.
Chunks are read incrementally into the upstream parser's bounded buffer (at most 4
MiB for any single header/chunk), while the total file size, chunk count, metadata,
and decoded network-message limits remain configurable. The convenience
`teehistorian_py.parse(path)` and `open(path)` helpers use this file-backed path.

The default file-backed JSON-header ceiling is 4,194,287 bytes so the 16-byte
format UUID, header, and terminator remain within that bounded buffer. Use the bytes
constructor only when the recording is already in memory.

### Methods

#### `__iter__()`
Returns the parser itself as an iterator.

#### `__next__()`
Returns the next chunk from the parser.

**Returns:**
- Chunk object or `None` at EOF

**Raises:**
- `ParseError`: If chunk parsing fails

#### `next_batch(max_items: int = 1024)`

Pull at most `max_items` chunks from the current parser position. The batch is
bounded to 65,536 items and parsing stops early at EOF. Repeated calls provide
batch-oriented backpressure without materializing the remaining recording.

```python
while batch := parser.next_batch(512):
    process(batch)
```

#### `header()`
Get the header data as bytes.

**Returns:**
- `bytes`: Header bytes

**Raises:**
- `ParseError`: If header parsing fails

#### `register_custom_uuid(uuid_string: str)`
Register a custom UUID handler.

**Parameters:**
- `uuid_string` (str): The UUID string to register

**Returns:**
- `None`

**Raises:**
- `ValidationError`: If UUID format is invalid

#### `get_registered_uuids()`
Get registered handler UUIDs.

**Returns:**
- `list[str]`: List of registered UUID strings

### Properties

#### `chunk_count`
Get the current chunk count.

**Returns:**
- `int`: Number of chunks processed

## TeehistorianParser

Alias for `Teehistorian` provided for backward compatibility.

```python
TeehistorianParser = Teehistorian
```
