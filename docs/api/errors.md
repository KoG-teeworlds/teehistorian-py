# Errors API

## Exception Hierarchy

```
TeehistorianError
├── ParseError
├── ValidationError
└── FileError
```

## TeehistorianError

::: teehistorian_py.TeehistorianError

Base exception for all teehistorian parsing errors.

All other exceptions inherit from this class.

**Example:**
```python
try:
    parser = th.Teehistorian(data)
except th.TeehistorianError as e:
    print(f"Error: {e}")
```

## ParseError

::: teehistorian_py.ParseError

Exception for parsing errors.

Raised when the parser encounters invalid data or cannot parse a chunk.

**Example:**
```python
try:
    parser = th.Teehistorian(corrupted_data)
    for chunk in parser:
        pass
except th.ParseError as e:
    print(f"Parse failed: {e}")
```

## ValidationError

::: teehistorian_py.ValidationError

Exception for validation errors.

Raised when input data fails validation checks (e.g., empty data, too short, invalid format).

**Example:**
```python
try:
    parser = th.Teehistorian(b"")
except th.ValidationError as e:
    print(f"Validation failed: {e}")
```

## FileError

::: teehistorian_py.FileError

Exception for file I/O errors.

Raised when there are issues reading or accessing the file.

**Example:**
```python
try:
    with open("demo.teehistorian", "rb") as f:
        data = f.read()
    parser = th.Teehistorian(data)
except th.FileError as e:
    print(f"File error: {e}")
```

## Error Handling Best Practices

1. **Catch specific exceptions first**: Handle more specific exceptions before the base exception
2. **Provide context**: Include filename or other context in error messages
3. **Log errors appropriately**: Use Python's logging module for production code
4. **Clean up resources**: Use context managers for file handling

See [Error Handling Guide](../guide/error-handling.md) for more detailed information and examples.
