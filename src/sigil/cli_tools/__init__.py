# lives here to trigger registration logic without manual imports for module discovery

# Source - modified from https://stackoverflow.com/a/1057534

import glob
from os.path import basename, dirname, isfile, join

modules = glob.glob(join(dirname(__file__), "*.py"))

__all__ = []
for mod in modules:
    if not isfile(mod):
        continue
    if mod.endswith('__init__.py'):
        continue
    with open(mod) as f:
        if '# CLI_NO_IMPORT' in f.read():
            continue
    base = basename(mod)[:-3]
    imported = __import__(f'{__name__}.{base}', globals(), locals())
    __all__.append(base)

