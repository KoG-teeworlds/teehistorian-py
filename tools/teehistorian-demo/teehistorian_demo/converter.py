"""Convert teehistorian files to demo files using tee-hee."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional, Union

from teehistorian_header import parse_header
from teehistorian_downloader import download as download_teehistorian
from teehistorian_map import download_map
from teehistorian_shared import (
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    S3Error,
)


class ConversionError(Exception):
    """Raised when tee-hee conversion fails."""

    pass


class TeeHeeNotFoundError(Exception):
    """Raised when tee-hee is not installed."""

    pass


def _get_ddnet_data_dir() -> Optional[Path]:
    """Get the DDNet data directory based on platform."""
    system = platform.system()

    if system == "Darwin":  # macOS
        path = Path.home() / "Library" / "Application Support" / "DDNet"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            path = Path(appdata) / "DDNet"
        else:
            return None
    else:  # Linux and others
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            path = Path(xdg_data) / "ddnet"
        else:
            path = Path.home() / ".local" / "share" / "ddnet"

    return path if path.exists() else None


def _find_map_in_ddnet(map_name: str) -> Optional[Path]:
    """Check if a map exists in DDNet's maps folders."""
    ddnet_dir = _get_ddnet_data_dir()
    if not ddnet_dir:
        return None

    # Check downloadedmaps first (more common)
    downloadedmaps = ddnet_dir / "downloadedmaps" / f"{map_name}.map"
    if downloadedmaps.exists():
        return downloadedmaps

    # Check maps folder
    maps = ddnet_dir / "maps" / f"{map_name}.map"
    if maps.exists():
        return maps

    return None


def _install_map_to_ddnet(
    map_data: bytes,
    map_name: str,
    prompt_func: Optional[Callable[[str], bool]] = None,
    verbose: bool = False,
) -> bool:
    """Install a map to DDNet's downloadedmaps folder.

    Args:
        map_data: Map file contents.
        map_name: Name of the map (without .map extension).
        prompt_func: Function to prompt user for confirmation.
                     Takes a message, returns True/False.
                     If None, installs without prompting.
        verbose: Print verbose output.

    Returns:
        True if map was installed, False otherwise.
    """
    ddnet_dir = _get_ddnet_data_dir()
    if not ddnet_dir:
        if verbose:
            print("Could not find DDNet data directory")
        return False

    downloadedmaps = ddnet_dir / "downloadedmaps"
    downloadedmaps.mkdir(parents=True, exist_ok=True)

    map_path = downloadedmaps / f"{map_name}.map"

    if prompt_func:
        msg = f"Map '{map_name}' not found in DDNet. Install to {map_path}?"
        if not prompt_func(msg):
            return False

    map_path.write_bytes(map_data)
    if verbose:
        print(f"Installed map to: {map_path}")
    return True


def _check_tee_hee() -> str:
    """Check if tee-hee is installed and return its path."""
    tee_hee = shutil.which("tee-hee")
    if not tee_hee:
        raise TeeHeeNotFoundError(
            "tee-hee not found in PATH. Install it from https://github.com/heinrich5991/teehistorian"
        )
    return tee_hee


def convert_to_demo(
    source: Union[str, Path],
    *,
    output: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    map_file: Optional[Union[str, Path]] = None,
    verbose: bool = False,
    prompt_func: Optional[Callable[[str], bool]] = None,
) -> Path:
    """Convert a teehistorian file to a demo file.

    Args:
        source: UUID to download, or path to local .teehistorian file.
        output: Output .demo file path. If not specified, uses {game_uuid}.demo.
        output_dir: Directory for output file. Defaults to current directory.
        map_file: Path to local .map file. If not specified, downloads from S3.
        verbose: Print verbose output.
        prompt_func: Function to prompt user for map installation.
                     Takes a message, returns True/False.

    Returns:
        Path to the generated .demo file.

    Raises:
        TeeHeeNotFoundError: If tee-hee is not installed.
        ConversionError: If tee-hee conversion fails.
        ConfigurationError: If S3 configuration is missing.
        NotFoundError: If teehistorian or map file not found.
    """
    tee_hee = _check_tee_hee()

    source_path = Path(source) if not _is_uuid(str(source)) else None
    is_uuid = source_path is None

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Step 1: Get teehistorian file
        if is_uuid:
            if verbose:
                print(f"Downloading teehistorian: {source}")
            th_data = download_teehistorian(str(source), save=False)
            th_file = temp_path / f"{source}.teehistorian"
            th_file.write_bytes(th_data)
        else:
            th_file = source_path
            if not th_file.exists():
                raise NotFoundError(f"Teehistorian file not found: {th_file}")

        # Step 2: Parse header to get map info and game_uuid
        header = parse_header(th_file)
        game_uuid = header.get("game_uuid", "unknown")
        map_sha256 = header.get("map_sha256")

        if verbose:
            print(f"Game UUID: {game_uuid}")
            print(f"Map: {header.get('map_name')} (sha256: {map_sha256})")

        # Step 3: Get map file
        map_name = header.get("map_name", "unknown")
        map_data: Optional[bytes] = None

        if map_file:
            map_path = Path(map_file)
            if not map_path.exists():
                raise NotFoundError(f"Map file not found: {map_path}")
            map_data = map_path.read_bytes()
            # Copy to temp with correct name for tee-hee
            temp_map = temp_path / f"{map_sha256}.map"
            shutil.copy(map_path, temp_map)
            map_path = temp_map
        else:
            if verbose:
                print(f"Downloading map...")
            try:
                map_data = download_map(header, save=False)
                # tee-hee expects map named as {sha256}.map
                map_path = temp_path / f"{map_sha256}.map"
                map_path.write_bytes(map_data)
            except (ConfigurationError, NotFoundError, S3Error) as e:
                raise NotFoundError(f"Could not get map file: {e}") from e

        # Step 3b: Check if map is installed in DDNet, offer to install
        if map_data and not _find_map_in_ddnet(map_name):
            _install_map_to_ddnet(
                map_data,
                map_name,
                prompt_func=prompt_func,
                verbose=verbose,
            )

        # Step 4: Determine output path
        if output:
            demo_path = Path(output)
        else:
            out_dir = Path(output_dir) if output_dir else Path.cwd()
            demo_path = out_dir / f"{game_uuid}.demo"

        demo_path.parent.mkdir(parents=True, exist_ok=True)

        # Step 5: Run tee-hee
        cmd = [
            tee_hee,
            "replay",
            str(th_file),
            "--demo", str(demo_path),
            "--map", str(map_path),
        ]

        if verbose:
            print(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise ConversionError(
                    f"tee-hee failed with code {result.returncode}:\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )
        except FileNotFoundError:
            raise TeeHeeNotFoundError("tee-hee not found")

        if verbose:
            print(f"Created: {demo_path}")

        return demo_path


def _is_uuid(s: str) -> bool:
    """Check if string looks like a UUID."""
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(s))
