"""Configuration loading for teehistorian tools."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

# Use tomllib (Python 3.11+) or tomli as fallback
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

CONFIG_FILENAME = ".teehistorian.toml"

_cached_config: Optional[dict[str, Any]] = None


def _load_config_file() -> dict[str, Any]:
    """Load configuration from .teehistorian.toml file.

    Searches in the following order:
    1. Current working directory
    2. User's home directory

    Returns:
        Dictionary with full configuration, empty if no config file found.
    """
    global _cached_config
    if _cached_config is not None:
        return _cached_config

    search_paths = [
        Path.cwd() / CONFIG_FILENAME,
        Path.home() / CONFIG_FILENAME,
    ]

    for config_path in search_paths:
        if config_path.is_file():
            with open(config_path, "rb") as f:
                _cached_config = tomllib.load(f)
                return _cached_config

    _cached_config = {}
    return _cached_config


def clear_config_cache() -> None:
    """Clear the cached configuration (useful for testing)."""
    global _cached_config
    _cached_config = None


def get_s3_config(
    profile: str,
    endpoint: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    bucket: Optional[str] = None,
) -> dict[str, Any]:
    """Get S3 configuration for a specific profile.

    Args:
        profile: Config profile name ('teehistorian' or 'maps')
        endpoint: Override endpoint URL
        access_key: Override access key
        secret_key: Override secret key
        bucket: Override bucket name

    Returns:
        Dictionary with endpoint, access_key, secret_key, bucket, use_ssl

    Raises:
        ValueError: If required configuration is missing.
    """
    # Load config file
    file_config = _load_config_file()
    profile_config = file_config.get(profile, {}).get("s3", {})

    # Environment variable prefix based on profile
    env_prefix = profile.upper()

    # Priority: parameter > env var > config file > default
    result_endpoint = (
        endpoint
        or os.environ.get(f"{env_prefix}_S3_ENDPOINT")
        or profile_config.get("endpoint")
        or "http://localhost:9000"
    )
    result_access_key = (
        access_key
        or os.environ.get(f"{env_prefix}_S3_ACCESS_KEY")
        or profile_config.get("access_key")
    )
    result_secret_key = (
        secret_key
        or os.environ.get(f"{env_prefix}_S3_SECRET_KEY")
        or profile_config.get("secret_key")
    )
    result_bucket = (
        bucket
        or os.environ.get(f"{env_prefix}_S3_BUCKET")
        or profile_config.get("bucket")
    )

    # Get additional profile-specific config
    extra = {}
    if profile == "maps":
        extra["pattern"] = (
            os.environ.get("MAPS_S3_PATTERN")
            or profile_config.get("pattern")
            or "{map_name}_{map_sha256}.map"
        )

    # Credentials are optional (bucket might be public)
    if not result_bucket:
        raise ValueError(
            f"Missing bucket for {profile}. Set {env_prefix}_S3_BUCKET "
            f"environment variable, add to .teehistorian.toml [{profile}.s3], "
            "or pass bucket parameter."
        )

    # Infer SSL from endpoint URL
    parsed = urlparse(result_endpoint)
    use_ssl = parsed.scheme == "https"

    return {
        "endpoint": result_endpoint,
        "access_key": result_access_key,
        "secret_key": result_secret_key,
        "bucket": result_bucket,
        "use_ssl": use_ssl,
        **extra,
    }


def get_download_dir(output_dir: Optional[str] = None, profile: str = "teehistorian") -> Path:
    """Get download directory from parameter, environment variable, or config file.

    Args:
        output_dir: Override output directory
        profile: Config profile name

    Returns:
        Path to output directory.
    """
    if output_dir:
        return Path(output_dir)

    env_prefix = profile.upper()
    env_dir = os.environ.get(f"{env_prefix}_DOWNLOAD_DIR")
    if env_dir:
        return Path(env_dir)

    file_config = _load_config_file()
    config_dir = file_config.get(profile, {}).get("download_dir")
    if config_dir:
        return Path(config_dir)

    return Path.cwd()
