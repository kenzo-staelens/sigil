# Sigil

> Declarative argparse, without the CLI boilerplate.

Sigil is a lightweight, declarative CLI framework for Python. Define your command tree in YAML (or any other format),
and sigil builds the `argparse` parser on the fly. Complete with subcommands and dynamic script loading.  
It plays nicely with `argcomplete` out of the box.

[![PyPI Version](https://img.shields.io/pypi/v/sigil-cli)](https://pypi.python.org/pypi/sigil-cli)
[![PyPI Wheel](https://img.shields.io/pypi/wheel/sigil-cli.svg)](https://pypi.org/project/sigil-cli/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/sigil-cli)](https://pepy.tech/project/sigil-cli)
[![Tests](https://github.com/kenzo-staelens/sigil/actions/workflows/tests.yml/badge.svg)](https://github.com/kenzo-staelens/sigil/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/kenzo-staelens/sigil/badge.svg?branch=main)](https://coveralls.io/github/kenzo-staelens/sigil?branch=main)

<div align="center">
  <sub>in production since April 2026</sub>
</div>

---

## Features

- Declarative command hierarchies (parents, subparsers, defaults)
- Each command can point to a dynamically imported Python script
- `argcomplete` integration for tab‑completion
- Pluggable data sources - YAML is the default, but JSON, a dict or custom datasource are trivial to swap in
- No boilerplate argparse code in your main logic

## The alternatives

[Click](https://click.palletsprojects.com/) and [Typer](https://typer.tiangolo.com/) define commands in Python
(decorators, type hints). Sigil
defines the command tree as data (YAML by default; JSON or a dict work
too, or whatever datasource you decide to wire up), and each command points to a script module loaded by name.

**Consider Sigil when** you have many subcommands, the tree changes more
often than the logic, you want it generated or merged from several files
or you want to stay on the standard library's argparse without the boilerplate.
Arguments map 1:1 to argparse `add_argument` kwargs, so there's no new API
to learn, and `sigil validate` / `sigil tree` help you check the config.

**Stick with Click or Typer when** you have a small app, want type-hint
driven arguments (`type:` here only supports Python builtins), or need their
ecosystem and plugins.

## Quick Start

### Install

```bash
pip install sigil-cli
```

*optionally include argcomplete with `sigil-cli[completion]`*

The `init` command generates a project directory with a sample configuration and entrypoint:

```bash
sigil init demo
sigil validate demo/ # optional, should not output anything for correct configurations
cd demo
python main.py --help
```

For a full walkthrough with custom commands and arguments, see steps 0-4 below.

### 0. Recommended file structure

```text
project_root/
├── mycli.py              # drop‑in bootstrap script (alias this)
├── manifest.yml          # lists all YAML config files to load
├── yml/                  
│   ├── root.yml          # root command definition
│   ├── root_run.yml      # subcommand definition(s)
│   └── ...               
└── scripts/              
    ├── run.py            # implements the 'run' command
    └── ...               # other scripts
```

> [!Important]
> Don't shoot yourself in the foot, don't symlink the bootstrap script.
> if using a venv remember to use/alias the right python runtime

### 1. Entry script

Create `mycli.py`:

```python
#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
from pathlib import Path
from sigil import run_from_config

if __name__ == "__main__":
    run_from_config(Path(__file__).parent)
```

### 2. Configuration files

List all your YAML definitions in `manifest.yml`:

```yaml
- root.yml
- root_run.yml
```

Define the root command in `root.yml`:

```yaml
root:
  name: mycli
  script_dir: scripts
```

Define a subcommand in `root_run.yml`:

```yaml
root_run:
  name: run
  parent: root
  help: command utility to run containers
  script: run
  args:
    - help: port to run, autoincrements from 8080
      name:
        - -p
        - --port
```

### 3. Write the script

Create `scripts/run.py`:

```python
import argparse
from typing import Any

def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:
    port = getattr(args, "port", 8080)
    port = find_next_free_port_logic(port)
    print(f"Running container on port {port}")
```

### 4. Run it

```bash
chmod +x mycli.py
./mycli.py run --port 9000
# Running container on port 9000

./mycli.py run
# Running container on port 8080

./mycli.py run
# Running container on port 8081
```

## Configuration Reference

### Root Command

| Field | Description |
| --- | --- |
| `name` | Program name (used as `prog` in argparse) |
| `script_dir` | Directory (relative to the config root) where command scripts are located |

> [!NOTE]
> this section contains only sigil-specific configurations, other argparse arguments still apply

### Command

| Field | Description |
| --- | --- |
| `name` | Subcommand name |
| `parent` | Parent command (must exist elsewhere in a config) |
| `help` | Help text for this subcommand |
| `script` | Python module name (without `.py`) inside `script_dir`, absolute paths supported |
| `args` | List of argument definitions (see below) |
| `default` | If `True`, this subcommand is used when no subcommand is given |
| `load` | If `False` skips this command (or top level object) from being loaded into the command tree (default `True`) |
| `requirements` | (Optional) List of pip requirements that this subcommand requires. |
| any other parser kwarg | except for `dest`, `parents` and `formatter_class` they are all supported |

> [!NOTE]
> this section contains only sigil-specific configurations, other argparse arguments still apply
<!---->
> [!IMPORTANT]
> `parent` does not refer to argparse's `parents` parameter but is only used to resolve the parser tree.
> Parser (multi-)inheritance isn't supported but can be (rougly) emulated by
> adding arguments to `parent` commands in the tree.

### Argument

Each argument entry can be a plain dict which maps 1-to-1 with argparse `add_argument`, except name which maps its `*args`

```yaml
- name: ["-p", "--port"]   # or a single string, e.g. "positional"
  required: false
  default: 8069
  help: "port number"
```

Groups and mutex groups are also supported via the "kind" parameter (defaults to `argument`)

```yaml
# mutex group
- kind: mutex
  args:
    - <any recursive args/group/mutex construct here>
    ...
  ... # any valid mutex group arguments go here

- kind: group
  ...  # same
```

The `name` field can be `--flag` for flags or a string for positional arguments.
Both literal string and list of strings are supported.

Types (`type:`) only support Python builtins

### Script files

Each script file must define a `def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None` method.

Args is the namespace supplied by argparse (parsed with parse_known_args). Any additional args can be found in `ctx['other_args']`.

Scripts run in sequence from command -> subcommand -> sub sub command -> ... and each may add to,
remove or otherwise modify `args` and `ctx` to enrich or modify the behaviour of subsequent scripts.

## Sigil CLI Commands

`sigil` ships with its own lightweight toolbelt to manage your projects:

| Command | Purpose |
| --- | --- |
| `sigil init [project_name]` | Creates a new project folder with a sample ready-to-run Python entrypoint. |
| `sigil validate [project_path, default '.']` | Checks your sigil definition for schema errors and missing references. Run this after heavy edits to catch mistakes early. |
| `sigil tree [project_path, default '.']` | Print the command structure of a sigil. |
| `sigil requirements [project_path, default '.']` | Generate a requirements.txt file from active subcommands in the sigil. |

> [!NOTE]
> Your generated CLI (the one you build with Sigil) is completely separate from the `sigil` management
> commands above. You alias and run `main.py`. The `sigil` prefix is a different namespace.

### Misc

`load: False` may be used to detach commands from the command tree for any purpose
(deprecation, development, etc) or for non schema-compliant objects at the top level of a file. This may be useful to
define anchors or references that should not directly be read as a command.

## Tab‑Completion (argcomplete)

Sigil registers itself with `argcomplete` automatically if available on your system.  
To enable completion, install [argcomplete](https://github.com/kislyuk/argcomplete) and activate it for your entry
script (or use the builtin argcomplete comment):

```bash
pip install argcomplete
activate-global-python-argcomplete
```

Then run your script and hit <kbd>Tab</kbd> - subcommands and flags will complete.

## Pluggable Backends

Sigil uses YAML by default, but you can supply any datasource whose output can be converted into `ParserConfig`:

```python
from sigil import run_from_config
from pathlib import Path

# Use JSON instead:
class JsonReader:
    def read_manifest(self, root_path: Path, target: str) -> list | None:
        # read target paths for loading configuration
        ...
    
    def read_configuration(self, root_path: Path, target: str) -> dict | None:
        # read *.json, parse, convert to dict of raw data
        ...


run_from_config("/path/to/config", datasource=JsonReader)
```

You can also pass a pre‑loaded dictionary directly by wrapping it:

```python
# exact dictreader implementation deliberately omitted
run_from_config(my_dict, datasource=DictReader)
```
