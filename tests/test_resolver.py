from sigil import ParserConfig, Resolver


def test_resolver_build_tree(raw_config_dict):
    """Test that resolve_inheritance correctly attaches subparsers."""
    resolver = Resolver()
    root = resolver.resolve_inheritance(raw_config_dict)

    assert root.name == "mycli"
    assert "sub" in root.subparsers
    assert root.subparsers["sub"].parent == "root"
    assert "leaf" in root.subparsers["sub"].subparsers
    assert root.subparsers["sub"].subparsers["leaf"].parent == "sub"


def test_resolver_unattached_warning(caplog):
    """Test that unattached items produce a warning."""
    config = {
        "root": ParserConfig.factory(name="root"),
        "orphan": ParserConfig.factory(name="orphan", parent="nonexistent"),
    }
    resolver = Resolver()
    with caplog.at_level("WARNING"):
        root = resolver.resolve_inheritance(config)

    assert "may be orphaned" in caplog.text
    assert "orphan" not in root.subparsers

def test_yaml_reader_load_ignore(tmp_path):
    """Test that entries with load: False are skipped."""
    manifest = tmp_path / "manifest.yml"
    manifest.write_text("- ignored.yml\n- kept.yml\n")

    config = {
        "root": ParserConfig.factory(name="root"),
        "ignored": ParserConfig.factory(name="ignored", load=False, parent="root"),
        "kept": ParserConfig.factory(name="kept", parent="root"),
    }
    resolver = Resolver()
    resolved = resolver.resolve_inheritance(config)
    print(resolved)

    assert "kept" in resolved.subparsers
    assert "ignored" not in resolved.subparsers
