from argparse import _StoreTrueAction

import pytest

from sigil import Argument, ArgumentGroup, Builder, LibArgParser, ParserConfig


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


def test_argument_group_factory():
    """Test that ArgumentGroup.factory creates groups with
    correct mutex flag and passes kwargs."""
    # Normal group
    group = ArgumentGroup.factory(
        kind='group',
        args=[{'name': '--foo'}, {'name': '--bar'}],
        title='my group',
        description='some description'
    )
    assert group.mutex is False
    assert len(group.args) == 2
    assert group.kw.get('title') == 'my group'
    assert group.kw.get('description') == 'some description'

    # Mutually exclusive group
    mutex = ArgumentGroup.factory(
        kind='mutex',
        args=[{'name': '--baz'}, {'name': '--qux'}],
        required=True
    )
    assert mutex.mutex is True
    assert len(mutex.args) == 2
    assert mutex.kw.get('required') is True


def test_builder_attach_argument_group():
    """Test attaching a normal argument group to a parser."""
    parser = LibArgParser(prog='test')
    group_def = ArgumentGroup.factory(
        kind='group',
        args=[
            {'name': '--foo', 'help': 'foo help', 'action': 'store_true'},
            {'name': '--bar', 'type': 'int'}
        ],
        title='test group'
    )
    Builder.attach_argumentgroup(parser, group_def)
    # Find our group by title
    group_actions = [g for g in parser._action_groups if g.title == 'test group']
    assert len(group_actions) == 1
    group = group_actions[0]
    actions = group._group_actions
    assert len(actions) == 2
    assert any(a.dest == 'foo' for a in actions)
    assert any(a.dest == 'bar' for a in actions)

    # Parsing should work normally
    args = parser.parse_args(['--foo', '--bar', '42'])
    assert args.foo is True   # store_true default
    assert args.bar == 42


def test_builder_attach_argument_mutex_group():
    """Test attaching a mutually exclusive group and verifying mutual exclusion."""
    parser = LibArgParser(prog='test')
    mutex_def = ArgumentGroup.factory(
        kind='mutex',
        args=[
            {'name': '--foo', 'action': 'store_true'},
            {'name': '--bar', 'action': 'store_true'}
        ],
        required=True
    )
    Builder.attach_argumentgroup(parser, mutex_def)

    # There should be one mutually exclusive group in the parser
    assert len(parser._mutually_exclusive_groups) == 1
    group = parser._mutually_exclusive_groups[0]
    actions = group._group_actions
    assert len(actions) == 2
    assert any(a.dest == 'foo' for a in actions)
    assert any(a.dest == 'bar' for a in actions)

    # Providing both should raise SystemExit (argparse error)
    with pytest.raises(SystemExit):
        parser.parse_args(['--foo', '--bar'])

    # Providing one works
    args = parser.parse_args(['--foo'])
    assert args.foo is True
    assert args.bar is False

    # Providing none also fails because required=True
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_builder_build_with_group_in_command_args(resolved_config):
    """Test that the builder correctly processes a command that
    has an ArgumentGroup in its args."""
    # We'll extend the resolved_config fixture by adding a
    # group to one of the subcommands.
    # But we can also build a new config from scratch for clarity.
    from sigil.models import ParserConfig

    root = ParserConfig.factory(
        name='mycli',
        script_dir='scripts'
    )
    group_def = ArgumentGroup.factory(
        kind='group',
        args=[{'name': '--opt1'}, {'name': '--opt2'}],
        title='my options'
    )
    sub = ParserConfig.factory(
        name='sub',
        parent='root',
        args=[group_def]   # pass the group as an argument
    )
    root.subparsers = {'sub': sub}

    parser = Builder.build(root)
    # Parse with subcommand and group options
    args = parser.parse_args(['sub', '--opt1', 'value'])

    assert args.opt1 == 'value'
    assert args.opt2 is None   # default absent

    # get our subparser handle
    subparser = parser._subparsers._group_actions[0]._name_parser_map['sub']

    # Verify that the group appears in the help text (optional)
    help_output = subparser.format_help()
    assert 'my options' in help_output
    assert '--opt1' in help_output
    assert '--opt2' in help_output
