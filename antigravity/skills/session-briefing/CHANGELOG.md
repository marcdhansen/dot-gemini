# Changelog

All notable changes to this skill are documented here.

A **breaking change** is any modification that causes the agent to behave
differently on previously-working queries: renaming the skill, removing or
substantially changing trigger phrases, or restructuring instructions in a way
that invalidates existing behaviour.


## [1.2.0] - 2026-03-16

### Changed
- Renamed skill from `initialization-briefing` to `session-briefing` to reduce routing collisions

## [1.1.0] - 2026-03-15

### Changed
- Added compatibility field to frontmatter
- Added metadata block (author, version, category, tags)
- Added negative trigger to description
- Migrated Gemini-specific fields into metadata block

## [1.0.0] - Initial release

### Added
- Initial skill implementation
