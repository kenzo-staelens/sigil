import argparse
from pathlib import Path
from typing import Any


def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    directory = Path(args.directory)
    files = directory.iterdir()
    if args.extension:
        files = (f for f in files if f.suffix == args.extension)
    count = sum(1 for _ in files)
    print(f"Count: {count}")
