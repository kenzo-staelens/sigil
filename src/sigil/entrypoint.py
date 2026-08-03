from pathlib import Path
from typing import Any

from .datasource import DataSource, YmlSource
from .script_sources import FilesystemScriptSource, ScriptSource
from .stages import Builder, Parser, Resolver, ScriptLoader


# default to yamlloader, use whatever datastore you feel like
def run_from_config(
        config_root: str | Path,
        datasource: DataSource | type[DataSource] = YmlSource,
        manifest_target='manifest.yml',
        script_source: ScriptSource=FilesystemScriptSource  # also default to FS scripts
    ) -> None:
    raw_data = Parser(datasource).load(config_root, manifest_target)
    resolved = Resolver.resolve_inheritance(raw_data)
    # parser beyond here is an argparser
    parser = Builder.build(resolved)

    execution_context = {}

    if resolved.known_args:
        args, other_args = parser.parse_known_args()
        execution_context: dict[str, Any] = {'other_args': other_args}
    else:
        args = parser.parse_args()


    scriptloader = ScriptLoader(config_root, resolved.script_dir, script_source)
    scripts = scriptloader.get_scripts(args, 'root', parser, {'root': resolved})
    scriptloader.run_scripts(scripts, args, execution_context)
