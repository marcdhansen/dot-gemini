import subprocess
import re
from pathlib import Path
from typing import Optional
from .common import check_tool_available


def check_workspace_integrity(*args) -> tuple[bool, list[str]]:
    """Verify workspace integrity by checking for mandatory directories and files."""
    if args:
        if args[0] == "task":
            # Check for task.md in brain directory
            brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
            if brain_dir.exists():
                session_dirs = sorted(
                    [d for d in brain_dir.iterdir() if d.is_dir()],
                    key=lambda x: x.stat().st_mtime,
                    reverse=True,
                )[:1]
                for d in session_dirs:
                    if (d / "task.md").exists():
                        return True, [str(d / "task.md")]
            return False, ["task.md not found in recent brain directory"]
        if args[0] == "cleanup":
            # Verify temporary artifacts like task.md are NOT in root
            temp_files = ["task.md", "debrief.md"]
            present = [f for f in temp_files if (Path.cwd() / f).exists()]
            if present:
                return False, present
            return True, ["No temporary artifacts found"]

    mandatory_paths = [
        Path(".git"),
        Path(".agent"),
        Path(".beads"),
    ]

    missing = []
    for path in mandatory_paths:
        if not path.exists():
            missing.append(str(path))

    return len(missing) == 0, missing


def check_git_status(turbo: bool = False) -> tuple[bool, str]:
    """Check if git working directory is clean. Detects code changes for Turbo escalation."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            changes = result.stdout.strip()
            if not changes:
                return True, "Working directory clean"

            # Detect code changes (.py, .sh, .js, .ts, etc.)
            code_extensions = {".py", ".sh", ".js", ".ts", ".go", ".c", ".cpp"}
            code_changes = []
            for line in result.stdout.split("\n"):
                if len(line) > 3:
                    file_path = line[3:]
                    if any(file_path.endswith(ext) for ext in code_extensions):
                        code_changes.append(file_path)

            if turbo:
                if code_changes:
                    return (
                        False,
                        f"ESCALATION REQUIRED: Code changes detected in Turbo Mode: {', '.join(code_changes)}. Please switch to Full SOP.",
                    )
                else:
                    return True, "Metadata changes only (Turbo safe)"

            return False, f"Uncommitted changes:\n{changes}"
        return False, "Git command failed"
    except Exception as e:
        return False, f"Git check failed: {e}"


def check_sop_infrastructure_changes() -> tuple[bool, str]:
    """Check if changes involve SOP infrastructure (Orchestrator, skills, SOP docs).

    SOP infrastructure changes require Full Mode escalation per the SOP Modification workflow.

    Returns:
        tuple[bool, str]: (requires_full_mode, status_message)
    """
    try:
        # Get list of changed files from git diff
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            # Try checking staged changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                timeout=10,
            )

        if result.returncode != 0:
            return False, "Could not determine changed files (skipping SOP infrastructure check)"

        changed_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Define SOP infrastructure patterns
        sop_patterns = [
            ".gemini/antigravity/skills/Orchestrator/scripts/",
            ".gemini/antigravity/skills/",  # Any skill script
            "/SKILL.md",  # Any SKILL.md file
            ".agent/docs/SOP_COMPLIANCE_CHECKLIST.md",
            ".agent/docs/sop/",
            ".gemini/antigravity/skills/sop-modification/",
        ]

        sop_files = []
        for file_path in changed_files:
            if not file_path:
                continue
            # Check if file matches any SOP infrastructure pattern
            if any(pattern in file_path for pattern in sop_patterns):
                sop_files.append(file_path)

        if sop_files:
            files_str = "\n  - ".join(sop_files)
            return (
                True,
                f"SOP infrastructure changes detected (Full Mode required):\n  - {files_str}",
            )

        return False, "No SOP infrastructure changes detected"

    except subprocess.TimeoutExpired:
        return False, "Git command timed out (skipping SOP infrastructure check)"
    except Exception as e:
        return False, f"SOP infrastructure check error (skipping): {e}"


def check_branch_info(*args) -> tuple[str, bool]:
    """Get current branch and check if it's a feature branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            is_feature = branch.startswith(("agent/", "feature/", "chore/"))
            return branch, is_feature
        return "unknown", False
    except Exception:
        return "unknown", False


