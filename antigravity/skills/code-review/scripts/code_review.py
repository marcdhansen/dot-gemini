#!/usr/bin/env python3
import sys
import os
import subprocess
import yaml
from pathlib import Path

def is_non_interactive():
    return (
        not sys.stdin.isatty() or
        os.getenv("CI") or 
        os.getenv("GITHUB_ACTIONS") or
        os.getenv("AUTOMATED_MODE")
    )

def safe_input(prompt, default=None, choices=None):
    if is_non_interactive():
        return default or (choices[0] if choices else "auto")
    
    try:
        response = input(f"{prompt} ").strip()
        if choices and response not in choices:
            print(f"⚠️ Invalid choice. Please select from: {choices}")
            return safe_input(prompt, default, choices)
        return response if response else default
    except (EOFError, KeyboardInterrupt):
        return default

class CodeReviewer:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "defaults.yaml"
        self.config = self._load_config()
        self.review_status = "PENDING"

    def _load_config(self):
        defaults = {
            "max_diff_lines": 500,
            "require_tests": True,
            "block_on_request_changes": True,
            "checklist": []
        }
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                return {**defaults, **user_config}
        return defaults

    def get_diff(self):
        try:
            # Check staged and unstaged changes
            diff = subprocess.check_output(["git", "diff", "HEAD"], text=True)
            return diff
        except Exception:
            return ""

    def validate_size(self, diff):
        lines = len(diff.splitlines())
        max_lines = self.config.get("max_diff_lines", 500)
        if lines > max_lines:
            print(f"⚠️ Large PR detected: {lines} lines (Limit: {max_lines})")
            return False
        return True

    def check_tests(self):
        # Heuristic: Look for new files and check if matching test files exist
        try:
            new_files = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], text=True).splitlines()
            missing_tests = []
            for f in new_files:
                if f.endswith(".py") and "/tests/" not in f and not f.startswith("tests/"):
                    test_file = f.replace(".py", "_test.py") # Simple heuristic
                    if not os.path.exists(test_file):
                        # Try another pattern
                        p = Path(f)
                        alt_test = p.parent / "tests" / f"test_{p.name}"
                        if not alt_test.exists():
                            missing_tests.append(f)
            
            if missing_tests:
                print(f"⚠️ New code files might be missing tests: {missing_tests}")
                return False
            return True
        except Exception:
            return True

    def run_interactive_checklist(self):
        print("\n📝 CODE REVIEW CHECKLIST")
        print("========================")
        results = []
        for item in self.config.get("checklist", []):
            ans = safe_input(f"[ ] {item} (y/n):", default="y", choices=["y", "n", "Y", "N"])
            results.append(ans.lower() == "y")
        
        if all(results):
            return "APPROVE"
        else:
            return "REQUEST_CHANGES"

    def execute(self):
        diff = self.get_diff()
        if not diff:
            print("✅ No changes detected for review.")
            return True

        size_ok = self.validate_size(diff)
        tests_ok = self.check_tests()

        if is_non_interactive():
            if size_ok and tests_ok:
                print("🤖 Auto-Review: Pass")
                return True
            else:
                print("🤖 Auto-Review: Blocked due to size or missing tests")
                return False

        status = self.run_interactive_checklist()
        if status == "APPROVE":
            print("\n✅ Review APPROVED.")
            return True
        else:
            print("\n❌ Review: CHANGES REQUESTED.")
            if self.config.get("block_on_request_changes", True):
                print("🚨 Blocking finalization per policy.")
                return False
            return True

if __name__ == "__main__":
    reviewer = CodeReviewer()
    if not reviewer.execute():
        sys.exit(1)
