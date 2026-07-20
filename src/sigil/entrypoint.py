from typing import Any

from .stages import Builder, Resolver, ScriptLoader, YamlReader


# default to yamlloader, use whatever datastore you feel like
def run_from_config(config_root: str, loader_class = YamlReader):
    raw_data = loader_class.load(config_root)
    resolved = Resolver.resolve_inheritance(raw_data)
    parser = Builder.build(resolved)
    args, other_args = parser.parse_known_args()
    scripts = ScriptLoader.get_scripts(args, 'root', parser, {'root': resolved})

    execution_context: dict[str, Any] = {'other_args': other_args}
    for script in scripts:
        try:
            module = ScriptLoader.import_module(
                config_root,
                resolved.script_dir,
                script
            )
        except FileNotFoundError as e:
            print(f'failed to load script "{script}"\n  {e}')
            return
        module.run(args, execution_context)
