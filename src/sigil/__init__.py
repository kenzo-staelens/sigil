from importlib.metadata import version

__version__ = version('sigil-cli')

from .entrypoint import run_from_config
from .models import (
    Argument,
    ArgumentGroup,
    LibArgParser,
    ParserConfig,
    SubcommandModule,
)
from .stages import (
    Builder,
    Parser,
    Resolver,
    ScriptLoader,
)

__all__ = (
    'run_from_config',
    'Argument',
    'ArgumentGroup',
    'LibArgParser',
    'ParserConfig',
    'SubcommandModule',
    'Parser',
    'Resolver',
    'Builder',
    'ScriptLoader',
)
