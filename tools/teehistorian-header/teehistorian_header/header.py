"""Teehistorian header parser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

import teehistorian_py as th


def parse_header(
    source: Union[str, Path, bytes],
) -> dict[str, Any]:
    """Parse the header from a teehistorian file.

    Args:
        source: Path to teehistorian file, or raw bytes.

    Returns:
        Dictionary containing header fields.

    Raises:
        ValueError: If the file cannot be parsed.
    """
    if isinstance(source, (str, Path)):
        data = Path(source).read_bytes()
    else:
        data = source

    parser = th.Teehistorian(data)
    header_bytes = parser.header()

    try:
        return json.loads(header_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to parse header as JSON: {e}") from e


def format_header(
    header: dict[str, Any],
    format: str = "json",
) -> str:
    """Format header for display.

    Args:
        header: Header dictionary from parse_header().
        format: Output format - 'json' (pretty), 'raw' (compact), or 'table'.

    Returns:
        Formatted string representation of the header.
    """
    if format == "raw":
        return json.dumps(header, separators=(",", ":"))
    elif format == "table":
        lines = []
        max_key_len = max(len(str(k)) for k in header.keys()) if header else 0
        for key, value in header.items():
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            lines.append(f"{key:<{max_key_len}}  {value_str}")
        return "\n".join(lines)
    else:  # json (pretty)
        return json.dumps(header, indent=2)


def get_header(
    source: Union[str, Path, bytes],
    format: str = "json",
) -> str:
    """Parse and format a teehistorian header in one call.

    Args:
        source: Path to teehistorian file, or raw bytes.
        format: Output format - 'json' (pretty), 'raw' (compact), or 'table'.

    Returns:
        Formatted string representation of the header.
    """
    header = parse_header(source)
    return format_header(header, format)
