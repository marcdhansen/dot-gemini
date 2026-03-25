# Eval Schemas

JSON structures used by skill-evaluator and skill-creator.

---

## evals.json — Output Quality Eval Set

Located at `evals/evals.json` in the skill workspace.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "name": "descriptive-name",
      "prompt": "Concrete user prompt with real context, file names, column names, etc.",
      "expected_output": "One sentence: what does success look like?",
      "files": ["evals/files/sample.pdf"],
      "expectations": [
        "The output includes X (prefer content checks over existence checks)",
        "The skill used script Y rather than reinventing it",
        "The output does NOT contain Z"
      ]
    }
  ]
}
```

Fields:
- `id`: unique integer
- `name`: short descriptive slug used as directory name
- `prompt`: the task — make it concrete and realistic, not abstract
- `expected_output`: human-readable success description for review context
- `files`: optional input files, paths relative to skill root
- `expectations`: 3–6 verifiable assertions per eval

---

## trigger-evals.json — Triggering Eval Set

Located at `evals/trigger-evals.json` in the skill workspace.

```json
[
  {
    "query": "I want to build a new skill for my Claude agent. where do I start?",
    "should_trigger": true
  },
  {
    "query": "write unit tests for my Python module",
    "should_trigger": false
  }
]
```

Fields:
- `query`: realistic user prompt — concrete, specific, with real context
- `should_trigger`: true if this skill should be loaded for this query

Design guidelines:
- ~50% should-trigger, ~50% should-not-trigger
- Should-not-trigger queries must be near-misses, not obviously irrelevant
- Run each query 3× in run_eval.py — triggering has variance

---

## grading.json — Output from Grader

Located at `<run-dir>/grading.json`.

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "Would also pass for a hallucinated document — consider checking it appears as primary contact"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

Important: field names are exact — the eval viewer reads `text`/`passed`/`evidence`,
not `name`/`met`/`details`. Use this schema verbatim.

---

## trigger-results.json — Output from run_eval.py

```json
{
  "skill_name": "my-skill",
  "description": "The description that was tested",
  "results": [
    {
      "query": "the user prompt",
      "should_trigger": true,
      "trigger_rate": 0.67,
      "triggers": 2,
      "runs": 3,
      "pass": true
    }
  ],
  "summary": {
    "total": 20,
    "passed": 16,
    "failed": 4
  }
}
```

---

## baseline-summary.json — Recommended baseline record format

Save this before making any changes to a skill.

```json
{
  "skill_name": "my-skill",
  "skill_version": "1.0.0",
  "baseline_date": "2026-03-16",
  "environment": "Claude.ai inline / Claude Code subagents",
  "output_quality": {
    "overall_pass_rate": 0.30,
    "total_passed": 8,
    "total_assertions": 27,
    "by_eval": {
      "eval-name-1": 0.0,
      "eval-name-2": 0.17
    }
  },
  "triggering": {
    "status": "estimated / not yet run / run",
    "precision": 0.5,
    "recall": 0.4,
    "accuracy": 0.55,
    "notes": "Estimated from description analysis — run run_eval.py to confirm"
  },
  "gates": {
    "output_quality_target": 0.75,
    "triggering_precision_target": 0.80,
    "triggering_recall_target": 0.70,
    "regressions_allowed": false
  }
}
```
