"""CLI entry point for teehistorian-demo."""

import argparse
import sys

from .converter import (
    convert_to_demo,
    ConversionError,
    TeeHeeNotFoundError,
)
from teehistorian_shared import (
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    S3Error,
)


def _prompt_yes_no(message: str) -> bool:
    """Prompt user for yes/no confirmation."""
    while True:
        try:
            response = input(f"{message} [y/N]: ").strip().lower()
            if response in ("y", "yes"):
                return True
            if response in ("", "n", "no"):
                return False
        except (EOFError, KeyboardInterrupt):
            print()
            return False


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="teehistorian-demo",
        description="Convert teehistorian files to demo files using tee-hee",
    )
    parser.add_argument(
        "source",
        help="UUID to download, or path to local .teehistorian file",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output .demo file path (default: {game_uuid}.demo)",
    )
    parser.add_argument(
        "-d", "--output-dir",
        help="Directory for output file (default: current directory)",
    )
    parser.add_argument(
        "-m", "--map",
        dest="map_file",
        help="Path to local .map file (default: download from S3)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output",
    )

    args = parser.parse_args()

    try:
        demo_path = convert_to_demo(
            args.source,
            output=args.output,
            output_dir=args.output_dir,
            map_file=args.map_file,
            verbose=args.verbose,
            prompt_func=_prompt_yes_no,
        )
        print(f"Created: {demo_path}")
        return 0

    except TeeHeeNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ConversionError as e:
        print(f"Conversion error: {e}", file=sys.stderr)
        return 1
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
