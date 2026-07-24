import logging
import sys

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

        if 'root' not in raw_config:
            _logger.critical('missing root definition, aborting.')
            sys.exit(1)

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

                if not parent or parent not in resolved:
                    continue

                # only attach if we can
                changed = True
                if config_item.load:
                    # only actually attach if loaded
                    # so we can still warn on actual orphans
                    # while ignoring intentionally disabled objects
                    subparsers = resolved[parent].subparsers
                    subparsers[config_item.name]= config_item
                    resolved[parent].subparsers = subparsers
                else:
                    _logger.info(f"{internal_id} marked as unloaded, ignoring tree")
                    # no continue as we still need to register the key
                    # such that it's children don't cause warnings
                resolved[internal_id] = config_item

        # log unattached items:
        for item in (raw_config.keys() - resolved.keys()):
            _logger.warning(f'Command {item} may be orphaned')

        return resolved['root']  # one "root" is required
