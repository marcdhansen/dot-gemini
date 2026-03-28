---
name: call-subagent
description: Delegate tasks to sub-agents — code review, plan review, feedback, or any command. Supports local execution, Tailscale peer delegation, and OpenClaw gateway.
allowed-tools: all
version: "1.0.0"
labels:
  - delegation
  - review
  - collaboration
  - subagent
---

# call-subagent

Delegate a task to another agent or process and get the result back.

## When to Use

- **Code review**: After opening a PR, delegate review to a peer or LLM
- **Plan review**: Ask another agent to critique your implementation plan
- **Feedback**: Get a second opinion on architecture decisions
- **Any shell task**: Run scripts, tests, or analysis as a sub-task

## Backends

| Backend | Use when | Requires |
|---------|----------|----------|
| `local` | Running scripts/commands on this machine | Nothing |
| `peer` | Delegating to another agent via Tailscale | Peer running `notify_server.py` |
| `openclaw` | Delegating to OpenClaw orchestrator | Gateway running (`pnpm gateway:dev`) |

## Usage

### CLI

```bash
# Local: run a review script
python -m agent_harness.scripts.call_subagent \
  --task "bash scripts/agent-review.sh /tmp/pr.diff" \
  --backend local --json

# Peer: ask another agent to review
python -m agent_harness.scripts.call_subagent \
  --task "Please review PR #42 on marcdhansen/agent-harness" \
  --backend peer --target left --json

# OpenClaw: delegate to orchestrator
python -m agent_harness.scripts.call_subagent \
  --task "code-review" \
  --backend openclaw \
  --context '{"pr_number": "42", "repo": "marcdhansen/agent-harness"}' \
  --json
```

### Python API

```python
from agent_harness.subagent import call_subagent, SubagentRequest

# Simple local command
result = call_subagent(SubagentRequest(task="echo hello"))
print(result.output)  # "hello"

# Delegate code review to a peer
result = call_subagent(SubagentRequest(
    task="Review PR #42 for architectural fit and edge cases",
    backend="peer",
    target="left",
    context={"pr_number": "42", "repo": "marcdhansen/agent-harness"},
))

if result.success:
    print(result.output)
else:
    print(f"Failed: {result.error}")
```

## Code Review Workflow (Primary Use Case)

After pushing a PR, request review:

```bash
# Option 1: Use request-review.sh (wrapper around call-subagent)
bash scripts/request-review.sh

# Option 2: Direct call-subagent for custom review
python -m agent_harness.scripts.call_subagent \
  --task "bash scripts/agent-review.sh /tmp/pr.diff /tmp/pr-body.txt" \
  --backend local --json

# Option 3: Ask a peer agent to review
python -m agent_harness.scripts.call_subagent \
  --task "Please review my PR: https://github.com/marcdhansen/agent-harness/pull/42" \
  --backend peer --target right
```

## Context Variables

When using the `local` backend, context dict items become `SUBAGENT_*` environment variables:

```python
SubagentRequest(
    task="bash scripts/agent-review.sh",
    context={"pr_number": "42", "repo": "marcdhansen/agent-harness"},
)
# → SUBAGENT_PR_NUMBER=42, SUBAGENT_REPO=marcdhansen/agent-harness
```

## Peer Resolution

Peer names (e.g., `left`, `right`) are resolved from `config/peers.json`.
You can also pass a direct URL: `--target http://100.102.115.14:8080`.

## Error Handling

All backends return a `SubagentResult` with `success`, `output`, `error`, and `duration_s`.
Failures are always graceful — never crashes, always returns a result.
