import logging
from pathlib import Path

import pytest

from sigil.cli_tools.validate import validate_project


def test_validate_project_success(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that validate_project succeeds with a valid project structure."""
    # Arrange: create a minimal valid project
    project_root = tmp_path / "mycli"
    project_root.mkdir()

    manifest = project_root / "manifest.yml"
    manifest.write_text("- root.yml\n")

    root_yml = project_root / "root.yml"
    root_yml.write_text("""
root:
  name: mycli
  script_dir: scripts
""")

    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "root.py").touch()

    # Act & Assert: should not raise or exit
    with caplog.at_level(logging.WARNING):
        validate_project(project_root)

    # No warnings or errors should be logged
    assert not caplog.records

def test_validate_project_missing_manifest( tmp_path: Path) -> None:
    """Test that validate_project exits with code 1 when manifest.yml is missing."""
    project_root = tmp_path / "mycli"
    project_root.mkdir()

    with pytest.raises(SystemExit) as exc_info:
        validate_project(project_root)

    assert exc_info.value.code == 1

def test_validate_project_missing_root_key(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture
) -> None:
    """Test that validate_project logs an error and exits when
    'root' key is missing."""
    project_root = tmp_path / "mycli"
    project_root.mkdir()

    manifest = project_root / "manifest.yml"
    manifest.write_text("- root.yml\n")

    root_yml = project_root / "root.yml"
    root_yml.write_text("""
not_root:
  name: mycli
""")

    with pytest.raises(SystemExit) as exc_info:
        with caplog.at_level(logging.ERROR):
            validate_project(project_root)

    assert exc_info.value.code == 2
    assert "missing required root command" in caplog.text

def test_validate_project_missing_script_dir(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture) -> None:
    """Test that validate_project logs a warning when script_dir is missing."""
    project_root = tmp_path / "mycli"
    project_root.mkdir()

    manifest = project_root / "manifest.yml"
    manifest.write_text("- root.yml\n")

    root_yml = project_root / "root.yml"
    root_yml.write_text("""
root:
  name: mycli
  script_dir: scripts
""")

    # Do NOT create scripts/ directory

    with caplog.at_level(logging.WARNING):
        validate_project(project_root)

    assert "script_dir may be missing or unreachable" in caplog.text

def test_validate_project_missing_help_text(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture
) -> None:
    """Test that validate_project logs a warning for commands missing help text."""
    project_root = tmp_path / "mycli"
    project_root.mkdir()

    manifest = project_root / "manifest.yml"
    manifest.write_text("""
- root.yml
- greet.yml
""")

    root_yml = project_root / "root.yml"
    root_yml.write_text("""
root:
  name: mycli
  script_dir: scripts
""")

    greet_yml = project_root / "greet.yml"
    greet_yml.write_text("""
greet:
  # No help field
  name: greet
  script: greet
""")

    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "root.py").touch()
    (scripts_dir / "greet.py").touch()

    with caplog.at_level(logging.WARNING):
        validate_project(project_root)

    assert "command greet may be missing help text" in caplog.text

def test_validate_project_missing_script_file(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture
) -> None:
    """Test that validate_project logs a warning when
    a referenced script file is missing."""
    project_root = tmp_path / "mycli"
    project_root.mkdir()

    manifest = project_root / "manifest.yml"
    manifest.write_text("""
- root.yml
- greet.yml
""")

    root_yml = project_root / "root.yml"
    root_yml.write_text("""
root:
  name: mycli
  script_dir: scripts
""")

    greet_yml = project_root / "greet.yml"
    greet_yml.write_text("""
greet:
  help: Greet the user
  name: greet
  script: greet
""")

    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "root.py").touch()
    # Do NOT create greet.py

    with caplog.at_level(logging.WARNING):
        validate_project(project_root)

    assert 'script "greet" defined on command "greet" not found' in caplog.text

def test_validate_project_script_without_script_dir(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture
) -> None:
    """Test that validate_project logs a warning when a script
    is defined but script_dir is missing."""
    project_root = tmp_path / "mycli"
    project_root.mkdir()

    manifest = project_root / "manifest.yml"
    manifest.write_text("""
- root.yml
- greet.yml
""")

    root_yml = project_root / "root.yml"
    root_yml.write_text("""
root:
  name: mycli
  # No script_dir defined
""")

    greet_yml = project_root / "greet.yml"
    greet_yml.write_text("""
greet:
  help: Greet the user
  name: greet
  script: greet
""")

    # Do NOT create scripts/ directory

    with caplog.at_level(logging.WARNING):
        validate_project(project_root)

    assert 'script defined on "greet" but no script dir defined' in caplog.text

def test_validate_project_multiple_default_subcommands(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture
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
  help: Foo command
  default: true
  script: foo
""")

    bar_yml = project_root / "bar.yml"
    bar_yml.write_text("""
bar:
  name: bar
  parent: root
  help: Bar command
  default: true
  script: bar
""")

    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir()
    for cmd in ("root", "foo", "bar"):
        (scripts_dir / f"{cmd}.py").touch()

    validate_project(project_root)

    assert 'last default bar overridden with foo' in caplog.text
