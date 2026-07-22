import argparse

from sigil import __version__
from sigil.cli_tools.init import create_project
from sigil.cli_tools.validate import validate_project


def main():
    # let's not start self hosting here
    parser = argparse.ArgumentParser(prog='sigil')
    parser.add_argument('--version', action='version', version=f'Sigil {__version__}')
    sub = parser.add_subparsers(title="subcommands", dest='command')

    init = sub.add_parser(name="init", help="generate a minimal sigil")
    init.add_argument('name', help="project name to create")

    validate = sub.add_parser(name="validate", help="validate structure of a sigil")
    validate.add_argument('path', help="project to validate")

    args = parser.parse_args()

    if args.command == 'init':
        create_project(args.name)
        return
    if args.command == 'validate':
        validate_project(args.path)
        return

if __name__ == "__main__":
    main()
