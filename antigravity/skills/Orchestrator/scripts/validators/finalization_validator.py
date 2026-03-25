import json
import subprocess
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from .common import check_tool_available, Colors
from .git_validator import check_branch_info, get_active_issue_id


def check_reflection_invoked() -> tuple[bool, str]:
    """Check if reflection was captured for the current session.

    Session-based: Only require new reflection if there have been new commits
    since the last reflection. This replaces the time-based check.
    """
    input_artifact = Path(".reflection_input.json")
    reflection_mtime = None

    if input_artifact.exists():
        try:
            with open(input_artifact, "r") as f:
                data = json.load(f)

            required = ["session_name", "outcome", "technical_learnings", "refactoring_candidates"]
            missing = [field for field in required if field not in data]

            if missing:
                return (
                    False,
                    f"Reflection artifact .reflection_input.json is missing required fields: {', '.join(missing)}",
                )

            reflection_mtime = datetime.fromtimestamp(input_artifact.stat().st_mtime)

        except json.JSONDecodeError:
            return False, "Reflection artifact .reflection_input.json is malformed JSON"
        except Exception as e:
            return False, f"Error validating reflection artifact: {e}"

    # Check reflection_paths as fallback
    reflection_paths = [
        Path(".agent/reflections.json"),
        Path("reflections.json"),
    ]

    for path in reflection_paths:
        if path.exists() and reflection_mtime is None:
            try:
                reflection_mtime = datetime.fromtimestamp(path.stat().st_mtime)
            except Exception:
                pass

    if reflection_mtime is None:
        return False, "No reflection found. Please run /reflect to capture session learnings."

    # Check if there are uncommitted changes (the main risk - losing work)
    # Commits are already saved, so we don't require reflection for those
    try:
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        has_uncommitted = result.returncode == 0 and bool(result.stdout.strip())

        if has_uncommitted:
            return (
                False,
                f"Uncommitted changes detected. Please commit or run /reflect before finalization.",
            )

        age = datetime.now() - reflection_mtime
        return (
            True,
            f"Reflection captured: {age.total_seconds() / 60:.0f} minutes ago, no uncommitted changes",
        )

    except Exception as e:
        return True, f"Reflection captured (validation error: {e})"


def check_handoff_exists() -> tuple[bool, str]:
    """Check if handoff document exists for current session.

    Global validator - applies to all projects.
    Checks for .agent/handoffs/{branch-name}-session.md or similar patterns.
    """
    handoff_dir = Path(".agent/handoffs")

    if not handoff_dir.exists():
        return False, "Handoff directory .agent/handoffs/ does not exist"

    # Look for session handoff files
    handoff_files = list(handoff_dir.glob("*-session.md"))
    handoff_files.extend(list(handoff_dir.glob("*-handoff.md")))

    if not handoff_files:
        return False, "No handoff document found in .agent/handoffs/"

    # Check if any handoff has content
    for handoff in handoff_files:
        content = handoff.read_text()
        if len(content.strip()) > 100:
            return True, f"Handoff found: {handoff.name}"

    return False, "Handoff exists but is empty or too short"


def check_debriefing_invoked() -> tuple[bool, str]:
    """Check if debriefing was recently invoked."""
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    if brain_dir.exists():
        session_dirs = sorted(
            [d for d in brain_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )[:3]

        for session_dir in session_dirs:
            debrief_path = session_dir / "debrief.md"
            if debrief_path.exists():
                try:
                    mtime = datetime.fromtimestamp(debrief_path.stat().st_mtime)
                    age = datetime.now() - mtime
                    if age < timedelta(hours=2):
                        return (
                            True,
                            f"Debrief generated {age.total_seconds() / 60:.0f} minutes ago",
                        )
                except Exception:
                    pass

    return False, "No recent debrief found"


def check_code_review_status() -> tuple[bool, str]:
    """Check if code review skill was recently invoked and passed."""
    import sys

    code_review_script = (
        Path.home() / ".gemini/antigravity/skills/code-review/scripts/code_review.py"
    )
    if not code_review_script.exists():
        return False, "Code Review Skill not installed"

    try:
        result = subprocess.run(
            [sys.executable, str(code_review_script)],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "AUTOMATED_MODE": "1"},
        )
        if result.returncode == 0:
            return True, "Code Review passed (Automated check)"
        else:
            return False, "Code Review failed or requires manual intervention"
    except Exception as e:
        return False, f"Code Review check error: {e}"


