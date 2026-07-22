import sys
from unittest.mock import patch

import pytest
import yaml

from sigil import (
    Argument,
    Builder,
    LibArgParser,
    ParserConfig,
    ScriptLoader,
    run_from_config,
)


def test_integration_run_from_config_with_capsys(tmp_path, capsys):
    """Test run_from_config and capture output."""
    # Same setup as above
    manifest = tmp_path / "manifest.yml"
    manifest.write_text("- root.yml\n- hello.yml\n")

    root_data = {"root": {"name": "hello", "script_dir": "scripts"}}
    (tmp_path / "root.yml").write_text(yaml.dump(root_data))

    hello_data = {
        "hello_cmd": {
            "name": "hello",
            "parent": "root",
            "script": "hello",
            "args": [{"name": "--name", "default": "world"}],
        }
    }
    (tmp_path / "hello.yml").write_text(yaml.dump(hello_data))

    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_file = script_dir / "hello.py"
    script_file.write_text(
        "import argparse\n"
        "def run(args, ctx):\n"
        "    print(f'Hello, {args.name}!')\n"
    )

    with patch.object(sys, "argv", ["prog", "hello", "--name", "Sigil"]):
        run_from_config(str(tmp_path))

    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, Sigil!"

def test_integration_run_from_config_with_unknown_args(tmp_path, capsys):
    """Test run_from_config and capture output."""
    # Same setup as above
    manifest = tmp_path / "manifest.yml"
    manifest.write_text("- root.yml\n- hello.yml\n")

    root_data = {
        "root":
            {
                "name": "hello",
                "script_dir": "scripts",
                "known_args": False,
            }
        }
    (tmp_path / "root.yml").write_text(yaml.dump(root_data))

    hello_data = {
        "hello_cmd": {
            "name": "hello",
            "parent": "root",
            "script": "hello",
            "args": [{"name": "--name", "default": "world"}],
        }
    }
    (tmp_path / "hello.yml").write_text(yaml.dump(hello_data))

    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_file = script_dir / "hello.py"
    script_file.write_text(
        "import argparse\n"
        "def run(args, ctx):\n"
        "    print(ctx['other_args'])\n"
    )

    with patch.object(sys, "argv", ["prog", "hello", "--name", "Sigil", "--unknown"]):
        with pytest.raises(SystemExit):
            run_from_config(str(tmp_path))
        root_data['root']['known_args'] = True
        (tmp_path / "root.yml").write_text(yaml.dump(root_data))

        run_from_config(str(tmp_path))

    captured = capsys.readouterr()
    assert captured.out.strip() == "['--unknown']"

def test_builder_required_args():
    """Test that positional args are marked required."""
    parser = LibArgParser()
    arg = Argument.factory(name="positional", required=False) # type: ignore that's what kwargs is
    Builder.attach_argument(parser, arg)

    # Required positional arguments have required=True by argparse
    # required False should be ignored
    action = next(a for a in parser._actions if a.dest == "positional")
    assert action.required is True


def test_script_loader_no_subcommand(capsys):
    """Test that when no subcommand is given, help is printed and sys.exit is called."""
    # Build a parser with a subparser
    root = ParserConfig.factory(
        name="mycli",
        subparsers={"foo": ParserConfig.factory(name="foo", script="foo")},
    )
    parser = Builder.build(root)
    data = {"root": root}
    args = parser.parse_args([])  # no subcommand
    # get_scripts will print help and sys.exit
    with pytest.raises(SystemExit):
        ScriptLoader.get_scripts(args, "root", parser, data)
    captured = capsys.readouterr()
    assert "usage:" in captured.out or "usage:" in captured.err
