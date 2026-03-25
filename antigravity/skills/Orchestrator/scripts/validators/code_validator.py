import subprocess
from pathlib import Path


def validate_tdd_compliance() -> tuple[bool, str]:
    """Validate that code/config changes are preceded by or accompanied by test changes.

    Enforces the 'Spec-Driven TDD' rule from tdd-workflow.md.
    Skips check for docs-only changes (they can't break anything).
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return False, "Failed to get git status"

        lines = result.stdout.strip().split("\n")
        if not lines or (len(lines) == 1 and not lines[0]):
            return True, "No changes detected"

        code_files = []
        test_files = []
        doc_files = []

        # Extensions that count as code (require TDD)
        code_exts = {".py", ".js", ".ts", ".go", ".c", ".cpp", ".java", ".rs", ".rb"}

        # Extensions that are docs (skip TDD)
        doc_exts = {".md", ".txt", ".rst", ".adoc"}

        # Extensions that are config (require TDD - can break production!)
        config_exts = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf"}

        for line in lines:
            if len(line) < 4:
                continue
            status = line[:2].strip()
            file_path = line[3:].strip()

            # Skip deleted files
            if status == "D":
                continue

            ext = Path(file_path).suffix

            # Check for test files first
            if "test" in file_path.lower() or file_path.startswith("tests/"):
                test_files.append(file_path)
            elif ext in doc_exts:
                doc_files.append(file_path)
            elif ext in code_exts or ext in config_exts:
                code_files.append(file_path)

        # If only docs changed, skip TDD check
        if doc_files and not code_files and not test_files:
            return True, "Docs-only changes - TDD check skipped"

        if not code_files and test_files:
            return (
                True,
                f"Red Phase: Test stubs detected without implementation ({', '.join(test_files)})",
            )

        if code_files and not test_files:
            return (
                False,
                f"TDD Violation: Implementation/config changes detected without corresponding tests: {', '.join(code_files)}",
            )

        return True, "TDD compliance verified (Balanced changes)"

    except Exception as e:
        return False, f"TDD validation error: {e}"
