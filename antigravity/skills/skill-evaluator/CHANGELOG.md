# Changelog

All notable changes to skill-evaluator are documented here.

A **breaking change** is any modification that causes the agent to behave
differently on previously-working queries: renaming the skill, removing or
substantially changing trigger phrases, or restructuring instructions in a way
that invalidates existing behaviour.

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
