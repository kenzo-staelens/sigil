
from pathlib import Path

import pytest

from sigil.cli_tools.init import create_project


def test_create_project_success(tmp_path: Path):
    """Test that create_project scaffolds all expected files and directories."""
    project_name = "testproject"
    target_dir = str(tmp_path)

    # Run the function
    create_project(project_name, target_dir)

    # Check base directory exists
    base_path = tmp_path / project_name
    assert base_path.exists()
    assert base_path.is_dir()

    # Check directories
    yml_path = base_path / "yml"
    scripts_path = base_path / "scripts"
    assert yml_path.exists()
    assert yml_path.is_dir()
    assert scripts_path.exists()
    assert scripts_path.is_dir()

    # Check files exist
    assert (base_path / "manifest.yml").exists()
    assert (base_path / "main.py").exists()
    assert (yml_path / "root.yml").exists()
    assert (scripts_path / "root.py").exists()

    # Check root.yml contains the project name
    root_yml = (yml_path / "root.yml").read_text()
    assert "name: testproject" in root_yml
    assert "--shout" in root_yml
    assert "--verbose" in root_yml

    # Check root.py contains the run function
    root_py = (scripts_path / "root.py").read_text()
    assert "def run(args: argparse.Namespace, ctx: dict[str, Any]) -> None:" in root_py
    assert "message = f'hello {args.name}!'" in root_py

def test_create_project_already_exists(tmp_path: Path):
    """Test that create_project exits with error if project already exists."""
    project_name = "existing"
    target_dir = str(tmp_path)

    # Create the directory first
    (tmp_path / project_name).mkdir()

    # Should exit with SystemExit
    with pytest.raises(SystemExit) as exc_info:
        create_project(project_name, target_dir)
    assert exc_info.value.code == 0

def test_create_project_nested_path(tmp_path: Path):
    """Test that create_project handles nested target paths correctly."""
    project_name = "mycli"
    nested_target = tmp_path / "deep" / "nest"

    create_project(project_name, str(nested_target))

    base_path = nested_target / project_name
    assert (base_path / "manifest.yml").exists()
    assert (base_path / "yml" / "root.yml").exists()
    assert (base_path / "scripts" / "root.py").exists()
