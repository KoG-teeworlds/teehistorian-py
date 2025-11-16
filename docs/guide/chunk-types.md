# Chunk Types

## Player Lifecycle

### Join
Player joins the server.

```python
chunk.client_id  # int
```

### JoinVer6
Player joins with version 6 protocol.

```python
chunk.client_id  # int
```

### Drop
Player disconnects from the server.

```python
chunk.client_id  # int
chunk.reason     # str
```

### PlayerReady
Player becomes ready to play.

```python
chunk.client_id  # int
```

## Player State

### PlayerNew
New player spawn position.

```python
chunk.client_id  # int
chunk.x          # int
chunk.y          # int
```

### PlayerOld
Player leaves the game (but not server).

```python
chunk.client_id  # int
```

### PlayerTeam
Player changes team.

```python
chunk.client_id  # int
chunk.team       # int
```

### PlayerName
Player changes name.

```python
chunk.client_id  # int
chunk.name       # str
```

### PlayerDiff
Player position difference/update.

```python
chunk.client_id  # int
chunk.dx         # int
chunk.dy         # int
```

## Input Events

### InputNew
New player input state.

```python
chunk.client_id  # int
chunk.input      # str
```

### InputDiff
Player input difference from previous state.

```python
chunk.client_id  # int
chunk.input      # List[int]
```

## Communication

### NetMessage
Network message from/to player.

```python
chunk.client_id  # int
chunk.message    # str
```

### ConsoleCommand
Console command executed by player.

```python
chunk.client_id  # int
chunk.flags      # int
chunk.command    # str
chunk.args       # str
```

## Authentication & Version

### AuthLogin
Player authentication/login.

```python
chunk.client_id  # int
chunk.level      # int
chunk.name       # str
```

### DdnetVersion
DDNet client version information.

```python
chunk.client_id     # int
chunk.connection_id # str
chunk.version       # int
chunk.version_str   # bytes
```

## Server Events

### TickSkip
Server tick skip.

```python
chunk.dt  # int
```

### TeamLoadSuccess
Team save loaded successfully.

```python
chunk.team  # int
chunk.save  # str
```

### TeamLoadFailure
Team save load failed.

```python
chunk.team  # int
```

### AntiBot
Anti-bot system event.

```python
chunk.data  # str
```

## Special Chunks

### Eos
End of stream marker.

No attributes.

### Unknown
Unknown chunk with UUID.

```python
chunk.uuid  # str
chunk.data  # bytes
```

### CustomChunk
Custom chunk with registered handler.

```python
chunk.uuid          # str
chunk.data          # bytes
chunk.handler_name  # str
```

### Generic
Generic/fallback chunk type.

```python
chunk.data  # str
```
