"""CLI entry point for teehistorian-header."""

import argparse
import sys

from .header import get_header


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="teehistorian-header",
        description="Parse and display teehistorian file headers",
    )
    parser.add_argument(
        "file",
        help="Path to teehistorian file",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "raw", "table"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    try:
        output = get_header(args.file, format=args.format)
        print(output)
        return 0
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
