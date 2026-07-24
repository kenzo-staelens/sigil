import yaml

from sigil import ParserConfig, YamlReader
from sigil.models.command import UNSUPPORTED_KWARGS


def test_yaml_reader_load(tmp_path, sample_manifest):
    """Test that YamlReader.load reads all YAML files and converts args."""
    config_root = sample_manifest
    loaded = YamlReader.load(config_root)

    assert "root" in loaded
    assert "sub" in loaded

    root = loaded["root"]
    sub = loaded["sub"]

    assert isinstance(root, ParserConfig)
    assert root.name == "mycli"
    assert root.script_dir == "scripts"

    assert isinstance(sub, ParserConfig)
    assert sub.name == "sub"
    assert sub.parent == "root"
    assert sub.script == "sub_script"
    assert len(sub.args) == 1
    assert sub.args[0].name == ["--flag"]
    assert sub.args[0].kw['action'] == "store_true"


def test_yaml_reader_duplicate_warning(caplog, tmp_path):
    """Test that duplicate keys trigger a warning and the later file overrides."""
    manifest = tmp_path / "manifest.yml"
    manifest.write_text("- a.yml\n- b.yml\n")

    a_data = {"cmd": {"name": "cmd", "help": "from a"}}
    b_data = {"cmd": {"name": "cmd", "help": "from b"}}  # same key

    (tmp_path / "a.yml").write_text(yaml.dump(a_data))
    (tmp_path / "b.yml").write_text(yaml.dump(b_data))

    with caplog.at_level("WARNING"):
        loaded = YamlReader.load(tmp_path)

    assert "[cmd] already defined" in caplog.text
    assert loaded["cmd"].help == "from a"  # first wins


def test_yaml_reader_invalid_arg(caplog, tmp_path):
    """Test that invalid argument definitions are skipped."""
    manifest = tmp_path / "manifest.yml"
    manifest.write_text("- cmd.yml\n")

    cmd_data = {
        "cmd": {
            "name": "cmd",
            "args": [
                {"name": "valid", "help": "ok"},
                {"invalid": "no name field"},  # invalid
            ],
        }
    }
    (tmp_path / "cmd.yml").write_text(yaml.dump(cmd_data))

    with caplog.at_level("ERROR"):
        loaded = YamlReader.load(tmp_path)

    assert "invalid argument definition" in caplog.text
    assert len(loaded["cmd"].args) == 1
    assert loaded["cmd"].args[0].name == ["valid"]

def test_invalid_parser(caplog, tmp_path):
    manifest = tmp_path / "manifest.yml"
    manifest.write_text("- cmd.yml\n")

    cmd_data = {
        "cmd": {
            "name": "cmd",
            "dest":"not_supported",
            "formatter_class": "not_supported",
            "parents": "not_supported",

        }
    }
    (tmp_path / "cmd.yml").write_text(yaml.dump(cmd_data))

    with caplog.at_level("WARNING"):
        YamlReader.load(tmp_path)

    for kw in UNSUPPORTED_KWARGS:
        assert f"'{kw}' unsupported" in caplog.text
