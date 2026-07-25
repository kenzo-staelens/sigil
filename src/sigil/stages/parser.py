import logging
import sys
from pathlib import Path
from typing import Any

from sigil.datasource import DataSource
from sigil.models import Argument, ParserConfig

_logger = logging.getLogger(__name__)

# This class converts raw data to dataclasses
# it takes a datasource class to interface with any desired IO
class Parser:
    def __init__(self, datasource: DataSource | type[DataSource]):
        if isinstance(datasource, type):
            datasource: DataSource = datasource()
        self.datasource = datasource

    @classmethod
    def handle_duplicates(
        cls,
        loaded_entry: dict[str, Any],
        loaded_config: dict[str, Any],
        entry: str
    ):
        # warning: in place mutation if you decide to make changes to loaded config
        if duplicates := (loaded_entry.keys() & loaded_config.keys()):
            for duplicate in duplicates:
                _logger.warning(f"{entry}[{duplicate}] already defined, ignoring")

    def load(
        self,
        config_root: str | Path,
        manifest_file='manifest.yml',
    ) -> dict[str, ParserConfig]:
        config_root_path = Path(config_root)

        manifest = self.datasource.read_manifest(config_root_path/manifest_file)
        if not manifest:
            _logger.critical("could not load manifest, aborting")
            sys.exit(1)
        loaded_config = {}

        for entry in manifest:
            loaded_entry = self.datasource.read_configuration(config_root_path/entry)
            if not loaded_entry:
                continue
            tmp = {}
            for k, v in loaded_entry.items():
                if not v.get('load', True):
                    _logger.info(f'{k} marked as unloaded')
                    # truncate extra data
                    # the key will later be used for differentiating
                    # orphaned children vs intentionally unloaded subtrees
                    tmp[k] = ParserConfig.construct_unloaded_data(k, v)
                    continue
                tmp[k] = v  # pesky can't del in for loop :/
            loaded_entry = tmp
            self.handle_duplicates(loaded_entry, loaded_config, entry)
            self.convert_args(loaded_entry)
            # override loaded entry duplicates by already found
            loaded_config = loaded_entry | loaded_config

        for k, v in loaded_config.items():
            try:
                loaded_config[k] = ParserConfig.factory(**v)
            except Exception as e:
                _logger.error(f"failed to parse config '{k}', ignoring\n  {e}")
        # pesky "dictionary changed size during iteration"
        loaded_config = {
            k: v
            for k,v in loaded_config.items()
            if isinstance(v, ParserConfig)
        }
        return loaded_config

    @classmethod
    def convert_args(
        cls,
        loaded_entry: dict[str, dict[str, Any]],
    ):
        # while yes default factory; this fixes the edge case where the key is defined
        # but without values
        for command_def in loaded_entry.values():
            args = command_def.get('args') or []
            build_args = []
            for arg in args:
                try:
                    build_args.append(Argument.factory(**arg))
                except Exception: # any failure is skipped
                    _logger.error(f'invalid argument definition,\n{arg}\nskipping')
            command_def['args'] = build_args
