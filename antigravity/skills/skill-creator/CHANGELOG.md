# Changelog

All notable changes to skill-creator are documented here.

A **breaking change** is any modification that causes the agent to behave
differently on previously-working queries: renaming the skill, removing or
substantially changing trigger phrases, or restructuring instructions in a way
that invalidates existing behaviour.

## [1.0.0] - 2026-03-16

### Added
- Initial release — merges skill-making (gemini), coleam00/skill-creator,
  and Anthropic's canonical skill-creator
- Workflow A: TDD-first skill creation (design evals before drafting)
- Workflow B: structured skill review with spec checklist
- Workflow C: triggering diagnosis (under- and over-triggering)
- Workflow D: update existing skill with baseline-first discipline
- references/spec.md: merged quality checklist, frontmatter rules,
  progressive disclosure table, common violations
- references/non-interactive-patterns.md: CI-safe Python patterns
  (ported from skill-making; moved to Level 3 reference)
- scripts/create_skill.py: scaffold generator — fixed from skill-making:
  now uses kebab-case (not snake_case), generates YAML frontmatter,
  adds CHANGELOG.md, creates evals/ stubs, removes README inside folder
- skill-evaluator referenced as the canonical eval tool at Workflow A Step 3
  and Workflow D

### Changed (vs skill-making@1.1.0)
- Renamed skill-making → skill-creator (kebab-case, clearer scope)
- create_skill.py: folder/name now kebab-case (was snake_case)
- create_skill.py: SKILL.md now includes YAML frontmatter (was body-only)
- create_skill.py: creates CHANGELOG.md (was missing)
- create_skill.py: creates evals/ stubs (new)
- create_skill.py: no longer creates README.md inside skill folder (spec violation)
- Non-interactive Python patterns moved from SKILL.md body to references/
  (progressive disclosure — was inline, now Level 3)
