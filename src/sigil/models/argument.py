import builtins
import logging
from dataclasses import dataclass, field
from typing import Any, cast

AGGREGATE_TYPES = [
    'group',
    'mutex'
]

ALLOWED_KINDS = [
    'argument',
    *AGGREGATE_TYPES
]


_logger = logging.getLogger(__name__)

@dataclass
class ArgumentGroup:
    args: 'list[Argument | ArgumentGroup]'
    mutex: bool
    # anything else not specifically in here
    kw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def factory(cls, **kwargs: dict[str, Any]) -> 'ArgumentGroup':
        kind: str = cast(str, kwargs.pop('kind', 'argument'))
        # yes argparse only supports these 2 groupings for now
        # but it can't hurt to not write an if/else ladder in the future
        is_mutex = {
            'group': False,
            'mutex': True
        }.get(kind, False)
        incoming_args: list[dict[str, Any]] = cast(
            list[dict[str, Any]],
            kwargs.pop('args',  [])
        )
        group_content = [
            Argument.factory(**arg)
            for arg in incoming_args
        ]
        uncaught_kwargs = {k: kwargs[k] for k in kwargs if k not in cls.__match_args__}
        return cls(args=group_content, mutex=is_mutex, kw=uncaught_kwargs)


@dataclass
class Argument:
    name: list[str]
    required: bool = False
    # help is so uber-common that while yes it could go into
    # kw i still explicitly defined it
    help: str | None = None
    # anything we haven't explicitly defined.. yet
    kw: dict[str, Any] = field(default_factory=dict)

    # Source - https://stackoverflow.com/a/74459763

    @classmethod
    def factory(cls, **kwargs: dict[str, Any]) -> 'Argument | ArgumentGroup':
        kind = kwargs.get('kind', 'argument')  # default to argument
        if kind not in ALLOWED_KINDS:
            raise ValueError(f'invalid kind {kind}')
        if kind in AGGREGATE_TYPES:
            return ArgumentGroup.factory(**kwargs)
        name = kwargs.get('name')
        if isinstance(name, str):
            kwargs['name'] = [name] # type: ignore
        uncaught_kwargs = {k: kwargs[k] for k in kwargs if k not in cls.__match_args__}
        caught_kwargs = {k: kwargs[k] for k in kwargs if k in cls.__match_args__}
        return cls(**caught_kwargs, kw=uncaught_kwargs) # type: ignore

    def __post_init__(self):
        if argtype := self.kw.get('type'):
            if not isinstance(argtype, str):
                # default implementation assumes string
                # though there are builtin constructors to apply classes directly
                # in those cases, just skip
                return
            if not hasattr(builtins, argtype):
                del self.kw['type']
                _logger.warning(
                    f"unable to find builtin type '{argtype}', "
                    "ignoring key 'type'"
                )
            else:
                self.kw['type'] = getattr(builtins, argtype)
