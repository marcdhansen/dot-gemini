#!/usr/bin/env python3
"""
Auto-Init - Session Startup Automation

Performs automatic setup at session start:
1. Check required tools
2. Show session context (active issue, branch, recent changes)
3. Suggest next task from beads queue
4. Check for unread handoffs

Usage:
    python auto_init.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta


def run(cmd: list) -> tuple[bool, str]:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def check_tools() -> list:
    """Check all required tools are available."""
    tools = ["bd", "git", "python3", "npm"]
    results = []

    for tool in tools:
        success, output = run(["which", tool])
        status = "✅" if success else "❌"
        results.append(f"  {status} {tool}")

    return results


def get_context() -> dict:
    """Get current session context."""
    context = {}

    # Current branch
    success, branch = run(["git", "branch", "--show-current"])
    context["branch"] = branch if success else "unknown"

    # Active beads issue
    success, issue = run(["bd", "list", "--status", "in_progress", "--json"])
    if success and issue:
        try:
            issues = json.loads(issue)
            if issues:
                context["active_issue"] = issues[0]
        except:
            pass

    # Recent commits
    success, commits = run(["git", "log", "--oneline", "-5"])
    context["recent_commits"] = commits.split("\n") if success else []

    # Uncommitted changes
    success, status = run(["git", "status", "--porcelain"])
    context["has_changes"] = bool(status)
    context["change_count"] = len(status.split("\n")) if status else 0

    return context


def suggest_task() -> str:
    """Suggest next task from beads queue."""
    success, output = run(["bd", "ready", "--json"])

    if not success:
        return "  ⚠️ Could not get beads ready list"

    try:
        issues = json.loads(output)
        if not issues:
            return "  ℹ️ No ready tasks in queue"

        # Show top 3 ready tasks
        lines = ["  📋 Suggested tasks:"]
        for issue in issues[:3]:
            lines.append(f"    • {issue.get('id')}: {issue.get('title', 'Untitled')[:60]}")

        return "\n".join(lines)
    except Exception as e:
        return f"  ⚠️ Error parsing ready list: {e}"


def check_handoffs() -> str:
    """Check for unread session handoffs."""
    handoff_dir = Path(".agent/handoffs")

    if not handoff_dir.exists():
        return "  ℹ️ No handoffs directory"

    handoffs = list(handoff_dir.glob("*.md"))

    if not handoffs:
        return "  ℹ️ No pending handoffs"

    lines = [f"  📬 {len(handoffs)} pending handoff(s):"]
    for h in handoffs[:5]:
        lines.append(f"    • {h.name}")

    return "\n".join(lines)


def main():
    print("🚀 Auto-Init - Session Startup")
    print("=" * 40)
    print()

    # 1. Tool Check
    print("🔧 Required Tools:")
    for result in check_tools():
        print(result)
    print()

    # 2. Context
    print("📍 Current Context:")
    context = get_context()
    print(f"  📌 Branch: {context.get('branch', 'unknown')}")

    if "active_issue" in context:
        issue = context["active_issue"]
        print(f"  🎯 Active: {issue.get('id')}: {issue.get('title', '')[:50]}")
    else:
        print("  🎯 Active: None")

    if context.get("has_changes"):
        print(f"  ⚠️ Uncommitted changes: {context.get('change_count')} files")
    else:
        print("  ✅ Working tree clean")
    print()

    # 3. Task Suggestion
    print("🎯 Next Task:")
    print(suggest_task())
    print()

    # 4. Handoffs
    print("📬 Handoffs:")
    print(check_handoffs())
    print()

    # Summary
    print("=" * 40)
    print("✅ Auto-init complete. Ready to work!")

    # Suggest next command
    if "active_issue" not in context:
        print("\n💡 Next: Run 'bd ready' to find tasks, or check specific area:")


if __name__ == "__main__":
    main()
