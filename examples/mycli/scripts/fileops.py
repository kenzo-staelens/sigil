import argparse
import sys
from pathlib import Path
from typing import Any


def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        sys.exit()
    print(f"Operating on: {directory}")
    # The subcommand will be invoked after this, so this script runs first
