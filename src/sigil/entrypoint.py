import logging
import sys
from pathlib import Path
from typing import Any

from .datasource import DataSource, YmlSource
from .stages import Builder, Parser, Resolver, ScriptLoader

_logger = logging.getLogger(__name__)

# default to yamlloader, use whatever datastore you feel like
def run_from_config(
        config_root: str | Path,
        datasource: DataSource | type[DataSource] = YmlSource
    ) -> None:
    raw_data = Parser(datasource).load(config_root)
    resolved = Resolver.resolve_inheritance(raw_data)
    # parser beyond here is an argparser
    parser = Builder.build(resolved)

    execution_context = {}

    if resolved.known_args:
        args, other_args = parser.parse_known_args()
        execution_context: dict[str, Any] = {'other_args': other_args}
    else:
        args = parser.parse_args()

    scripts = ScriptLoader.get_scripts(args, 'root', parser, {'root': resolved})
    for script in scripts:
        try:
            module = ScriptLoader.import_module(
                config_root,
                resolved.script_dir,
                script
            )
            if not module:
                continue
        except FileNotFoundError as e:
            # prevent your subcommand from turning your environment
            # into undefined soup by not continuing execution
            _logger.critical(f'failed to load script "{script}"\n  {e}')
            sys.exit(2)
        module.run(args, execution_context)
