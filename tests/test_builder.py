from argparse import _StoreTrueAction

from sigil import Argument, Builder, LibArgParser, ParserConfig


def test_builder_attach_argument():
    """Test that arguments are attached correctly to a parser."""
    parser = LibArgParser()
    arg = Argument.factory(name="--verbose", action="store_true", help="verbose")
    Builder.attach_argument(parser, arg)

    actions = parser._actions
    verbose_action = next(a for a in actions if a.dest == "verbose")
    assert verbose_action.option_strings == ["--verbose"]
    assert verbose_action.help == "verbose"
    assert isinstance(verbose_action, _StoreTrueAction)


def test_builder_build_subparsers(resolved_config):
    """Test that subparsers are built with defaults."""
    builder = Builder()
    parser = builder.build(resolved_config)

    # Check root arguments (none here)
    # Check subcommand 'sub'
    sub_parser = parser._subparsers._group_actions[0]._name_parser_map["sub"]
    assert sub_parser.prog == "mycli sub"
    # Check subcommand 'leaf' inside sub
    leaf_parser = sub_parser._subparsers._group_actions[0]._name_parser_map["leaf"]
    assert leaf_parser.prog == "mycli sub leaf"

    # Test default subparser (we didn't set default, so none)
    # We can set default in config and test later


def test_builder_default_subparser():
    """Test that the default subparser is set correctly."""
    root = ParserConfig.factory(
        name="mycli",
        subparsers={
            "foo": ParserConfig.factory(name="foo", default=True),
            "bar": ParserConfig.factory(name="bar"),
        },
    )
    builder = Builder()
    parser = builder.build(root)

    # The default subparser should be 'foo'
    # We can test by parsing with no subcommand: it should fallback to foo
    args = parser.parse_args([])
    assert args.mycli == "foo"  # dest is the parent name


