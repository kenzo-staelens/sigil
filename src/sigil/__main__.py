import argparse

from sigil import __version__
from sigil.cli_tools.util import COMMAND_REGISTRY, REGISTER_CALLABLES
from sigil.datasource import REAL_SOURCES


def main():
    parser = argparse.ArgumentParser(prog='sigil')
    parser.add_argument('--version', action='version', version=f'Sigil {__version__}')
    parser.add_argument(
        '--datasource',
        default='YmlSource' if 'YmlSource' in REAL_SOURCES else 'JSONSource',
        choices=REAL_SOURCES.keys(),
        help='datasource for sigil tools, default to YmlSource or JSONSource'
    )
    sub = parser.add_subparsers(title="subcommands", dest='command')
    for fn in REGISTER_CALLABLES:
        fn(sub)

    args = parser.parse_args()
    if args.command not in COMMAND_REGISTRY:
        parser.parse_args(['-h'])
        return
    COMMAND_REGISTRY[args.command](args)


if __name__ == "__main__":
    main()
