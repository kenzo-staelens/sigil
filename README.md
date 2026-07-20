# Sigil

> Declarative argparse, without the CLI boilerplate.

Sigil is a lightweight, declarative CLI framework for Python. Define your command tree in YAML (or any other format), and sigil builds the `argparse` parser on the fly. Complete with subcommands and dynamic script loading.  
It plays nicely with `argcomplete` out of the box.

[![pypi](https://badge.fury.io/py/sigil-cli.svg)](https://pypi.python.org/pypi/sigil-cli)
[![PyPI Wheel](https://img.shields.io/pypi/wheel/sigil-cli.svg)](https://pypi.org/project/sigil-cli/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/sigil-cli)](https://pepy.tech/project/sigil-cli)
[![Tests](https://github.com/kenzo-staelens/sigil/actions/workflows/tests.yml/badge.svg)](https://github.com/kenzo-staelens/sigil/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/kenzo-staelens/sigil/badge.svg?branch=main)](https://coveralls.io/github/kenzo-staelens/sigil?branch=main)

---

## Features

- Declarative command hierarchies (parents, subparsers, defaults)
- Each command can point to a dynamically imported Python script
- `argcomplete` integration for tab‑completion
- Pluggable data sources – YAML is the default, but JSON, TOML, or a dict are trivial to swap in
- No boilerplate argparse code in your main logic

## Quick Start

### Install

```bash
pip install sigil-cli
```

or include argcomplete

```bash
pip install sigil-cli[completion]
```

### 0. Recommended file structure

```text
project_root/
├── mycli.py              # drop‑in entry script (alias this)
├── manifest.yml          # lists all YAML config files to load
├── yml/                  
│   ├── root.yml          # root command definition
│   ├── root_run.yml      # subcommand definition(s)
│   └── ...               
└── scripts/              
    ├── run.py            # implements the 'run' command
    └── ...               # other scripts
```

### 1. Entry script

Create `mycli.py`:

```python
#!/usr/bin/env python3
from pathlib import Path
from sigil import run_from_config

if __name__ == "__main__":
    run_from_config(Path(__file__).parent)
```

### 2. Configuration files

List all your YAML definitions in `manifest.yml`:

```yaml
---
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

### Root

| Field | Description |
| --- | --- |
| `name` | Program name (used as `prog` in argparse) |
| `script_dir` | Directory (relative to the config root) where command scripts are located |

### Command

| Field | Description |
| --- | --- |
| `name` | Subcommand name |
| `parent` | Parent command (must exist elsewhere in a config) |
| `help` | Help text for this subcommand |
| `script` | Python module name (without `.py`) inside `script_dir` or as absolute path |
| `args` | List of argument definitions (see below) |
| `default` | If `true`, this subcommand is used when no subcommand is given |
| any other parser kwarg | except for `dest` and `formatter_class` they are all supported |

Note that `parent` does not refer to argparse's parent parameter but is only used to resolve the parser tree. Parser (multi-)inheritance isn't supported but can be emulated by adding arguments to `this` command's parents in the tree.

### Argument

Each argument entry can be a plain dict which maps 1-to-1 with argparse `add_argument`, except name which maps it's `*args`

```yaml
- name: ["-p", "--port"]   # or a single string, e.g. "positional"
  required: false
  default: 8069
  help: "port number"
```

Groups and mutex groups are also suppored via the "kind" parameter (defaults to `argument`)

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

## Tab‑Completion (argcomplete)

Sigil registers itself with `argcomplete` automatically if available on your system.  
To enable completion, install [argcomplete](https://github.com/kislyuk/argcomplete) and activate it for your entry script:

```bash
pip install argcomplete
activate-global-python-argcomplete
```

Then run your script and hit <kbd>Tab</kbd> – subcommands and flags will complete.

## Pluggable Backends

Sigil uses yaml by default, but you can supply any loader that returns a `dict[str, ParserConfig]`:

```python
from sigil import run_from_config

# Use JSON instead:
class JsonReader:
    @classmethod
    def load(cls, config_root):
        # read *.json, parse, convert to dict of ParserConfig
        ...

run_from_config("/path/to/config", loader_class=JsonReader)
```

You can also pass a pre‑loaded dictionary directly by wrapping it:

```python
run_from_config(my_dict, loader_class=DictLoader)
```
