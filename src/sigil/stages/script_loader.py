import logging
import sys
from argparse import Namespace
from pathlib import Path

from sigil.models import LibArgParser, ParserConfig
from sigil.script_sources import ScriptSource

_logger = logging.getLogger(__name__)

class ScriptLoader:
    def __init__(
        self,
        config_root: Path,
        script_dir: str | None,
        script_source: ScriptSource | type[ScriptSource]
    ):
        self.config_root = config_root
        self.script_dir = script_dir
        if isinstance(script_source, type):
            script_source = script_source()
        self.script_source = script_source

    def _get_next_parser_name(cls, args: Namespace, target: str, parser: ParserConfig):
        # get the name of the next subcommand
        if target != 'root':
            # normal case a subcommand just points to the next arg
            next_value = getattr(args, target)
        else:
            # root is a special case because the top level parser
            # is required to be called root (id, not name parameter)
            # therefore root needs to grab the next part by name instead
            next_value = getattr(args, parser.name)
        return next_value

    def get_scripts(
        cls,
        args: Namespace,
        target: str,
        root_parser: LibArgParser,
        data: dict[str, ParserConfig]
    ) -> list[str]:
        found_scripts = []

        target_parser: ParserConfig = data[target]
        subparsers = target_parser.subparsers
        script = target_parser.script

        if script:
            found_scripts.append(script)
        if not subparsers:
            # nothing to keep exploring anymore -> early exit
            return found_scripts

        next_value = cls._get_next_parser_name(args, target, target_parser)

        if next_value is None:
            # if subcommands exist but no subcommand is used print help instead
            root_parser.parse_args(sys.argv[1:] + ['--help'])
            sys.exit(2) # nothing to do here

        return found_scripts + cls.get_scripts(
            args,
            next_value,
            root_parser,
            subparsers,
        )

    def run_scripts(self, script_targets, namespace, context):
        for script in script_targets:
            try:
                module = self.script_source.import_module(
                    self.config_root,
                    self.script_dir,
                    script
                )
                if not module:
                    continue
            except Exception as e:
                # prevent your subcommand from turning your environment
                # into undefined soup by not continuing execution
                _logger.critical(f'failed to load script "{script}"\n  {e}')
                sys.exit(2)
            module.run(namespace, context)
