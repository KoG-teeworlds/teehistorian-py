# Writing Teehistorian Files

This guide will show you how to create teehistorian files from scratch using the `TeehistorianWriter` API.

## Overview

The `TeehistorianWriter` provides a Pythonic interface for creating teehistorian files programmatically. It follows Python best practices with:

- **Context manager support** - Automatic cleanup and EOS writing
- **Method chaining** - Fluent API for readable code
- **Type safety** - Strong typing for all operations
- **Flexible output** - Save to file, get as bytes, or write to file-like objects

## Your First Teehistorian File

Let's create a simple teehistorian file with one player joining, saying something, and leaving:

```python
import teehistorian_py as th

# Create a new teehistorian file
with th.create() as writer:
    # Set some metadata
    writer.set_header("server_name", "My Test Server")
    writer.set_header("comment", "First recording")
    
    # Player joins
    writer.write(th.Join(0))
    
    # Set player name
    writer.write(th.PlayerName(0, "TestPlayer"))
    
    # Player spawns at coordinates (100, 200)
    writer.write(th.PlayerNew(0, 100, 200))
    
    # Player sends a message
    writer.write(th.NetMessage(0, "Hello, world!"))
    
    # Some time passes (30 ticks)
    writer.write(th.TickSkip(30))
    
    # Player leaves
    writer.write(th.PlayerOld(0))
    writer.write(th.Drop(0, "quit"))
    
    # Save the file
    writer.save("my_first_recording.teehistorian")
    # EOS chunk is automatically written when exiting the context
```

That's it! You've created your first teehistorian file.

## Understanding Headers

Headers contain metadata about the recording. Common headers include:

```python
with th.create() as writer:
    # Server information
    writer.set_header("server_name", "KoG Server")
    writer.set_header("server_version", "DDNet 17.4.2")
    
    # Recording information
    writer.set_header("comment", "Epic race on Sunny Side Up")
    writer.set_header("map_name", "Sunny Side Up")
    
    # Timestamps (automatically set, but can be overridden)
    writer.set_header("start_time", "2024-01-15T10:30:00Z")
    
    # Custom fields
    writer.set_header("recorder", "My Bot v1.0")
    writer.set_header("game_type", "DDRace")
```

You can also set headers during creation:

```python
writer = th.create(
    server_name="My Server",
    comment="Automated recording",
    map_name="dm1"
)
```

## Chunk Types and Usage

### Player Lifecycle

Track players joining and leaving:

```python
# Player joins
writer.write(th.Join(client_id))
writer.write(th.JoinVer6(client_id))  # For version 6 protocol

# Player becomes ready
writer.write(th.PlayerReady(client_id))

# Player leaves
writer.write(th.PlayerOld(client_id))
writer.write(th.Drop(client_id, reason))
```

### Player Information

Set and update player information:

```python
# Set player name
writer.write(th.PlayerName(client_id, "PlayerName"))

# Set player team
writer.write(th.PlayerTeam(client_id, team_id))

# Player spawns at position
writer.write(th.PlayerNew(client_id, x, y))

# Player moves (relative movement)
writer.write(th.PlayerDiff(client_id, dx, dy))
```

### Communication

Record chat messages and commands:

```python
# Chat message
writer.write(th.NetMessage(client_id, "Hello everyone!"))

# Console command
writer.write(th.ConsoleCommand(client_id, flags, "say", "message"))

# Authentication
writer.write(th.AuthLogin(client_id, level, "admin_name"))
```

### Server Events

Record server-side events:

```python
# Time skip (when server is idle)
writer.write(th.TickSkip(ticks))

# Team events (for team-based games)
writer.write(th.TeamLoadSuccess(team_id, save_data))
writer.write(th.TeamLoadFailure(team_id))

# Anti-cheat data
writer.write(th.AntiBot("detection_data"))

# Version information
writer.write(th.DdnetVersion(client_id, connection_id, version, version_str))

# End of stream (automatically added by context manager)
writer.write(th.Eos())
```

## Realistic Example: Recording a Race

Here's a more complete example of recording a DDRace game:

```python
import teehistorian_py as th
from datetime import datetime

def record_race():
    """Record a typical DDRace session."""
    
    with th.create() as writer:
        # Set up recording metadata
        writer.update_headers({
            "server_name": "KoG Gores",
            "map_name": "Sunny Side Up", 
            "game_type": "DDRace",
            "comment": "Race recording with 3 players",
            "start_time": datetime.utcnow().isoformat() + "Z"
        })
        
        # Three players join
        for player_id in range(3):
            writer.write(th.Join(player_id))
            
        # Set player names
        player_names = ["Alice", "Bob", "Charlie"]
        for player_id, name in enumerate(player_names):
            writer.write(th.PlayerName(player_id, name))
            
        # Players become ready
        for player_id in range(3):
            writer.write(th.PlayerReady(player_id))
            
        # Players spawn at start position
        start_positions = [(100, 200), (110, 200), (120, 200)]
        for player_id, (x, y) in enumerate(start_positions):
            writer.write(th.PlayerNew(player_id, x, y))
            
        # Race begins - players move
        writer.write(th.NetMessage(0, "Ready?"))
        writer.write(th.TickSkip(60))  # 1 second pause
        writer.write(th.NetMessage(0, "GO!"))
        
        # Simulate some movement and events
        movements = [
            (0, 5, -2),   # Alice moves right and up
            (1, 3, 1),    # Bob moves right and down  
            (2, 4, 0),    # Charlie moves right
        ]
        
        for player_id, dx, dy in movements:
            writer.write(th.PlayerDiff(player_id, dx, dy))
            
        # More race events
        writer.write(th.TickSkip(300))  # 5 seconds of racing
        writer.write(th.NetMessage(1, "Nice jump!"))
        
        writer.write(th.TickSkip(600))  # 10 more seconds
        writer.write(th.NetMessage(0, "Almost there!"))
        
        # Alice finishes first
        writer.write(th.NetMessage(0, "Yes! Personal best!"))
        writer.write(th.PlayerOld(0))
        writer.write(th.Drop(0, "finished"))
        
        # Others finish
        writer.write(th.TickSkip(180))  # 3 seconds later
        writer.write(th.PlayerOld(1))
        writer.write(th.Drop(1, "finished"))
        
        writer.write(th.TickSkip(300))  # 5 seconds later
        writer.write(th.PlayerOld(2))
        writer.write(th.Drop(2, "timeout"))
        
        # Save the recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"race_recording_{timestamp}.teehistorian"
        writer.save(filename)
        
        print(f"Race recording saved: {filename}")
        print(f"File size: {writer.size} bytes")

# Run the recording
record_race()
```

