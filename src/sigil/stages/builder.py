from sigil.models import Argument, ArgumentGroup, LibArgParser, ParserConfig

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
                argparser = argparse_group.add_parser(
                    subcommand.name,
                    help=subcommand.help,
                    **subcommand.parser_kwargs,
                )
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
        argument_config: Argument | ArgumentGroup
    ) -> None:
        if isinstance(argument_config, ArgumentGroup):
            cls.attach_argumentgroup(parser, argument_config)
            return

        conditional_args: dict[str, Any] = {}
        if any(x.startswith('-') for x in argument_config.name):
            # if no '--name' or '-n' exists it's required by default
            conditional_args['required']=argument_config.required

        parser.add_argument(
            *argument_config.name,
            help=argument_config.help,
            action=argument_config.action,
            **(argument_config.kw | conditional_args)
        )

    @classmethod
    def attach_argumentgroup(
        cls,
        parser: LibArgParser,
        argument_config: ArgumentGroup
    ):
        if argument_config.mutex:
            group_method = parser.add_mutually_exclusive_group
        else:
            group_method = parser.add_argument_group
        grp = group_method(**argument_config.kw)
        for arg in argument_config.args:
            # for all intents and purposes in attach_argument(group)
            # a group has the same interface used in these methods
            # as a parser has; we can thus assume group is a parser
            cls.attach_argument(grp, arg)

    @classmethod
    def build(
        cls,
        root_data: ParserConfig
    ) -> LibArgParser:
        root_parser = LibArgParser(
            root_data.name,
            **root_data.parser_kwargs,
        )
        for arg in root_data.args or []:
            cls.attach_argument(root_parser, arg)

        cls._build_subparsers(root_parser, root_data)
        if USE_ARGCOMPLETE:
            argcomplete.autocomplete(root_parser)

        return root_parser
