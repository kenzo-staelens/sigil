from dataclasses import dataclass, field
from typing import Any


@dataclass
class Argument:
    name: list[str]
    required: bool = False
    default: bool = False
    help: str | None = None
    action: str | None = None
    # anything we haven't explicitly defined.. yet
    kw: dict[str, Any] = field(default_factory=dict)

    # Source - https://stackoverflow.com/a/74459763

    @classmethod
    def factory(cls, **kwargs: dict):
        name = kwargs.get('name')
        if isinstance(name, str):
            kwargs['name'] = [name]
        return cls(**{k: kwargs[k] for k in kwargs if k in cls.__match_args__})
