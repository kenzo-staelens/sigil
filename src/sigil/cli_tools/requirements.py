
import argparse
import os

from sigil import Parser

from .util import get_datasource, registers


def resolve_requirements(projectroot, datasource_name='YmlSource'):
    datasource = get_datasource(datasource_name)
    raw = Parser(datasource).load(projectroot)
    reqs_list = []
    for key, parsed_data in raw.items():
        if not parsed_data.load:
            continue  # not loaded -> skip
        if not parsed_data.requirements:
            continue # nothing of value
        if not isinstance(parsed_data.requirements, list):
            print(
                f'requirements for {parsed_data.name}[{key}]'
                ' not in list format, ignoring...'
            )
            continue # invalid format
        reqs_list += ['',f'# {key}']
        reqs_list += parsed_data.requirements
    return '\n'.join(reqs_list).strip()

@registers('requirements', 'build requirements.txt from a sigil.')
def add_sigil_requirements(command: argparse.ArgumentParser):
    command.add_argument(
        'path',
        help="target project, default '.'",
        nargs='?',
        default='.'
    )
    command.add_argument(
        '--outfile',
        '-o',
        help="outfile",
        default='requirements.txt',
    )
    def _(args: argparse.Namespace):
        overwrite='y'
        if os.path.exists(args.outfile):
            overwrite = input(
                f'{args.outfile} already exists, overwrite? [y/n]: ',
            ).lower()
        if overwrite not in {'y', 'yes'}:
            print('aborting')
            return
        reqs = resolve_requirements(args.path, args.datasource)
        if not reqs:
            print('no requirements detected, aborting.')
            return
        with open(args.outfile, 'w') as f:
            f.write(reqs)
    return _
