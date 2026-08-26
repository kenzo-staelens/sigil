import argparse

import pytest

from sigil.cli_tools.util import COMMAND_REGISTRY, REGISTER_CALLABLES


def test_cli_util(
    capsys: pytest.CaptureFixture
) -> None:
    parser = argparse.ArgumentParser(prog='sigil')
    parser.add_argument('--version', action='version', version='Sigil x.x.x')
    sub = parser.add_subparsers(title="subcommands", dest='command')

    assert len(REGISTER_CALLABLES) == 3
    for fn in REGISTER_CALLABLES:
        fn(sub)

    with pytest.raises(SystemExit):
        # argparse raises on -h :/
        parser.parse_args(['-h'])

    # # Act & Assert: should not raise or exit
    captured = capsys.readouterr().out.strip()
    print('xxx',captured)
    for k in COMMAND_REGISTRY.keys():
        assert k in captured
