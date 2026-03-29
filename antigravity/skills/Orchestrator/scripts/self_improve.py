#!/usr/bin/env python3
"""
Self-Improvement Loop - Pattern Detection & Issue Creation

Analyzes session patterns and creates beads issues for improvements:
- Detects recurring issues
- Identifies process improvements
- Creates tracking issues automatically

Usage:
    python self_improve.py analyze    # Analyze patterns
    python self_improve.py create     # Create improvement issues
    python self_improve.py status     # Show improvement status
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_trace_history() -> list:
    """Get trace history for pattern analysis."""
    archive = Path(".agent/trace-archive.jsonl")
    if not archive.exists():
        return []

    entries = []
    for line in archive.read_text().strip().split("\n"):
        if line:
            try:
                entries.append(json.loads(line))
            except:
                pass

    return entries


def analyze_patterns() -> dict:
    """Analyze traces for patterns."""
    entries = get_trace_history()

    if not entries:
        return {"message": "No history available"}

    # Count actions and outcomes
    actions = {}
    failures = {}
    intents = {}

    for e in entries:
        action = e.get("action", "unknown")
        outcome = e.get("outcome", "")
        intent = e.get("intent", "")

        actions[action] = actions.get(action, 0) + 1

        if "fail" in outcome.lower() or "error" in outcome.lower():
            failures[action] = failures.get(action, 0) + 1

        if intent:
            intents[intent] = intents.get(intent, 0) + 1

    # Find problematic patterns
    problem_actions = []
    for action, count in failures.items():
        if failures[action] > 0:
            rate = count / actions[action]
            if rate > 0.2:
                problem_actions.append(
                    {
                        "action": action,
                        "failures": count,
                        "total": actions[action],
                        "rate": rate,
                    }
                )

    return {
        "total_entries": len(entries),
        "unique_actions": len(actions),
        "problem_actions": sorted(problem_actions, key=lambda x: -x["rate"]),
    }


def get_recent_issues() -> list:
    """Get recently created issues."""
    result = subprocess.run(
        ["bd", "list", "--json"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return []

    try:
        return json.loads(result.stdout)
    except:
        return []


def check_existing_improvement(title: str) -> bool:
    """Check if improvement issue already exists."""
    issues = get_recent_issues()

    title_lower = title.lower()
    for issue in issues:
        if title_lower in issue.get("title", "").lower():
            return True

    return False


def create_improvement_issue(pattern: dict) -> str:
    """Create a beads issue for a detected pattern."""
    action = pattern["action"]
    rate = pattern["rate"]
    failures = pattern["failures"]

    title = f"SOP Improvement: {action} has {rate:.0%} failure rate"
    description = f"""## Detected Pattern

Action `{action}` has a {rate:.0%} failure rate ({failures} failures).

## Suggested Fix

- Investigate root cause of failures
- Add documentation or automation
- Consider deprecating if too problematic

## Tracking

This issue was auto-created by the self-improvement system.
Created: {datetime.now().isoformat()}
"""

    # Check if already exists
    if check_existing_improvement(title):
        return f"Issue already exists for: {action}"

    # Create issue
    result = subprocess.run(
        ["bd", "create", title, "--description", description, "-t", "chore", "-p", "3"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return f"Created issue for: {action}"
    else:
        return f"Failed to create: {result.stderr}"


def main():
    parser = argparse.ArgumentParser(description="Self-Improvement Loop")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("analyze", help="Analyze patterns in trace history")
    subparsers.add_parser("create", help="Create improvement issues for patterns")
    subparsers.add_parser("status", help="Show improvement status")

    args = parser.parse_args()

    if args.command == "analyze" or args.command is None:
        print("🔍 Analyzing Patterns...")
        print("=" * 40)

        patterns = analyze_patterns()

        if "message" in patterns:
            print(patterns["message"])
            return

        print(f"Total entries: {patterns['total_entries']}")
        print(f"Unique actions: {patterns['unique_actions']}")
        print()

        if patterns["problem_actions"]:
            print("⚠️  Problematic Actions (high failure rate):")
            for p in patterns["problem_actions"]:
                print(f"  • {p['action']}: {p['failures']}/{p['total']} failures ({p['rate']:.0%})")
        else:
            print("✅ No problematic patterns detected")

    elif args.command == "create":
        print("📝 Creating Improvement Issues...")
        print("=" * 40)

        patterns = analyze_patterns()

        if "message" in patterns or not patterns.get("problem_actions"):
            print("No patterns to create issues for")
            return

        created = 0
        for p in patterns["problem_actions"][:3]:  # Limit to top 3
            result = create_improvement_issue(p)
            print(f"  {result}")
            created += 1

        print(f"\nCreated {created} improvement issue(s)")

    elif args.command == "status":
        print("📊 Improvement Status")
        print("=" * 40)

        issues = get_recent_issues()
        improvements = [i for i in issues if "improvement" in i.get("title", "").lower()]

        print(f"Total issues: {len(issues)}")
        print(f"Improvement issues: {len(improvements)}")

        if improvements:
            print("\nOpen improvements:")
            for i in improvements[:5]:
                status = i.get("status", "?")
                print(f"  • {i['id']}: {i['title'][:50]} [{status}]")


if __name__ == "__main__":
    main()
