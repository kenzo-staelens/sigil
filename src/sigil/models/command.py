import logging
from dataclasses import dataclass, field

from .argument import Argument

_logger = logging.getLogger(__name__)

@dataclass
class ParserConfig:
    name: str
    script_dir: str | None = None # only for root
    help: str | None = None
    args: list[Argument] = field(default_factory=list)
    script: str | None = None
    parent: str | None = None
    default: bool = False
    load: bool = True
    subparsers: 'dict[str, ParserConfig]' = field(default_factory=dict)

    @classmethod
    def factory(cls, **kwargs):
        for k in kwargs:
            if k not in cls.__match_args__:
                _logger.warning(
                    f'found unknown key "{k}" in parser '
                    f'"{kwargs.get("name")}", ignoring'
                )
        return cls(**{k: kwargs[k] for k in kwargs if k in cls.__match_args__})
