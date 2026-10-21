# for everyone's sanity: not to be confused with __init__
import argparse
import sys
from importlib.resources import files
from pathlib import Path

from .util import registers


def create_project(project_name: str, target_dir: str = "."):
    """Scaffold a new Sigil project."""
    base_path = Path(target_dir) / project_name
    yml_path = base_path / "yml"
    scripts_path = base_path / "scripts"

    if base_path.exists():
        print(f"project '{base_path}' already exists. aborting.")
        sys.exit(0)

    # 1. Create directories
    yml_path.mkdir(parents=True, exist_ok=False)
    scripts_path.mkdir(parents=True, exist_ok=False)

    bootstrap_info: list[tuple[Path, str, tuple]] = [
        (base_path, 'manifest.yml', (project_name,)),
        (base_path, 'main.py', ()),
        (yml_path, 'root.yml', (project_name,)),
        (scripts_path, 'root.py', ()),
    ]

    tpl = files("sigil.cli_tools.templates")
    for (_target_dir, target_file, fmt) in bootstrap_info:
        tpl_content = tpl.joinpath(target_file+'.tpl').read_text().format(*fmt)
        (_target_dir / target_file).write_text(tpl_content)

    print(f"Initialized new Sigil project in ./{project_name}")
    print("Next steps:")
    print(f"  cd {project_name}")
    print("  python main.py hello --help")
    print("  create an alias")

@registers('init', 'generate a minimal sigil')
def add_sigil_init(command: argparse.ArgumentParser):
    command.add_argument('name', help="project name to create")
    return lambda args: create_project(args.name)
