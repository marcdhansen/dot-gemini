#!/usr/bin/env python3
"""
Auto-Finalize - Session Cleanup Automation

Performs automatic cleanup at session end:
1. Detect temp files to clean up
2. Validate issue closures have proper notes
3. Generate handoff summary
4. Check for uncommitted changes

Usage:
    python auto_finalize.py
    python auto_finalize.py clean
    python auto_finalize.py validate
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


TEMP_PATTERNS = [
    "*.pyc",
    "__pycache__",
    "*.log",
    ".coverage.*",
    "*.tmp",
    "*.swp",
    "*~",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",  # if in wrong place
    "dist/",
    "build/",
    "*.egg-info/",
]

IGNORE_DIRS = [
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "env",
]


def find_temp_files() -> list:
    """Find temporary files that should be cleaned up."""
    temp_files = []

    for pattern in TEMP_PATTERNS:
        if "*" in pattern:
            # Glob pattern
            for f in Path(".").rglob(pattern):
                if any(ignore in f.parts for ignore in IGNORE_DIRS):
                    continue
                temp_files.append(str(f))
        elif pattern.endswith("/"):
            # Directory
            d = Path(pattern.rstrip("/"))
            if d.exists():
                temp_files.append(str(d))

    return sorted(set(temp_files))


def clean_temp_files(files: list) -> dict:
    """Remove temp files."""
    removed = []
    errors = []

    for f in files:
        try:
            p = Path(f)
            if p.is_file():
                p.unlink()
                removed.append(f)
            elif p.is_dir():
                import shutil

                shutil.rmtree(p)
                removed.append(f)
        except Exception as e:
            errors.append(f"{f}: {e}")

    return {"removed": removed, "errors": errors}


def validate_closures() -> str:
    """Check if recently closed issues have proper closure notes."""
    result = subprocess.run(
        ["bd", "list", "--status", "closed", "--json"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return "⚠️ Could not get closed issues"

    try:
        issues = json.loads(result.stdout)
    except:
        return "⚠️ Could not parse issues"

    # Check last 5 closed issues
    issues = issues[:5]

    if not issues:
        return "ℹ️ No closed issues to validate"

    lines = ["📝 Recent closures:"]
    for issue in issues:
        iid = issue.get("id", "?")
        has_note = issue.get("comment_count", 0) > 0

        if has_note:
            lines.append(f"  ✅ {iid}: has closure note")
        else:
            lines.append(f"  ⚠️ {iid}: MISSING closure note")

    return "\n".join(lines)


def generate_handoff() -> str:
    """Generate a session handoff summary."""
    # Get current context
    branch = (
        subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        ).stdout.strip()
        or "unknown"
    )

    # Get recent commits
    commits = (
        subprocess.run(["git", "log", "--oneline", "-3"], capture_output=True, text=True)
        .stdout.strip()
        .split("\n")
    )

    # Get active issue
    active = subprocess.run(
        ["bd", "list", "--status", "in_progress", "--json"], capture_output=True, text=True
    )

    active_issue = None
    if active.returncode == 0:
        try:
            issues = json.loads(active.stdout)
            if issues:
                active_issue = issues[0]
        except:
            pass

    # Build handoff
    lines = [
        "# Session Handoff",
        "",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Branch**: {branch}",
        "",
    ]

    if active_issue:
        lines.append(f"## Active Issue: {active_issue.get('id')}")
        lines.append(f"**Title**: {active_issue.get('title', 'N/A')}")
        lines.append(f"**Status**: {active_issue.get('status', 'N/A')}")
        lines.append("")

    lines.append("## Recent Work")
    for c in commits:
        lines.append(f"- {c}")
    lines.append("")

    lines.append("## Notes")
    lines.append("- Add any context for next session here")
    lines.append("")

    return "\n".join(lines)


def check_uncommitted() -> tuple[bool, str]:
    """Check for uncommitted changes."""
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

    if not result.stdout.strip():
        return True, "✅ Working tree clean"

    files = result.stdout.strip().split("\n")
    return False, f"⚠️ {len(files)} uncommitted file(s)"


def main():
    parser = argparse.ArgumentParser(description="Auto-Finalize")
    parser.add_argument("--clean", action="store_true", help="Clean temp files")
    parser.add_argument("--validate", action="store_true", help="Validate closures")
    parser.add_argument("--handoff", action="store_true", help="Generate handoff")
    parser.add_argument("--all", action="store_true", help="Run all checks")

    args = parser.parse_args()

    # Default: run all
    run_all = not (args.clean or args.validate or args.handoff)

    print("🧹 Auto-Finalize - Session Cleanup")
    print("=" * 40)
    print()

    # 1. Check uncommitted
    print("📋 Git Status:")
    clean, msg = check_uncommitted()
    print(f"  {msg}")
    print()

    # 2. Find temp files
    print("🗑️  Temp Files:")
    temp_files = find_temp_files()
    if temp_files:
        print(f"  Found {len(temp_files)} temp file(s):")
        for f in temp_files[:10]:
            print(f"    - {f}")
        if len(temp_files) > 10:
            print(f"    ... and {len(temp_files) - 10} more")
    else:
        print("  ✅ No temp files found")
    print()

    # Clean if requested
    if (args.clean or args.all) and temp_files:
        print("🧹 Cleaning temp files...")
        result = clean_temp_files(temp_files)
        print(f"  Removed {len(result['removed'])} item(s)")
        if result["errors"]:
            print(f"  Errors: {result['errors']}")
        print()

    # Validate closures
    if args.validate or args.all:
        print("✅ Closure Validation:")
        print(validate_closures())
        print()

    # Generate handoff
    if args.handoff or args.all:
        print("📄 Handoff Summary:")
        print(generate_handoff())

    if run_all:
        print("=" * 40)
        print("Run with --help for more options")


if __name__ == "__main__":
    main()
