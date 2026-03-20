# Changelog

All notable changes to skill-evaluator are documented here.

A **breaking change** is any modification that causes the agent to behave
differently on previously-working queries: renaming the skill, removing or
substantially changing trigger phrases, or restructuring instructions in a way
that invalidates existing behaviour.

## [1.1.0] - 2026-03-17

### Added
- Workflow E: Post-Use Retrospective (Roses/Buds/Thorns)
  - Applies RBT framework to each skill used in a session
  - Classifies findings by failure mode (triggering, output quality,
    progressive disclosure, missing, structural)
  - Converts Thorns and significant Buds into beads issue proposals
  - Full beads issue template with failure mode, proposed fix, and evals needed
  - Enforces the rule: never patch a skill directly from a retrospective;
    all changes go through the full SOP via beads issues
- Updated description to include post-use retrospective use case
- Updated Environment Quick Reference to include Workflow E row
- Added Example 4 (post-session retrospective with planning/tdd/finalization)
- Added note explaining Workflow E as the "immune system" for the skill library

## [1.0.1] - 2026-03-16

### Fixed
- Workflow B Step 1: added explicit instruction to ask for the target skill's
  path if the user hasn't provided it. Previously the step said "Read the target
  skill's SKILL.md" with no fallback for when the path was absent — caught by
  eval-3 (run-existing-evals) during inline grading of this skill itself.

## [1.0.0] - 2026-03-16

### Added
- Initial release
- Workflow A: design eval suite (evals.json + trigger-evals.json)
- Workflow B: run output quality evals inline (any environment)
- Workflow C: run triggering evals (Claude Code / Cowork)
- Workflow D: TDD baseline loop
- references/schemas.md: eval, grading, trigger-results, baseline-summary formats
- references/run-commands.md: exact commands for run_eval.py and run_loop.py
