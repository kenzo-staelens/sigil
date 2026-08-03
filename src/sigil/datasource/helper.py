from collections.abc import Iterable
from pathlib import Path


def _expandpath(config_root: Path, path_pattern: Path) -> Iterable[Path]:
        _has_glob = lambda part: any(ch in part for ch in "*?[")  # noqa: E731
        p: Path = (config_root/path_pattern).resolve()
        str_p = str(p)

        # Quick check: does this path contain any glob pattern at all?
        if not _has_glob(str_p):
            yield p.resolve()
            return  # is this cursed? yes, does it work somehow? also yes
        parts = p.parts

        # Find the first part that contains a wildcard
        first_glob_idx = 0
        for i, part in enumerate(parts):
            if _has_glob(part):
                first_glob_idx = i
                break

        # Build the literal base directory and the relative glob pattern
        if first_glob_idx == 0:
            base = Path('.')
            if parts[0] == '/':  # pesky absolute paths
                base = Path('/')
                parts = parts[1:]
        else:
            base = Path(*parts[:first_glob_idx])

        pattern = "/".join(parts[first_glob_idx:])
        # Expand the pattern relative to the base, and resolve each match
        for match in base.glob(pattern):
            yield match.resolve()
