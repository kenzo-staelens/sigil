# Changelog

## [1.4.2] - 27/07/2026

### Added

- Added support for relative imports in scripts previously not working.
- Added support for stateful datasource classes (type annotation)

### Fixed

- Added missing argcomplete markers in examples and `sigil init` project

## [1.4.1] - 25/07/2026

### Fixed

- Fixed a bug where datasource wasn't being respected and always reverted to yaml
- Fixed README referring to an old parameter name

## [1.4.0] - 24/07/2026

### Changed

- Refactored old YamlLoader into Parser and Datasources for better integration of future datasources.
  This way custom data sources no longer need to manually convert to internal representation.

## [1.3.0] - 24/07/2026

### Added

- Added proper exit codes and "exited with x errors and y warnings" to validator
- `sigil validate` now outputs a validation success message instead of silently exiting.
- Added an info level log message for `load: false` entries
- Added a `sigil tree` command to print out the overall command structure of a sigil.

### Changed

- Renamed `load_ignore` (default false) to `load` (default true) to have a more sensible name.
- Updated validation such that intentionally unloaded trees don't cause orphan warnings.
- Added exception handling to argparse instantiation such that malformed parameters
  still has partial availability instead of erroring.

### Fixed

- Fixed error handling for missing name parameters on commands, now logs and continues instead of raising an error.

## [1.2.0] - 22/07/2026

### Added

- `sigil validate` command to run basic validation on a sigil.
  Useful for catching schema errors early in development or CI
  without running the actual commands.
- `sigil --version` added.
- This changelog file, retroactively documenting all prior releases.
- Added a toggle for `parse_args`/`parse_known_args` (default `parse_args`)

### Fixed

- Several internal type annotations corrected for improved static analysis.
- Fixed missing keys in the json-schema.

### Changed

- Updated the README documentation.
- Improved logging for subcommands that are actively unloaded via
  `load_ignore: true`. A clear log message now indicates intentional skipping,
  reducing diagnostic guesswork.

## [1.1.1]

### Fixed

- `sigil init` no longer generates a YAML file with a leftover hardcoded name.

## [1.1.0]

### Added

- `sigil init` command that generates a minimal “Hello, World!” example script.
  Running `sigil init` scaffolds a working file
  to help new users get started immediately.

## [1.0.0]

### Added

- **Argument groups & mutex groups** – full support for
  `add_argument_group()` and `add_mutually_exclusive_group()`.
- **Primitive argument types** – arguments can now be declared using plain
  Python types (`str`, `int`, `float`, `bool`). The type converter is
  automatically inferred, removing the need to pass an explicit `type=`
  callable for common cases.
- **Extended parser configuration** – additional parser‑level options
  (`description`, `epilog`, `formatter_class`, `add_help`, etc.) are now
  exposed.

### Fixed

- `store_true` / `store_false` arguments no longer incorrectly have a
  `default` of `None`. The default now correctly defaults to the opposite
  boolean value, as in standard `argparse`.

## [0.1.0]

### Added

- Initial release.
- Supports basic argument definition, subparsers, and all built‑in actions
  (`store`, `store_const`, `store_true`, `store_false`, `append`,
  `append_const`, `count`, `help`, `version`, `extend`).
- *Not yet implemented:* automatic type inference (primitive types),
  argument groups, and mutex groups.
  