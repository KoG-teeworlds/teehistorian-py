"""CLI entry point for teehistorian-map."""

import argparse
import sys

from .map_downloader import download_map, get_map_url
from teehistorian_shared import (
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    S3Error,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="teehistorian-map",
        description="Download map files from S3/R2 based on teehistorian headers",
    )
    parser.add_argument(
        "file",
        help="Path to teehistorian file",
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save the file",
    )
    parser.add_argument(
        "--pattern",
        help="S3 key pattern (default: {map_name}_{map_sha256}.map)",
    )
    parser.add_argument(
        "--endpoint",
        help="S3/R2 endpoint URL",
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
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show download URL",
    )

    args = parser.parse_args()

    try:
        if args.verbose:
            url = get_map_url(
                args.file,
                pattern=args.pattern,
                endpoint=args.endpoint,
                bucket=args.bucket,
            )
            print(f"URL: {url}", file=sys.stderr)

        if args.stdout:
            data = download_map(
                args.file,
                save=False,
                pattern=args.pattern,
                endpoint=args.endpoint,
                bucket=args.bucket,
                access_key=args.access_key,
                secret_key=args.secret_key,
            )
            sys.stdout.buffer.write(data)
        else:
            path = download_map(
                args.file,
                save=True,
                output_dir=args.output_dir,
                pattern=args.pattern,
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
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
