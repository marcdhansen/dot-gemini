#!/usr/bin/env python3
"""Check PR size against defined limits."""

import subprocess
import sys
from pathlib import Path

LIMITS = {
    "code": {"soft": 400, "hard": 1000},
    "docs": {"soft": 800, "hard": 2000},
    "mechanical": {"soft": 800, "hard": 2000},
}


def get_diff_stats():
    """Get diff statistics from main branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "main", "--shortstat"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        if not output:
            return None
        parts = output.split()
        total = int(parts[-2]) if len(parts) >= 2 else 0
        return total
    except subprocess.CalledProcessError:
        return None


def detect_change_type():
    """Detect type of changes (code/docs/mechanical)."""
    try:
        result = subprocess.run(
            ["git", "diff", "main", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = result.stdout.strip().split("\n")

        doc_extensions = {".md", ".txt", ".rst"}
        doc_files = [f for f in files if any(f.endswith(ext) for ext in doc_extensions)]

        mechanical_patterns = ["rename", "format", ".pre-commit"]
        mechanical = any(any(p in f.lower() for p in mechanical_patterns) for f in files)

        if mechanical:
            return "mechanical"
        elif len(doc_files) > len(files) / 2:
            return "docs"
        else:
            return "code"
    except subprocess.CalledProcessError:
        return "code"


def check_size():
    """Check if PR size is within limits."""
    total = get_diff_stats()
    if total is None:
        print("⚠️ Could not determine diff (maybe already on main?)")
        return 0

    change_type = detect_change_type()
    limits = LIMITS[change_type]

    print(f"📊 Change type: {change_type}")
    print(f"📏 Lines changed: {total}")
    print(f"   Soft limit: {limits['soft']}")
    print(f"   Hard limit: {limits['hard']}")
    print()

    if total > limits["hard"]:
        print(f"❌ BLOCKED: Exceeds hard limit ({limits['hard']})")
        print("   Split into smaller PRs")
        return 1
    elif total > limits["soft"]:
        print(f"⚠️ WARNING: Exceeds soft limit ({limits['soft']})")
        print("   Consider splitting")
        return 0
    else:
        print("✅ OK: Within limits")
        return 0


if __name__ == "__main__":
    sys.exit(check_size())
