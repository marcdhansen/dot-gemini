# Run Commands — Triggering Evals (Claude Code / Cowork)

These commands require `claude -p` from the Claude Code CLI.
They will NOT work in a plain terminal session.

The scripts live in the Anthropic skill-creator example:
`~/GitHub/anthropics/skills/skills/skill-creator/scripts/`
(or `/mnt/skills/examples/skill-creator/scripts/` if mounted)

---

## Critical: Run from inside a Claude Code bash session

This is the most important thing to get right. `run_eval.py` works by:
1. Writing a temporary skill description into `.claude/commands/<uuid>.md`
2. Spawning `claude -p <query>` as a subprocess
3. Watching the stream for a `Skill` or `Read` tool call on that UUID

Step 3 only works if the `claude -p` subprocess inherits an **active Claude Code
session context** — that's what populates `available_skills` in the system prompt
and makes Claude aware of the injected command file. A standalone terminal session
has no such context, so skills are invisible and every query returns trigger_rate=0.0.

**Run the commands from Claude Code's bash tool, not from your terminal.**

You can verify the session context is working when you see trigger_rate > 0 for
at least some should-trigger queries. If everything is still 0.0 after seeding
the `.claude/` directory, the session context is missing.

---

## Seed the .claude/ directory (one-time setup)

The project root (the directory containing `.claude/`) must exist before running.
`find_project_root()` in `run_eval.py` walks up from `cwd` looking for `.claude/`.

```bash
mkdir -p ~/GitHub/anthropics/skills/.claude/commands
```

Run evals from `~/GitHub/anthropics/skills/skills/skill-creator` so `find_project_root()`
walks up and finds `~/GitHub/anthropics/skills/.claude/`.

---

## Quick start: run triggering evals against a skill

```bash
cd ~/GitHub/anthropics/skills/skills/skill-creator

python -m scripts.run_eval \
  --eval-set /path/to/evals/trigger-evals.json \
  --skill-path /path/to/your-skill \
  --runs-per-query 3 \
  --verbose \
  > /path/to/workspace/trigger-results.json
```

---

## Establish a baseline before making changes

```bash
# Step 1: baseline the current skill
python -m scripts.run_eval \
  --eval-set /path/to/evals/trigger-evals.json \
  --skill-path /path/to/your-skill \
  --runs-per-query 3 \
  --verbose \
  > /path/to/workspace/baseline/trigger-baseline.json

# Step 2: make your changes to the skill

# Step 3: measure the candidate
python -m scripts.run_eval \
  --eval-set /path/to/evals/trigger-evals.json \
  --skill-path /path/to/your-skill \
  --runs-per-query 3 \
  --verbose \
  > /path/to/workspace/candidate/trigger-results.json
```

Accept the change only if `summary.passed` >= the baseline value.

---

## Optimize the description automatically

Use this when triggering evals are failing and manual tweaks aren't working.
Requires `improve_description.py`, which calls `claude -p` as a subprocess —
this also requires Claude Code session context for the same reason as `run_eval.py`.

Note: if `improve_description.py` exits with `claude -p exited 1` and empty
stderr, it's a PATH issue — the subprocess can't find the `claude` binary.
Fix: run from inside Claude Code's bash tool so PATH is inherited correctly.

```bash
cd ~/GitHub/anthropics/skills/skills/skill-creator

python -m scripts.run_loop \
  --eval-set /path/to/evals/trigger-evals.json \
  --skill-path /path/to/your-skill \
  --model claude-sonnet-4-6 \
  --max-iterations 5 \
  --holdout 0.4 \
  --runs-per-query 3 \
  --verbose \
  --results-dir /path/to/workspace/description-optimization
```

The loop selects `best_description` by **test** score (not train — avoids
overfitting). Take that value and update the `description:` field in SKILL.md.

---

## Skill-specific paths for skill-creator-workspace

```bash
# Baseline skill-making (archived, before rewrite)
python -m scripts.run_eval \
  --eval-set ~/.gemini/antigravity/skill-creator-workspace/trigger-evals.json \
  --skill-path ~/.gemini/antigravity/skills/skill-making-archived \
  --runs-per-query 3 --verbose \
  > ~/.gemini/antigravity/skill-creator-workspace/baseline/trigger-baseline.json

# Candidate skill-creator (after rewrite)
python -m scripts.run_eval \
  --eval-set ~/.gemini/antigravity/skill-creator-workspace/trigger-evals.json \
  --skill-path ~/.gemini/antigravity/skills/skill-creator \
  --runs-per-query 3 --verbose \
  > ~/.gemini/antigravity/skill-creator-workspace/candidate/trigger-results.json

# Optimize skill-creator description if needed
python -m scripts.run_loop \
  --eval-set ~/.gemini/antigravity/skill-creator-workspace/trigger-evals.json \
  --skill-path ~/.gemini/antigravity/skills/skill-creator \
  --model claude-sonnet-4-6 \
  --max-iterations 5 --verbose
```

---

## Reading the results

Key fields in trigger-results.json:
- `summary.passed` / `summary.total` — headline score
- `results[].pass` — per-query verdict
- `results[].trigger_rate` — e.g. 0.67 means triggered 2 of 3 runs
- `results[].should_trigger` — what was expected

Calculate precision/recall yourself:
- TP = triggered AND should_trigger
- FP = triggered AND NOT should_trigger
- FN = NOT triggered AND should_trigger
- TN = NOT triggered AND NOT should_trigger
- Precision = TP / (TP + FP)
- Recall    = TP / (TP + FN)
- Accuracy  = (TP + TN) / total
