import argparse

# because setting default subommands is kind of a pain in std. argparse

class LibArgParser(argparse.ArgumentParser):
    def set_default_subparser(self, name, args=None, positional_args=0):
        for action in self._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            if name in action._name_parser_map.keys():
                action.default=name
