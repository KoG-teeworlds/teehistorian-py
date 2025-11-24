"""
Validated Python wrapper classes for teehistorian chunks.

These wrappers provide Pydantic-style coercive validation while wrapping
the underlying Rust chunk implementations.
"""

from __future__ import annotations

from typing import Any

from . import _rust
from .protocols import (
    AntiBotProtocol,
    AuthLoginProtocol,
    ConsoleCommandProtocol,
    CustomChunkProtocol,
    DdnetVersionProtocol,
    DropProtocol,
    EosProtocol,
    GenericProtocol,
    InputDiffProtocol,
    InputNewProtocol,
    JoinProtocol,
    JoinVer6Protocol,
    NetMessageProtocol,
    PlayerDiffProtocol,
    PlayerNameProtocol,
    PlayerNewProtocol,
    PlayerOldProtocol,
    PlayerReadyProtocol,
    PlayerTeamProtocol,
    TeamLoadFailureProtocol,
    TeamLoadSuccessProtocol,
    TickSkipProtocol,
    UnknownProtocol,
)
from .validators import (
    CLIENT_ID_MAX,
    CLIENT_ID_MIN,
    TEAM_MAX,
    TEAM_MIN,
    ValidationError,
    validate_bytes,
    validate_int,
    validate_list_int,
    validate_str,
    validate_uuid,
)

__all__ = [
    "Join",
    "JoinVer6",
    "Drop",
    "PlayerReady",
    "PlayerNew",
    "PlayerOld",
    "PlayerTeam",
    "PlayerName",
    "PlayerDiff",
    "InputNew",
    "InputDiff",
    "NetMessage",
    "ConsoleCommand",
    "AuthLogin",
    "DdnetVersion",
    "TickSkip",
    "TeamLoadSuccess",
    "TeamLoadFailure",
    "AntiBot",
    "Eos",
    "Unknown",
    "CustomChunk",
    "Generic",
]


# Player Lifecycle Chunks
# ============================================================================


class Join:
    """Player joins the server (validated)."""

    def __init__(self, client_id: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self._rust = _rust.Join(client_id=self.client_id)

    def chunk_type(self) -> str:
        return "Join"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "Join", "client_id": self.client_id}

    def __repr__(self) -> str:
        return f"Join(client_id={self.client_id})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (Join, _rust.Join)) and self.client_id == getattr(other, "client_id", None)

    def __hash__(self) -> int:
        return hash(("Join", self.client_id))


class JoinVer6:
    """Player joins the server (version 6 protocol, validated)."""

    def __init__(self, client_id: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self._rust = _rust.JoinVer6(client_id=self.client_id)

    def chunk_type(self) -> str:
        return "JoinVer6"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "JoinVer6", "client_id": self.client_id}

    def __repr__(self) -> str:
        return f"JoinVer6(client_id={self.client_id})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (JoinVer6, _rust.JoinVer6)) and self.client_id == getattr(other, "client_id", None)

    def __hash__(self) -> int:
        return hash(("JoinVer6", self.client_id))


class Drop:
    """Player disconnects from server (validated)."""

    def __init__(self, client_id: int, reason: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.reason = validate_str(reason, "reason", max_len=128)
        self._rust = _rust.Drop(client_id=self.client_id, reason=self.reason)

    def chunk_type(self) -> str:
        return "Drop"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "Drop", "client_id": self.client_id, "reason": self.reason}

    def __repr__(self) -> str:
        return f"Drop(client_id={self.client_id}, reason={self.reason!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (Drop, _rust.Drop)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.reason == getattr(other, "reason", None)
        )

    def __hash__(self) -> int:
        return hash(("Drop", self.client_id, self.reason))


class PlayerReady:
    """Player is ready to receive game data (validated)."""

    def __init__(self, client_id: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self._rust = _rust.PlayerReady(client_id=self.client_id)

    def chunk_type(self) -> str:
        return "PlayerReady"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "PlayerReady", "client_id": self.client_id}

    def __repr__(self) -> str:
        return f"PlayerReady(client_id={self.client_id})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (PlayerReady, _rust.PlayerReady)) and self.client_id == getattr(other, "client_id", None)

    def __hash__(self) -> int:
        return hash(("PlayerReady", self.client_id))


# Player State Chunks
# ============================================================================


class PlayerNew:
    """New player position data (validated)."""

    def __init__(self, client_id: int, x: int, y: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.x = validate_int(x, "x")
        self.y = validate_int(y, "y")
        self._rust = _rust.PlayerNew(client_id=self.client_id, x=self.x, y=self.y)

    def chunk_type(self) -> str:
        return "PlayerNew"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "PlayerNew", "client_id": self.client_id, "x": self.x, "y": self.y}

    def __repr__(self) -> str:
        return f"PlayerNew(client_id={self.client_id}, x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (PlayerNew, _rust.PlayerNew)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.x == getattr(other, "x", None)
            and self.y == getattr(other, "y", None)
        )

    def __hash__(self) -> int:
        return hash(("PlayerNew", self.client_id, self.x, self.y))


