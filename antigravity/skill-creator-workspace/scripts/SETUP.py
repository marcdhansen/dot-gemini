#!/usr/bin/env python3
"""
Scripts sourced from Anthropic's skill-creator example.
Original location: /mnt/skills/examples/skill-creator/scripts/

These scripts require `claude -p` (Claude Code CLI) to run.
They are NOT usable from Claude.ai.

To use from Claude Code, either:
  a) Run from the Anthropic skill-creator directory directly:
       cd /mnt/skills/examples/skill-creator
       python -m scripts.run_loop --eval-set /path/to/trigger-evals.json ...

  b) Or copy the scripts here:
       cp /mnt/skills/examples/skill-creator/scripts/*.py \
          ~/.gemini/antigravity/skill-creator-workspace/scripts/
       cp /mnt/skills/examples/skill-creator/scripts/__init__.py \
          ~/.gemini/antigravity/skill-creator-workspace/scripts/

Scripts needed:
  - utils.py            (parse_skill_md helper)
  - run_eval.py         (trigger eval runner)
  - run_loop.py         (eval + improve loop)
  - improve_description.py  (description optimizer)
  - generate_report.py  (HTML report generator, needed by run_loop)
"""
