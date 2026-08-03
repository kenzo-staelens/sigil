import itertools
import json
import logging
from pathlib import Path

from .datasource import DataSource
from .helper import _expandpath

_logger = logging.getLogger(__name__)


# base defines abstract as not-classmethod
# though instantiation is not a requirement
# if you don't need instance data, classmethods are fine too
class JSONSource(DataSource):
    def read(self, root_path: Path, filename: str) -> dict:
        try:
            target = root_path/filename
            with open(target) as f:
                return json.load(f)
                # return yaml.load(f.read(), Loader=yaml.SafeLoader)
        except FileNotFoundError:
            _logger.error(f"file '{target}' not found")
            return
        except json.JSONDecodeError as e:
            _logger.error(f"malformed json file ({target})\n  {e}")
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

