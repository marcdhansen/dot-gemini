#!/usr/bin/env python3
"""
Auto-Commit - Intelligent Commit Message Generator

Analyzes changes and generates conventional commit messages.
Suggests type, scope, and description based on diff.

Usage:
    python auto_commit.py              # Analyze and suggest
    python auto_commit.py --commit     # Auto-commit with suggested message
    python auto_commit.py --amend     # Amend last commit
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path


TYPE_MAP = {
    "feat": "New feature",
    "fix": "Bug fix",
    "docs": "Documentation",
    "style": "Code style (formatting)",
    "refactor": "Code refactoring",
    "perf": "Performance improvement",
    "test": "Tests",
    "chore": "Maintenance",
    "ci": "CI/CD changes",
}

FILE_TYPE_MAP = {
    "test_": "test",
    "_test": "test",
    "tests/": "test",
    "/tests/": "test",
    "docs/": "docs",
    "README": "docs",
    "CHANGELOG": "docs",
    ".md": "docs",
    "src/agent_harness/": "feat",
    "src/bridge/": "feat",
    "src/orchestrator/": "feat",
    ".github/": "ci",
    "workflows/": "ci",
    "pyproject.toml": "chore",
    "package.json": "chore",
    "requirements.txt": "chore",
    ".env": "chore",
}


def get_changed_files() -> list:
    """Get list of changed files."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--staged"],
        capture_output=True,
        text=True,
    )
    if not result.stdout.strip():
        # Try unstaged
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
        )
    return [f for f in result.stdout.strip().split("\n") if f]


def get_diff_summary() -> str:
    """Get diff stats."""
    result = subprocess.run(
        ["git", "diff", "--stat"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def detect_type(files: list) -> str:
    """Detect commit type from changed files."""
    types = {}

    for f in files:
        matched = False
        for pattern, ctype in FILE_TYPE_MAP.items():
            if pattern in f:
                types[ctype] = types.get(ctype, 0) + 1
                matched = True
                break

        if not matched:
            if f.endswith(".py"):
                types["feat"] = types.get("feat", 0) + 1
            else:
                types["chore"] = types.get("chore", 0) + 1

    if not types:
        return "chore"

    # Return most common type
    return max(types.items(), key=lambda x: x[1])[0]


def detect_scope(files: list) -> str:
    """Detect scope from changed files."""
    dirs = set()
    for f in files:
        parts = Path(f).parts
        if len(parts) > 1:
            dirs.add(parts[0])

    # Common scopes
    if "src" in dirs:
        return "src"
    if "docs" in dirs:
        return "docs"
    if ".github" in dirs:
        return "ci"

    # Return largest directory
    if dirs:
        return sorted(dirs)[0]
    return ""


def generate_description(files: list, diff_summary: str) -> str:
    """Generate commit description."""
    if not files:
        return "No changes"

    # Use first changed file as basis
    first_file = files[0]

    # Check for common patterns
    if len(files) == 1:
        # Single file change - use filename
        name = Path(first_file).stem.replace("_", " ").replace("-", " ")
        return name[:50]

    # Multiple files
    if len(files) <= 3:
        names = [Path(f).stem[:20] for f in files[:3]]
        return ", ".join(names)

    return f"Update {len(files)} files"


def suggest_commit_message(files: list) -> dict:
    """Generate a commit message suggestion."""
    ctype = detect_type(files)
    scope = detect_scope(files)
    diff_summary = get_diff_summary()
    description = generate_description(files, diff_summary)

    # Build message
    if scope:
        msg = f"{ctype}({scope}): {description}"
    else:
        msg = f"{ctype}: {description}"

    # Add body with stats
    body = f"\n\n{diff_summary}" if diff_summary else ""

    return {
        "type": ctype,
        "scope": scope,
        "message": msg,
        "body": body,
        "full": msg + body,
    }


def auto_commit(message: str, amend: bool = False) -> bool:
    """Perform auto-commit."""
    cmd = ["git", "commit"]
    if amend:
        cmd.append("--amend")
    cmd.extend(["-m", message])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return False

    print(f"✅ Committed: {message[:60]}...")
    return True


def main():
    parser = argparse.ArgumentParser(description="Auto-Commit")
    parser.add_argument("--commit", action="store_true", help="Auto-commit with suggested message")
    parser.add_argument("--amend", action="store_true", help="Amend last commit")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be committed")

    args = parser.parse_args()

    files = get_changed_files()

    if not files:
        print("No changes to commit")
        sys.exit(0)

    print("📝 Auto-Commit")
    print("=" * 40)
    print(f"Changed files ({len(files)}):")
    for f in files[:10]:
        print(f"  - {f}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")
    print()

    suggestion = suggest_commit_message(files)

    print("Suggested commit:")
    print(f"  Type: {suggestion['type']}")
    if suggestion["scope"]:
        print(f"  Scope: {suggestion['scope']}")
    print()
    print(f"Message:")
    print(f"  {suggestion['message']}")
    print()

    if args.commit or args.amend:
        if args.dry_run:
            print("(dry-run mode - no commit made)")
        else:
            auto_commit(suggestion["full"], amend=args.amend)
    else:
        print("Run with --commit to commit, --amend to amend")


if __name__ == "__main__":
    main()
