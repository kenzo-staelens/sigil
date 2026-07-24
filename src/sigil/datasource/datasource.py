from abc import ABC, abstractmethod
from pathlib import Path


# currently network based datasources are not planned
# but if you do *need* one for some reason, feel free to make a PR
class DataSource(ABC):
    @classmethod
    @abstractmethod
    def read_manifest(cls, target: Path) -> list | None:
        # current implementation expects a list of files, or none on error
        ...

    @classmethod
    @abstractmethod
    def read_configuration(cls, target: Path) -> dict | None:
        # raw data roughly mapping to internal models
        # validation happens in a later stage
        # datasources shouldn't need to validate
        # for duplicates or malformed data
        ...
