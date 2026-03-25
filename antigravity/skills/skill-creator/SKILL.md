---
name: skill-creator
description: Create new skills, review and improve existing skills, and diagnose triggering problems. Use when building a skill from scratch, turning a workflow into a reusable skill, reviewing a SKILL.md for spec violations, fixing a skill that loads at the wrong times, or iterating on a skill with test-driven discipline. Make sure to use this skill whenever the user mentions creating, editing, reviewing, packaging, or improving an agent skill, even if they don't use the word "skill" explicitly. Do NOT use for general Python coding, building MCP servers, writing documentation unrelated to skills, or testing non-skill software — use skill-evaluator for running evals on an existing skill.
compatibility: No network access required. create_skill.py scaffold in scripts/. Quality checklist in references/spec.md. Non-interactive Python patterns in references/non-interactive-patterns.md.
metadata:
  author: Workshop Team
  version: 1.0.0
  category: meta
  tags: [skill-authoring, skill-review, tdd, meta, triggering, scaffolding]
---

# Skill Creator

Creates, reviews, and improves agent skills. Applies a test-driven discipline:
design evals first, draft second, accept only changes that pass.

Pay attention to context cues about the user's familiarity with coding. Adjust
how you explain terms like "eval", "frontmatter", and "assertion" accordingly.
A plumber who just discovered Claude Code needs different language than a
senior engineer — but both deserve a great skill.

---

## Workflow A: Create a New Skill

### Step 1: Capture intent

If the current conversation already contains a workflow the user wants to
capture, extract from it first — tools used, step sequence, corrections made,
input/output formats. Confirm with the user before proceeding.

Otherwise, gather:
1. What should this skill enable Claude to do?
2. When should it trigger? (what phrases/contexts)
3. What's the expected output format?
4. What tools or external dependencies are needed?

### Step 2: Interview and research

Ask about edge cases, input/output formats, example files, success criteria,
and dependencies. Check available MCPs if they'd help research the domain.
Come prepared — reduce burden on the user.

### Step 3: Design evals first (TDD)

Before writing a single line of SKILL.md, use **skill-evaluator Workflow A** to
design the eval suite:
- Write 3–5 output quality evals (`evals/evals.json`)
- Write 18–24 triggering evals (`evals/trigger-evals.json`)
- Review with the user before proceeding

This baseline defines "done". Every iteration either moves the needle or gets
reverted. If skill-evaluator is not available, write the evals manually following
the same format — the discipline matters more than the tool.

### Step 4: Draft the SKILL.md

Fill in these components:

**Frontmatter** — load `references/spec.md` for exact rules. Key points:
- `name`: kebab-case, matches folder name, no capitals/underscores
- `description`: WHAT + WHEN + at least one negative trigger. Make it slightly
  "pushy" — Claude has a natural tendency to undertrigger, so be explicit about
  edge cases and adjacent use cases you want to capture
- `metadata`: author, version, category, tags

**Body** — recommended sections:
- One-line overview
- `## When to Use` with bullet triggers and a "Do not use for:" sentence
- `## Instructions` with numbered, actionable steps (say what TO DO, not what to know)
- `## Examples` with at least 2 User/Response pairs
- `## Notes` for caveats and edge cases

Explain the *why* behind instructions rather than issuing heavy-handed MUSTs.
Today's models follow reasoning better than rigid rules.

For file-generating skills, add a pre-output checklist step.

**Progressive disclosure** — load `references/spec.md` for the full table. Short version:
- Keep SKILL.md body under 500 lines
- Large tables, API schemas, lookup data → `references/`
- Reference files clearly from the body with guidance on when to read them

To scaffold the directory structure, run:
```bash
python ~/.gemini/antigravity/skills/skill-creator/scripts/create_skill.py \
  "skill-name" "Brief description" --category utility
```

### Step 5: Run evals and iterate

Run **skill-evaluator Workflow B** (output quality, inline) immediately after
drafting. Don't wait — early failures are cheap. Then:

1. Present results to the user
2. Improve the skill based on feedback — generalise from failures, don't overfit
3. Re-run evals; accept only if pass rate improves and nothing regresses
4. When output quality is solid, hand off `trigger-evals.json` for Claude Code

Keep the prompt lean. If a section isn't pulling its weight, cut it.

### Step 6: Self-review before presenting

Load `references/spec.md` and run the full quality checklist. Fix anything that
fails before showing the user. Don't present a skill with known spec violations.

---

## Workflow B: Review an Existing Skill

Load `references/spec.md`, then evaluate the skill against each checklist item.

Produce a structured report:

