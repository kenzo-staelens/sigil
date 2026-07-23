import contextlib
import logging
import sys
from pathlib import Path

from sigil import Builder, Resolver, YamlReader


# small helper to capture logs from in the guts of sigil
class WarningCollector(logging.Handler):
    """A handler that stores all records at WARNING level or above."""
    def __init__(self):
        super().__init__()
        self.warnings = []

    def emit(self, record):
        # Only store warnings and errors (you could also filter by level)
        if record.levelno >= logging.WARNING:
            self.warnings.append(record)

@contextlib.contextmanager
def capture_package_warnings(package_name):
    """
    Captures WARNING-level (and higher) logs from the given package tree.
    Example: capture_package_warnings('myproject')
    """
    collector = WarningCollector()
    # Get the package root logger – children will propagate to it
    package_logger = logging.getLogger(package_name)
    package_logger.addHandler(collector)
    try:
        yield collector
    finally:
        package_logger.removeHandler(collector)

# might as well use a logger and have cleaner counting logic
_logger = logging.getLogger(__name__)


# actual validation logging
def _validate_project(projectroot):
    projectpath = Path(projectroot)

    if not (projectpath/'manifest.yml').exists():
        _logger.error('missing manifest.yml, aborting.')
        sys.exit(1)

    raw = YamlReader.load(projectroot)

    # these are easier for us to check
    if 'root' not in raw:
        _logger.error('missing required root command')
        sys.exit(2)

    resolved = Resolver.resolve_inheritance(raw) #alerts basic structural errors for us
    Builder.build(resolved)  # catches the case for "only one default subcommand"

    script_root = None
    if not raw['root'].script_dir or not (projectpath/raw['root'].script_dir).exists():
        _logger.warning('script_dir may be missing or unreachable')
    else:
        script_root = projectpath/raw['root'].script_dir

    for c_id, command_def in raw.items():
        if not command_def.help and c_id != 'root':
            _logger.warning(f'command {c_id} may be missing help text')
        if command_def.script:
            if script_root:
                if not (
                    script_root/f'{command_def.script}.py'
                ).exists():
                    _logger.warning(
                        f'script "{command_def.script}" defined on '
                        f'command "{c_id}" not found'
                    )
            else:
                _logger.warning(f'script defined on "{c_id}" but no script dir defined')

# exit code wrapper
# validation partially happens deep in the guts of sigil,
# this caputures all validation logs, counts and converts to exit code
def validate_project(projectroot):
    package_name = __name__.split('.', 1)[0]
    with capture_package_warnings(package_name) as collector:
        try:
            _validate_project(projectroot)
        except SystemExit:  # special case to not hard exit
            pass

    errors = [r for r in collector.warnings if r.levelno >= logging.ERROR]
    warnings = [r for r in collector.warnings if r.levelno == logging.WARNING]

    for rec in collector.warnings:
        print(f"{rec.levelname}: {rec.getMessage()}", file=sys.stderr)

    error_count = len(errors)
    warning_count = len(warnings)

    if error_count > 0:
        print(
            f'Validation failed with {error_count} error(s) '
            f'and {warning_count} warning(s).',
            file=sys.stderr
        )
        sys.exit(2)
    elif warning_count > 0:
        print(
            f"Validation had {warning_count} warning(s) (no errors).",
            file=sys.stderr
        )
        sys.exit(1)
    else:
        print("Validation passed successfully.", file=sys.stderr)
