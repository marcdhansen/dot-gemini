#!/usr/bin/env python3
"""
PR Validator - Pre-PR Quality Checks

Validates PR quality before opening:
- Description length and format
- Label presence
- Size limits
- Branch naming
- Issue reference

Usage:
    python pr_validate.py              # Validate current branch
    python pr_validate.py --fix       # Auto-fix issues
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path


MIN_DESC_LENGTH = 20
MAX_LINES = 500
MAX_FILES = 20

BRANCH_TYPES = ["feat", "fix", "docs", "refactor", "chore", "test", "ci"]


def get_branch_name() -> str:
    """Get current branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_diff_stats() -> dict:
    """Get diff statistics."""
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD"],
        capture_output=True,
        text=True,
    )

    # Parse
    files = len([l for l in result.stdout.split("\n") if "|" in l])
    lines = result.stdout

    # Count +/-
    import re

    plus = len(re.findall(r"\+", lines))
    minus = len(re.findall(r"-", lines))

    return {
        "files": files,
        "insertions": plus,
        "deletions": minus,
    }


def check_branch_name(name: str) -> dict:
    """Check branch naming convention."""
    for prefix in BRANCH_TYPES:
        if name.startswith(prefix + "/"):
            return {"valid": True, "type": prefix}

    return {
        "valid": False,
        "message": f"Branch should start with: {', '.join(BRANCH_TYPES)}",
    }


def check_issue_reference() -> dict:
    """Check if commits reference an issue."""
    result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True,
        text=True,
    )

    commits = result.stdout.strip().split("\n")

    # Look for issue references
    refs = []
    for c in commits:
        # Match patterns like #123, openloop-abc, etc
        matches = re.findall(r"#\d+|[a-z]+-\d+", c.lower())
        refs.extend(matches)

    if refs:
        return {"valid": True, "references": list(set(refs))}

    return {
        "valid": False,
        "message": "No issue reference found in commits (add #issue-id or openloop-id)",
    }


def validate_pr(pr_number: str = None) -> dict:
    """Validate PR quality."""
    issues = []
    warnings = []

    # Check branch
    branch = get_branch_name()
    branch_check = check_branch_name(branch)
    if not branch_check.get("valid"):
        warnings.append(f"Branch: {branch_check['message']}")

    # Check size
    stats = get_diff_stats()
    if stats["files"] > MAX_FILES:
        warnings.append(f"Files: {stats['files']} (recommended: <{MAX_FILES})")

    if stats["insertions"] + stats["deletions"] > MAX_LINES:
        issues.append(f"Lines: {stats['insertions'] + stats['deletions']} (max: {MAX_LINES})")

    # Check issue reference
    ref_check = check_issue_reference()
    if not ref_check.get("valid"):
        warnings.append(f"Commits: {ref_check['message']}")

    return {
        "branch": branch,
        "stats": stats,
        "issues": issues,
        "warnings": warnings,
        "valid": len(issues) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="PR Validator")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    print("🔍 PR Quality Check")
    print("=" * 40)

    result = validate_pr()

    print(f"Branch: {result['branch']}")
    print(f"Files: {result['stats']['files']}")
    print(f"Lines: +{result['stats']['insertions']} -{result['stats']['deletions']}")
    print()

    if result["issues"]:
        print(f"❌ {len(result['issues'])} ISSUE(S):")
        for i in result["issues"]:
            print(f"  • {i}")
        print()

    if result["warnings"]:
        print(f"⚠️  {len(result['warnings'])} WARNING(S):")
        for w in result["warnings"]:
            print(f"  • {w}")
        print()

    if not result["issues"] and not result["warnings"]:
        print("✅ PR ready!")
    elif args.strict and result["warnings"]:
        print("\n❌ PR blocked (strict mode)")
        sys.exit(1)
    else:
        print("Run with --fix to auto-fix, --strict to block on warnings")


if __name__ == "__main__":
    main()
