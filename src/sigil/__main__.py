import argparse

from sigil.cli_tools.init import create_project
from sigil.cli_tools.validate import validate_project


def main():
    # let's not start self hosting here
    parser = argparse.ArgumentParser(prog='sigil')
    sub = parser.add_subparsers(title="subcommands", dest='command')
    init = sub.add_parser(name="init", help="generate a minimal sigil")
    validate = sub.add_parser(name="validate", help="validate structure of a sigil")
    init.add_argument('name', help="project name to create")
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
