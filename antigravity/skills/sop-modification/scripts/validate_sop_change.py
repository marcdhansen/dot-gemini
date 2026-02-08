#!/usr/bin/env python3
"""
Pre-commit hook/validation script to block SOP gate changes without tests.
"""
import subprocess
import sys
from pathlib import Path

# Keywords that indicate a mandatory gate
GATE_KEYWORDS = ["MANDATORY", "MUST", "BLOCKER", "🔒"]

def get_modified_files():
    """Get list of modified files in the current git repository."""
    result = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()

def check_for_gate_changes(file_path):
    """Check if a file contains mandatory gate changes."""
    content = Path(file_path).read_text()
    for kw in GATE_KEYWORDS:
        if kw in content:
            return True
    return False

def find_test_for_gate(file_path):
    """Try to find a corresponding test for the SOP gate file."""
    # Pattern: ~/.agent/docs/sop/tdd-workflow.md -> tests/gatekeeper/test_sop_gate_tdd_workflow.py
    stem = Path(file_path).stem.replace("-", "_")
    test_file_name = f"test_sop_gate_{stem}.py"
    
    # Check in multiple locations
    possible_paths = [
        Path("tests/gatekeeper") / test_file_name,
        Path("tests") / test_file_name,
    ]
    
    for p in possible_paths:
        if p.exists():
            return p
    return None

def main():
    modified_files = get_modified_files()
    sop_files = [f for f in modified_files if f.endswith(".md") and (".agent/docs" in f or "AGENTS.md" in f)]
    
    if not sop_files:
        print("✅ No SOP documentation changes detected.")
        sys.exit(0)
    
    missing_tests = []
    for f in sop_files:
        if check_for_gate_changes(f):
            test_path = find_test_for_gate(f)
            if not test_path:
                missing_tests.append(f)
    
    if missing_tests:
        print("❌ SOP gate modified without corresponding test!")
        print("Mandatory gates require TDD verification.")
        for f in missing_tests:
            print(f"  - {f}")
        print("\nPlease create a test in tests/gatekeeper/ before committing.")
        sys.exit(1)
    
    print("✅ All SOP gate changes have corresponding tests.")
    sys.exit(0)

if __name__ == "__main__":
    main()