def get_active_issue_id() -> Optional[str]:
    """Identify the active beads issue ID."""
    # Try branch name first
    branch, _ = check_branch_info()
    if branch.startswith(("agent/", "feature/", "chore/")):
        parts = branch.split("/")
        if len(parts) > 1:
            return parts[-1]

    # Try bd ready
    if check_tool_available("bd"):
        try:
            result = subprocess.run(["bd", "ready"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                # Skip header and empty lines, find first line with ID: Title pattern
                for line in lines:
                    line = line.strip()
                    if not line or "Ready work" in line:
                        continue
                    # Match pattern like "1. [● P0] [task] issue-id: Title"
                    match = re.search(r"([a-zA-Z0-9-]+):", line)
                    if match:
                        return match.group(1).strip()
        except Exception:
            pass
    return None


def validate_atomic_commits() -> tuple[bool, list[str]]:
    """Validate atomic commit requirements per SOP git-workflow."""
    errors = []

    try:
        # Determine base branch for comparison (prefer origin/main, fallback to main)
        base_branch = "origin/main"
        res = subprocess.run(
            ["git", "rev-parse", "--verify", base_branch],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            base_branch = "main"
            res = subprocess.run(
                ["git", "rev-parse", "--verify", base_branch],
                capture_output=True,
                text=True,
            )
            if res.returncode != 0:
                base_branch = "master"
                res = subprocess.run(
                    ["git", "rev-parse", "--verify", base_branch],
                    capture_output=True,
                    text=True,
                )

        if res.returncode != 0:
            errors.append(
                "Could not identify base branch (main/master/origin/main) for comparison."
            )
            return False, errors

        # Check 1: Count commits ahead of base branch
        result = subprocess.run(
            ["git", "log", "--oneline", f"{base_branch}..HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            errors.append(f"Could not compare with {base_branch}.")
            return False, errors

        commits = [line for line in result.stdout.strip().split("\n") if line]
        commit_count = len(commits)

        if commit_count == 0:
            current_branch, _ = check_branch_info()
            if current_branch in ["main", "master", "origin/main"]:
                upstream = "@{u}"
                res = subprocess.run(
                    ["git", "rev-parse", "--verify", upstream], capture_output=True, text=True
                )
                if res.returncode == 0:
                    result = subprocess.run(
                        ["git", "log", "--oneline", f"{upstream}..HEAD"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    commits = [line for line in result.stdout.strip().split("\n") if line]
                    commit_count = len(commits)
                    if commit_count == 0:
                        return True, []

        if commit_count > 1:
            errors.append(
                f"Multiple commits detected ({commit_count}). Squash required before merging to ensure atomic history."
            )
            errors.append(f"  Run: git rebase -i {base_branch}")

        # Check 2: Detect merge commits
        result = subprocess.run(
            ["git", "log", "--merges", f"{base_branch}..HEAD", "--oneline"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            merge_commits = result.stdout.strip().split("\n")
            errors.append(
                f"Merge commits not allowed ({len(merge_commits)} detected). Merge commits are strictly forbidden by SOP."
            )
            errors.append(f"  Action: Rebase onto {base_branch} instead of merging it.")
            errors.append(f"  Run: git rebase {base_branch}")
        elif result.returncode != 0:
            errors.append(f"Merge commit check failed for range {base_branch}..HEAD")

        # Check 3 & 4: Validate commit message format
        if commit_count == 1:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                commit_msg = result.stdout.strip()
                issue_pattern = r"\[([a-zA-Z0-9-.]+)\]"
                if not re.search(issue_pattern, commit_msg):
                    errors.append("Commit message must include Beads issue ID in format [issue-id]")
                conv_pattern = (
                    r"^(feat|fix|docs|chore|test|refactor|perf|ci|build|style)(\([^)]+\))?: .+"
                )
                if not re.match(conv_pattern, commit_msg.split("\n")[0]):
                    errors.append("Commit message does not follow conventional commit format")

        return len(errors) == 0, errors

    except Exception as e:
        errors.append(f"Atomic commit validation system error: {e}")
        return False, errors
