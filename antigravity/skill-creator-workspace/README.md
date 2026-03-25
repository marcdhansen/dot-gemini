# skill-creator Eval Workspace

Two separate eval dimensions, tracked independently.

---

## Eval Type A — Output Quality (run inline in Claude.ai)

Tests: *Given a prompt, does the skill guide Claude to produce correct output?*

**Files:**
- `evals.json` — 5 test cases with assertions
- `baseline/eval-1-grading.json` through `baseline/eval-5-grading.json` — per-eval results
- `baseline/benchmark.json` — aggregate baseline

**Baseline results (skill-making@1.1.0):**

| Eval | Pass rate |
|------|-----------|
| 1 — new-skill-from-scratch | 0/6 (0%) |
| 2 — review-bad-skill | 1/6 (17%) |
| 3 — fix-under-triggering | 0/4 (0%) |
| 4 — scaffold-file-structure | 2/6 (33%) |
| 5 — non-interactive-eof-fix | 5/5 (100%) |
| **Overall** | **8/27 (30%)** |

**Gate:** Eval 5 must stay at 100%. Overall target ≥ 75% (20/27).

---

## Eval Type B — Triggering (requires Claude Code / `claude -p`)

Tests: *Given a prompt, does Claude even load the skill in the first place?*

**Files:**
- `trigger-evals.json` — 20 queries (10 should-trigger, 10 should-not-trigger)
- `scripts/` — Anthropic's run_eval.py, run_loop.py, improve_description.py, utils.py

**Manual baseline estimate for skill-making@1.1.0:**

Current description:
> "Comprehensive guidelines and patterns for creating robust, reliable skills that work in
> both interactive and non-interactive (CI/CD) environments. Use when building a new skill,
> debugging EOF or non-interactive failures in an existing skill, or reviewing a skill's
> design for robustness. Do NOT use as a general Python or software design reference."

Estimated triggering behaviour:
- Should-trigger (10 queries): ~4 will fire — catches "build a new skill", "review SKILL.md",
  "EOF crash in CI", maybe "improve an existing skill". Misses entirely: description field
  guidance, naming rules, over-triggering diagnosis, packaging, turning workflow into skill.
- Should-not-trigger (10 queries): ~3-4 false positives expected — "non-interactive shell",
  "CI/CD pipeline", "python project structure", "keyboard interrupts" all share keywords
  with the current description.
- Estimated precision: ~50%, recall: ~40%, accuracy: ~55%

**To run the actual triggering baseline from Claude Code:**

```bash
cd /Users/marchansen/.gemini/antigravity/skill-creator-workspace

# Baseline: measure current skill-making description
python -m scripts.run_eval \
  --eval-set trigger-evals.json \
  --skill-path ~/.gemini/antigravity/skills/skill-making \
  --runs-per-query 3 \
  --verbose \
  > baseline/trigger-baseline.json

# After writing the merged skill-creator, measure it:
python -m scripts.run_eval \
  --eval-set trigger-evals.json \
  --skill-path ~/.gemini/antigravity/skills/skill-creator \
  --runs-per-query 3 \
  --verbose \
  > candidate/trigger-results.json

# Or run the full optimization loop to find the best description:
python -m scripts.run_loop \
  --eval-set trigger-evals.json \
  --skill-path ~/.gemini/antigravity/skills/skill-creator \
  --model claude-sonnet-4-6 \
  --max-iterations 5 \
  --verbose
```

**Gate:** Merged skill-creator must improve on the baseline trigger accuracy.
Eval 5 (non-interactive-eof-fix) must still trigger — don't lose that use case.

---

## Acceptance criteria summary

| Dimension | Baseline | Gate |
|-----------|----------|------|
| Output quality — eval 5 (non-interactive) | 100% | Must not regress |
| Output quality — overall | 30% (8/27) | ≥ 75% (20/27) |
| Triggering — recall (should-trigger) | ~40% est. | > 70% |
| Triggering — precision (no false positives) | ~50% est. | > 80% |
