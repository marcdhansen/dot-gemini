#!/usr/bin/env python3
"""
Browser Manager Fix for Non-Interactive Environments
Patches browser_manager.py to handle EOF errors in CI/automated environments
"""

import sys
import os
from pathlib import Path


def patch_browser_manager():
    """Apply non-interactive fixes to browser_manager.py"""

    browser_manager_path = Path(__file__).parent / "scripts" / "browser_manager.py"

    if not browser_manager_path.exists():
        print(f"❌ Browser manager not found at {browser_manager_path}")
        return False

    # Read the original file
    with open(browser_manager_path, "r") as f:
        content = f.read()

    # Check if already patched
    if "Non-interactive mode detected" in content:
        print("✅ Browser manager already patched")
        return True

    # Find the input line and add non-interactive check before it
    lines = content.split("\n")
    patched_lines = []

    for i, line in enumerate(lines):
        if "response = input(prompt).strip().lower()" in line:
            # Add non-interactive check before this line
            indent = len(line) - len(line.lstrip())
            spaces = " " * indent

            patch_lines = [
                f"{spaces}# Check for non-interactive environment",
                f"{spaces}is_non_interactive = (",
                f"{spaces}    not sys.stdin.isatty() or",
                f"{spaces}    os.getenv('CI') or",
                f"{spaces}    os.getenv('GITHUB_ACTIONS') or",
                f"{spaces}    os.getenv('AUTOMATED_MODE')",
                f"{spaces})",
                f"{spaces}",
                f"{spaces}if is_non_interactive:",
                f'{spaces}    print(f"\\n{{Colors.YELLOW}}🤖 Non-interactive mode - Auto-approving cleanup{{Colors.END}}")',
                f"{spaces}    response = 'y'  # Auto-approve",
                f"{spaces}else:",
                spaces + "    try:",
            ]

            for patch_line in patch_lines:
                patched_lines.append(patch_line)

            # Indent the original try block
            patched_lines.append(spaces + "        " + line.strip())

        elif (
            "except EOFError:" in line and "Permission timeout" in lines[i + 1]
            if i + 1 < len(lines)
            else False
        ):
            # This is part of the input exception handling - adjust indentation
            indent = len(line) - len(line.lstrip())
            spaces = " " * indent
            patched_lines.append(spaces + "    " + line.strip())
        elif (
            "except KeyboardInterrupt:" in line
            and "Operation cancelled by user" in lines[i + 1]
            if i + 1 < len(lines)
            else False
        ):
            # Also adjust this exception handling
            indent = len(line) - len(line.lstrip())
            spaces = " " * indent
            patched_lines.append(spaces + "    " + line.strip())
        else:
            patched_lines.append(line)

    # Write the patched version
    with open(browser_manager_path, "w") as f:
        f.write("\n".join(patched_lines))

    print("✅ Browser manager patched for non-interactive environments")
    return True


if __name__ == "__main__":
    patch_browser_manager()
