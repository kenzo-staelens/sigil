# tests/test_requirements.py
import argparse
from pathlib import Path

import pytest

from sigil.cli_tools.requirements import add_sigil_requirements, resolve_requirements
from sigil.cli_tools.util import COMMAND_REGISTRY


def _handler_wrapper():
    if 'requirements' in COMMAND_REGISTRY:
        # return if already registered
        return COMMAND_REGISTRY['requirements']
    # otherwise make the dummy first
    parser = argparse.ArgumentParser(prog='test-sigil')
    sub = parser.add_subparsers(title="subcommands", dest='command')
    add_sigil_requirements(sub)
    return COMMAND_REGISTRY['requirements']

def _write_project(project_root: Path, extra: str = "") -> None:
    """Minimal valid Sigil project: root + optional extra commands."""
    (project_root / "manifest.yml").write_text("- all.yml\n")
    (project_root / "all.yml").write_text(
        "root:\n"
        "  name: mycli\n"
        "  script_dir: scripts\n"
        + extra
    )


def test_resolve_requirements_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "empty"
    project_root.mkdir()
    _write_project(project_root)

    assert resolve_requirements(project_root) == ""


def test_resolve_requirements_single(tmp_path: Path) -> None:
    project_root = tmp_path / "single"
    project_root.mkdir()
    _write_project(project_root, extra="""
foo:
  name: foo
  parent: root
  requirements:
    - requests
    - click
""")

    assert resolve_requirements(project_root) == "# foo\nrequests\nclick"


def test_resolve_requirements_multiple(tmp_path: Path) -> None:
    project_root = tmp_path / "multi"
    project_root.mkdir()
    _write_project(project_root, extra="""
foo:
  name: foo
  parent: root
  requirements:
    - requests

bar:
  name: bar
  parent: root
  requirements:
    - pyyaml
""")

    result = resolve_requirements(project_root)
    assert "# foo" in result
    assert "requests" in result
    assert "# bar" in result
    assert "pyyaml" in result
    assert result.count("#") == 2


def test_resolve_requirements_skips_unloaded(tmp_path: Path) -> None:
    project_root = tmp_path / "skip_unload"
    project_root.mkdir()
    _write_project(project_root, extra="""
unloaded:
  name: unloaded
  parent: root
  load: false
  requirements:
    - ignored

loaded:
  name: loaded
  parent: root
  requirements:
    - included
""")

    assert resolve_requirements(project_root) == "# loaded\nincluded"


def test_resolve_requirements_skips_invalid_format(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    project_root = tmp_path / "skip_invalid"
    project_root.mkdir()
    _write_project(project_root, extra="""
bad:
  name: bad
  parent: root
  requirements: not-a-list
""")

    assert resolve_requirements(project_root) == ""
    assert "not in list format" in capsys.readouterr().out

def test_handler_writes_requirements_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "writes_file"
    outfile = project_root / 'requirements.txt'
    project_root.mkdir()
    _write_project(project_root, extra="""
foo:
  name: foo
  parent: root
  requirements:
    - requests

bar:
  name: bar
  parent: root
  requirements:
    - pyyaml
""")
    monkeypatch.chdir(tmp_path)

    handler = _handler_wrapper()
    handler(argparse.Namespace(
        path=str(project_root),
        datasource="YmlSource",
        outfile=outfile
    ))
    assert outfile.read_text() == "# foo\nrequests\n\n# bar\npyyaml"

def test_handler_aborts_when_no_requirements(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    project_root = tmp_path / "no_reqs"
    outfile = project_root / 'requirements.txt'
    project_root.mkdir()
    _write_project(project_root)
    monkeypatch.chdir(tmp_path)

    handler = _handler_wrapper()
    handler(argparse.Namespace(
        path=str(project_root),
        datasource="YmlSource",
        outfile=outfile
    ))
    assert not outfile.exists()
    assert capsys.readouterr().out.strip() == "no requirements detected, aborting."


def test_handler_does_not_prompt_when_file_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "file_absent"
    outfile = project_root / 'requirements.txt'
    project_root.mkdir()
    _write_project(project_root, extra="""
foo:
  name: foo
  parent: root
  requirements:
    - requests
""")
    monkeypatch.chdir(tmp_path)

    def _boom(_):
        raise AssertionError("input() should not be called")

    monkeypatch.setattr("builtins.input", _boom)
    handler = _handler_wrapper()
    handler(argparse.Namespace(
        path=str(project_root),
        datasource="YmlSource",
        outfile=outfile
    ))
    assert outfile.read_text() == "# foo\nrequests"



def test_handler_prompt_no(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    project_root = tmp_path / "prompt_no"
    outfile = project_root / 'requirements.txt'
    project_root.mkdir()
    _write_project(project_root, extra="""
foo:
  name: foo
  parent: root
  requirements:
    - requests
""")
    monkeypatch.chdir(tmp_path)
    outfile.write_text("original")
    prompts = []
    monkeypatch.setattr(
        "builtins.input",
        lambda p: (prompts.append(p), "n")[1],
    )

    handler = _handler_wrapper()
    handler(argparse.Namespace(
                path=str(project_root),
                datasource="YmlSource",
                outfile=outfile
            ))

    assert prompts == [f"{outfile} already exists, overwrite? [y/n]: "]
    assert outfile.read_text() == "original"
    assert capsys.readouterr().out.strip() == "aborting"


def test_handler_prompt_yes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "prompt_yes"
    outfile = project_root / 'requirements.txt'
    project_root.mkdir()
    _write_project(project_root, extra="""
foo:
  name: foo
  parent: root
  requirements:
    - requests
""")
    monkeypatch.chdir(tmp_path)
    outfile.write_text("stale")
    monkeypatch.setattr("builtins.input", lambda _: "y")
    handler = _handler_wrapper()
    handler(argparse.Namespace(
        path=str(project_root),
        datasource="YmlSource",
        outfile=outfile
    ))
    assert outfile.read_text() == "# foo\nrequests"
