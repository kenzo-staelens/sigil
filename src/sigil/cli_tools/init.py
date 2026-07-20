# for everyone's sanity: not to be confused with __init__

import sys
from pathlib import Path

# initial file contents
MANIFEST="""- yml/root.yml
"""

BOOTSTRAP = """#!/usr/bin/env python3
from pathlib import Path

from sigil import run_from_config

if __name__ == "__main__":
    run_from_config(Path(__file__).parent)
"""

YML_ROOT = """
root:
  name: testproject
  script: root
  script_dir: scripts
  args:
    - name: name
      help: your name
    - name: --shout
      action: store_true
      help: Increase volume
    - name:
        - --verbose
        - -v
      action: store_true
      help: increase verbosity
""".lstrip()

SCRIPT_ROOT = """
import argparse
from typing import Any


def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    message = f'hello {args.name}!'
    if args.shout:
        message = message.upper()

    print(message)

    if args.verbose:
        print("[DEBUG] Verbose mode enabled")
""".lstrip()

def create_project(project_name: str, target_dir: str = "."):
    """Scaffold a new Sigil project."""
    base_path = Path(target_dir) / project_name
    yml_path = base_path / "yml"
    scripts_path = base_path / "scripts"

    if base_path.exists():
        print(f"project '{base_path}' already exists. aborting.")
        sys.exit()

    # 1. Create directories
    yml_path.mkdir(parents=True, exist_ok=False)
    scripts_path.mkdir(parents=True, exist_ok=False)

    (base_path / "manifest.yml").write_text(MANIFEST)
    (base_path / "main.py").write_text(BOOTSTRAP)
    (yml_path / "root.yml").write_text(YML_ROOT.format(project_name))
    (scripts_path / "root.py").write_text(SCRIPT_ROOT)

    print(f"Initialized new Sigil project in ./{project_name}")
    print("Next steps:")
    print(f"  cd {project_name}")
    print("  python main.py hello --help")
    print("  create an alias")
