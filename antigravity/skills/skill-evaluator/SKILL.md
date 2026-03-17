---
name: skill-evaluator
description: Design and run evaluations for agent skills, covering both failure modes: triggering (does the agent load the skill for the right queries?) and output quality (does the loaded skill guide correct output?). Use when testing a new skill before shipping, establishing a baseline before modifying an existing skill, diagnosing why a skill triggers at the wrong times, or running an existing eval suite and reporting results. Enforces a TDD discipline: baseline first, change second, accept only improvements. Do NOT use for testing general Python code, REST APIs, CLI tools, or any software that is not an agent skill defined by a SKILL.md file.
compatibility: Output quality evals run inline in any environment. Triggering evals require the claude CLI (claude -p), available in Claude Code and Cowork only. Schemas in references/schemas.md. Run commands in references/run-commands.md.
metadata:
  author: Workshop Team
  version: 1.0.1
  category: meta
  tags: [skill-testing, eval, tdd, triggering, output-quality, baseline, meta]
---

# Skill Evaluator

Designs and runs two-dimensional evaluations for agent skills. Enforces a
baseline-first discipline so every change can be measured objectively.

## The Two Failure Modes

Every skill can fail in two independent ways. Both must be tested.

| Failure mode | The question | Tool |
|---|---|---|
| **Triggering** | Does the agent load the skill for the right queries? | trigger-evals.json + run_eval.py (Claude Code) |
| **Output quality** | Once loaded, does it guide correct output? | evals.json + inline grading or subagent |

A skill that triggers but produces bad output is useless.
A skill that produces great output but never loads is invisible.
Fix these failure modes separately — they have different causes and different fixes.

## When to Use

- Shipping a new skill: design the eval suite, establish a baseline, confirm both dimensions pass
- Modifying an existing skill: baseline BEFORE touching anything
- Diagnosing a triggering problem: skill doesn't load when it should, or loads when it shouldn't
- Running an existing eval suite: evals.json or trigger-evals.json already exist — run and report

**Do not use for**: testing Python modules, REST APIs, CLI tools, MCP servers,
or anything that does not have a SKILL.md. Use pytest or standard tooling for those.

---

## Workflow A: Design the Eval Suite

Use when evals.json or trigger-evals.json are missing or thin.

### Step 1: Read the skill

Read the target SKILL.md fully. Note what it does, what phrases should trigger it,
and what adjacent queries should NOT trigger it.

### Step 2: Write output quality evals (evals.json)

Write 3–5 prompts a real user would actually send. For each:
- Make the prompt concrete: include file names, column names, real context.
  Not "process this file" but "the CSV called Q4_final.csv has revenue in column C..."
- Write 3–6 expectations per eval. Each expectation must be hard to satisfy
  without doing the actual work — prefer content checks over existence checks.
- Avoid trivially-passing assertions (e.g. "a file was created" passes even for
  an empty file).

Save to `evals/evals.json` in the skill's workspace. Schema: `references/schemas.md`.

### Step 3: Write triggering evals (trigger-evals.json)

Write 18–24 queries split roughly 50/50 should-trigger / should-not-trigger.

**Should-trigger (9–12):** Different phrasings of the same intent — formal,
casual, abbreviated, indirect. Include edge cases and cases where this skill
competes with a neighbour skill.

**Should-not-trigger (9–12):** These are the most valuable. Write near-misses —
queries that share keywords but need something different. "Write unit tests for
my Python module" is a bad negative for skill-evaluator (too easy). "How do I
test my MCP server's tool responses?" is good — adjacent domain, genuine
ambiguity.

Rule of thumb: if a negative case wouldn't fool a human for a second, it won't
teach you anything.

Save to `evals/trigger-evals.json`. Schema: `references/schemas.md`.

### Step 4: Review with user before running

Show a summary of the eval cases. Ask the user to confirm or adjust.
Bad eval queries produce misleading results and waste iteration cycles.

---

## Workflow B: Run Output Quality Evals (inline — any environment)

Use when you have evals.json and no subagents.

### Step 1: Load the target skill

If the user has not provided a path to the target skill's SKILL.md, ask for it
before proceeding — you cannot grade output quality against a skill you haven't read.

Once you have the path, read it fully. You will simulate what an agent following
that skill would do.

### Step 2: Execute each eval inline

For each eval:
1. Follow the skill's instructions to complete the prompt
2. Produce or describe the output (for file-generating skills, describe content
   and structure in detail)
