import argparse
from typing import Any

# example script
def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    message = f'hello {{args.name}}!'
    if args.shout:
        message = message.upper()

    print(message)

    if args.verbose:
        print("[DEBUG] Verbose mode enabled")