import logging
from pathlib import Path

import yaml

from .datasource import DataSource

_logger = logging.getLogger(__name__)


class YmlSource(DataSource):

    @classmethod
    def read(cls, target):
        try:
            with open(target) as f:
                return yaml.load(f.read(), Loader=yaml.SafeLoader)
        except FileNotFoundError:
            _logger.error(f"file '{target}' not found")
            return
        except yaml.error.YAMLError:
            _logger.error(f"malformed yaml file ({target})")
            return


    @classmethod
    def read_manifest(cls, manifest_file: Path) -> list | None:
        # indirection? yes
        # can new datasources implement a better manifest vs data? also yes
        return cls.read(manifest_file)


    @classmethod
    def read_configuration(cls, target: Path) -> dict | None:
        return cls.read(target)

