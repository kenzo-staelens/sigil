from sigil.models import Argument, LibArgParser, ParserConfig

try:
    import argcomplete
    USE_ARGCOMPLETE = True
except Exception:
    USE_ARGCOMPLETE=False
import logging
from typing import Any

_logger = logging.getLogger(__name__)

class Builder:
    # also in place modification, returning just causes more problems anyway
    @classmethod
    def _build_subparsers(
        cls,
        base_parser: LibArgParser,
        parser_data: ParserConfig
    ) -> None:
        if parser_data.subparsers:
            argparse_group = base_parser.add_subparsers(
                dest=parser_data.name,
                title='subcommands',
            )
            last_default = None  # find the last default
            for _, subcommand in parser_data.subparsers.items():
                subcommand_name = subcommand.name
                subcmd_help = subcommand.help
                argparser = argparse_group.add_parser(subcommand_name, help=subcmd_help)
                for arg in subcommand.args:
                    cls.attach_argument(argparser, arg)
                if subcommand.default:
                    if last_default:
                        _logger.warning(
                            f'last default {last_default} overridden '
                            f'with {subcommand.name}'
                        )
                    last_default = subcommand.name
                if subcommand.subparsers:
                    cls._build_subparsers(argparser, subcommand)
            if last_default:
                base_parser.set_default_subparser(last_default)

    @classmethod
    def attach_argument(
        cls,
        parser: LibArgParser,
        argument_config: Argument
    ) -> None:
        conditional_args: dict[str, Any] = {}
        if any(x.startswith('-') for x in argument_config.name):
            # if no '--name' or '-n' exists it's required by default
            conditional_args['required']=argument_config.required

        parser.add_argument(
            *argument_config.name,
            help=argument_config.help,
            action=argument_config.action,
            default=argument_config.default,
            **(argument_config.kw | conditional_args)
        )

    @classmethod
    def build(
        cls,
        root_data: ParserConfig
    ) -> LibArgParser:
        root_name = root_data.name
        root_parser = LibArgParser(prog=root_name)
        for arg in root_data.args or []:
            cls.attach_argument(root_parser, arg)

        cls._build_subparsers(root_parser, root_data)
        if USE_ARGCOMPLETE:
            argcomplete.autocomplete(root_parser)

        return root_parser
