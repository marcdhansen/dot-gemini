#!/usr/bin/env python3
"""
Todo Continuation Enforcer (oh-my-opencode pattern)
Purpose: Ensure all tasks in task.md are completed before allowing RTB or Debrief.
"""

import sys
import re
from pathlib import Path

def find_task_md():
    """Find the current task.md file."""
    # Check current directory
    local_task = Path("task.md")
    if local_task.exists():
        return local_task
    
    # Check .agent directory
    agent_task = Path(".agent/task.md")
    if agent_task.exists():
        return agent_task
        
    # Check brain directory (most recent session)
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    if brain_dir.exists():
        # Get session directories sorted by modification time
        session_dirs = sorted(
            [d for d in brain_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        for session_dir in session_dirs:
            task_file = session_dir / "task.md"
            if task_file.exists():
                return task_file
                
    return None

def check_todos(task_file):
    """Check for unfinished todos in the task file."""
    content = task_file.read_text()
    
    # Find all todo items: - [ ] or * [ ]
    # We only care about root-level tasks in the "Current Task" or "Tasks" sections
    # but for safety, we'll check all [ ] items.
    
    todos = re.findall(r'^[ \t]*[-*+]\s*\[ \]', content, re.MULTILINE)
    
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