class PlayerOld:
    """Player removed from game (validated)."""

    def __init__(self, client_id: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self._rust = _rust.PlayerOld(client_id=self.client_id)

    def chunk_type(self) -> str:
        return "PlayerOld"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "PlayerOld", "client_id": self.client_id}

    def __repr__(self) -> str:
        return f"PlayerOld(client_id={self.client_id})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (PlayerOld, _rust.PlayerOld)) and self.client_id == getattr(other, "client_id", None)

    def __hash__(self) -> int:
        return hash(("PlayerOld", self.client_id))


class PlayerTeam:
    """Player team assignment (validated)."""

    def __init__(self, client_id: int, team: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.team = validate_int(team, "team", TEAM_MIN, TEAM_MAX)
        self._rust = _rust.PlayerTeam(client_id=self.client_id, team=self.team)

    def chunk_type(self) -> str:
        return "PlayerTeam"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "PlayerTeam", "client_id": self.client_id, "team": self.team}

    def __repr__(self) -> str:
        return f"PlayerTeam(client_id={self.client_id}, team={self.team})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (PlayerTeam, _rust.PlayerTeam)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.team == getattr(other, "team", None)
        )

    def __hash__(self) -> int:
        return hash(("PlayerTeam", self.client_id, self.team))


class PlayerName:
    """Player name information (validated)."""

    def __init__(self, client_id: int, name: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.name = validate_str(name, "name", max_len=16, allow_empty=False)
        self._rust = _rust.PlayerName(client_id=self.client_id, name=self.name)

    def chunk_type(self) -> str:
        return "PlayerName"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "PlayerName", "client_id": self.client_id, "name": self.name}

    def __repr__(self) -> str:
        return f"PlayerName(client_id={self.client_id}, name={self.name!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (PlayerName, _rust.PlayerName)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.name == getattr(other, "name", None)
        )

    def __hash__(self) -> int:
        return hash(("PlayerName", self.client_id, self.name))


class PlayerDiff:
    """Player position delta (validated)."""

    def __init__(self, client_id: int, dx: int, dy: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.dx = validate_int(dx, "dx")
        self.dy = validate_int(dy, "dy")
        self._rust = _rust.PlayerDiff(client_id=self.client_id, dx=self.dx, dy=self.dy)

    def chunk_type(self) -> str:
        return "PlayerDiff"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "PlayerDiff", "client_id": self.client_id, "dx": self.dx, "dy": self.dy}

    def __repr__(self) -> str:
        return f"PlayerDiff(client_id={self.client_id}, dx={self.dx}, dy={self.dy})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (PlayerDiff, _rust.PlayerDiff)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.dx == getattr(other, "dx", None)
            and self.dy == getattr(other, "dy", None)
        )

    def __hash__(self) -> int:
        return hash(("PlayerDiff", self.client_id, self.dx, self.dy))


# Input Chunks
# ============================================================================


class InputNew:
    """New player input state (validated)."""

    def __init__(self, client_id: int, input: list[int]) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.input = validate_list_int(input, "input")
        self._rust = _rust.InputNew(client_id=self.client_id, input=self.input)

    def chunk_type(self) -> str:
        return "InputNew"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "InputNew", "client_id": self.client_id, "input": self.input}

    def __repr__(self) -> str:
        return f"InputNew(client_id={self.client_id}, input={self.input})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (InputNew, _rust.InputNew)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.input == getattr(other, "input", None)
        )

    def __hash__(self) -> int:
        return hash(("InputNew", self.client_id, tuple(self.input)))


class InputDiff:
    """Player input delta (validated)."""

    def __init__(self, client_id: int, input: list[int]) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.input = validate_list_int(input, "input")
        self._rust = _rust.InputDiff(client_id=self.client_id, input=self.input)

    def chunk_type(self) -> str:
        return "InputDiff"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "InputDiff", "client_id": self.client_id, "input": self.input}

    def __repr__(self) -> str:
        return f"InputDiff(client_id={self.client_id}, input={self.input})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (InputDiff, _rust.InputDiff)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.input == getattr(other, "input", None)
        )

    def __hash__(self) -> int:
        return hash(("InputDiff", self.client_id, tuple(self.input)))


# Communication Chunks
# ============================================================================


class NetMessage:
    """Network message sent to/from player (validated)."""

    def __init__(self, client_id: int, message: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.message = validate_str(message, "message")
        self._rust = _rust.NetMessage(client_id=self.client_id, message=self.message)

    def chunk_type(self) -> str:
        return "NetMessage"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "NetMessage", "client_id": self.client_id, "message": self.message}

    def __repr__(self) -> str:
        return f"NetMessage(client_id={self.client_id}, message={self.message!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (NetMessage, _rust.NetMessage)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.message == getattr(other, "message", None)
        )

    def __hash__(self) -> int:
        return hash(("NetMessage", self.client_id, self.message))


