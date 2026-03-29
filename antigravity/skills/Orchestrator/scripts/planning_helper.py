#!/usr/bin/env python3
"""
Planning Helper - Implementation Plan Automation

Performs planning-related automation:
1. Generate ImplementationPlan.md from issue description
2. Perform blast radius analysis (files affected, dependencies, risks)
3. Suggest test strategy
4. Estimate effort

Usage:
    python planning_helper.py generate <issue-id>
    python planning_helper.py blast <file-list>
    python planning_helper.py analyze
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def get_issue(issue_id: str) -> dict:
    """Get issue details from beads."""
    result = subprocess.run(
        ["bd", "show", issue_id, "--json"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return {"error": f"Could not get issue: {issue_id}"}

    try:
        return json.loads(result.stdout)
    except:
        return {"error": "Could not parse issue"}


def analyze_files(files: list) -> dict:
    """Analyze files for blast radius."""
    analysis = {
        "total": len(files),
        "by_type": {},
        "by_dir": {},
        "risks": [],
    }

    for f in files:
        path = Path(f)

        # By type
        ext = path.suffix or "no-ext"
        analysis["by_type"][ext] = analysis["by_type"].get(ext, 0) + 1

        # By directory
        if len(path.parts) > 1:
            dir_name = path.parts[0]
            analysis["by_dir"][dir_name] = analysis["by_dir"].get(dir_name, 0) + 1

    # Risk assessment
    risky_dirs = ["src/agent_harness", "src/bridge", "src/orchestrator"]
    for d in risky_dirs:
        if d in analysis["by_dir"]:
            analysis["risks"].append(f"High-impact: {d} ({analysis['by_dir'][d]} files)")

    return analysis


def find_dependencies(file_path: str) -> list:
    """Find dependencies (imports) of a file."""
    path = Path(file_path)
    if not path.exists() or path.suffix != ".py":
        return []

    try:
        content = path.read_text()
        imports = re.findall(r"^import\s+(\S+)|^from\s+(\S+)\s+import", content, re.MULTILINE)
        return [imp[0] or imp[1] for imp in imports]
    except:
        return []


def suggest_test_strategy(analysis: dict) -> str:
    """Suggest test strategy based on blast radius."""
    total = analysis.get("total", 0)

    if total == 0:
        return "No files to test"

    if total <= 3:
        return "Full unit tests + integration test recommended"
    elif total <= 10:
        return "Unit tests for new/changed files + integration test"
    else:
        return f"Large change ({total} files). Prioritize integration tests, add unit tests for critical paths only."


def generate_plan(issue_id: str) -> str:
    """Generate ImplementationPlan.md for an issue."""
    issue = get_issue(issue_id)

    if "error" in issue:
        return issue["error"]

    title = issue.get("title", "Untitled")
    description = issue.get("description", "")
    priority = issue.get("priority", "unknown")

    # Extract key info from description
    lines = []
    lines.append(f"# Implementation Plan: {title}")
    lines.append("")
    lines.append(f"**Issue**: {issue_id}")
    lines.append(f"**Priority**: {priority}")
    lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append(description[:500] + "..." if len(description) > 500 else description)
    lines.append("")

    lines.append("## Scope")
    lines.append("")
    lines.append("### Files (TBD - add after analysis)")
    lines.append("```")
    lines.append("# Add affected files here")
    lines.append("```")
    lines.append("")

    lines.append("### Dependencies")
    lines.append("- [ ] List external dependencies")
    lines.append("- [ ] Check for breaking changes")
    lines.append("")

    lines.append("## Blast Radius Analysis")
    lines.append("")
    lines.append("| Area | Impact | Risk |")
    lines.append("|------|--------|------|")
    lines.append("| TBD | TBD | TBD |")
    lines.append("")

    lines.append("## Implementation Steps")
    lines.append("")
    lines.append("1. [ ] ")
    lines.append("2. [ ] ")
    lines.append("3. [ ] ")
    lines.append("")

    lines.append("## Test Strategy")
    lines.append("TBD - run `python planning_helper.py blast` after identifying files")
    lines.append("")

    lines.append("## Acceptance Criteria")
    lines.append("")
    lines.append("- [ ] ")
    lines.append("- [ ] ")
    lines.append("- [ ] ")
    lines.append("")

    lines.append("## Rollback Plan")
    lines.append("Describe how to revert if issues arise...")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Planning Helper")
    subparsers = parser.add_subparsers(dest="command")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate ImplementationPlan.md for issue")
    gen_parser.add_argument("issue", help="Issue ID (e.g., openloop-123)")
    gen_parser.add_argument("--output", "-o", help="Output file (default: ImplementationPlan.md)")

    # blast command
    blast_parser = subparsers.add_parser("blast", help="Perform blast radius analysis")
    blast_parser.add_argument("files", nargs="*", help="Files to analyze")
    blast_parser.add_argument("--find-deps", action="store_true", help="Find dependencies")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze current branch changes")

    args = parser.parse_args()

    if args.command == "generate":
        plan = generate_plan(args.issue)

        output = args.output or "ImplementationPlan.md"
        Path(output).write_text(plan)
        print(f"✅ Generated: {output}")
        print()
        print("Next steps:")
        print("1. Edit ImplementationPlan.md with specific details")
        print("2. Run 'planning_helper.py blast' on affected files")

    elif args.command == "blast":
        if not args.files:
            print("No files provided. Usage: planning_helper.py blast src/foo.py src/bar.py")
            sys.exit(1)

        analysis = analyze_files(args.files)

        print("💥 Blast Radius Analysis")
        print("=" * 40)
        print(f"Total files: {analysis['total']}")
        print()

        print("By file type:")
        for ext, count in sorted(analysis["by_type"].items(), key=lambda x: -x[1]):
            print(f"  {ext}: {count}")
        print()

        print("By directory:")
        for d, count in sorted(analysis["by_dir"].items(), key=lambda x: -x[1]):
            print(f"  {d}: {count}")
        print()

        if analysis["risks"]:
            print("⚠️  Risk Areas:")
            for risk in analysis["risks"]:
                print(f"  {risk}")
            print()

        print("Test strategy:")
        print(f"  {suggest_test_strategy(analysis)}")

        if args.find_deps:
            print()
            print("Dependencies found:")
            all_deps = set()
            for f in args.files:
                deps = find_dependencies(f)
                all_deps.update(deps)
            for dep in sorted(all_deps):
                print(f"  - {dep}")

    elif args.command == "analyze":
        print("📊 Analyzing current branch changes...")

        # Get changed files
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
        )

        files = [f for f in result.stdout.strip().split("\n") if f]

        if not files:
            print("No changed files found")
            sys.exit(0)

        analysis = analyze_files(files)

        print()
        print(f"Changed files: {len(files)}")
        print()

        print("By directory:")
        for d, count in sorted(analysis["by_dir"].items(), key=lambda x: -x[1]):
            print(f"  {d}: {count}")

        print()
        print("Test strategy:")
        print(f"  {suggest_test_strategy(analysis)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