3. Keep a structured trace of steps taken

### Step 3: Grade against expectations

For each expectation:
- Cite specific evidence from your trace
- Mark PASS or FAIL — no partial credit
- Flag any expectation that seems too weak (would pass for clearly wrong output)

### Step 4: Report

Produce a summary including per-eval pass rates, overall pass rate, flagged weak
assertions, and concrete observations about where the skill's instructions caused
failures. Format per `references/schemas.md`.

**Inline grading caveat**: you authored or read the skill and are also running it,
so you have full context. Treat inline results as a fast-iteration signal, not a
definitive verdict. Claude Code subagent runs are more rigorous for final sign-off.

---

## Workflow C: Run Triggering Evals (Claude Code / Cowork only)

Load `references/run-commands.md` for exact commands.

Key things to know:
- `run_eval.py` injects the skill description as a `.claude/commands/` file,
  fires `claude -p` per query, and detects whether the agent reads that file
- Run each query 3× — triggering has variance; single runs are unreliable
- A trigger rate ≥ 2/3 counts as "triggered" (default threshold 0.5)
- Use `run_loop.py`'s 60/40 train/test split to avoid overfitting the description
- Select best description by **test** score, never train score

Report precision, recall, and accuracy. Highlight false negatives (should have
triggered, didn't) separately from false positives.

---

## Workflow D: TDD Baseline Loop

The core discipline for any skill change.

1. **Baseline first** — run both eval types on the current skill. Record scores.
   Do not skip this even when you're confident the change is safe.
2. **Change one thing at a time** — isolate changes so you know what moved the needle.
3. **Re-run both eval types** — compare to baseline.
4. **Accept only improvements** — if output quality regresses on any previously-passing
   eval, or triggering accuracy gets worse, revert. Partial improvements are OK only
   if they don't regress anything that was already passing.
5. **Promote the baseline** — once satisfied, the new version becomes the next baseline.

For description-field changes specifically: if triggering evals fail after a change,
use `run_loop.py` to optimize the description automatically rather than guessing.

---

## Environment Quick Reference

| Capability | Claude.ai | Claude Code / Cowork |
|---|---|---|
| Design eval suite | ✅ | ✅ |
| Run output quality evals | ✅ inline (manual) | ✅ via subagents |
| Run triggering evals | ❌ needs claude -p | ✅ run_eval.py |
| Optimize description automatically | ❌ | ✅ run_loop.py |
| HTML eval viewer | ❌ | ✅ generate_review.py |

---

## Examples

### Example 1: New skill, no evals yet

User: "I just finished writing log-analyzer. How do I test it before shipping?"

1. Read log-analyzer/SKILL.md
2. Run Workflow A — design both evals.json and trigger-evals.json
3. Present to user for review and adjust
4. Run Workflow B inline for output quality; report results
5. Hand off trigger-evals.json with run commands for Claude Code
6. Report both dimensions together and flag failures

### Example 2: About to modify an existing skill

User: "I want to rewrite the instructions section of my pdf skill"

1. Stop: "Let me establish a baseline first before we touch anything"
2. Check if evals.json exists — if not, run Workflow A
3. Run Workflow B to baseline output quality; record scores
4. Ask user to run triggering baseline from Claude Code (or estimate if unavailable)
5. Record baseline prominently and confirm before proceeding
6. After the change: re-run both, compare, accept only if no regressions

### Example 3: Triggering diagnosis

User: "My recipe-helper skill never loads for meal planning queries"

1. Check trigger-evals.json — if missing, design one focused on the problem area
2. Inspect the current description for missing keywords and concepts
3. Propose a revised description with specific additions
4. In Claude Code: run run_loop.py to find the best description automatically
5. In Claude.ai: manually reason through which description phrases would match
   the failing queries, propose a revision, and note it needs verification in Claude Code

---

## Notes

- The two failure modes are independent. Don't fix a triggering problem by rewriting
  the skill instructions — fix the description. Don't fix an output quality problem
  by tweaking the description — fix the instructions. Mixing these up wastes cycles.
- When writing negative trigger cases, think about what neighbour skills might
  claim the same query space. The most useful negatives are genuinely ambiguous.
- Inline Workflow B has a self-grading bias. Use it for fast iteration.
  For final validation of important skills, use Claude Code subagent runs.
- If a skill has no evals yet, the first thing to do is always Workflow A,
  not Workflow D. You can't baseline what you haven't defined.
