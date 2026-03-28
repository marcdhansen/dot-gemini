---
name: structured-retrospective
description: Implements the 18-question interrogation protocol with trajectory log validation. Uses structured JSON output with per-question validation. Questions filtered by task difficulty (mandatory sections per difficulty level).
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
labels: self-improvement, skill, retrospective
---

# Structured Retrospective Skill

Implements the 18-question interrogation protocol for comprehensive post-session analysis with trajectory log validation.

## Usage

```bash
# Interactive mode
python ~/.gemini/antigravity/skills/structured-retrospective/scripts/retrospective_18q.py

# With task difficulty (affects which questions are mandatory)
python ~/.gemini/antigravity/skills/structured-retrospective/scripts/retrospective_18q.py --difficulty medium

# Non-interactive (provide session ID)
python ~/.gemini/antigravity/skills/structured-retrospective/scripts/retrospective_18q.py --session-id <session-id>

# Output only JSON (for automation)
python ~/.gemini/antigravity/skills/structured-retrospective/scripts/retrospective_18q.py --json-only
```

## 18-Question Protocol

Questions organized by 6 categories (3 questions each):

### Category 1: Task Outcome (Q1-Q3)
1. **Q1**: Was the task completed successfully? What was the final outcome?
2. **Q2**: What deliverables were produced? List all files modified/created.
3. **Q3**: What is the measurable success? (metrics, tests, acceptance criteria)

### Category 2: Process (Q4-Q6)
4. **Q4**: Did the SOP workflow execute correctly? Which phases passed/failed?
5. **Q5**: What blockers or warnings were encountered?
6. **Q6**: How long did each phase take? Was time tracking accurate?

### Category 3: Knowledge (Q7-Q9)
7. **Q7**: What information was discovered during this session?
8. **Q8**: What assumptions were made? Were any proven wrong?
9. **Q9**: What documentation was missing or outdated?

### Category 4: Skills (Q10-Q12)
10. **Q10**: What skills were used effectively?
11. **Q11**: What skill gaps caused friction or rework?
12. **Q12**: What new skills should be learned or created?

### Category 5: Model (Q13-Q15)
13. **Q13**: Which model(s) were used? How did they perform?
14. **Q14**: Were there model-specific issues? (context limits, token count, reasoning)
15. **Q15**: Would a different model have been better for this task?

### Category 6: System (Q16-Q18)
16. **Q16**: What system issues affected execution? (tools, permissions, infra)
17. **Q17**: What would you do differently next time?
18. **Q18**: What systematic improvements should be proposed?

## Task Difficulty Filtering

| Difficulty | Mandatory Categories | Optional Categories |
|------------|---------------------|---------------------|
| trivial    | Q1-Q3 only          | Q4-Q18 optional     |
| easy       | Q1-Q6               | Q7-Q18 optional    |
| medium     | Q1-Q9               | Q10-Q18 optional   |
| hard       | Q1-Q12              | Q13-Q18 optional   |
| expert     | Q1-Q18 (all)        | None                |

## Validation Rules

The skill validates answers against trajectory logs:

- **Q5 validation**: If stall_count > 0, answer cannot be "none", "n/a", or empty
- **Q6 validation**: If execution_time exceeds estimate by >50%, flag warning
- **Q10 validation**: Cross-reference with trajectory tool usage counts
- **Q13 validation**: Cross-reference with trajectory model names
- **Q14 validation**: If context overflow errors in trajectory, require detailed answer

### Perfunctory Answer Rejection

These answers are automatically rejected and require elaboration:
- "none", "n/a", "nothing", "no issues" when trajectory shows otherwise
- "good", "fine", "okay" without specifics
- Empty answers for mandatory questions

## Output JSON Schema

{
  "session_id": "uuid",
  "task_difficulty": "medium",
  "timestamp": "ISO8601",
  "questions": [
    {
      "id": "Q1",
      "category": "task_outcome",
      "question": "Was the task completed successfully?...",
      "answer": "The task was completed successfully...",
      "validation_pass": true,
      "validation_note": "Matches trajectory outcome"
    }
  ],
  "overall_validation_pass": true,
  "metadata": {
    "total_questions": 18,
    "mandatory_answered": 9,
    "validation_failures": 0,
    "trajectory_logged": true
  }
}

## Trajectory Log Integration

The skill reads from trajectory logs located at:
- logs/trajectories/<date>/session_<session_id>_<time>.jsonl

Key metrics validated:
- stall_count from ProtocolState
- execution_time_ms from trajectory entries
- tool usage from trajectory
- model from LLM calls

## Integration with Other Skills

- **Reflect**: Uses reflection learnings as input
- **Retrospective**: Complementary - structured vs strategic analysis
- **Orchestrator**: Called after Finalization
- **SOP Checklists**: Validates against checklist outcomes
