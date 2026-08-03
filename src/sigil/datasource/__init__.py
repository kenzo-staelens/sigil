from .datasource import DataSource
from .json_source import JSONSource

__all__ = [
    'DataSource',
    'JSONSource',
]

try:
    # preparation for PEP 771 or conversion to `pip install sigil-cli[yaml]` install
    # any datasources with dependencies should import like this
    from .yml_source import YmlSource  # noqa: F401
    __all__.append('YmlSource')
except ImportError:
    pass
