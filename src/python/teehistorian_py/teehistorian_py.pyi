#!/usr/bin/env python3
"""
Type stubs for the Rust teehistorian extension module.

This file provides type hints for the Rust extension module so that
type checkers like Pyright/Pylance can understand the module structure.

Place this file as:
- teehistorian.pyi (if Rust module is named 'teehistorian')
- or teehistorian_py.pyi (if Rust module is named 'teehistorian_py')

In the same directory as your Rust extension or in a stubs directory.
"""

from typing import Iterator, Union, Protocol, runtime_checkable

__version__: str

class TeehistorianError(Exception):
    """Exception raised for teehistorian parsing errors"""
    def __init__(self, message: str) -> None: ...

@runtime_checkable
class Chunk(Protocol):
    """Base protocol for all chunk types"""
    def __repr__(self) -> str: ...

class Teehistorian:
    """Main teehistorian parser class"""

    def __init__(self, data: bytes) -> None:
        """Create parser from raw file data"""
        ...

    def register_custom_uuid(self, uuid_string: str) -> None:
        """Register a custom UUID handler"""
        ...

    def header(self) -> bytes:
        """Get the JSON header as bytes"""
        ...

    def __iter__(self) -> Iterator[Chunk]:
        """Iterator support for processing chunks"""
        ...

    def __next__(self) -> Chunk:
        """Get next chunk"""
        ...

# Base chunk classes
class BaseChunk:
    """Base class for all chunk types"""
    def __repr__(self) -> str: ...

# Time-related chunks
class TickSkip(BaseChunk):
    """Represents a tick skip event"""
    dt: int
    def __init__(self, dt: int) -> None: ...
    def __repr__(self) -> str: ...

# Player connection chunks
class Join(BaseChunk):
    """Player join chunk"""
    client_id: int
    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...

class JoinVer6(BaseChunk):
    """Version 6 join chunk"""
    client_id: int
    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...

class Drop(BaseChunk):
    """Player drop chunk"""
    client_id: int
    reason: str
    def __init__(self, client_id: int, reason: str) -> None: ...
    def __repr__(self) -> str: ...

# Player state chunks
class PlayerReady(BaseChunk):
    """Player ready state chunk"""
    client_id: int
    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...

class PlayerNew(BaseChunk):
    """New player spawn chunk"""
    client_id: int
    x: int
    y: int
    def __init__(self, client_id: int, x: int, y: int) -> None: ...
    def __repr__(self) -> str: ...

class PlayerOld(BaseChunk):
    """Player leaving chunk"""
    client_id: int
    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...

class PlayerTeam(BaseChunk):
    """Player team change chunk"""
    client_id: int
    team: int
    def __init__(self, client_id: int, team: int) -> None: ...
    def __repr__(self) -> str: ...

class PlayerName(BaseChunk):
    """Player name change chunk"""
    client_id: int
    name: str
    def __init__(self, client_id: int, name: str) -> None: ...
    def __repr__(self) -> str: ...

class PlayerDiff(BaseChunk):
    """Player position difference chunk"""
    client_id: int
    dx: int
    dy: int
    def __init__(self, client_id: int, dx: int, dy: int) -> None: ...
    def __repr__(self) -> str: ...

# Authentication chunks
class AuthLogin(BaseChunk):
    """Authentication login chunk"""
    client_id: int
    level: int
    name: str
    def __init__(self, client_id: int, level: int, name: str) -> None: ...
    def __repr__(self) -> str: ...

# Version and connection info chunks
class DdnetVersion(BaseChunk):
    """DDNet version information chunk"""
    client_id: int
    connection_id: str
    version: int
    version_str: Union[bytes, list[int]]
    def __init__(
        self,
        client_id: int,
        connection_id: str,
        version: int,
        version_str: Union[bytes, list[int]]
    ) -> None: ...
    def __repr__(self) -> str: ...

# Command and communication chunks
class ConsoleCommand(BaseChunk):
    """Console command chunk"""
    client_id: int
    flags: int
    command: str
    args: str
    def __init__(
        self,
        client_id: int,
        flags: int,
        command: str,
        args: str
    ) -> None: ...
    def __repr__(self) -> str: ...

class NetMessage(BaseChunk):
    """Network message chunk"""
    client_id: int
    message: str
    def __init__(self, client_id: int, message: str) -> None: ...
    def __repr__(self) -> str: ...

# Input chunks
class InputNew(BaseChunk):
    """New player input chunk"""
    client_id: int
    input: str
    def __init__(self, client_id: int, input: str) -> None: ...
    def __repr__(self) -> str: ...

class InputDiff(BaseChunk):
    """Input state difference chunk"""
    client_id: int
    input: list[int]
    def __init__(self, client_id: int, input: list[int]) -> None: ...
    def __repr__(self) -> str: ...

# Team management chunks
class TeamLoadSuccess(BaseChunk):
    """Successful team load chunk"""
    team: int
    save: str
    def __init__(self, team: int, save: str) -> None: ...
    def __repr__(self) -> str: ...

class TeamLoadFailure(BaseChunk):
    """Failed team load chunk"""
    team: int
    def __init__(self, team: int) -> None: ...
    def __repr__(self) -> str: ...

# Anti-bot chunks
class AntiBot(BaseChunk):
    """AntiBot event chunk"""
    data: str
    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...

# Special chunks
class Eos(BaseChunk):
    """End of stream chunk"""
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...

class CustomChunk(BaseChunk):
    """Custom UUID chunk (registered)"""
    uuid: str
    data: bytes
    def __init__(self, uuid: str, data: bytes) -> None: ...
    def __repr__(self) -> str: ...

class Unknown(BaseChunk):
    """Unknown chunk type"""
    uuid: str
    data: bytes
    def __init__(self, uuid: str, data: bytes) -> None: ...
    def __repr__(self) -> str: ...

class Generic(BaseChunk):
    """Generic fallback chunk"""
    data: str
    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...

# Type unions for easier type checking
PlayerChunk = Union[
    Join, JoinVer6, Drop, PlayerReady, PlayerNew, PlayerOld,
    PlayerTeam, PlayerName, PlayerDiff, AuthLogin, DdnetVersion,
    ConsoleCommand, NetMessage, InputNew, InputDiff
]

ServerChunk = Union[
    TickSkip, TeamLoadSuccess, TeamLoadFailure, AntiBot, Eos
]

CustomChunkTypes = Union[CustomChunk, Unknown, Generic]

AnyChunk = Union[PlayerChunk, ServerChunk, CustomChunkTypes]

# Helper functions for type checking
def is_player_chunk(chunk: Chunk) -> bool:
    """Check if chunk is player-related"""
    ...

def is_server_chunk(chunk: Chunk) -> bool:
    """Check if chunk is server-related"""
    ...

def is_custom_chunk(chunk: Chunk) -> bool:
    """Check if chunk is custom/unknown"""
    ...
