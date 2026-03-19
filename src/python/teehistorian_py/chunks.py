"""Validated Python wrapper classes for teehistorian chunks.

These wrappers provide Pydantic-style coercive validation while wrapping
the underlying Rust chunk implementations.
"""

from __future__ import annotations

from typing import Any

from . import _rust
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
    "ValidatedChunk",
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


class ValidatedChunk:
    """Base class for all validated chunk types.

    All field values must be hashable (no dicts, sets, or other mutable
    non-list containers). Lists are automatically converted to tuples
    for hashing.
    """

    _chunk_name: str
    _fields: tuple[str, ...] = ()
    _rust_cls: type

    def chunk_type(self) -> str:
        return self._chunk_name

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": self._chunk_name}
        for f in self._fields:
            d[f] = getattr(self, f)
        return d

    def __repr__(self) -> str:
        args = ", ".join(f"{f}={getattr(self, f)!r}" for f in self._fields)
        return f"{self._chunk_name}({args})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (type(self), self._rust_cls)):
            return False
        return all(
            getattr(self, f) == getattr(other, f, None) for f in self._fields
        )

    def __hash__(self) -> int:
        vals = tuple(
            tuple(v) if isinstance(v := getattr(self, f), list) else v
            for f in self._fields
        )
        return hash((self._chunk_name, *vals))


# Player Lifecycle Chunks