```
## Skill Review: [skill-name]

### Critical issues (will break loading or cause spec violations)
- [issue] → [fix]

### Quality issues (will cause under/over-triggering or poor output)
- [issue] → [fix]

### Progressive disclosure issues (content in wrong level)
- [issue] → [fix]

### Suggestions (optional improvements)
- [suggestion]

### Verdict
[Ready to ship / Needs fixes / Major rework required]
```

---

## Workflow C: Diagnose Triggering Problems

**Under-triggering** (skill doesn't load when it should):

1. Ask for 3 example queries that should have triggered but didn't
2. Compare against the `description` field word by word
3. Identify missing keywords or user-intent phrases
4. Suggest concrete additions — and produce a revised description draft
5. Remember: descriptions should focus on the user's *intent*, not the skill's
   *implementation*. "Help me write a commit message" not "formats conventional commits"

**Over-triggering** (skill loads when it shouldn't):

1. Ask for 3 example queries that incorrectly loaded the skill
2. Identify which part of the description matched those queries
3. Add negative trigger phrases ("Do NOT use for...")
4. Narrow scope with more specific phrasing

For either case: don't fix a triggering problem by rewriting the skill body —
fix the `description` field. The two failure modes have different causes.

In Claude Code/Cowork: use `run_loop.py` to optimise the description
automatically. See `references/non-interactive-patterns.md` for the commands.

---

## Workflow D: Update an Existing Skill

Before touching anything: use **skill-evaluator Workflow D** (TDD baseline loop).
Baseline both eval types first. Accept only changes that improve scores without
regressing anything that was already passing.

When packaging or installing:
- Preserve the original `name` field and folder name exactly
- If the skill path is read-only, copy to `/tmp/skill-name/` before editing
- Use `scripts/package_skill.py` from the Anthropic skill-creator to produce a `.skill` file

---

## Platform Notes

### Claude.ai
- Workflows A–D all work
- Run evals inline with skill-evaluator (Workflow B)
- Triggering evals and `run_loop.py` require Claude Code — hand off the
  `trigger-evals.json` file and commands from skill-evaluator's `references/run-commands.md`
- No subagents: run test cases one at a time, present results inline

### Claude Code / Cowork
- Full workflow available including subagent test runs and description optimisation
- After iterating to satisfaction, always run `run_loop.py` to verify the
  description before shipping
- Generate the eval viewer with `generate_review.py` so the user can review
  outputs before you make changes — do this BEFORE evaluating yourself
- For packaging: `python -m scripts.package_skill <path/to/skill>`

---

## Examples

### Example 1: New skill from a workflow

User: "We just figured out how to triage Kubernetes pod crashes together. Turn this into a skill."

1. Extract intent from conversation: what was done, tools used, key decision points
2. Confirm scope with user: "Should this also handle node-level issues or just pods?"
3. Design evals first — write 3 crash-log triage prompts with expectations
4. Scaffold: `create_skill.py "pod-crash-triage" "Triage Kubernetes pod crash logs"`
5. Draft SKILL.md following the conversation's actual workflow
6. Run evals inline; iterate once; hand off triggering evals for Claude Code

### Example 2: Review a SKILL.md

User: "Can you review this?" (pastes SKILL.md with `name: My_SQLHelper`)

1. Load references/spec.md
2. Immediate critical flag: underscore and capital in name
3. Check description — vague? missing negative trigger? no user-intent phrases?
4. Check instructions — numbered? actionable? or vague ("handle errors appropriately")?
5. Produce structured report with verdict

### Example 3: Fix under-triggering

User: "My recipe skill never loads for meal planning queries."

1. Check trigger-evals.json — design one if missing, focused on the gap
2. Current description: "Finds and adapts recipes for dietary restrictions"
3. Missing phrases: "meal planning", "what to cook this week", "weekly meals"
4. Produce revised description draft that covers the user's actual intent
5. Note: in Claude Code, run `run_loop.py` to find the best description empirically

---

## Notes

- The `description` field is the single most important thing to get right. A
  great skill that never triggers is invisible. A mediocre description wastes
  every invocation.
- Explain the *why* behind instructions. Lean instructions with clear reasoning
  outperform long instructions with rigid rules.
- If you find yourself writing ALWAYS or NEVER in all caps, that's a yellow flag —
  try explaining the reason instead so the model understands the intent.
- The most common spec violation is an underscore in the skill name or folder.
  Check this first on every review.
- If a skill has no evals yet, Workflow A (design evals) must come before
  Workflow D (iterate). You can't baseline what you haven't defined.
