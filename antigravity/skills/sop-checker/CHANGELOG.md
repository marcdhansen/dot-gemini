# Changelog

All notable changes to this skill are documented here.

A **breaking change** is any modification that causes the agent to behave
differently on previously-working queries: renaming the skill, removing or
substantially changing trigger phrases, or restructuring instructions in a way
that invalidates existing behaviour.


## [1.2.0] - 2026-03-16

### Changed
- Renamed skill from `orchestrator` to `sop-checker` to reduce routing collisions

## [1.1.0] - 2026-03-15

### Changed
- Renamed folder from Orchestrator to orchestrator (kebab-case compliance)
- Fixed name field from "Orchestrator" to "orchestrator"
- Added compatibility, metadata, and negative trigger to frontmatter
- Migrated disable-model-invocation and allowed-tools into metadata block

## [1.0.0] - Initial release

### Added
- Initial skill implementation
