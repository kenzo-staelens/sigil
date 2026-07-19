import argparse
from pathlib import Path
from typing import Any


def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    directory = Path(args.directory)
    items = list(directory.iterdir())
    for item in sorted(items):
        if args.long:
            stat = item.stat()
            print(f"{stat.st_size:>10}  {item.name}")
        else:
            print(item.name)
