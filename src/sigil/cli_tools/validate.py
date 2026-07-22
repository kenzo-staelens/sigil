import logging
import sys
from pathlib import Path

from sigil import Builder, Resolver, YamlReader

_logger = logging.getLogger(__name__)

def validate_project(projectroot):
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
