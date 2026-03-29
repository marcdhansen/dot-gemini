#!/usr/bin/env python3
"""
Guardrails - Pre-commit Safety Checks

Blocks dangerous patterns before commit:
- Secrets/keys in code
- Hardcoded credentials
- TODO without issue reference
- Large files
- Missing tests for new code

Usage:
    python guardrails.py           # Run checks
    python guardrails.py --fix    # Auto-fix safe issues
    python guardrails.py --enforce  # Exit with error if issues found
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


SECRET_PATTERNS = [
    (r'password\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded password"),
    (r'api_key\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded API key"),
    (r'secret\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded secret"),
    (r'token\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded token"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"-----BEGIN (RSA|EC|DSA) PRIVATE KEY-----", "Private key"),
]

TODO_PATTERN = r"TODO\s*\("
TODO_FIX_PATTERN = r"todo!\(["

UNSAFE_PATTERNS = [
    (r"eval\s*\(", "eval() is dangerous"),
    (r"exec\s*\(", "exec() is dangerous"),
    (r"os\.system\s*\(", "os.system() is dangerous"),
    (r"subprocess\.call\s*\([^,]+shell\s*=\s*True", "shell=True is dangerous"),
]

MAX_FILE_SIZE = 100_000  # 100KB


def get_staged_files() -> list:
    """Get list of staged files."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--staged"],
        capture_output=True,
        text=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def check_file(filepath: str) -> list:
    """Check a file for issues."""
    issues = []

    path = Path(filepath)

    # Check file size
    try:
        size = path.stat().st_size
        if size > MAX_FILE_SIZE:
            issues.append(
                {
                    "type": "size",
                    "severity": "warning",
                    "file": filepath,
                    "message": f"File too large: {size / 1024:.1f}KB (max {MAX_FILE_SIZE / 1024}KB)",
                }
            )
    except:
        pass

    # Skip binary files
    if path.suffix not in [".py", ".js", ".ts", ".md", ".yaml", ".yml", ".json", ".sh"]:
        return issues

    try:
        content = path.read_text()
    except:
        return issues

    # Check for secrets
    for pattern, desc in SECRET_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(
                {
                    "type": "security",
                    "severity": "error",
                    "file": filepath,
                    "message": f"Potential secret detected: {desc}",
                }
            )

    # Check for TODOs without issue reference
    todos = re.findall(TODO_PATTERN, content)
    if todos:
        # Check if they have issue references
        has_ref = re.search(r"TODO\([^)]*[-:]?[a-z]+-\d+", content, re.IGNORECASE)
        if not has_ref:
            issues.append(
                {
                    "type": "todo",
                    "severity": "warning",
                    "file": filepath,
                    "message": f"TODO without issue reference ({len(todos)} found)",
                }
            )

    # Check for unsafe patterns
    for pattern, desc in UNSAFE_PATTERNS:
        if re.search(pattern, content):
            issues.append(
                {
                    "type": "security",
                    "severity": "error",
                    "file": filepath,
                    "message": f"Unsafe pattern: {desc}",
                }
            )

    return issues


def check_tests_for_new_code(files: list) -> list:
    """Check if new code has corresponding tests."""
    issues = []

    py_files = [f for f in files if f.endswith(".py") and "test" not in f]
    test_files = [f for f in files if "test" in f]

    for f in py_files:
        # Check if test exists
        test_name = f.replace(".py", "_test.py")
        test_name_alt = f"{Path(f).parent}/test_{Path(f).stem}.py"

        if not Path(test_name).exists() and not Path(test_name_alt).exists():
            if not any(t in f for t in ["test_", "_test.py", "tests/"]):
                issues.append(
                    {
                        "type": "test",
                        "severity": "warning",
                        "file": f,
                        "message": "No corresponding test file found",
                    }
                )

    return issues


def main():
    parser = argparse.ArgumentParser(description="Guardrails - Pre-commit Safety Checks")
    parser.add_argument("--fix", action="store_true", help="Auto-fix safe issues")
    parser.add_argument("--enforce", action="store_true", help="Exit with error if issues found")
    parser.add_argument("--warn-only", action="store_true", help="Warn but don't fail")

    args = parser.parse_args()

    files = get_staged_files()

    if not files:
        print("✅ No staged files to check")
        sys.exit(0)

    print("🛡️ Guardrails - Pre-commit Checks")
    print("=" * 40)
    print(f"Checking {len(files)} file(s)...")
    print()

    all_issues = []

    for f in files:
        issues = check_file(f)
        all_issues.extend(issues)

    # Check for missing tests
    test_issues = check_tests_for_new_code(files)
    all_issues.extend(test_issues)

    if not all_issues:
        print("✅ All checks passed!")
        sys.exit(0)

    # Group by severity
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]

    if errors:
        print(f"❌ {len(errors)} ERROR(S):")
        for i in errors:
            print(f"  [{i['type']}] {i['file']}: {i['message']}")
        print()

    if warnings:
        print(f"⚠️  {len(warnings)} WARNING(S):")
        for i in warnings:
            print(f"  [{i['type']}] {i['file']}: {i['message']}")
        print()

    # Exit based on args
    if args.enforce and errors:
        print("\n❌ Commit blocked due to errors")
        sys.exit(1)

    if not args.warn_only and (errors or warnings):
        print("\n⚠️  Run with --warn-only to bypass, or --enforce to block")
        sys.exit(1)


if __name__ == "__main__":
    main()
