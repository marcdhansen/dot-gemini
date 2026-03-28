#!/bin/bash

# OpenClaw SOP Orchestrator Script
# Invokes OpenClaw for intelligent SOP orchestration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OPENCLAW_PATH="$HOME/GitHub/marcdhansen/openclaw"
TIMEOUT=${TIMEOUT:-120}

# Check if OpenClaw is available
if [ ! -d "$OPENCLAW_PATH" ]; then
    echo "❌ OpenClaw not found at $OPENCLAW_PATH"
    echo "Please install OpenClaw first: git clone https://github.com/openclaw/openclaw.git $OPENCLAW_PATH"
    exit 1
fi

# Set up environment
export OLLAMA_API_KEY="ollama-local"

# Get command
COMMAND=${1:-next}
ISSUE_ID=${2:-}

case "$COMMAND" in
    init)
        if [ -z "$ISSUE_ID" ]; then
            echo "Usage: $0 init <issue-id>"
            exit 1
        fi
        MESSAGE="You are working in the agent-harness project at ~/GitHub/marcdhansen/agent-harness. The Beads database is at ~/GitHub/marcdhansen/agent-harness/.beads. Initialize a new agent session for issue $ISSUE_ID. Run 'cd ~/GitHub/marcdhansen/agent-harness && bd update $ISSUE_ID --claim' to claim the task, then validate SOP compliance."
        ;;
    validate)
        PHASE=${2:-execution}
        MESSAGE="You are working in the agent-harness project at ~/GitHub/marcdhansen/agent-harness. The Beads database is at ~/GitHub/marcdhansen/agent-harness/.beads. Validate SOP compliance for the $PHASE phase. Check session state at .harness/session.json, run 'bd list' to see in-progress tasks, check git status, and reference .agent/docs/SOP_COMPLIANCE_CHECKLIST.md"
        ;;
    close)
        MESSAGE="You are working in the agent-harness project at ~/GitHub/marcdhansen/agent-harness. The Beads database is at ~/GitHub/marcdhansen/agent-harness/.beads. Close the current agent session. Run quality gates (lint, test), check git status, run 'bd list' to see in-progress tasks, run '/reflect', and create handoff docs. Reference .agent/docs/SOP_COMPLIANCE_CHECKLIST.md"
        ;;
    status)
        MESSAGE="You are working in the agent-harness project at ~/GitHub/marcdhansen/agent-harness. The Beads database is at ~/GitHub/marcdhansen/agent-harness/.beads. Check current session status. Run 'cd ~/GitHub/marcdhansen/agent-harness && bd list' to see in-progress tasks, check git status at .harness/session.json, and validate SOP compliance."
        ;;
    validate)
        PHASE=${2:-execution}
        MESSAGE="Validate SOP compliance for the $PHASE phase. Check session state, task progress, and any violations. Reference .agent/docs/SOP_COMPLIANCE_CHECKLIST.md"
        ;;
    close)
        MESSAGE="Close the current agent session. Run quality gates, check for cleanup violations, verify git status, update beads issue, run /reflect, and create handoff docs."
        ;;
    next)
        MESSAGE="You are working in the agent-harness project at ~/GitHub/marcdhansen/agent-harness. The Beads database is at ~/GitHub/marcdhansen/agent-harness/.beads. Run 'cd ~/GitHub/marcdhansen/agent-harness && bd ready --json' to get available tasks. Analyze priorities and dependencies, then recommend what to work on next with specific bd commands to claim tasks."
        ;;
    status)
        MESSAGE="Check current session status. Check .harness/session.json, run 'bd started', check git status, and validate SOP compliance."
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  init <issue-id>    Initialize session for issue"
        echo "  validate [phase]    Validate SOP compliance (default: execution)"
        echo "  close              Close current session"
        echo "  next               Get next task recommendation"
        echo "  status             Show session status"
        exit 1
        ;;
esac

echo "🔄 Invoking OpenClaw for '$COMMAND'..."
echo ""

# Set BEADS_DIR to point to agent-harness beads db
export BEADS_DIR="$HOME/GitHub/marcdhansen/agent-harness/.beads"

# Run OpenClaw agent from agent-harness dir so bd commands work
cd "$HOME/GitHub/marcdhansen/agent-harness"
npx --prefix "$OPENCLAW_PATH" openclaw agent --agent harness --message "$MESSAGE" --timeout "$TIMEOUT" --local
