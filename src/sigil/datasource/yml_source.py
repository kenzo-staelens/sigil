import logging
from pathlib import Path

import yaml

from .datasource import DataSource

_logger = logging.getLogger(__name__)


# base defines abstract as not-classmethod
# though instantiation is not a requirement
# if you don't need instance data, classmethods are fine too
class YmlSource(DataSource):
    def read(self, target) -> dict:
        try:
            with open(target) as f:
                return yaml.load(f.read(), Loader=yaml.SafeLoader)
        except FileNotFoundError:
            _logger.error(f"file '{target}' not found")
            return
        except yaml.error.YAMLError as e:
            _logger.error(f"malformed yaml file ({target})\n  {e}")
            return


    def read_manifest(self, target: Path) -> list | None:
        # indirection? yes
        # can new datasources implement a better manifest vs data? also yes
        return self.read(target)


    def read_configuration(self, target: Path) -> dict | None:
        return self.read(target)

