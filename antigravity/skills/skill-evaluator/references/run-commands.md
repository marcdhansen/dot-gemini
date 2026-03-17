# Run Commands — Triggering Evals (Claude Code / Cowork)

These commands require `claude -p` from the Claude Code CLI.
They will NOT work in Claude.ai.

The scripts live in the Anthropic skill-creator example:
`/mnt/skills/examples/skill-creator/scripts/`

---

## Quick start: run triggering evals against a skill

```bash
cd /mnt/skills/examples/skill-creator

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

Compare `baseline/trigger-baseline.json` vs `candidate/trigger-results.json`.
Accept the change only if `summary.passed` is >= the baseline value.

---

## Optimize the description automatically

Use this when triggering evals are failing and manual tweaks aren't working.

```bash
cd /mnt/skills/examples/skill-creator

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

The loop:
1. Evaluates the current description on train (60%) + test (40%) split
2. Calls Claude to propose an improved description based on failures
3. Evaluates the new description, repeats up to max-iterations
4. Returns `best_description` selected by **test** score (not train — avoids overfitting)
5. Writes an HTML report you can open in the browser

Take the `best_description` from the JSON output and update the `description:`
field in the skill's SKILL.md frontmatter.

---

## Skill-specific paths for skill-creator-workspace

```bash
# Baseline skill-making (current, before rewrite)
python -m scripts.run_eval \
  --eval-set ~/.gemini/antigravity/skill-creator-workspace/trigger-evals.json \
  --skill-path ~/.gemini/antigravity/skills/skill-making \
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
