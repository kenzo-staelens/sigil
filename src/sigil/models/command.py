import logging
from dataclasses import dataclass, field
from typing import Any

from .argument import Argument

_logger = logging.getLogger(__name__)

UNSUPPORTED_KWARGS = [
    'dest',  # screws with loading scripts
    'formatter_class', # is a class, not a string
    'parents',  # no inheritance supported
]

@dataclass
class ParserConfig:
    name: str
    script_dir: str | None = None # only for root
    # help is so uber-common that while yes it could go into
    # parser_kwargs i still explicitly defined it
    help: str | None = None
    args: list[Argument] = field(default_factory=list)
    script: str | None = None
    # parent not arparse parent,
    # this one is just for resolving the config files into a tree
    parent: str | None = None
    default: bool = False
    load: bool = True
    subparsers: 'dict[str, ParserConfig]' = field(default_factory=dict)
    # anything not already in here
    parser_kwargs: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def factory(cls, **kwargs):
        uncaught_kwargs = {k: kwargs[k] for k in kwargs if k not in cls.__match_args__}
        caught_kwargs = {k: kwargs[k] for k in kwargs if k in cls.__match_args__}
        parser_kwargs = {}
        for kwarg, value in uncaught_kwargs.items():
            if kwarg in UNSUPPORTED_KWARGS:
                if kwarg == 'parents':
                    _logger.warning(
                        f"parser kwarg '{kwarg}' unsupported, "
                        "ignoring. Did you mean 'parent'?")
                else:
                    _logger.warning(f"parser kwarg '{kwarg}' unsupported, ignoring")
            else:
                parser_kwargs[kwarg] = value
        return cls(**caught_kwargs, parser_kwargs=parser_kwargs)
