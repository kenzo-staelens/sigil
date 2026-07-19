import logging
from pathlib import Path
from typing import Any

import yaml

from sigil.models import Argument, ParserConfig

_logger = logging.getLogger(__name__)

# This class converts raw data to dataclasses,
# however swap it out if you want to use a different form of IO
class YamlReader:
    @classmethod
    def handle_duplicates(
        cls,
        loaded_entry: dict[str],
        loaded_config: dict[str],
        entry: str
    ):
        # warning: in place mutation if you decide to make changes to loaded config
        if duplicates := (loaded_entry.keys() & loaded_config.keys()):
            for duplicate in duplicates:
                _logger.warning(f"{entry}[{duplicate}] already defined, ignoring")

    @classmethod
    def load(
        cls,
        config_root: str,
        manifest_file='manifest.yml'
    ) -> dict[str, ParserConfig]:
        config_root_path = Path(config_root)
        manifest = cls.read_file(config_root_path/manifest_file)
        loaded_config = {}

        for entry in manifest:
            loaded_entry = cls.read_file(config_root_path/entry)
            if not loaded_entry:
                continue
            loaded_entry = {
                k:v
                for k, v in loaded_entry.items()
                if not v.get('load_ignore')
            }
            cls.handle_duplicates(loaded_entry, loaded_config, entry)
            cls.convert_args(loaded_entry)
            # override loaded entry duplicates by already found
            loaded_config = loaded_entry | loaded_config

        for k, v in loaded_config.items():
            try:
                loaded_config[k] = ParserConfig.factory(**v)
            except Exception:
                _logger.error(f'failed to parse config {k}, ignoring')
        # pesky "dictionary changed size during iteration"
        loaded_config = {
            k: v
            for k,v in loaded_config.items()
            if isinstance(v, ParserConfig)
        }

        return loaded_config

    @classmethod
    def convert_args(cls, loaded_entry: dict[str, dict[str, Any]]):
        # while yes default factory this fixes the edge case where the key is defined
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

    # actual IO, also adaptable
    @classmethod
    def read_file(cls, filename) -> dict:
        try:
            with open(filename) as f:
                return yaml.load(f.read(), Loader=yaml.SafeLoader)
        except FileNotFoundError:
            _logger.error(f'failed to load file {filename}, skipping')
            return None
