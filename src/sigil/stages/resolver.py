import logging

from sigil.models import ParserConfig

_logger = logging.getLogger(__name__)

class Resolver:
    @classmethod
    def resolve_inheritance(
        cls,
        raw_config: dict[str, ParserConfig],
    ) -> ParserConfig:
        # build the tree starting at "root", then attack items until
        # items can no longer be attached
        # note that this dictionary contains *references* to every resolved
        # object, therefore editing an object at the root of this dictionary
        # also edits it at an arbitrary nested point (because thats how references work)
        # in the end we will just return "root"
        resolved: dict[str, ParserConfig] = {}
        changed = True

        while changed:
            changed = False # stays false unless something is attached
            for internal_id, config_item in raw_config.items():
                if internal_id in resolved: # already resolved, "del" is dangerous
                    continue

                if internal_id == 'root':
                    changed=True
                    resolved[internal_id] = config_item
                    break

                parent = config_item.parent

                if parent and parent in resolved:
                    changed = True # only run a new pass if something was attached
                    subparsers = resolved[parent].subparsers
                    subparsers[config_item.name]= config_item
                    resolved[parent].subparsers = subparsers
                    resolved[internal_id] = config_item

        # log unattached items:
        for item in (raw_config.keys() - resolved.keys()):
            _logger.warning(f'failed to resolve command path for {item}')

        return resolved['root']  # one "root" is required
