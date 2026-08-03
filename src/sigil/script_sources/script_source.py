from abc import ABC, abstractmethod
from pathlib import Path

from sigil.models import SubcommandModule


class ScriptSource(ABC):
    @abstractmethod
    def import_module(
        cls,
        config_root: Path,  # config root
        script_dir: str | None,  # script dir according to root config
        module_name: str  # data in config file
    ) -> SubcommandModule | None: ...
