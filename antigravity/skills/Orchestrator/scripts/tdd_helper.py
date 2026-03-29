#!/usr/bin/env python3
"""
TDD Helper - Test-Driven Development Automation

Performs TDD-related automation:
1. Scaffold test templates for new modules
2. Detect missing tests for new code
3. Enforce test-first workflow
4. Run tests with coverage

Usage:
    python tdd_helper.py scaffold <module_path>
    python tdd_helper.py check
    python tdd_helper.py run
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


TEST_TEMPLATE = '''#!/usr/bin/env python3
"""Tests for {module_name}"""

import pytest
from {import_path} import {class_name}


class Test{class_name}:
    """Test cases for {class_name}."""

    def test_placeholder(self):
        """Placeholder test - implement actual tests."""
        assert True, "Implement your first test"


# Add more test methods:
# def test_something(self):
#     result = {class_name}().method()
#     assert result == expected
'''

SCAFFOLD_TEMPLATE = '''#!/usr/bin/env python3
"""Auto-generated TDD test for {module_name}

Run with: python -m pytest {test_file} -v
"""

import pytest
from {import_path} import {class_name}


class Test{class_name}:
    """Test cases for {class_name}."""

    @pytest.fixture
    def instance(self):
        """Create an instance for testing."""
        return {class_name}()

    def test_creation(self, instance):
        """Test {class_name} can be created."""
        assert instance is not None

    # TODO: Add your test-first tests below
    # Follow Red-Green workflow:
    # 1. Write failing test first (Red)
    # 2. Implement code to pass (Green)  
    # 3. Refactor
'''


def get_module_info(module_path: str) -> dict:
    """Extract module and class info from path."""
    path = Path(module_path)

    if not path.exists():
        return {"error": f"Module not found: {module_path}"}

    module_name = path.stem

    # Try to find class definitions
    try:
        content = path.read_text()
        classes = re.findall(r"^class (\w+)", content, re.MULTILINE)
    except:
        classes = []

    return {
        "module_name": module_name,
        "module_path": str(path),
        "classes": classes,
    }


def scaffold_test(module_path: str, force: bool = False) -> str:
    """Generate a test file for the given module."""
    info = get_module_info(module_path)

    if "error" in info:
        return info["error"]

    # Determine test path
    module_path = Path(module_path)
    test_dir = module_path.parent / "tests"

    # If module is in tests/, put test alongside
    if "tests" in module_path.parts:
        test_dir = module_path.parent

    test_dir.mkdir(exist_ok=True)

    test_name = f"test_{module_path.stem}.py"
    test_path = test_dir / test_name

    if test_path.exists() and not force:
        return f"Test already exists: {test_path}"

    # Determine import path
    parts = list(module_path.parts)
    # Find src/ or similar root
    try:
        src_idx = parts.index("src")
        import_parts = parts[src_idx:]
        import_path = ".".join(import_parts).replace(".py", "")
    except ValueError:
        # Fallback: use relative
        import_path = module_path.stem

    # Use first class if found, else use module name
    class_name = (
        info["classes"][0] if info["classes"] else info["module_name"].title().replace("_", "")
    )

    content = SCAFFOLD_TEMPLATE.format(
        module_name=info["module_name"],
        import_path=import_path,
        class_name=class_name,
        test_file=test_path.name,
    )

    test_path.write_text(content)
    return f"✅ Created test: {test_path}"


def check_missing_tests() -> str:
    """Check for new code files without tests."""
    # Get list of .py files in src/
    src_dir = Path("src")
    if not src_dir.exists():
        return "No src/ directory found"

    py_files = list(src_dir.rglob("*.py"))
    test_files = list(src_dir.rglob("test_*.py"))
    test_files.extend(list(src_dir.rglob("*_test.py")))

    # Extract tested modules
    tested = set()
    for tf in test_files:
        # Extract module name from test name
        name = tf.stem.replace("test_", "").replace("_test", "")
        tested.add(name)

    # Find untested
    missing = []
    for pf in py_files:
        if pf.name.startswith("__"):
            continue
        module_name = pf.stem
        if module_name not in tested and f"test_{module_name}" not in [t.name for t in test_files]:
            missing.append(str(pf.relative_to(".")))

    if not missing:
        return "✅ All modules appear to have tests"

    lines = [f"⚠️ {len(missing)} modules without tests:"]
    for m in missing[:10]:
        lines.append(f"  • {m}")

    return "\n".join(lines)


def run_tests(args: list) -> tuple[int, str]:
    """Run pytest with coverage."""
    cmd = ["python", "-m", "pytest"]
    if "--cov" not in " ".join(args):
        cmd.extend(["--cov=.beads", "--cov-report=term-missing", "-v"])
    else:
        cmd.extend(args)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description="TDD Helper")
    subparsers = parser.add_subparsers(dest="command")

    # scaffold command
    scaffold_parser = subparsers.add_parser("scaffold", help="Generate test template for a module")
    scaffold_parser.add_argument("module", help="Path to module (e.g., src/foo.py)")
    scaffold_parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing test"
    )

    # check command
    subparsers.add_parser("check", help="Check for missing tests")

    # run command
    run_parser = subparsers.add_parser("run", help="Run tests with coverage")
    run_parser.add_argument("args", nargs="*", help="Additional pytest args")

    args = parser.parse_args()

    if args.command == "scaffold":
        result = scaffold_test(args.module, args.force)
        print(result)

    elif args.command == "check":
        print(check_missing_tests())

    elif args.command == "run":
        code, output = run_tests(args.args)
        print(output)
        sys.exit(code)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
