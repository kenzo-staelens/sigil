import argparse
from pathlib import Path

import pytest

from sigil.cli_tools.tree import display_project, parser_tree


def test_parser_tree_with_subcommands(
    tmp_path: Path,
    capsys: pytest.CaptureFixture
) -> None:
    """Test that validate_project exits when multiple subcommands have default: true."""
    project_root = tmp_path / "mycli"
    project_root.mkdir()

    manifest = project_root / "manifest.yml"
    manifest.write_text("""
- root.yml
- foo.yml
- bar.yml
""")

    root_yml = project_root / "root.yml"
    root_yml.write_text("""
root:
  name: mycli
  script_dir: scripts
""")

    foo_yml = project_root / "foo.yml"
    foo_yml.write_text("""
foo:
  name: foo
  parent: root

foo_sub1:
  name: leaf1
  parent: foo

foo_sub2:
  name: leaf2
  parent: foo
""")

    bar_yml = project_root / "bar.yml"
    bar_yml.write_text("""
bar:
  name: bar
  parent: root

bar_sub1:
  name: leaf3
  parent: bar

bar_sub2:
  name: leaf4
  parent: bar
""")
    display_project(project_root)

    excpected_tree = """
mycli
├── bar
│   ├── leaf3
│   └── leaf4
└── foo
    ├── leaf1
    └── leaf2
""".strip()
    captured = capsys.readouterr().out.strip()
    assert captured == excpected_tree


def test_parser_tree_empty_parser():
    """Test that parser_tree handles a parser with no subcommands gracefully."""
    parser = argparse.ArgumentParser(prog="empty")
    tree = parser_tree(parser)
    # Only the root line should be present (no subcommands)
    assert tree == "empty\n"