class Join(ValidatedChunk):
    _chunk_name = "Join"
    _fields = ("client_id",)
    _rust_cls = _rust.Join

    def __init__(self, client_id: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self._rust = _rust.Join(client_id=self.client_id)


class JoinVer6(ValidatedChunk):
    _chunk_name = "JoinVer6"
    _fields = ("client_id",)
    _rust_cls = _rust.JoinVer6

    def __init__(self, client_id: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self._rust = _rust.JoinVer6(client_id=self.client_id)


class Drop(ValidatedChunk):
    _chunk_name = "Drop"
    _fields = ("client_id", "reason")
    _rust_cls = _rust.Drop

    def __init__(self, client_id: int, reason: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.reason = validate_str(reason, "reason", max_len=128)
        self._rust = _rust.Drop(client_id=self.client_id, reason=self.reason)


class PlayerReady(ValidatedChunk):
    _chunk_name = "PlayerReady"
    _fields = ("client_id",)
    _rust_cls = _rust.PlayerReady

    def __init__(self, client_id: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self._rust = _rust.PlayerReady(client_id=self.client_id)


# Player State Chunks

class PlayerNew(ValidatedChunk):
    _chunk_name = "PlayerNew"
    _fields = ("client_id", "x", "y")
    _rust_cls = _rust.PlayerNew

    def __init__(self, client_id: int, x: int, y: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.x = validate_int(x, "x")
        self.y = validate_int(y, "y")
        self._rust = _rust.PlayerNew(client_id=self.client_id, x=self.x, y=self.y)


class PlayerOld(ValidatedChunk):
    _chunk_name = "PlayerOld"
    _fields = ("client_id",)
    _rust_cls = _rust.PlayerOld

    def __init__(self, client_id: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self._rust = _rust.PlayerOld(client_id=self.client_id)


class PlayerTeam(ValidatedChunk):
    _chunk_name = "PlayerTeam"
    _fields = ("client_id", "team")
    _rust_cls = _rust.PlayerTeam

    def __init__(self, client_id: int, team: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.team = validate_int(team, "team", TEAM_MIN, TEAM_MAX)
        self._rust = _rust.PlayerTeam(client_id=self.client_id, team=self.team)


class PlayerName(ValidatedChunk):
    _chunk_name = "PlayerName"
    _fields = ("client_id", "name")
    _rust_cls = _rust.PlayerName

    def __init__(self, client_id: int, name: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.name = validate_str(name, "name", max_len=16, allow_empty=False)
        self._rust = _rust.PlayerName(client_id=self.client_id, name=self.name)


class PlayerDiff(ValidatedChunk):
    _chunk_name = "PlayerDiff"
    _fields = ("client_id", "dx", "dy")
    _rust_cls = _rust.PlayerDiff

    def __init__(self, client_id: int, dx: int, dy: int) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.dx = validate_int(dx, "dx")
        self.dy = validate_int(dy, "dy")
        self._rust = _rust.PlayerDiff(client_id=self.client_id, dx=self.dx, dy=self.dy)


# Input Chunks

class InputNew(ValidatedChunk):
    _chunk_name = "InputNew"
    _fields = ("client_id", "input")
    _rust_cls = _rust.InputNew

    def __init__(self, client_id: int, input: list[int]) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.input = validate_list_int(input, "input")
        self._rust = _rust.InputNew(client_id=self.client_id, input=self.input)


class InputDiff(ValidatedChunk):
    _chunk_name = "InputDiff"
    _fields = ("client_id", "input")
    _rust_cls = _rust.InputDiff

    def __init__(self, client_id: int, input: list[int]) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.input = validate_list_int(input, "input")
        self._rust = _rust.InputDiff(client_id=self.client_id, input=self.input)


# Communication Chunks

class NetMessage(ValidatedChunk):
    _chunk_name = "NetMessage"
    _fields = ("client_id", "message")
    _rust_cls = _rust.NetMessage

    def __init__(self, client_id: int, message: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.message = validate_str(message, "message")
        self._rust = _rust.NetMessage(client_id=self.client_id, message=self.message)


class ConsoleCommand(ValidatedChunk):
    _chunk_name = "ConsoleCommand"
    _fields = ("client_id", "flags", "command", "args")
    _rust_cls = _rust.ConsoleCommand

    def __init__(self, client_id: int, flags: int, command: str, args: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.flags = validate_int(flags, "flags", min_val=0)
        self.command = validate_str(command, "command", allow_empty=False)
        self.args = validate_str(args, "args")
        self._rust = _rust.ConsoleCommand(
            client_id=self.client_id, flags=self.flags, command=self.command, args=self.args
        )


# Authentication & Version Chunks

class AuthLogin(ValidatedChunk):
    _chunk_name = "AuthLogin"
    _fields = ("client_id", "level", "auth_name")
    _rust_cls = _rust.AuthLogin

    def __init__(self, client_id: int, level: int, auth_name: str) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.level = validate_int(level, "level", min_val=0)
        self.auth_name = validate_str(auth_name, "auth_name", allow_empty=False)
        self._rust = _rust.AuthLogin(client_id=self.client_id, level=self.level, auth_name=self.auth_name)


class DdnetVersion(ValidatedChunk):
    _chunk_name = "DdnetVersion"
    _fields = ("client_id", "connection_id", "version", "version_str")
    _rust_cls = _rust.DdnetVersion

    def __init__(self, client_id: int, connection_id: str, version: int, version_str: bytes) -> None:
        self.client_id = validate_int(client_id, "client_id", CLIENT_ID_MIN, CLIENT_ID_MAX)
        self.connection_id = validate_uuid(connection_id, "connection_id")
        self.version = validate_int(version, "version", min_val=0)
        self.version_str = validate_bytes(version_str, "version_str")
        self._rust = _rust.DdnetVersion(
            client_id=self.client_id, connection_id=self.connection_id,
            version=self.version, version_str=self.version_str,
        )


# Server Event Chunks

class TickSkip(ValidatedChunk):
    _chunk_name = "TickSkip"
    _fields = ("dt",)
    _rust_cls = _rust.TickSkip

    def __init__(self, dt: int) -> None:
        self.dt = validate_int(dt, "dt", min_val=1)
        self._rust = _rust.TickSkip(dt=self.dt)


class TeamLoadSuccess(ValidatedChunk):
    _chunk_name = "TeamLoadSuccess"
    _fields = ("team", "save_id", "save")
    _rust_cls = _rust.TeamLoadSuccess

    def __init__(self, team: int, save_id: str, save: str) -> None:
        self.team = validate_int(team, "team", TEAM_MIN, TEAM_MAX)
        self.save_id = validate_uuid(save_id, "save_id")
        self.save = validate_str(save, "save")
        self._rust = _rust.TeamLoadSuccess(team=self.team, save_id=self.save_id, save=self.save)


class TeamLoadFailure(ValidatedChunk):
    _chunk_name = "TeamLoadFailure"
    _fields = ("team",)
    _rust_cls = _rust.TeamLoadFailure

    def __init__(self, team: int) -> None:
        self.team = validate_int(team, "team", TEAM_MIN, TEAM_MAX)
        self._rust = _rust.TeamLoadFailure(team=self.team)


class AntiBot(ValidatedChunk):
    _chunk_name = "AntiBot"
    _fields = ("data",)
    _rust_cls = _rust.AntiBot

    def __init__(self, data: str) -> None:
        self.data = validate_str(data, "data")
        self._rust = _rust.AntiBot(data=self.data)


# Special Chunks

class Eos(ValidatedChunk):
    _chunk_name = "Eos"
    _fields = ()
    _rust_cls = _rust.Eos

    def __init__(self) -> None:
        self._rust = _rust.Eos()


class Unknown(ValidatedChunk):
    _chunk_name = "Unknown"
    _fields = ("uuid", "data")
    _rust_cls = _rust.Unknown

    def __init__(self, uuid: str, data: bytes) -> None:
        self.uuid = validate_uuid(uuid, "uuid")
        self.data = validate_bytes(data, "data")
        self._rust = _rust.Unknown(uuid=self.uuid, data=self.data)


class CustomChunk(ValidatedChunk):
    _chunk_name = "CustomChunk"
    _fields = ("uuid", "data", "handler_name")
    _rust_cls = _rust.CustomChunk

    def __init__(self, uuid: str, data: bytes, handler_name: str) -> None:
        self.uuid = validate_uuid(uuid, "uuid")
        self.data = validate_bytes(data, "data")
        self.handler_name = validate_str(handler_name, "handler_name", allow_empty=False)
        self._rust = _rust.CustomChunk(uuid=self.uuid, data=self.data, handler_name=self.handler_name)


class Generic(ValidatedChunk):
    _chunk_name = "Generic"
    _fields = ("data",)
    _rust_cls = _rust.Generic

    def __init__(self, data: str) -> None:
        self.data = validate_str(data, "data")
        self._rust = _rust.Generic(data=self.data)
