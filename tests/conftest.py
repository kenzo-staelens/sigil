import pytest
import yaml

from sigil import ParserConfig, Resolver


@pytest.fixture
def sample_manifest(tmp_path):
    """Create a minimal manifest and two YAML files in a temporary directory."""
    root_yml = {
        "root": {
            "name": "mycli",
            "script_dir": "scripts",
            "help": "root help",
        }
    }
    sub_yml = {
        "sub": {
            "name": "sub",
            "parent": "root",
            "help": "subcommand help",
            "script": "sub_script",
            "args": [{"name": "--flag", "action": "store_true"}],
        }
    }

    manifest_path = tmp_path / "manifest.yml"
    manifest_path.write_text("- root.yml\n- sub.yml\n")

    (tmp_path / "root.yml").write_text(yaml.dump(root_yml))
    (tmp_path / "sub.yml").write_text(yaml.dump(sub_yml))

    return tmp_path

@pytest.fixture
def raw_config_dict():
    """Return a raw configuration dict (not yet resolved) for testing Resolver."""
    root = ParserConfig.factory(
        name="mycli", script_dir="scripts", help="root help"
    )
    sub = ParserConfig.factory(
        name="sub", parent="root", help="sub help", script="sub_script"
    )
    leaf = ParserConfig.factory(
        name="leaf", parent="sub", help="leaf help", script="leaf_script"
    )
    return {"root": root, "sub": sub, "leaf": leaf}

@pytest.fixture
def resolved_config(raw_config_dict):
    """Return a resolved tree (after Resolver) for testing Builder and ScriptLoader."""
    resolver = Resolver()
    return resolver.resolve_inheritance(raw_config_dict)  # returns root
