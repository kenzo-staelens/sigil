import argparse
from typing import Any


def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    result = args.a + args.b
    if getattr(args, "verbose", False):
        print(f"{args.a} + {args.b} = {result}")
    else:
        print(result)
