import argparse
from typing import Any


def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    print('Hello World!')
    if args.verbose:
        print('Hello Verbose World!')