class ConsoleCommand:
    """Console command executed (validated)."""

    def __init__(self, client_id: int, flags: int, command: str, args: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.flags = validate_int(flags, "flags", min_val=0)
        self.command = validate_str(command, "command", allow_empty=False)
        self.args = validate_str(args, "args")
        self._rust = _rust.ConsoleCommand(
            client_id=self.client_id, flags=self.flags, command=self.command, args=self.args
        )

    def chunk_type(self) -> str:
        return "ConsoleCommand"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ConsoleCommand",
            "client_id": self.client_id,
            "flags": self.flags,
            "command": self.command,
            "args": self.args,
        }

    def __repr__(self) -> str:
        return f"ConsoleCommand(client_id={self.client_id}, flags={self.flags}, command={self.command!r}, args={self.args!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (ConsoleCommand, _rust.ConsoleCommand)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.flags == getattr(other, "flags", None)
            and self.command == getattr(other, "command", None)
            and self.args == getattr(other, "args", None)
        )

    def __hash__(self) -> int:
        return hash(("ConsoleCommand", self.client_id, self.flags, self.command, self.args))


# Authentication & Version Chunks
# ============================================================================


class AuthLogin:
    """Player authentication information (validated)."""

    def __init__(self, client_id: int, level: int, auth_name: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.level = validate_int(level, "level", min_val=0)
        self.auth_name = validate_str(auth_name, "auth_name", allow_empty=False)
        self._rust = _rust.AuthLogin(client_id=self.client_id, level=self.level, auth_name=self.auth_name)

    def chunk_type(self) -> str:
        return "AuthLogin"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "AuthLogin",
            "client_id": self.client_id,
            "level": self.level,
            "auth_name": self.auth_name,
        }

    def __repr__(self) -> str:
        return f"AuthLogin(client_id={self.client_id}, level={self.level}, auth_name={self.auth_name!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (AuthLogin, _rust.AuthLogin)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.level == getattr(other, "level", None)
            and self.auth_name == getattr(other, "auth_name", None)
        )

    def __hash__(self) -> int:
        return hash(("AuthLogin", self.client_id, self.level, self.auth_name))


class DdnetVersion:
    """DDNet client version information (validated)."""

    def __init__(self, client_id: int, connection_id: str, version: int, version_str: bytes) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.connection_id = validate_uuid(connection_id, "connection_id")
        self.version = validate_int(version, "version", min_val=0)
        self.version_str = validate_bytes(version_str, "version_str")
        self._rust = _rust.DdnetVersion(
            client_id=self.client_id,
            connection_id=self.connection_id,
            version=self.version,
            version_str=self.version_str,
        )

    def chunk_type(self) -> str:
        return "DdnetVersion"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "DdnetVersion",
            "client_id": self.client_id,
            "connection_id": self.connection_id,
            "version": self.version,
            "version_str": self.version_str,
        }

    def __repr__(self) -> str:
        return f"DdnetVersion(client_id={self.client_id}, connection_id={self.connection_id!r}, version={self.version}, version_str={self.version_str!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (DdnetVersion, _rust.DdnetVersion)):
            return False
        return (
            self.client_id == getattr(other, "client_id", None)
            and self.connection_id == getattr(other, "connection_id", None)
            and self.version == getattr(other, "version", None)
            and self.version_str == getattr(other, "version_str", None)
        )

    def __hash__(self) -> int:
        return hash(("DdnetVersion", self.client_id, self.connection_id, self.version, self.version_str))


# Server Event Chunks
# ============================================================================


class TickSkip:
    """Server skipped ticks (validated)."""

    def __init__(self, dt: int) -> None:
        self.dt = validate_int(dt, "dt", min_val=1)
        self._rust = _rust.TickSkip(dt=self.dt)

    def chunk_type(self) -> str:
        return "TickSkip"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "TickSkip", "dt": self.dt}

    def __repr__(self) -> str:
        return f"TickSkip(dt={self.dt})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (TickSkip, _rust.TickSkip)) and self.dt == getattr(other, "dt", None)

    def __hash__(self) -> int:
        return hash(("TickSkip", self.dt))


