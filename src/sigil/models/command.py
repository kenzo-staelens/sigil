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
    known_args: bool = False  # whether to use parse_args, or parse_known_args
    # help is so uber-common that while yes it could go into
    # parser_kwargs i still explicitly defined it
    help: str | None = None
    args: list[Argument] = field(default_factory=list)
    script: str | None = None
    # parent not arparse parent,
    # this one is just for resolving the config files into a tree
    parent: str | None = None
    default: bool = False
    subparsers: 'dict[str, ParserConfig]' = field(default_factory=dict)
    # anything not already in here
    parser_kwargs: dict[str, Any] = field(default_factory=dict)
    load: bool = True

    @classmethod
    def factory(cls, **kwargs):
        if 'name' not in kwargs:
            raise ValueError("required argument 'name' not defined.")
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

    @classmethod
    def construct_unloaded_data(cls, key: str, source: dict):
        # this dataclass requires several attributes for either validation checks
        # or instantiation requirements
        # all get defined here, regardless of source data
        # since this object is later required to validate and build tree
        # structure minimal data is required
        return {
            'name': key,
            'help': source.get('help', 'missing'),
            'load': source.get('load'),
            'parent': source.get('parent')
        }
