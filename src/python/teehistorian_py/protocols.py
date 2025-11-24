"""
Protocol definitions for teehistorian chunk types.

These protocols enable static type checking with mypy while allowing
both Rust and Python implementations of chunks.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol


class ChunkProtocol(Protocol):
    """Base protocol that all chunks must implement."""

    def chunk_type(self) -> str:
        """Get the type identifier for this chunk."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert chunk to dictionary representation."""
        ...

    def __repr__(self) -> str:
        """Get string representation of the chunk."""
        ...


# Player Lifecycle Chunks
# ============================================================================


class JoinProtocol(ChunkProtocol, Protocol):
    """Player joins the server."""

    client_id: int

    def chunk_type(self) -> Literal["Join"]:
        ...


class JoinVer6Protocol(ChunkProtocol, Protocol):
    """Player joins the server (version 6 protocol)."""

    client_id: int

    def chunk_type(self) -> Literal["JoinVer6"]:
        ...


class DropProtocol(ChunkProtocol, Protocol):
    """Player disconnects from server."""

    client_id: int
    reason: str

    def chunk_type(self) -> Literal["Drop"]:
        ...


class PlayerReadyProtocol(ChunkProtocol, Protocol):
    """Player is ready to receive game data."""

    client_id: int

    def chunk_type(self) -> Literal["PlayerReady"]:
        ...


# Player State Chunks
# ============================================================================


class PlayerNewProtocol(ChunkProtocol, Protocol):
    """New player position data."""

    client_id: int
    x: int
    y: int

    def chunk_type(self) -> Literal["PlayerNew"]:
        ...


class PlayerOldProtocol(ChunkProtocol, Protocol):
    """Player removed from game."""

    client_id: int

    def chunk_type(self) -> Literal["PlayerOld"]:
        ...


class PlayerTeamProtocol(ChunkProtocol, Protocol):
    """Player team assignment."""

    client_id: int
    team: int

    def chunk_type(self) -> Literal["PlayerTeam"]:
        ...


class PlayerNameProtocol(ChunkProtocol, Protocol):
    """Player name information."""

    client_id: int
    name: str

    def chunk_type(self) -> Literal["PlayerName"]:
        ...


class PlayerDiffProtocol(ChunkProtocol, Protocol):
    """Player position delta."""

    client_id: int
    dx: int
    dy: int

    def chunk_type(self) -> Literal["PlayerDiff"]:
        ...


# Input Chunks
# ============================================================================


class InputNewProtocol(ChunkProtocol, Protocol):
    """New player input state."""

    client_id: int
    input: list[int]

    def chunk_type(self) -> Literal["InputNew"]:
        ...


class InputDiffProtocol(ChunkProtocol, Protocol):
    """Player input delta."""

    client_id: int
    input: list[int]

    def chunk_type(self) -> Literal["InputDiff"]:
        ...


# Communication Chunks
# ============================================================================


class NetMessageProtocol(ChunkProtocol, Protocol):
    """Network message sent to/from player."""

    client_id: int
    message: str

    def chunk_type(self) -> Literal["NetMessage"]:
        ...


class ConsoleCommandProtocol(ChunkProtocol, Protocol):
    """Console command executed."""

    client_id: int
    flags: int
    command: str
    args: str

    def chunk_type(self) -> Literal["ConsoleCommand"]:
        ...


# Authentication & Version Chunks
# ============================================================================


class AuthLoginProtocol(ChunkProtocol, Protocol):
    """Player authentication information."""

    client_id: int
    level: int
    auth_name: str

    def chunk_type(self) -> Literal["AuthLogin"]:
        ...


class DdnetVersionProtocol(ChunkProtocol, Protocol):
    """DDNet client version information."""

    client_id: int
    connection_id: str
    version: int
    version_str: bytes

    def chunk_type(self) -> Literal["DdnetVersion"]:
        ...


# Server Event Chunks
# ============================================================================


class TickSkipProtocol(ChunkProtocol, Protocol):
    """Server skipped ticks."""

    dt: int

    def chunk_type(self) -> Literal["TickSkip"]:
        ...


class TeamLoadSuccessProtocol(ChunkProtocol, Protocol):
    """Team save loaded successfully."""

    team: int
    save_id: str
    save: str

    def chunk_type(self) -> Literal["TeamLoadSuccess"]:
        ...


class TeamLoadFailureProtocol(ChunkProtocol, Protocol):
    """Team save load failed."""

    team: int

    def chunk_type(self) -> Literal["TeamLoadFailure"]:
        ...


class AntiBotProtocol(ChunkProtocol, Protocol):
    """Antibot data."""

    data: str

    def chunk_type(self) -> Literal["AntiBot"]:
        ...


# Special Chunks
# ============================================================================


class EosProtocol(ChunkProtocol, Protocol):
    """End of stream marker."""

    def chunk_type(self) -> Literal["Eos"]:
        ...


class UnknownProtocol(ChunkProtocol, Protocol):
    """Unknown chunk type with UUID."""

    uuid: str
    data: bytes

    def chunk_type(self) -> Literal["Unknown"]:
        ...


class CustomChunkProtocol(ChunkProtocol, Protocol):
    """Custom chunk with registered UUID handler."""

    uuid: str
    data: bytes
    handler_name: str

    def chunk_type(self) -> Literal["CustomChunk"]:
        ...


class GenericProtocol(ChunkProtocol, Protocol):
    """Generic fallback for unhandled chunks."""

    data: str

    def chunk_type(self) -> Literal["Generic"]:
        ...


# Union Type
# ============================================================================

Chunk = (
    JoinProtocol
    | JoinVer6Protocol
    | DropProtocol
    | PlayerReadyProtocol
    | PlayerNewProtocol
    | PlayerOldProtocol
    | PlayerTeamProtocol
    | PlayerNameProtocol
    | PlayerDiffProtocol
    | InputNewProtocol
    | InputDiffProtocol
    | NetMessageProtocol
    | ConsoleCommandProtocol
    | AuthLoginProtocol
    | DdnetVersionProtocol
    | TickSkipProtocol
    | TeamLoadSuccessProtocol
    | TeamLoadFailureProtocol
    | AntiBotProtocol
    | EosProtocol
    | UnknownProtocol
    | CustomChunkProtocol
    | GenericProtocol
)
