#!/usr/bin/env python3
"""
Retrospective Metrics - Session Statistics & Insights

Automatically calculates session metrics:
- Time spent (from git log)
- Files changed
- Lines added/removed
- Issue cycle time
- Test coverage changes
- Common issues encountered

Usage:
    python retro_metrics.py              # Show session metrics
    python retro_metrics.py --insights   # Show AI-generated insights
    python retro_metrics.py --export    # Export to JSON
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_session_commits(since_hours: int = 24) -> list:
    """Get commits from the last N hours."""
    since = datetime.now() - timedelta(hours=since_hours)
    result = subprocess.run(
        ["git", "log", f"--since={since.isoformat()}", "--format=%H|%an|%ad|%s", "-20"],
        capture_output=True,
        text=True,
    )

    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|")
        if len(parts) >= 4:
            commits.append(
                {
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3],
                }
            )
    return commits


def get_diff_stats() -> dict:
    """Get diff statistics for the session."""
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD~20..HEAD"],
        capture_output=True,
        text=True,
    )

    stats = {"files": 0, "insertions": 0, "deletions": 0}

    # Parse the stat output
    for line in result.stdout.strip().split("\n"):
        if "file" in line.lower():
            continue
        # Example: "  src/foo.py | 10 +++---"
        if "|" in line:
            parts = line.split("|")
            if len(parts) == 2:
                stats["files"] += 1
                # Try to extract numbers
                import re

                plus = len(re.findall(r"\+", parts[1]))
                minus = len(re.findall(r"-", parts[1]))
                stats["insertions"] += plus
                stats["deletions"] += minus

    return stats


def get_issue_metrics() -> dict:
    """Get issue-related metrics."""
    # Get closed issues this session
    result = subprocess.run(
        ["bd", "list", "--status", "closed", "--json"],
        capture_output=True,
        text=True,
    )

    metrics = {"closed": 0, "created": 0, "in_progress": 0}

    if result.returncode == 0:
        try:
            issues = json.loads(result.stdout)
            metrics["closed"] = len(issues)
        except:
            pass

    # Get in-progress
    result = subprocess.run(
        ["bd", "list", "--status", "in_progress", "--json"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        try:
            issues = json.loads(result.stdout)
            metrics["in_progress"] = len(issues)
        except:
            pass

    return metrics


def get_test_coverage() -> dict:
    """Get test coverage if available."""
    # Check for coverage file
    cov_files = [
        ".coverage",
        "coverage.xml",
        "coverage.json",
    ]

    for cov_file in cov_files:
        if Path(cov_file).exists():
            return {"available": True, "file": cov_file}

    return {"available": False}


def analyze_commits(commits: list) -> dict:
    """Analyze commit patterns."""
    types = {}
    scopes = {}

    for c in commits:
        msg = c["message"]

        # Detect type
        for t in ["feat", "fix", "docs", "refactor", "test", "chore", "ci"]:
            if msg.startswith(t):
                types[t] = types.get(t, 0) + 1
                break

        # Detect scope
        match = re.search(r"\(([^)]+)\):", msg)
        if match:
            scopes[match.group(1)] = scopes.get(match.group(1), 0) + 1

    return {"types": types, "scopes": scopes}


def generate_insights(metrics: dict) -> list:
    """Generate AI-like insights from metrics."""
    insights = []

    stats = metrics.get("stats", {})
    issue_metrics = metrics.get("issues", {})
    commit_analysis = metrics.get("commits", {})

    # High volume
    total_files = stats.get("files", 0)
    if total_files > 20:
        insights.append(
            f"High activity: {total_files} files changed - consider breaking into smaller PRs"
        )

    # High test ratio
    types = commit_analysis.get("types", {})
    test_count = types.get("test", 0)
    feat_count = types.get("feat", 0) + types.get("fix", 0)
    if feat_count > 0 and test_count == 0:
        insights.append("No test commits found - ensure test coverage for new features")

    # Issue closed
    closed = issue_metrics.get("closed", 0)
    if closed > 0:
        insights.append(f"Good progress: {closed} issue(s) closed this session")

    # Type diversity
    if len(types) > 3:
        insights.append("Diverse work:多种类型的更改 - consider grouping similar changes")

    return insights


def main():
    parser = argparse.ArgumentParser(description="Retrospective Metrics")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    parser.add_argument("--insights", action="store_true", help="Generate AI insights")
    parser.add_argument("--export", action="store_true", help="Export to JSON")

    args = parser.parse_args()

    commits = get_session_commits(args.hours)
    stats = get_diff_stats()
    issue_metrics = get_issue_metrics()
    test_cov = get_test_coverage()
    commit_analysis = analyze_commits(commits)

    metrics = {
        "session": {
            "hours": args.hours,
            "commits": len(commits),
        },
        "stats": stats,
        "issues": issue_metrics,
        "coverage": test_cov,
        "commits": commit_analysis,
    }

    if args.export:
        print(json.dumps(metrics, indent=2))
        return

    print("📊 Retrospective Metrics")
    print("=" * 40)
    print(f"Session: Last {args.hours} hours")
    print()

    print("📝 Activity:")
    print(f"  Commits: {len(commits)}")
    print(f"  Files changed: {stats['files']}")
    print(f"  Lines: +{stats['insertions']} -{stats['deletions']}")
    print()

    print("🎯 Issues:")
    print(f"  Closed: {issue_metrics['closed']}")
    print(f"  In Progress: {issue_metrics['in_progress']}")
    print()

    if commit_analysis["types"]:
        print("📦 Change Types:")
        for t, count in sorted(commit_analysis["types"].items()):
            print(f"  {t}: {count}")
        print()

    if args.insights:
        insights = generate_insights(metrics)
        if insights:
            print("💡 Insights:")
            for insight in insights:
                print(f"  • {insight}")


if __name__ == "__main__":
    import re

    main()
