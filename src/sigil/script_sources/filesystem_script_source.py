import importlib
import logging
import sys
from importlib.abc import Loader
from pathlib import Path
from typing import cast

from sigil.models import SubcommandModule

from .script_source import ScriptSource

_logger = logging.getLogger(__name__)


class FilesystemScriptSource(ScriptSource):
    @classmethod
    def _construct_package_name(
        cls,
        config_root_path: Path,
        module_dir: Path,
        module_name: str
    ) -> str:
        module_dir_str = str(module_dir)
        if module_dir_str not in sys.path:
            sys.path.insert(0, module_dir_str)

        root_str = str(config_root_path)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)

        try:
            rel_path = module_dir.relative_to(config_root_path)
        except ValueError:
            # If the module is outside config_root, fallback to a safe unique namespace
            rel_path = Path("_dynamic_") / module_dir.name

        package_name = ".".join(rel_path.parts)  # e.g., "subcommands.foo"
        fully_qualified_name = (
            f"{package_name}.{module_name}"
            if package_name
            else module_name
        )
        return fully_qualified_name

    @classmethod
    def import_module(
        cls,
        config_root: Path,
        path:str | None,
        module_name: str
    ) -> SubcommandModule | None:
        if path is None:
            _logger.warning(
                f"no root path declared for script loading, skipping {module_name}"
            )
            return None
        config_root_path = Path(config_root).resolve()
        module_dir = (config_root_path/path).resolve()
        file_path = str(module_dir/f'{module_name}.py')

        package_name = cls._construct_package_name(
            config_root_path,
            module_dir,
            module_name
        )

        spec = importlib.util.spec_from_file_location(package_name, file_path)
        if not spec:
            raise FileNotFoundError(file_path)
        module = importlib.util.module_from_spec(spec)
        cast(Loader, spec.loader).exec_module(module)
        return cast(SubcommandModule, module) # or at least assumed to be by contract
