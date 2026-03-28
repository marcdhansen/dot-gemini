#!/usr/bin/env python3
"""
Todo Continuation Enforcer (oh-my-opencode pattern)
Purpose: Ensure all tasks in task.md are completed before allowing RTB or Debrief.
"""

import sys
import re
from pathlib import Path


def find_task_md():
    """Find the current task.md file - only from current project, not old sessions."""
    # Check current directory (project root)
    local_task = Path("task.md")
    if local_task.exists():
        return local_task

    # Check .agent directory (project-level)
    agent_task = Path(".agent/task.md")
    if agent_task.exists():
        return agent_task

    return None


def check_todos(task_file):
    """Check for unfinished todos in the task file ONLY."""
    content = task_file.read_text()

    # Only check THIS file's unfinished todos
    todos = re.findall(r"^[-*+]\s*\[ \]", content, re.MULTILINE)

    if todos:
        return False, len(todos)
    return True, 0


def main():
    task_file = find_task_md()
    if not task_file:
        print("⚠️  No task.md found. Skipping todo enforcement.")
        sys.exit(0)

    print(f"🔍 Enforcing todos in: {task_file}")
    completed, count = check_todos(task_file)

    if not completed:
        print(f"❌ TODO ENFORCEMENT FAILED: {count} unfinished task(s) detected.")
        print("   Sisyphus says: BACK TO THE BOULDER! 🪨")
        print("   Please complete all tasks in task.md before proceeding.")
        sys.exit(1)

    print("✅ All tasks completed. The boulder is at the top! ⛰️")
    sys.exit(0)


if __name__ == "__main__":
    main()
