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

### Methods

#### `__iter__()`
Returns the parser itself as an iterator.

#### `__next__()`
Returns the next chunk from the parser.

**Returns:**
- Chunk object or `None` at EOF

**Raises:**
- `ParseError`: If chunk parsing fails

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
