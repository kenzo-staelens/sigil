import argparse
from types import ModuleType
from typing import Any


class SubcommandModule(ModuleType):
    @staticmethod
    def run(args: argparse.Namespace, ctx: dict[str, Any]): ...
