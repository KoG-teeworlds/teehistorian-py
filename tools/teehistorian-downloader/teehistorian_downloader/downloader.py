"""S3/Minio downloader for teehistorian files."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

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


def download(
    uuid: str,
    *,
    save: bool = False,
    output_dir: Optional[Union[str, Path]] = None,
    endpoint: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    bucket: Optional[str] = None,
) -> Union[bytes, Path]:
    """Download a teehistorian file from S3/Minio.

    Args:
        uuid: The UUID of the teehistorian file to download.
        save: If True, save to file and return path. If False, return bytes.
        output_dir: Directory to save file to (only used if save=True).
        endpoint: S3/Minio endpoint URL.
        access_key: S3/Minio access key.
        secret_key: S3/Minio secret key.
        bucket: S3 bucket name.

    Returns:
        If save=False: File contents as bytes.
        If save=True: Path to the downloaded file.

    Raises:
        ConfigurationError: If required configuration is missing.
        ConnectionError: If connection to S3/Minio fails.
        NotFoundError: If the file doesn't exist in the bucket.
        S3Error: For other S3-related errors.

    Example:
        >>> data = download("000c81cc-0922-4150-97e9-cd8f9776eb8e")
        >>> path = download("000c81cc-0922-4150-97e9-cd8f9776eb8e", save=True)
    """
    # Get configuration
    try:
        config = get_s3_config(
            profile="teehistorian",
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket,
        )
    except ValueError as e:
        raise ConfigurationError(str(e)) from e

    # Build the S3 key
    key = f"{uuid}.teehistorian"

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

    # Download the file
    try:
        response = client.get_object(Bucket=config["bucket"], Key=key)
        data = response["Body"].read()
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchKey"):
            raise NotFoundError(
                f"File '{key}' not found in bucket '{config['bucket']}'"
            ) from e
        raise S3Error(f"S3 error: {e}") from e
    except EndpointConnectionError as e:
        raise ConnectionError(f"Could not connect to {config['endpoint']}: {e}") from e

    # Return bytes or save to file
    if not save:
        return data

    out_dir = get_download_dir(str(output_dir) if output_dir else None, profile="teehistorian")
    output_path = out_dir / f"{uuid}.teehistorian"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return output_path
