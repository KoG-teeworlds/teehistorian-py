# Error Handling

## Exception Hierarchy

teehistorian-py provides a hierarchy of exceptions for different error scenarios:

```
TeehistorianError (base exception)
├── ParseError (parsing errors)
├── ValidationError (validation errors)
└── FileError (I/O errors)
```

## Basic Error Handling

```python
import teehistorian_py as th

try:
    with open("demo.teehistorian", "rb") as f:
        data = f.read()
    
    parser = th.Teehistorian(data)
    
    for chunk in parser:
        # Process chunks
        pass
        
except th.TeehistorianError as e:
    print(f"Error: {e}")
```

## Handling Specific Errors

### ValidationError

Raised when the input data fails validation:

```python
try:
    parser = th.Teehistorian(b"")  # Empty data
except th.ValidationError as e:
    print(f"Invalid data: {e}")
    # Output: Invalid data: Validation failed: Cannot parse empty data
```

### ParseError

Raised when parsing fails:

```python
try:
    parser = th.Teehistorian(invalid_data)
    for chunk in parser:
        pass
except th.ParseError as e:
    print(f"Parse failed: {e}")
```

### FileError

Raised for I/O related errors:

```python
try:
    with open("demo.teehistorian", "rb") as f:
        data = f.read()
    parser = th.Teehistorian(data)
except th.FileError as e:
    print(f"File error: {e}")
except FileNotFoundError:
    print("File not found")
```

## Comprehensive Error Handling

```python
import teehistorian_py as th

def parse_teehistorian_file(filename):
    try:
        # Read file
        with open(filename, "rb") as f:
            data = f.read()
        
        # Create parser
        parser = th.Teehistorian(data)
        
        # Process chunks
        chunks = []
        for chunk in parser:
            chunks.append(chunk)
        
        return chunks
        
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
        
    except th.ValidationError as e:
        print(f"Invalid teehistorian file: {e}")
        return None
        
    except th.ParseError as e:
        print(f"Failed to parse file: {e}")
        return None
        
    except th.FileError as e:
        print(f"I/O error: {e}")
        return None
        
    except th.TeehistorianError as e:
        print(f"Unexpected error: {e}")
        return None
```

## Best Practices

1. **Always validate input**: Check file existence and size before parsing
2. **Catch specific exceptions first**: Handle `ValidationError`, `ParseError`, and `FileError` before the base `TeehistorianError`
3. **Provide meaningful error messages**: Help users understand what went wrong
4. **Clean up resources**: Use context managers (`with` statements) for file handling
5. **Log errors appropriately**: Consider using Python's logging module for production code

## Example with Logging

```python
import logging
import teehistorian_py as th

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_file(filename):
    try:
        with open(filename, "rb") as f:
            data = f.read()
        
        logger.info(f"Parsing {filename} ({len(data)} bytes)")
        parser = th.Teehistorian(data)
        
        chunk_count = 0
        for chunk in parser:
            chunk_count += 1
        
        logger.info(f"Successfully parsed {chunk_count} chunks")
        
    except th.ValidationError as e:
        logger.error(f"Validation error in {filename}: {e}")
    except th.ParseError as e:
        logger.error(f"Parse error in {filename}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error parsing {filename}")
```
