from importlib.metadata import version

__version__ = version('sigil-cli')

from .datasource import (
    DataSource,
    JSONSource,
    YmlSource,
)
from .entrypoint import run_from_config
from .models import (
    Argument,
    ArgumentGroup,
    LibArgParser,
    ParserConfig,
    SubcommandModule,
)
from .script_sources import (
    FilesystemScriptSource,
    ScriptSource,
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
    'DataSource',
    'JSONSource',
    'YmlSource',
    'FilesystemScriptSource',
    'ScriptSource',
)
