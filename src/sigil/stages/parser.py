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
        manifest_entry: str
    ) ->  dict[str, Any]:
        """Handle duplicate yaml keys across multiple files.

        :param loaded_entry: currently handled manifest entry
        :type loaded_entry: dict[str, Any]
        :param loaded_config: already loaded configurations
        :type loaded_config: dict[str, Any]
        :param manifest_entry: target entry as defined in manifest.yml
        :type manifest_entry: str
        :return: merged config
        :rtype:  dict[str, Any]
        """
        # note: currently this is the warning only, there's a | elsewhere
        if duplicates := (loaded_entry.keys() & loaded_config.keys()):
            for duplicate in duplicates:
                _logger.warning(
                    f"{manifest_entry} [{duplicate}] already defined, ignoring"
                )
        valid_entries = loaded_entry | loaded_config
        return valid_entries

    @classmethod
    def handle_name_collisions(
        cls,
        loaded_config: dict[str, Any],
        manifest_entry: str
    ) -> dict[str, Any] :
        """Handle name collision where two sibling commands have
        the same argparse name parameter.

        :param loaded_config: deduplicated (by key) configurations
        :type loaded_config: dict[str, Any]
        :param manifest_entry: target entry as defined in manifest.yml
        :type manifest_entry: str
        :return: validated config
        :rtype: dict[str, Any]
        """
        loaded_command_names_config = set()
        valid_entries = {}
        for key, item in loaded_config.items():
            if (
                (item.get('parent', None), item.get('name', None))
                in loaded_command_names_config
            ):
                _logger.warning(
                    f"{manifest_entry} [{key}] found duplicated command "
                    f"[{item.get('name')}] in parent command "
                    f"[{item.get('parent', None)}], ignoring"
                )
            else:
                valid_entries[key] = item
            loaded_command_names_config.add(
                (item.get('parent', None), item.get('name', None))
            )
        return valid_entries

    def load(
        self,
        config_root: str | Path,
        manifest_file: str = 'manifest.yml',
    ) -> dict[str, ParserConfig]:
        config_root_path = Path(config_root)

        manifest = self.datasource.read_manifest(config_root_path, manifest_file)
        if not manifest:
            _logger.critical("could not load manifest, aborting")
            sys.exit(1)
        loaded_config = {}

        for entry in manifest:
            loaded_entry = self.datasource.read_configuration(config_root_path, entry)
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
            self.convert_args(loaded_entry)
            # remove duplicates by key
            loaded_config = self.handle_duplicates(loaded_entry, loaded_config, entry)
            # remove sibling duplicates by parent
            loaded_config = self.handle_name_collisions(loaded_config, entry)

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