class TeamLoadSuccess:
    """Team save loaded successfully (validated)."""

    def __init__(self, team: int, save_id: str, save: str) -> None:
        self.team = validate_int(team, "team", TEAM_MIN, TEAM_MAX)
        self.save_id = validate_uuid(save_id, "save_id")
        self.save = validate_str(save, "save")
        self._rust = _rust.TeamLoadSuccess(team=self.team, save_id=self.save_id, save=self.save)

    def chunk_type(self) -> str:
        return "TeamLoadSuccess"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "TeamLoadSuccess", "team": self.team, "save_id": self.save_id, "save": self.save}

    def __repr__(self) -> str:
        return f"TeamLoadSuccess(team={self.team}, save_id={self.save_id!r}, save={self.save!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (TeamLoadSuccess, _rust.TeamLoadSuccess)):
            return False
        return (
            self.team == getattr(other, "team", None)
            and self.save_id == getattr(other, "save_id", None)
            and self.save == getattr(other, "save", None)
        )

    def __hash__(self) -> int:
        return hash(("TeamLoadSuccess", self.team, self.save_id, self.save))


class TeamLoadFailure:
    """Team save load failed (validated)."""

    def __init__(self, team: int) -> None:
        self.team = validate_int(team, "team", TEAM_MIN, TEAM_MAX)
        self._rust = _rust.TeamLoadFailure(team=self.team)

    def chunk_type(self) -> str:
        return "TeamLoadFailure"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "TeamLoadFailure", "team": self.team}

    def __repr__(self) -> str:
        return f"TeamLoadFailure(team={self.team})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (TeamLoadFailure, _rust.TeamLoadFailure)) and self.team == getattr(other, "team", None)

    def __hash__(self) -> int:
        return hash(("TeamLoadFailure", self.team))


class AntiBot:
    """Antibot data (validated)."""

    def __init__(self, data: str) -> None:
        self.data = validate_str(data, "data")
        self._rust = _rust.AntiBot(data=self.data)

    def chunk_type(self) -> str:
        return "AntiBot"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "AntiBot", "data": self.data}

    def __repr__(self) -> str:
        return f"AntiBot(data={self.data!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (AntiBot, _rust.AntiBot)) and self.data == getattr(other, "data", None)

    def __hash__(self) -> int:
        return hash(("AntiBot", self.data))


# Special Chunks
# ============================================================================


class Eos:
    """End of stream marker (validated)."""

    def __init__(self) -> None:
        self._rust = _rust.Eos()

    def chunk_type(self) -> str:
        return "Eos"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "Eos"}

    def __repr__(self) -> str:
        return "Eos()"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (Eos, _rust.Eos))

    def __hash__(self) -> int:
        return hash("Eos")


class Unknown:
    """Unknown chunk type with UUID (validated)."""

    def __init__(self, uuid: str, data: bytes) -> None:
        self.uuid = validate_uuid(uuid, "uuid")
        self.data = validate_bytes(data, "data")
        self._rust = _rust.Unknown(uuid=self.uuid, data=self.data)

    def chunk_type(self) -> str:
        return "Unknown"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "Unknown", "uuid": self.uuid, "data": self.data}

    def __repr__(self) -> str:
        return f"Unknown(uuid={self.uuid!r}, data={self.data!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (Unknown, _rust.Unknown)):
            return False
        return self.uuid == getattr(other, "uuid", None) and self.data == getattr(other, "data", None)

    def __hash__(self) -> int:
        return hash(("Unknown", self.uuid, self.data))


class CustomChunk:
    """Custom chunk with registered UUID handler (validated)."""

    def __init__(self, uuid: str, data: bytes, handler_name: str) -> None:
        self.uuid = validate_uuid(uuid, "uuid")
        self.data = validate_bytes(data, "data")
        self.handler_name = validate_str(handler_name, "handler_name", allow_empty=False)
        self._rust = _rust.CustomChunk(uuid=self.uuid, data=self.data, handler_name=self.handler_name)

    def chunk_type(self) -> str:
        return "CustomChunk"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "CustomChunk",
            "uuid": self.uuid,
            "data": self.data,
            "handler_name": self.handler_name,
        }

    def __repr__(self) -> str:
        return f"CustomChunk(uuid={self.uuid!r}, data={self.data!r}, handler_name={self.handler_name!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (CustomChunk, _rust.CustomChunk)):
            return False
        return (
            self.uuid == getattr(other, "uuid", None)
            and self.data == getattr(other, "data", None)
            and self.handler_name == getattr(other, "handler_name", None)
        )

    def __hash__(self) -> int:
        return hash(("CustomChunk", self.uuid, self.data, self.handler_name))


class Generic:
    """Generic fallback for unhandled chunks (validated)."""

    def __init__(self, data: str) -> None:
        self.data = validate_str(data, "data")
        self._rust = _rust.Generic(data=self.data)

    def chunk_type(self) -> str:
        return "Generic"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "Generic", "data": self.data}

    def __repr__(self) -> str:
        return f"Generic(data={self.data!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, (Generic, _rust.Generic)) and self.data == getattr(other, "data", None)

    def __hash__(self) -> int:
        return hash(("Generic", self.data))