## Working with File-like Objects

You don't always need to save to disk. You can work with any file-like object:

```python
from io import BytesIO
import gzip

# Write to memory buffer
buffer = BytesIO()
with th.create() as writer:
    writer.write(th.Join(0))
    writer.writeto(buffer)

# Get the data
data = buffer.getvalue()
print(f"Teehistorian size: {len(data)} bytes")

# Write compressed file
with gzip.open("compressed.teehistorian.gz", "wb") as f:
    with th.create() as writer:
        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, "Player"))
        writer.writeto(f)
```

## Batch Operations

For better performance when writing many chunks:

```python
# Create many chunks
chunks = []
for i in range(100):
    chunks.extend([
        th.Join(i),
        th.PlayerName(i, f"Player{i}"),
        th.PlayerNew(i, i * 10, 200),
    ])

# Write them all at once
with th.create() as writer:
    writer.write_all(chunks)
    writer.save("batch_recording.teehistorian")
```

## Method Chaining

The writer supports fluent method chaining for readable code:

```python
# All methods return self, so you can chain them
recording = (th.create()
    .set_header("server_name", "Chain Server")
    .write(th.Join(0))
    .write(th.PlayerName(0, "ChainPlayer"))
    .write(th.PlayerNew(0, 100, 200)))

# Save when done
recording.save("chained_recording.teehistorian")
```

## Error Handling

Handle common errors gracefully:

```python
try:
    with th.create() as writer:
        writer.set_header("server_name", "My Server")
        writer.write(th.Join(0))
        
        # This will raise an error - can't modify headers after writing
        writer.set_header("comment", "Too late!")
        
except ValueError as e:
    print(f"Header error: {e}")

try:
    writer = th.create()
    writer.write(th.Join(0))
    
    # Manually closing and trying to write
    writer._closed = True
    writer.write(th.Drop(0, "quit"))  # Will raise ValueError
    
except ValueError as e:
    print(f"Closed writer error: {e}")
```

## Best Practices

### 1. Always Use Context Managers

```python
# Good - automatic cleanup and EOS
with th.create() as writer:
    writer.write(th.Join(0))

# Avoid - manual management
writer = th.create()
writer.write(th.Join(0))
writer.write(th.Eos())  # Must remember to add EOS
```

### 2. Set Headers Early

```python
# Good - headers set before any chunks
with th.create(server_name="My Server") as writer:
    writer.write(th.Join(0))

# Avoid - headers after chunks (will raise error)
with th.create() as writer:
    writer.write(th.Join(0))
    writer.set_header("server_name", "My Server")  # Error!
```

### 3. Use Batch Operations for Performance

```python
# Good - batch writing
chunks = [th.Join(i) for i in range(100)]
writer.write_all(chunks)

# Less efficient - individual writes
for i in range(100):
    writer.write(th.Join(i))
```

### 4. Handle Large Files Efficiently

```python
# Good - stream directly to file
with open("large_recording.teehistorian", "wb") as f:
    with th.create() as writer:
        # ... write many chunks ...
        writer.writeto(f)  # Stream directly

# Avoid - loading everything into memory first
with th.create() as writer:
    # ... write many chunks ...
    data = writer.getvalue()  # All in memory
    with open("large_recording.teehistorian", "wb") as f:
        f.write(data)
```

## Next Steps

- Check out the [Writer API Reference](../api/writer.md) for detailed method documentation
- Learn about all available [Chunk Types](../api/chunks.md)
- See the [Parser Guide](quickstart.md) for reading teehistorian files
- Browse the [examples](../../examples/) for more complex use cases

## Troubleshooting

### "Cannot modify header after writing has started"

Headers can only be set before writing the first chunk:

```python
# Fix: Set headers before any writes
with th.create() as writer:
    writer.set_header("server_name", "My Server")  # Must come first
    writer.write(th.Join(0))
```

### "Cannot write to closed writer"

This happens when trying to write after the context manager has exited:

```python
# Fix: Keep operations inside the context
with th.create() as writer:
    writer.write(th.Join(0))
    writer.save("file.teehistorian")  # Save inside context
```

### Large File Performance Issues

For very large recordings:

```python
# Fix: Use streaming and batch operations
with open("huge_recording.teehistorian", "wb") as f:
    with th.create() as writer:
        # Write in batches
        batch_size = 1000
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i+batch_size]
            writer.write_all(batch)
        writer.writeto(f)  # Stream to file
```
