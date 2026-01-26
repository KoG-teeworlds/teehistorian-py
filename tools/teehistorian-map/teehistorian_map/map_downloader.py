"""Map downloader from S3/R2 based on teehistorian header."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError

from teehistorian_shared import (
    get_s3_config,
    get_download_dir,
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    S3Error,
)
from teehistorian_header import parse_header


def _create_s3_client(
    endpoint: str,
    access_key: Optional[str],
    secret_key: Optional[str],
    use_ssl: bool,
):
    """Create a boto3 S3 client configured for S3-compatible storage."""
    from botocore import UNSIGNED
    from botocore.config import Config

    # Use unsigned requests for public buckets (no credentials)
    if not access_key or not secret_key:
        return boto3.client(
            "s3",
            endpoint_url=endpoint,
            use_ssl=use_ssl,
            config=Config(signature_version=UNSIGNED),
        )

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        use_ssl=use_ssl,
    )


def _build_map_key(header: dict[str, Any], pattern: str) -> str:
    """Build the S3 key for a map file from header fields.

    Args:
        header: Teehistorian header dictionary.
        pattern: Pattern with placeholders like {map_name}, {map_sha256}.

    Returns:
        The S3 key for the map file.

    Raises:
        ValueError: If required fields are missing from header.
    """
    # Extract fields that might be used in patterns
    fields = {
        "map_name": header.get("map_name"),
        "map_sha256": header.get("map_sha256"),
        "map_size": header.get("map_size"),
    }

    # Check which fields are needed by the pattern
    missing = []
    for field_name, value in fields.items():
        if f"{{{field_name}}}" in pattern and not value:
            missing.append(field_name)

    if missing:
        raise ValueError(
            f"Header missing required fields for pattern '{pattern}': {', '.join(missing)}"
        )

    return pattern.format(**{k: v for k, v in fields.items() if v is not None})


def get_map_url(
    source: Union[str, Path, bytes, dict[str, Any]],
    *,
    pattern: Optional[str] = None,
    endpoint: Optional[str] = None,
    bucket: Optional[str] = None,
) -> str:
    """Get the full URL for a map file without downloading.

    Args:
        source: Teehistorian file path, bytes, or already-parsed header dict.
        pattern: S3 key pattern. Default: "{map_name}_{map_sha256}.map"
        endpoint: S3/R2 endpoint URL.
        bucket: S3 bucket name.

    Returns:
        Full URL to the map file.
    """
    # Parse header if needed
    if isinstance(source, dict):
        header = source
    else:
        header = parse_header(source)

    # Get configuration (credentials not needed for URL)
    try:
        config = get_s3_config(
            profile="maps",
            endpoint=endpoint,
            access_key="dummy",  # Not needed for URL
            secret_key="dummy",
            bucket=bucket,
        )
    except ValueError as e:
        raise ConfigurationError(str(e)) from e

    # Use pattern from config if not provided
    key_pattern = pattern or config.get("pattern", "{map_name}_{map_sha256}.map")

    # Build the S3 key from header
    key = _build_map_key(header, key_pattern)

    # Build full URL
    endpoint_url = config["endpoint"].rstrip("/")
    return f"{endpoint_url}/{config['bucket']}/{key}"


def download_map(
    source: Union[str, Path, bytes, dict[str, Any]],
    *,
    save: bool = False,
    output_dir: Optional[Union[str, Path]] = None,
    pattern: Optional[str] = None,
    endpoint: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    bucket: Optional[str] = None,
) -> Union[bytes, Path]:
    """Download a map file from S3/R2 based on teehistorian header.

    Args:
        source: Teehistorian file path, bytes, or already-parsed header dict.
        save: If True, save to file and return path. If False, return bytes.
        output_dir: Directory to save file to (only used if save=True).
        pattern: S3 key pattern. Default: "{map_name}_{map_sha256}.map"
        endpoint: S3/R2 endpoint URL.
        access_key: S3/R2 access key.
        secret_key: S3/R2 secret key.
        bucket: S3 bucket name.

    Returns:
        If save=False: Map file contents as bytes.
        If save=True: Path to the downloaded file.

    Raises:
        ConfigurationError: If required configuration is missing.
        ConnectionError: If connection to S3/R2 fails.
        NotFoundError: If the map file doesn't exist in the bucket.
        S3Error: For other S3-related errors.
        ValueError: If header is missing required fields.

    Example:
        >>> map_data = download_map("recording.teehistorian")
        >>> path = download_map("recording.teehistorian", save=True)
    """
    # Parse header if needed
    if isinstance(source, dict):
        header = source
    else:
        header = parse_header(source)

    # Get configuration
    try:
        config = get_s3_config(
            profile="maps",
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket,
        )
    except ValueError as e:
        raise ConfigurationError(str(e)) from e

    # Use pattern from config if not provided
    key_pattern = pattern or config.get("pattern", "{map_name}_{map_sha256}.map")

    # Build the S3 key from header
    key = _build_map_key(header, key_pattern)

    # Create S3 client
    try:
        client = _create_s3_client(
            endpoint=config["endpoint"],
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            use_ssl=config["use_ssl"],
        )
    except NoCredentialsError as e:
        raise ConfigurationError(f"Invalid credentials: {e}") from e

    # Build full URL for error messages
    endpoint = config["endpoint"].rstrip("/")
    full_url = f"{endpoint}/{config['bucket']}/{key}"

    # Download the file
    try:
        response = client.get_object(Bucket=config["bucket"], Key=key)
        data = response["Body"].read()
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchKey"):
            raise NotFoundError(f"Map not found: {full_url}") from e
        raise S3Error(f"S3 error downloading {full_url}: {e}") from e
    except EndpointConnectionError as e:
        raise ConnectionError(f"Could not connect to {config['endpoint']}: {e}") from e

    # Return bytes or save to file
    if not save:
        return data

    # Determine output filename from map_name
    map_name = header.get("map_name", "unknown")
    out_dir = get_download_dir(str(output_dir) if output_dir else None, profile="maps")
    output_path = out_dir / f"{map_name}.map"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return output_path
