import argparse
import functools
from collections.abc import Callable

COMMAND_REGISTRY: 'dict[str, Callable[[argparse.Namespace]]]' = {}
REGISTER_CALLABLES = []

def registers(name: str, cmd_help: str):
    def decorator_fn(f: 'Callable[[argparse.ArgumentParser], Callable[[argparse.Namespace]]]'):  # noqa: E501
        @functools.wraps(f)
        def wrapper(parser: argparse._SubParsersAction):
            if name in COMMAND_REGISTRY:
                raise RuntimeError(f'{name} already registered')
            subparser: argparse.ArgumentParser = parser.add_parser(
                name=name,
                help=cmd_help
            )
            callable = f(subparser)
            COMMAND_REGISTRY[name] = callable
            return subparser
        # note: requires import in cli_tools.__init__ to auto trigger registration
        REGISTER_CALLABLES.append(wrapper)
        return wrapper
    return decorator_fn
