from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


# currently network based datasources are not planned
# but if you do *need* one for some reason, feel free to make a PR
class DataSource(ABC):
    @abstractmethod
    def read_manifest(self, root_path: Path, target: Any) -> list | None:
        # current implementation expects a list of files, or none on error
        ...

    @abstractmethod
    def read_configuration(self, root_path: Path, target: Any) -> dict | None:
        # raw data roughly mapping to internal models
        # validation happens in a later stage
        # datasources shouldn't need to validate
        # for duplicates or malformed data
        ...