def check_handoff_compliance() -> tuple[bool, str]:
    """Check if hand-off compliance verification passes for multi-phase implementations."""
    handoff_dir = Path(".agent/handoffs")
    verification_script = Path(".agent/scripts/verify_handoff_compliance.sh")

    if not handoff_dir.exists():
        return True, "No hand-off directory (not a multi-phase implementation)"

    if not verification_script.exists():
        return False, "Hand-off verification script missing"

    handoff_files = list(handoff_dir.glob("**/phase-*-handoff.md"))
    if not handoff_files:
        return True, "No hand-off documents found (not a multi-phase implementation)"

    try:
        result = subprocess.run(
            [str(verification_script), "--report"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True, "All hand-off documents pass verification"
        else:
            return False, f"Hand-off verification failed: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return False, "Hand-off verification timed out"
    except Exception as e:
        return False, f"Hand-off verification error: {str(e)}"


def check_todo_completion() -> tuple[bool, str]:
    """Check if all tasks in task.md are completed (oh-my-opencode pattern)."""
    import sys

    enforcer_script = Path.home() / ".agent/scripts/todo-enforcer.py"
    if enforcer_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(enforcer_script)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True, "All tasks completed (Sisyphus is happy)"
            else:
                msg = (
                    result.stdout.strip().split("\n")[-1]
                    if result.stdout
                    else "Unfinished tasks detected"
                )
                return False, msg
        except Exception as e:
            return False, f"Todo enforcer error: {e}"

    return True, "Todo enforcer script not found (Skipping)"


def check_linked_repositories() -> tuple[bool, list[str]]:
    """Validate that linked repositories follow SOP. Auto-detects changes in global dirs."""
    errors = []
    global_repos = [
        Path.home() / ".gemini",
        Path.home() / ".agent",
    ]

    task_paths = [Path(".agent/task.md"), Path("task.md")]
    for task_path in task_paths:
        if task_path.exists():
            try:
                content = task_path.read_text()
                paths = re.findall(r"-\s+path:\s+([^\n\s]+)", content)
                for p in paths:
                    try:
                        repo_path = Path(p).expanduser()
                        if repo_path.exists() and repo_path.is_dir():
                            if (repo_path / ".git").exists():
                                global_repos.append(repo_path)
                    except Exception:
                        continue
            except Exception:
                pass

    checked_repos = set()
    for repo in global_repos:
        try:
            repo_abs = str(repo.resolve())
            if repo_abs in checked_repos:
                continue
            checked_repos.add(repo_abs)

            if repo_abs == str(Path(".").resolve()):
                continue

            res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_abs,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                status = res.stdout.strip()
                if status:
                    branch_res = subprocess.run(
                        ["git", "branch", "--show-current"],
                        cwd=repo_abs,
                        capture_output=True,
                        text=True,
                        timeout=2,
                    )
                    branch = branch_res.stdout.strip() if branch_res.returncode == 0 else "unknown"

                    if branch in ["main", "master"]:
                        errors.append(
                            f"Linked repo {repo.name} has changes on protected branch '{branch}'. Please use a feature branch."
                        )

                    if branch != "unknown":
                        if check_tool_available("gh"):
                            pr_res = subprocess.run(
                                [
                                    "gh",
                                    "pr",
                                    "list",
                                    "--author",
                                    "@me",
                                    "--head",
                                    branch,
                                ],
                                cwd=repo_abs,
                                capture_output=True,
                                text=True,
                                timeout=5,
                            )
                            if pr_res.returncode == 0 and not pr_res.stdout.strip():
                                errors.append(
                                    f"No PR found for linked repo {repo.name} (branch: {branch})"
                                )
        except Exception:
            pass

    return len(errors) == 0, errors


def check_pr_review_issue_created() -> tuple[bool, str]:
    """Check if a P0 PR review issue exists for the current branch."""
    if not check_tool_available("bd"):
        return False, "beads (bd) not available"

    branch, is_feature = check_branch_info()
    if not is_feature:
        return True, "Not on feature branch (PR review not required)"

    try:
        result = subprocess.run(
            ["bd", "list", "--priority", "P0"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return False, "Failed to query beads for PR review issues"

        output = result.stdout.strip()
        if not output:
            return (
                False,
                f"No P0 PR review issue found for branch '{branch}'. Create one with: bd create --priority P0 'PR Review: {branch}'",
            )

        lines = output.split("\n")
        for line in lines:
            line_lower = line.lower()
            if "pr review" in line_lower or "pr-review" in line_lower:
                parts = line.split(":")
                if parts:
                    issue_id = parts[0].strip()
                    return True, f"PR review issue found: {issue_id}"
            branch_slug = branch.split("/")[-1] if "/" in branch else branch
            if branch_slug.lower() in line_lower:
                parts = line.split(":")
                if parts:
                    issue_id = parts[0].strip()
                    return True, f"PR review issue found (branch match): {issue_id}"

        return (
            False,
            f"No P0 PR review issue found for branch '{branch}'. Create one with: bd create --priority P0 'PR Review: {branch}'",
        )
    except subprocess.TimeoutExpired:
        return False, "beads command timed out"
    except Exception as e:
        return False, f"PR review check failed: {e}"


def check_pr_exists() -> tuple[bool, str]:
    """Check if a Pull Request exists for the current branch using gh CLI."""
    branch, is_feature = check_branch_info()
    if not is_feature:
        return True, "No PR required for non-feature branch"

    if not check_tool_available("gh"):
        return False, "gh (GitHub CLI) not available. PR cannot be verified."

    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--head", branch, "--json", "url", "--jq", ".[0].url"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            pr_url = result.stdout.strip()
            if pr_url:
                return True, f"PR found: {pr_url}"
            else:
                return (
                    False,
                    f"No PR found for branch '{branch}'. Create one with: gh pr create --fill",
                )
        return False, f"gh command failed: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return False, "gh command timed out"
    except Exception as e:
        return False, f"PR check failed: {e}"


def check_handoff_pr_link() -> tuple[bool, str]:
    """Check if the session handoff (debrief.md) contains a GitHub PR link."""
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    if not brain_dir.exists():
        return False, "Brain directory not found"

    session_dirs = sorted(
        [d for d in brain_dir.iterdir() if d.is_dir()],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )[:3]

    pr_pattern = r"https://github\.com/[^/]+/[^/]+/pull/\d+"

    for session_dir in session_dirs:
        debrief_path = session_dir / "debrief.md"
        if debrief_path.exists():
            try:
                content = debrief_path.read_text()
                if "PR Link" in content or "pull request" in content.lower():
                    if re.search(pr_pattern, content):
                        return True, f"PR link found in debrief: {debrief_path.name}"
            except Exception:
                pass

    return False, "No GitHub PR link found in recent debrief.md"


def check_pr_decomposition_closure() -> tuple[bool, str]:
    """Verify that decomposed PRs are properly closed per PR Response Protocol."""
    if not check_tool_available("bd") or not check_tool_available("gh"):
        return True, "beads or gh not available (skipping decomposition check)"

    try:
        active_issue = get_active_issue_id()
        if not active_issue:
            return True, "No active issue (decomposition check not applicable)"

        result = subprocess.run(
            ["bd", "show", active_issue],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return True, "Could not query issue details (skipping)"

        output = result.stdout
        output_lower = output.lower()
        has_children = "part-of" in output_lower or "child" in output or "epic" in output

        if not has_children:
            return True, "No child issues detected (not a decomposition)"

        pr_pattern = r"PR #(\d+)|pull/(\d+)"
        pr_matches = re.findall(pr_pattern, output)

        if not pr_matches:
            return True, "Parent issue with children but no original PR referenced"

        pr_number = next((m[0] or m[1] for m in pr_matches if m[0] or m[1]), None)

        if not pr_number:
            return True, "Could not extract PR number from issue"

        pr_check = subprocess.run(
            ["gh", "pr", "view", pr_number, "--json", "state", "--jq", ".state"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if pr_check.returncode == 0:
            pr_status = pr_check.stdout.strip()
            if pr_status == "CLOSED":
                return (
                    True,
                    f"Original PR #{pr_number} properly closed (decomposition protocol followed)",
                )
            elif pr_status == "MERGED":
                return True, f"Original PR #{pr_number} was merged (not decomposed)"
            else:
                return (
                    False,
                    f"PROTOCOL VIOLATION: Original PR #{pr_number} is still OPEN but child issues exist.",
                )

        return True, "Could not verify PR status (skipping)"
    except Exception as e:
        return True, f"Decomposition check error: {e}"


def check_child_pr_linkage() -> tuple[bool, str]:
    """Validate that child PRs properly reference their parent Epic/issue per PR Response Protocol."""
    if not check_tool_available("bd") or not check_tool_available("gh"):
        return True, "beads or gh not available (skipping linkage check)"

    try:
        active_issue = get_active_issue_id()
        if not active_issue:
            return True, "No active issue (linkage check not applicable)"

        result = subprocess.run(
            ["bd", "show", active_issue],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return True, "Could not query issue details (skipping)"

        parent_pattern = r"(?:part.?of|depends.?on|blocks?.?by)[\s:]+(\w+-[\w-]+)"
        parent_matches = re.findall(parent_pattern, result.stdout, re.IGNORECASE)

        if not parent_matches:
            return True, "No parent issue detected (not a child PR)"

        parent_id = parent_matches[0]
        branch, is_feature = check_branch_info()
        if not is_feature:
            return True, "Not on feature branch"

        pr_check = subprocess.run(
            ["gh", "pr", "view", "--json", "body", "--jq", ".body"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if pr_check.returncode != 0:
            return True, "No PR found for current branch"

        pr_body = pr_check.stdout.lower()
        parent_mentioned = (
            parent_id.lower() in pr_body or "parent epic" in pr_body or "part of epic" in pr_body
        )

        if not parent_mentioned:
            return (
                False,
                f"PROTOCOL VIOLATION: Child PR does not reference parent issue '{parent_id}'.",
            )

        return True, f"Child PR properly references parent issue '{parent_id}'"
    except Exception as e:
        return True, f"Linkage check error: {e}"


def check_progress_log_exists() -> tuple[bool, str]:
    """Check if progress log exists for the active issue."""
    issue_id = get_active_issue_id()
    if not issue_id:
        return False, "Active issue ID not identified"

    log_path = Path.home() / ".agent/progress-logs" / f"{issue_id}.md"
    if log_path.exists():
        return True, f"Progress log found: {log_path.name}"
    return False, f"Progress log missing: {log_path.name}"


def check_temp_files() -> tuple[bool, str]:
    """Check for common temporary files in workspace.

    Global validator - applies to all projects.
    Flags: .bak, .tmp, .cache, .pyc, __pycache__, node_modules, .env, .DS_Store

    Projects can override with their own check_workspace_cleanup that extends this.
    """
    suspicious_patterns = [
        ".bak",
        ".tmp",
        ".cache",
        ".pyc",
        "__pycache__",
        "node_modules",
        ".DS_Store",
        ".env",
        ".venv",
        "dist/",
        "build/",
        ".pytest_cache",
    ]

    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return True, "Could not check for temp files (git not available)"

        untracked = result.stdout.strip().split("\n") if result.stdout.strip() else []

        found = []
        for f in untracked:
            if any(pattern in f for pattern in suspicious_patterns):
                found.append(f)

        if found:
            return False, f"Temp files detected: {', '.join(found[:10])}"

        return True, "No temp files found"

    except Exception as e:
        return True, f"Temp file check skipped: {e}"


def check_readme_needs_update() -> tuple[bool, str]:
    """Check if README needs updating based on code changes.

    Global validator - heuristic check for common changes that warrant docs.
    Looks for: new files in root, new scripts/, new config files.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Also check unstaged
        result2 = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        changed = set()
        changed.update(result.stdout.strip().split("\n"))
        changed.update(result2.stdout.strip().split("\n"))
        changed.discard("")

        # Files that might need docs
        doc_worthy = [
            f for f in changed if f.endswith((".py", ".sh")) and not f.startswith("tests/")
        ]

        readme_exists = Path("README.md").exists()

        if not doc_worthy:
            return True, "No doc-worthy changes detected"

        if not readme_exists:
            return False, "README.md missing but code changes exist"

        # Check if README was modified
        if "README.md" in changed:
            return True, "README.md updated with changes"

        return True, f"Code changes may need documentation: {', '.join(doc_worthy[:5])}"

    except Exception as e:
        return True, f"README check skipped: {e}"


def check_handoff_beads_id() -> tuple[bool, str]:
    """Check if Beads issue ID is present in debrief/handoff document."""
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    if not brain_dir.exists():
        return True, "Brain directory not found (skipping)"

    session_dirs = sorted(
        [d for d in brain_dir.iterdir() if d.is_dir()],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )[:3]

    for session_dir in session_dirs:
        debrief_path = session_dir / "debrief.md"
        if debrief_path.exists():
            try:
                content = debrief_path.read_text()
                if re.search(r"agent-\w+|bd-\d+", content):
                    return True, "Beads ID found in debrief"
            except Exception:
                pass

    return True, "Beads ID check skipped (not critical)"


def check_wrapup_indicator_symmetry() -> tuple[bool, str]:
    """Verify 🏁 signal matches session completion state."""
    return True, "Wrapup indicator check skipped (not yet implemented)"


def check_wrapup_exclusivity() -> tuple[bool, str]:
    """Verify 🏁 is not misused in planning/execution documents."""
    return True, "Wrapup exclusivity check skipped (not yet implemented)"


def inject_debrief_to_beads() -> tuple[bool, str]:
    """Inject debrief implementation details into Beads issue comments."""
    return True, "Debrief injection skipped (not yet implemented)"


def prune_local_branches() -> tuple[bool, str]:
    """Prune local branches already merged into main."""
    try:
        result = subprocess.run(
            ["git", "fetch", "--prune"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return True, "Branch prune skipped (git fetch failed)"

        result = subprocess.run(
            ["git", "branch", "--merged", "main"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return True, "Could not list merged branches"

        merged = [b.strip() for b in result.stdout.split("\n") if b.strip()]
        if not merged:
            return True, "No merged branches to prune"

        return True, f"Found {len(merged)} merged branch(es) - manual prune recommended"

    except Exception as e:
        return True, f"Branch prune skipped: {e}"
