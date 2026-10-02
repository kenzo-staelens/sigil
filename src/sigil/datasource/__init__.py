from .datasource import DataSource
from .json_source import JSONSource

__all__ = [
    'DataSource',
    'JSONSource',
]

REAL_SOURCES = {
    x: local_cls
    for x in __all__
    if (local_cls:=globals().get(x))
    and issubclass(local_cls, DataSource)
    and not local_cls.is_abstract()
}


try:
    # preparation for PEP 771 or conversion to `pip install sigil-cli[yaml]` install
    # any datasources with dependencies should import like this
    from .yml_source import YmlSource  # noqa: F401
    REAL_SOURCES['YmlSource'] = YmlSource  # known not abstract
    __all__.append('YmlSource')
except (ImportError, ModuleNotFoundError):
    pass
