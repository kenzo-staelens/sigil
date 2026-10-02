import itertools
import logging
from pathlib import Path

import yaml

from .datasource import DataSource
from .helper import _expandpath

_logger = logging.getLogger(__name__)

# base defines abstract as not-classmethod
# though instantiation is not a requirement
# if you don't need instance data, classmethods are fine too
class YmlSource(DataSource):
    def read(self, root_path: Path, filename: str) -> dict:
        try:
            target = root_path/filename
            with open(target) as f:
                return yaml.load(f.read(), Loader=yaml.SafeLoader)
        except FileNotFoundError:
            _logger.error(f"file '{target}' not found")
            return
        except yaml.error.YAMLError as e:
            _logger.error(f"malformed yaml file ({target})\n  {e}")
            return


    def read_manifest(self, root_path: Path, filename: str) -> list | None:
        # indirection? yes
        # can new datasources implement a better manifest vs data? also yes
        raw_manifest = self.read(root_path, filename)
        res_manifest = []
        for line in raw_manifest:
            res_manifest = itertools.chain(
                res_manifest,
                _expandpath(root_path, Path(line))
            )
        return res_manifest


    def read_configuration(self, root_path: Path, filename: str) -> dict | None:
        return self.read(root_path, filename)

