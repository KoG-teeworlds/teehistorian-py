"""
Validation utilities for coercive, Pydantic-style validation.

These validators attempt to coerce values to the correct type before
validating constraints, making the API more forgiving of common mistakes.
"""

from __future__ import annotations

from typing import Any


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def validate_int(
    value: Any, name: str, min_val: int | None = None, max_val: int | None = None
) -> int:
    """
    Validate and coerce to integer.

    Args:
        value: Value to validate
        name: Field name for error messages
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        Validated integer value

    Raises:
        ValidationError: If validation fails

    Examples:
        >>> validate_int("5", "client_id", 0, 63)
        5
        >>> validate_int(5.0, "value")
        5
        >>> validate_int("invalid", "value")
        ValidationError: value must be an integer, got 'invalid'
    """
    try:
        result = int(value)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"{name} must be an integer, got {value!r}") from e

    if min_val is not None and result < min_val:
        raise ValidationError(f"{name} must be >= {min_val}, got {result}")

    if max_val is not None and result > max_val:
        raise ValidationError(f"{name} must be <= {max_val}, got {result}")

    return result


def validate_str(
    value: Any,
    name: str,
    min_len: int | None = None,
    max_len: int | None = None,
    allow_empty: bool = True,
) -> str:
    """
    Validate and coerce to string.

    Args:
        value: Value to validate
        name: Field name for error messages
        min_len: Minimum string length
        max_len: Maximum string length
        allow_empty: Whether to allow empty strings

    Returns:
        Validated string value

    Raises:
        ValidationError: If validation fails

    Examples:
        >>> validate_str(123, "name")
        '123'
        >>> validate_str("test", "name", min_len=1, max_len=10)
        'test'
    """
    try:
        result = str(value)
    except Exception as e:
        raise ValidationError(f"{name} must be a string, got {value!r}") from e

    if not allow_empty and not result:
        raise ValidationError(f"{name} cannot be empty")

    if min_len is not None and len(result) < min_len:
        raise ValidationError(f"{name} must be >= {min_len} characters, got {len(result)}")

    if max_len is not None and len(result) > max_len:
        raise ValidationError(f"{name} must be <= {max_len} characters, got {len(result)}")

    return result


def validate_bytes(
    value: Any,
    name: str,
    min_len: int | None = None,
    max_len: int | None = None,
) -> bytes:
    """
    Validate and coerce to bytes.

    Args:
        value: Value to validate (bytes, bytearray, or list of ints)
        name: Field name for error messages
        min_len: Minimum byte length
        max_len: Maximum byte length

    Returns:
        Validated bytes value

    Raises:
        ValidationError: If validation fails

    Examples:
        >>> validate_bytes(b"test", "data")
        b'test'
        >>> validate_bytes([65, 66, 67], "data")
        b'ABC'
    """
    if isinstance(value, bytes):
        result = value
    elif isinstance(value, bytearray):
        result = bytes(value)
    elif isinstance(value, list):
        try:
            result = bytes(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"{name} must be bytes or list of ints 0-255") from e
    else:
        raise ValidationError(f"{name} must be bytes, bytearray, or list of ints, got {type(value)}")

    if min_len is not None and len(result) < min_len:
        raise ValidationError(f"{name} must be >= {min_len} bytes, got {len(result)}")

    if max_len is not None and len(result) > max_len:
        raise ValidationError(f"{name} must be <= {max_len} bytes, got {len(result)}")

    return result


def validate_list_int(value: Any, name: str) -> list[int]:
    """
    Validate and coerce to list of integers.

    Args:
        value: Value to validate
        name: Field name for error messages

    Returns:
        Validated list of integers

    Raises:
        ValidationError: If validation fails

    Examples:
        >>> validate_list_int([1, 2, 3], "input")
        [1, 2, 3]
        >>> validate_list_int(["1", "2"], "input")
        [1, 2]
    """
    if not isinstance(value, (list, tuple)):
        raise ValidationError(f"{name} must be a list, got {type(value)}")

    try:
        return [int(item) for item in value]
    except (ValueError, TypeError) as e:
        raise ValidationError(f"{name} must contain only integers") from e


def validate_uuid(value: Any, name: str) -> str:
    """
    Validate UUID string format.

    Args:
        value: Value to validate
        name: Field name for error messages

    Returns:
        Validated UUID string

    Raises:
        ValidationError: If validation fails

    Examples:
        >>> validate_uuid("12345678-1234-5678-1234-567812345678", "uuid")
        '12345678-1234-5678-1234-567812345678'
    """
    uuid_str = validate_str(value, name)

    parts = uuid_str.split("-")
    if len(parts) != 5:
        raise ValidationError(f"{name} must be in UUID format (8-4-4-4-12), got {uuid_str!r}")

    expected_lengths = [8, 4, 4, 4, 12]
    for part, expected_len in zip(parts, expected_lengths):
        if len(part) != expected_len:
            raise ValidationError(
                f"{name} must be in UUID format (8-4-4-4-12), got {uuid_str!r}"
            )
        if not all(c in "0123456789abcdefABCDEF" for c in part):
            raise ValidationError(f"{name} must contain only hex digits, got {uuid_str!r}")

    return uuid_str.lower()


# Teeworlds-specific constraints
CLIENT_ID_MIN = 0
CLIENT_ID_MAX = 63
TEAM_MIN = 0
TEAM_MAX = 63
