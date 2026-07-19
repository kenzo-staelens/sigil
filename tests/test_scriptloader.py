from unittest.mock import MagicMock, patch

from sigil import Builder, ScriptLoader


def test_script_loader_get_scripts(resolved_config):
    """Test that get_scripts returns the correct scripts."""
    # Build parser to get the Namespace
    parser = Builder.build(resolved_config)
    # Simulate args: mycli sub leaf (leaf has script leaf_script)
    args = parser.parse_args(["sub", "leaf"])

    # data structure: we have root as ParserConfig;
    # we need to pass as dict for recursive lookup
    data = {"root": resolved_config}
    scripts = ScriptLoader.get_scripts(args, "root", parser, data)

    # The leaf script should be found
    assert "leaf_script" in scripts
    assert len(scripts) == 2


def test_script_loader_import_module(tmp_path):
    """Test that import_module correctly loads a Python module from a file."""
    # Create a dummy script
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_file = script_dir / "my_script.py"
    script_file.write_text(
        "import argparse\n"
        "def run(args, ctx):\n"
        "    print('Hello')\n"
    )

    loader = ScriptLoader()
    module = loader.import_module(str(tmp_path), "scripts", "my_script")
    assert hasattr(module, "run")
    assert callable(module.run)


@patch("sigil.stages.script_loader.importlib.util")
def test_script_loader_import_module_mock(mock_importlib, tmp_path):
    """Test import_module with mocked importlib to avoid actual file I/O."""
    # We'll just verify it builds the correct path and calls spec_from_file_location
    loader = ScriptLoader()
    # We need to mock the spec and loader
    mock_spec = MagicMock()
    mock_importlib.spec_from_file_location.return_value = mock_spec
    mock_module = MagicMock()
    mock_importlib.module_from_spec.return_value = mock_module

    loader.import_module(str(tmp_path), "scripts", "my_script")

    mock_importlib.spec_from_file_location.assert_called_once_with(
        "my_script", str(tmp_path / "scripts" / "my_script.py")
    )
    mock_importlib.module_from_spec.assert_called_once_with(mock_spec)
    mock_spec.loader.exec_module.assert_called_once_with(mock_module)

