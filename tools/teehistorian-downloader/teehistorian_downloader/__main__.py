"""CLI entry point for teehistorian-downloader."""

import argparse
import sys

from .downloader import download
from teehistorian_shared import (
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    S3Error,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="teehistorian-downloader",
        description="Download teehistorian files from S3/Minio",
    )
    parser.add_argument(
        "uuid",
        help="UUID of the teehistorian file to download",
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save the file",
    )
    parser.add_argument(
        "--endpoint",
        help="S3/Minio endpoint URL",
    )
    parser.add_argument(
        "--bucket",
        help="S3 bucket name",
    )
    parser.add_argument(
        "--access-key",
        help="S3 access key",
    )
    parser.add_argument(
        "--secret-key",
        help="S3 secret key",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Write file contents to stdout instead of saving",
    )

    args = parser.parse_args()

    try:
        if args.stdout:
            data = download(
                args.uuid,
                save=False,
                endpoint=args.endpoint,
                bucket=args.bucket,
                access_key=args.access_key,
                secret_key=args.secret_key,
            )
            sys.stdout.buffer.write(data)
        else:
            path = download(
                args.uuid,
                save=True,
                output_dir=args.output_dir,
                endpoint=args.endpoint,
                bucket=args.bucket,
                access_key=args.access_key,
                secret_key=args.secret_key,
            )
            print(f"Downloaded: {path}")
        return 0

    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except NotFoundError as e:
        print(f"Not found: {e}", file=sys.stderr)
        return 1
    except ConnectionError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        return 1
    except S3Error as e:
        print(f"S3 error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
