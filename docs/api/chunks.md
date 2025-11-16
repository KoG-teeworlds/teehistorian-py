# Chunks API

All chunk types share common methods and follow a consistent interface.

## Common Methods

All chunk types implement these methods:

### `chunk_type() -> str`
Returns the chunk type as a string.

### `to_dict() -> dict`
Converts the chunk to a dictionary for easier inspection.

### `__repr__() -> str`
Returns a string representation of the chunk.

### `__str__() -> str`
Returns a human-readable string representation.

## Chunk Type Reference

See [Chunk Types](../guide/chunk-types.md) for a complete list of all available chunk types and their attributes.

### Player Lifecycle Chunks
- `Join`
- `JoinVer6`
- `Drop`
- `PlayerReady`

### Player State Chunks
- `PlayerNew`
- `PlayerOld`
- `PlayerTeam`
- `PlayerName`
- `PlayerDiff`

### Input Chunks
- `InputNew`
- `InputDiff`

### Communication Chunks
- `NetMessage`
- `ConsoleCommand`

### Authentication & Version Chunks
- `AuthLogin`
- `DdnetVersion`

### Server Event Chunks
- `TickSkip`
- `TeamLoadSuccess`
- `TeamLoadFailure`
- `AntiBot`

### Special Chunks
- `Eos`
- `Unknown`
- `CustomChunk`
- `Generic`
