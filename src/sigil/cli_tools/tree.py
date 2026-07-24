import argparse

from sigil import Builder, Resolver, YamlReader


# adapted from https://stackoverflow.com/questions/78166654/how-can-i-print-the-tree-structure-of-subparsers-of-an-argparse-parser-in-python/78246362#78246362
def parser_tree(
        parser: argparse.ArgumentParser,
        start: str = "",
        down: str = "│   ",
        leaf: tuple = ("├── ", "└── ")
    ) -> str:
    out = f"{parser.prog or 'root'}\n" if not start else ""
    subparsers_actions = [
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]

    for subparsers_action in subparsers_actions:
        choices = list(subparsers_action.choices.items())
        for idx, (choice, subparser) in enumerate(choices):
            is_last = (idx == len(choices) - 1)
            # Prefix for this line: current indentation + branch symbol
            prefix = start + leaf[is_last]
            # Next indentation: if this is the last child, we stop vertical bars;
            # otherwise continue
            next_start = start + (down if not is_last else " " * len(down))
            # Recurse and append
            child_tree = parser_tree(subparser, next_start, down, leaf)
            out += prefix + choice + "\n"
            out += child_tree
    return out


def display_project(projectroot):
    raw = YamlReader.load(projectroot)
    resolved = Resolver.resolve_inheritance(raw)
    parser = Builder.build(resolved)
    print(parser_tree(parser))

