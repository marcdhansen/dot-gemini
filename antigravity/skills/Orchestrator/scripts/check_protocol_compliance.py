"""
Orchestrator - Agent Workflow Coordinator

Verifies SOP compliance at each phase (Initialization, Finalization) and validates that agents
complete each step adequately and invoke appropriate skills.

Usage:
    python check_protocol_compliance.py --init     # Initialization validation
    python check_protocol_compliance.py --finalize # Finalization validation
    python check_protocol_compliance.py --status   # Full orchestration status
    python check_protocol_compliance.py --help     # Show help
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add universal scripts to path
sys.path.append(str(Path.home() / ".agent/scripts"))
sys.path.append(str(Path.home() / ".agent/ledgers"))

try:
    from compliance_validators import validate_initialization
except ImportError:
    validate_initialization = None


def update_progress_ledger(phase: str, status: str, result: str):
    """Update the Progress Ledger with phase result."""
    manager = Path.home() / ".agent/ledgers/ledger-manager.py"
    if manager.exists():
        try:
            # We don't always have a task_id here, use 'system' or 'harness'
            subprocess.run(
                [
                    sys.executable,
                    str(manager),
                    "add-step",
                    "harness",
                    f"Phase: {phase}",
                    result,
                    "--status",
                    status,
                ],
                capture_output=True,
                text=True,
            )
        except Exception:
            pass


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def check_mark(passed: bool) -> str:
    """Return colored check or X mark."""
    if passed:
        return f"{Colors.GREEN}✅{Colors.END}"
    return f"{Colors.RED}❌{Colors.END}"


def warning_mark() -> str:
    """Return warning symbol."""
    return f"{Colors.YELLOW}⚠️{Colors.END}"


def check_tool_available(tool: str) -> bool:
    """Check if a command-line tool is available."""
    try:
        result = subprocess.run(
            ["which", tool],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse version string into a tuple of integers."""
    match = re.search(r'(\d+(?:\.\d+)+)', version_str)
    if match:
        return tuple(map(int, match.group(1).split('.')))
    return ()


def check_tool_version(tool: str, min_version: str, version_flag: str = "--version") -> tuple[bool, str]:
    """Check if a tool's version meets the minimum requirement."""
    if not check_tool_available(tool):
        return False, f"Tool '{tool}' not installed"

    try:
        result = subprocess.run(
            [tool, version_flag],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            # Some tools might use stderr for version info
            output = result.stdout.strip() or result.stderr.strip()
            if not output:
                return False, f"Could not get version for '{tool}'"
        else:
            output = result.stdout.strip() or result.stderr.strip()

        current_v = parse_version(output)
        required_v = parse_version(min_version)

        if not current_v:
            return False, f"Could not parse version from: {output}"

        if current_v < required_v:
            return False, f"Version for '{tool}' is too old: {output} (Required: {min_version})"

        return True, f"{tool} version {'.'.join(map(str, current_v))} is OK"
    except Exception as e:
        return False, f"Error checking {tool} version: {e}"


def check_workspace_integrity() -> tuple[bool, list[str]]:
    """Verify workspace integrity by checking for mandatory directories and files."""
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
            
            # Detect code changes (.py, .js, .ts, etc.)
            code_extensions = {".py", ".sh", ".js", ".ts", ".go", ".c", ".cpp"}
            code_changes = []
            for line in result.stdout.split("\n"):
                if len(line) > 3:
                    file_path = line[3:]
                    if any(file_path.endswith(ext) for ext in code_extensions):
                        code_changes.append(file_path)
            
            if turbo:
                if code_changes:
                    return False, f"ESCALATION REQUIRED: Code changes detected in Turbo Mode: {', '.join(code_changes)}. Please switch to Full SOP."
                else:
                    return True, "Metadata changes only (Turbo safe)"
            
            return False, f"Uncommitted changes:\n{changes}"
        return False, "Git command failed"
    except Exception as e:
        return False, f"Git check failed: {e}"


def check_branch_info() -> tuple[str, bool]:
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


def check_planning_docs() -> tuple[bool, list[str]]:
    """Check if planning documents exist and are readable."""
    missing = []
    paths_to_check = [
        Path(".agent/rules/ROADMAP.md"),
        Path(".agent/rules/ImplementationPlan.md"),
    ]

    for path in paths_to_check:
        if not path.exists():
            missing.append(str(path))

    return len(missing) == 0, missing


def check_beads_issue() -> tuple[bool, str]:
    """Check if there's an active beads issue."""
    if not check_tool_available("bd"):
        return False, "beads (bd) not available"

    try:
        result = subprocess.run(
            ["bd", "ready"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Extract first issue from output
            lines = result.stdout.strip().split("\n")
            if lines:
                return True, f"Issues ready: {len(lines)}"
        return False, "No active Beads issues found"  # Precise status
    except subprocess.TimeoutExpired:
        return False, "beads command timed out"
    except Exception as e:
        return False, f"beads check failed: {e}"


def get_active_issue_id() -> str | None:
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
            result = subprocess.run(
                ["bd", "ready"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if lines:
                    # Extract ID from first line (assuming format ID: Title)
                    first_line = lines[0]
                    if ":" in first_line:
                        return first_line.split(":")[0].strip()
        except Exception:
            pass
    return None


def check_progress_log_exists() -> tuple[bool, str]:
    """Check if progress log exists for the active issue."""
    issue_id = get_active_issue_id()
    if not issue_id:
        return False, "Active issue ID not identified"

    log_path = Path.home() / ".agent/progress-logs" / f"{issue_id}.md"
    if log_path.exists():
        return True, f"Progress log found: {log_path.name}"
    return False, f"Progress log missing: {log_path.name}"


def check_sop_simplification() -> tuple[bool, str]:
    """Check for SOP simplification proposals and their validation status."""
    # Look for simplification proposal files
    proposal_patterns = ["*.md", ".agent/sop_simplification_*.md", "sop_simplification_*.md"]

    proposals = []
    for pattern in proposal_patterns:
        proposals.extend(Path(".").glob(pattern))
        proposals.extend(Path(".agent").glob(pattern))

    if not proposals:
        return True, "No SOP simplification proposals found"

    # Check if any proposals need validation or approval
    pending_proposals = []
    approved_proposals = []

    for proposal in proposals:
        if "sop_simplification_" in proposal.name:
            content = proposal.read_text()

            # Check if proposal has been validated
            if "## Approval Section" in content:
                # Look for approval decision
                if "Approve Simplified" in content:
                    approved_proposals.append(proposal.name)
                elif "Approve Standard" in content or "Reject" in content:
                    # Decision made, no action needed
                    continue
                else:
                    pending_proposals.append(proposal.name)
            else:
                pending_proposals.append(proposal.name)

    if pending_proposals:
        return False, f"Pending SOP simplification proposals: {', '.join(pending_proposals)}"

    if approved_proposals:
        return True, f"Approved simplified SOP: {', '.join(approved_proposals)}"

    return True, "SOP simplification proposals processed"


def check_plan_approval(max_hours: int = 4) -> tuple[bool, str]:
    """Check if plan approval exists and is fresh."""
    # Look for task.md with approval marker
    task_paths = [
        Path(".agent/task.md"),
        Path("task.md"),
    ]

    # Also check brain directory
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    if brain_dir.exists():
        for session_dir in sorted(brain_dir.iterdir(), reverse=True)[:3]:
            if session_dir.is_dir():
                task_paths.append(session_dir / "task.md")

    for task_path in task_paths:
        if task_path.exists():
            try:
                content = task_path.read_text()
                if "## Approval" in content or "[x]" in content.lower():
                    # Check file modification time
                    mtime = datetime.fromtimestamp(task_path.stat().st_mtime)
                    age = datetime.now() - mtime

                    if age < timedelta(hours=max_hours):
                        hours_ago = age.total_seconds() / 3600
                        return True, f"Plan approved {hours_ago:.1f} hours ago"
                    else:
                        hours_ago = age.total_seconds() / 3600
                        return (
                            False,
                            f"Plan approval is {hours_ago:.1f} hours old (stale)",
                        )
            except Exception:
                pass

    return False, "No plan approval found"


def check_reflection_invoked() -> tuple[bool, str]:
    """Check if reflection was recently invoked."""
    # Check for recent reflection files
    reflection_paths = [
        Path(".agent/reflections.json"),
        Path("reflections.json"),
    ]

    for path in reflection_paths:
        if path.exists():
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                age = datetime.now() - mtime
                if age < timedelta(hours=2):
                    return (
                        True,
                        f"Reflection captured {age.total_seconds() / 60:.0f} minutes ago",
                    )
            except Exception:
                pass

    return False, "No recent reflection found"


def check_debriefing_invoked() -> tuple[bool, str]:
    """Check if debriefing was recently invoked."""
    # Look for debrief files in brain directory
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


def check_handoff_compliance() -> tuple[bool, str]:
    """Check if hand-off compliance verification passes for multi-phase implementations."""
    # Look for hand-off directory and verification script
    handoff_dir = Path(".agent/handoffs")
    verification_script = Path(".agent/scripts/verify_handoff_compliance.sh")

    if not handoff_dir.exists():
        return True, "No hand-off directory (not a multi-phase implementation)"

    if not verification_script.exists():
        return False, "Hand-off verification script missing"

    # Check if there are any hand-off documents to verify
    handoff_files = list(handoff_dir.glob("**/phase-*-handoff.md"))
    if not handoff_files:
        return True, "No hand-off documents found (not a multi-phase implementation)"

    # Run verification script on all hand-offs
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
    # Use the todo-enforcer script if available
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
                # Extract the failure message
                msg = (
                    result.stdout.strip().split("\n")[-1]
                    if result.stdout
                    else "Unfinished tasks detected"
                )
                return False, msg
        except Exception as e:
            return False, f"Todo enforcer error: {e}"

    return True, "Todo enforcer script not found (Skipping)"


def run_initialization(verbose: bool = False) -> bool:
    """Run Initialization validation."""
    print(f"{Colors.BOLD}📋 INITIALIZATION CHECK{Colors.END}")
    print("=" * 40)
    print()

    blockers = []
    warnings = []

    # Tool Check
    required_tools = [
        ("git", "2.25.0", "--version"),
        ("bd", "0.40.0", "version"),
    ]
    optional_tools = [
        ("uv", "0.5.0", "--version"),
        ("python3", "3.10.0", "--version"),
    ]

    tools_ok = True
    tool_details = []
    for tool, min_v, flag in required_tools:
        ok, msg = check_tool_version(tool, min_v, flag)
        if not ok:
            tools_ok = False
            blockers.append(msg)
        tool_details.append((tool, ok, msg))

    print(f"├── Tools: {check_mark(tools_ok)} ", end="")
    if tools_ok:
        print("Required tools version check passed")
    else:
        print("Tool version requirements not met")

    if verbose or not tools_ok:
        for tool, ok, msg in tool_details:
            print(f"│   └── {tool}: {check_mark(ok)} {msg}")

    # Optional tool warnings
    for tool, min_v, flag in optional_tools:
        ok, msg = check_tool_version(tool, min_v, flag)
        if not ok:
            warnings.append(f"Optional tool {msg}")

    # Workspace Integrity Check
    integrity_ok, missing_paths = check_workspace_integrity()
    print(f"├── Integrity: {check_mark(integrity_ok)} ", end="")
    if integrity_ok:
        print("Workspace integrity verified")
    else:
        print(f"Missing mandatory components: {missing_paths}")
        blockers.append(f"Workspace integrity failure: Missing {missing_paths}")

    # Context Check
    docs_ok, missing_docs = check_planning_docs()
    print(f"├── Context: {check_mark(docs_ok)} ", end="")
    if docs_ok:
        print("Planning documents accessible")
    else:
        print(f"Missing: {missing_docs}")
        warnings.append(f"Planning documents missing: {missing_docs}")

    # Issue Check (Optional for Init)
    issues_ok, issues_msg = check_beads_issue()
    issue_icon = check_mark(issues_ok) if issues_ok else f"{Colors.BLUE}ℹ️{Colors.END}"
    print(f"├── Issues: {issue_icon} {issues_msg} (Optional for planning)")
    # No warning/blocker for missing issues during initialization

    # SOP Simplification Check
    simplification_ok, simplification_msg = check_sop_simplification()
    print(f"├── Simplification: {check_mark(simplification_ok)} {simplification_msg}")
    if not simplification_ok:
        warnings.append(simplification_msg)

    # Plan Approval Check
    approval_ok, approval_msg = check_plan_approval()
    # Progress Log Check
    progress_ok, progress_msg = check_progress_log_exists()
    print(f"├── Progress Log: {check_mark(progress_ok)} {progress_msg}")

    print(f"└── Approval: {check_mark(approval_ok)} {approval_msg}")
    if not approval_ok:
        warnings.append(approval_msg)
    if not progress_ok:
        warnings.append("Progress log missing - run /log-progress to initialize context")

    print()

    # Summary
    if blockers:
        print(f"{Colors.RED}{Colors.BOLD}❌ INITIALIZATION BLOCKED{Colors.END}")
        print()
        print("BLOCKERS:")
        for i, blocker in enumerate(blockers, 1):
            print(f"  {i}. {blocker}")
        update_progress_ledger("Initialization", "failure", f"Blocked: {blockers}")
        return False
    elif warnings:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ INITIALIZATION PASSED WITH WARNINGS{Colors.END}")
        print()
        print("WARNINGS:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()
        print("Ready for execution (address warnings when possible)")
        update_progress_ledger("Initialization", "success", f"Passed with warnings: {warnings}")
        return True
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ INITIALIZATION COMPLETE{Colors.END}")
        print()
        print("Ready for execution!")
        update_progress_ledger("Initialization", "success", "Clean initialization complete")
        return True


def run_turbo_initialization(verbose: bool = False) -> bool:
    """Run lightweight Turbo Mode initialization validation."""
    print(f"{Colors.BOLD}⚡ TURBO INITIALIZATION (Turbo Create Protocol){Colors.END}")
    print("=" * 40)
    print("Turbo Mode: Administrative/Metadata tasks only.")
    print("Guidelines: No code changes, no full planning required.")
    print()

    # Tool Check (Only Git is strictly required for Turbo)
    git_ok = check_tool_available("git")
    print(f"├── Git: {check_mark(git_ok)}")
    
    # Check for existing code blockers (should not have uncommitted code changes)
    git_clean, git_msg = check_git_status(turbo=True)
    print(f"└── Git Clean: {check_mark(git_clean)} {git_msg.split(chr(10))[0]}")

    print()
    if not git_ok or not git_clean:
        print(f"{Colors.RED}{Colors.BOLD}❌ TURBO BLOCKED{Colors.END}")
        if not git_clean:
            print(f"  {warning_mark()} Code changes detected. Escalate to Full SOP (--init).")
        return False

    print(f"{Colors.GREEN}{Colors.BOLD}✅ TURBO READY{Colors.END}")
    print("Ready for administrative tasks (bd create, docs, research).")
    return True


def run_execution(verbose: bool = False) -> bool:
    """Run Execution Phase status check."""
    print(f"{Colors.BOLD}🚀 EXECUTION PHASE{Colors.END}")
    print("=" * 40)
    print()
    print("Execution: Active work phase - executing the task.")
    print()

    issues = []

    # Check we're on a feature branch (should be working, not on main)
    branch, is_feature = check_branch_info()
    print(f"├── Branch: {check_mark(is_feature)} ", end="")
    if is_feature:
        print(f"Working on {branch}")
    else:
        print(f"On {branch} (should be feature branch)")
        issues.append("Create a feature branch before starting work")

    # Check task.md exists in brain directory
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    task_found = False
    if brain_dir.exists():
        session_dirs = sorted(
            [d for d in brain_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )[:3]
        for session_dir in session_dirs:
            if (session_dir / "task.md").exists():
                task_found = True
                break

    print(f"├── Task Tracked: {check_mark(task_found)} ", end="")
    if task_found:
        print("task.md found")
    else:
        print("No task.md found")
        issues.append("Create task.md to track work")

    # MANDATORY Beads Issue Check for Execution
    issues_ok, issues_msg = check_beads_issue()
    print(f"├── Beads Issue: {check_mark(issues_ok)} {issues_msg}")
    if not issues_ok:
        issues.append("MANDATORY: Current rule requires a Beads issue before implementation")

    # Git status - during IFO, uncommitted changes are expected
    git_ok, git_msg = check_git_status()
    print(f"└── Git Status: ", end="")
    if git_ok:
        print(f"{Colors.BLUE}ℹ️{Colors.END} Clean (no changes yet)")
    else:
        print(f"{Colors.BLUE}ℹ️{Colors.END} Work in progress")

    print()

    # IFO Guidelines
    print(f"{Colors.BOLD}IFO Guidelines:{Colors.END}")
    print("  • Follow Spec-Driven TDD: Red → Green → Refactor")
    print("  • Update task.md as you complete items")
    print("  • Commit frequently with clear messages")
    print("  • Run quality gates before RTB")
    print()

    if issues:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ EXECUTION SETUP INCOMPLETE{Colors.END}")
        print()
        print("SETUP NEEDED:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ EXECUTION ACTIVE{Colors.END}")
        print()
        print("Execute the task. Run --finalize when ready to land.")
        return True


def run_finalization(verbose: bool = False) -> bool:
    """Run Finalization validation."""
    print(f"{Colors.BOLD}🛬 FINALIZATION CHECK{Colors.END}")
    print("=" * 40)
    print()
    print("Finalization focuses on safe landing: code quality, clean git, successful push.")
    print()

    blockers = []
    warnings = []

    # Git Status Check
    git_ok, git_msg = check_git_status()
    print(f"├── Git Status: {check_mark(git_ok)} {git_msg.split(chr(10))[0]}")
    if not git_ok:
        blockers.append(git_msg)

    # Branch Info
    branch, is_feature = check_branch_info()
    branch_icon = check_mark(is_feature) if is_feature else warning_mark()
    print(f"├── Branch: {branch_icon} {branch}")
    if not is_feature and branch not in ["main", "master"]:
        warnings.append(f"Not on a feature branch: {branch}")

    # SOP Simplification Check
    simplification_ok, simplification_msg = check_sop_simplification()
    print(f"├── Simplification: {check_mark(simplification_ok)} {simplification_msg}")
    if not simplification_ok:
        warnings.append(simplification_msg)

    # Hand-off Compliance Check (for multi-phase implementations)
    handoff_ok, handoff_msg = check_handoff_compliance()
    handoff_icon = check_mark(handoff_ok) if handoff_ok else warning_mark()
    print(f"├── Hand-offs: {handoff_icon} {handoff_msg}")
    if not handoff_ok and "not a multi-phase implementation" not in handoff_msg:
        blockers.append("Hand-off compliance failed - run verify_handoff_compliance.sh")

    # Reflection Check (Enforced at RTB to ensure it's not skipped)
    reflect_ok, reflect_msg = check_reflection_invoked()
    print(f"├── Reflection: {check_mark(reflect_ok)} {reflect_msg}")
    if not reflect_ok:
        blockers.append("Reflection not captured - invoke /reflect (Mandatory for RTB)")

    # Todo Completion Check (Sisyphus pattern)
    todo_ok, todo_msg = check_todo_completion()
    print(f"└── Todo Enforcer: {check_mark(todo_ok)} {todo_msg}")
    if not todo_ok:
        blockers.append(f"Todo Enforcer failed: {todo_msg}")

    print()

    # Summary
    if blockers:
        print(f"{Colors.RED}{Colors.BOLD}❌ FINALIZATION BLOCKED{Colors.END}")
        print()
        print("BLOCKERS:")
        for i, blocker in enumerate(blockers, 1):
            print(f"  {i}. {blocker}")
        print()
        print("Resolve blockers before completing Finalization.")
        update_progress_ledger("Finalization", "failure", f"Blocked: {blockers}")
        return False
    elif warnings:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ FINALIZATION PASSED WITH WARNINGS{Colors.END}")
        print()
        print("WARNINGS:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()
        print("Safe landing! Now proceed to Retrospective.")
        update_progress_ledger("Finalization", "success", f"Passed with warnings: {warnings}")
        return True
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ FINALIZATION COMPLETE{Colors.END}")
        print()
        print("Safe landing! Now proceed to Retrospective.")
        update_progress_ledger("Finalization", "success", "Clean Finalization complete")
        return True


def run_turbo_finalization(verbose: bool = False) -> bool:
    """Run lightweight Turbo Mode finalization validation."""
    print(f"{Colors.BOLD}⚡ TURBO FINALIZATION{Colors.END}")
    print("=" * 40)
    print()

    # Git Status Check (Escalation Detection)
    git_ok, git_msg = check_git_status(turbo=True)
    print(f"├── Git Status: {check_mark(git_ok)} {git_msg.split(chr(10))[0]}")
    
    # Beads Sync check (Optional but recommended)
    bd_ok = check_tool_available("bd")
    print(f"└── Beads Sync: {check_mark(bd_ok) if bd_ok else warning_mark()} {'Available' if bd_ok else 'Missing'}")

    print()
    if not git_ok:
        print(f"{Colors.RED}{Colors.BOLD}❌ TURBO FINALIZATION BLOCKED{Colors.END}")
        print(f"Error: {git_msg}")
        return False

    print(f"{Colors.GREEN}{Colors.BOLD}✅ TURBO FINALIZATION COMPLETE{Colors.END}")
    return True


def run_retrospective(verbose: bool = False) -> bool:
    """Run Retrospective validation."""
    print(f"{Colors.BOLD}🎖️ RETROSPECTIVE CHECK{Colors.END}")
    print("=" * 40)
    print()
    print("Retrospective: strategic learning and session closure.")
    print()

    blockers = []
    warnings = []

    # Reflection Check
    reflect_ok, reflect_msg = check_reflection_invoked()
    print(f"├── Reflection: {check_mark(reflect_ok)} {reflect_msg}")
    if not reflect_ok:
        warnings.append("Reflection not captured - invoke /reflect")

    # Debriefing Check
    debrief_ok, debrief_msg = check_debriefing_invoked()
    print(f"├── Debrief File: {check_mark(debrief_ok)} {debrief_msg}")
    if not debrief_ok:
        warnings.append("Debrief file not generated - run mission_debriefing.py")

    # Plan Approval Cleared Check
    approval_ok, approval_msg = check_plan_approval()
    # For debrief, we WANT approval to be stale/missing (means it was cleared)
    approval_cleared = not approval_ok or "stale" in approval_msg.lower()
    print(f"├── Plan Cleared: {check_mark(approval_cleared)} ", end="")
    if approval_cleared:
        print("Plan approval cleared or stale")
    else:
        print(f"Plan still active: {approval_msg}")
        warnings.append("Clear the ## Approval marker in task.md")

    # Progress Log Reflector Synthesis Check
    log_ok, log_msg = check_progress_log_exists()
    reflector_ok = False
    reflector_msg = "Progress log missing"
    if log_ok:
        try:
            issue_id = get_active_issue_id()
            log_path = Path.home() / ".agent/progress-logs" / f"{issue_id}.md"
            content = log_path.read_text()
            if "## Reflector Synthesis" in content:
                parts = content.split("## Reflector Synthesis")
                if len(parts) > 1:
                    # Skip the first line which might be the remainder of the heading
                    section_lines = parts[1].split("\n")[1:]
                    if any(line.strip() and not line.strip().startswith(("#", "!", "<!--")) for line in section_lines):
                        reflector_ok = True
                        reflector_msg = "Reflector synthesis captured in progress log"
                    else:
                        reflector_msg = "Reflector synthesis empty in progress log"
        except Exception as e:
            reflector_msg = f"Error checking reflector: {e}"

    print(f"├── Reflector: {check_mark(reflector_ok)} {reflector_msg}")
    if not reflector_ok:
        warnings.append(reflector_msg)

    # Todo Completion Check (Sisyphus pattern)
    todo_ok, todo_msg = check_todo_completion()
    print(f"└── Todo Enforcer: {check_mark(todo_ok)} {todo_msg}")
    if not todo_ok:
        blockers.append(f"Todo Enforcer failed: {todo_msg}")

    print()

    # Summary
    if blockers:
        print(f"{Colors.RED}{Colors.BOLD}❌ RETROSPECTIVE INCOMPLETE{Colors.END}")
        print()
        print("BLOCKERS:")
        for i, blocker in enumerate(blockers, 1):
            print(f"  {i}. {blocker}")
        return False
    elif warnings:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ RETROSPECTIVE INCOMPLETE{Colors.END}")
        print()
        print("MISSING:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()
        print("Complete these steps, then run --clean for final check.")
        return False
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ RETROSPECTIVE COMPLETE{Colors.END}")
        print()
        print("Now run --clean for final repo verification.")
        return True


def run_clean_state(verbose: bool = False) -> bool:
    """Run Clean State validation (formerly Cleanup)."""
    print(f"{Colors.BOLD}✨ CLEAN STATE CHECK{Colors.END}")
    print("=" * 40)
    print()
    print("Final verification: repo should be clean after PR merge.")
    print()

    issues = []

    # Branch Check
    branch, is_feature = check_branch_info()
    on_main = branch in ["main", "master"]
    print(f"├── Branch: {check_mark(on_main)} ", end="")
    if on_main:
        print(f"On {branch}")
    else:
        print(f"On {branch} (should be main)")
        issues.append(f"Merge PR and switch to main (currently on {branch})")

    # Git Status Check
    git_ok, git_msg = check_git_status()
    print(f"├── Git Clean: {check_mark(git_ok)} ", end="")
    if git_ok:
        print("Working tree clean")
    else:
        print("Uncommitted changes")
        issues.append("Commit and push remaining changes")

    # Up-to-date with remote
    up_to_date = True
    try:
        import subprocess

        result = subprocess.run(
            ["git", "status", "-uno"],
            capture_output=True,
            text=True,
        )
        if "behind" in result.stdout.lower():
            up_to_date = False
    except Exception:
        pass

    print(f"└── Synced: {check_mark(up_to_date)} ", end="")
    if up_to_date:
        print("Up to date with remote")
    else:
        print("Behind remote")
        issues.append("Pull latest changes from remote")

    # Artifact Cleanup Check
    temp_artifacts = list(Path(".").glob("task.md")) + list(Path(".").glob("walkthrough.md")) + list(Path(".").glob("debrief.md"))
    cleanup_ok = len(temp_artifacts) == 0
    print(f"\n├── Cleanup: {check_mark(cleanup_ok)} ", end="")
    if cleanup_ok:
        print("Temporary artifacts removed")
    else:
        print(f"Found temporary artifacts: {[f.name for f in temp_artifacts]}")
        issues.append(f"Remove temporary artifacts: {[f.name for f in temp_artifacts]}")

    print()

    # Summary
    if issues:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ REPO NOT CLEAN{Colors.END}")
        print()
        print("ISSUES:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
        print("Resolve issues to achieve clean state.")
        return False
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ REPO IS CLEAN{Colors.END}")
        print()
        print("Session complete. Ready for next mission!")
        return True


def run_status(verbose: bool = False) -> bool:
    """Show full orchestration status."""
    print(f"{Colors.BOLD}📊 ORCHESTRATOR STATUS{Colors.END}")
    print("=" * 40)
    print()

    # Current state
    branch, is_feature = check_branch_info()
    git_ok, _ = check_git_status()

    print(f"🌿 Branch: {branch}")
    print(f"📁 Git Clean: {'Yes' if git_ok else 'No'}")
    print()

    # Recent activity
    print("Recent Skill Status:")

    reflect_ok, reflect_msg = check_reflection_invoked()
    print(f"  - Reflect: {check_mark(reflect_ok)} {reflect_msg}")

    debrief_ok, debrief_msg = check_debriefing_invoked()
    print(f"  - Retrospective: {check_mark(debrief_ok)} {debrief_msg}")

    approval_ok, approval_msg = check_plan_approval()
    print(f"  - Plan Approval: {check_mark(approval_ok)} {approval_msg}")

    print()
    print("Run --init, --execute, --finalize, or --retrospective for detailed phase checks.")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrator - Agent Workflow Coordinator for SOP Compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run Initialization validation
    python check_protocol_compliance.py --init
    
    # Run Finalization check  
    python check_protocol_compliance.py --finalize
    
    # Show current status
    python check_protocol_compliance.py --status
        """,
    )

    parser.add_argument(
        "--init",
        "--pfc",
        action="store_true",
        help="Run Initialization validation (formerly PFC)",
    )
    parser.add_argument(
        "--execute",
        "--ifo",
        action="store_true",
        help="Run Execution Phase status check (formerly IFO)",
    )
    parser.add_argument(
        "--finalize",
        "--rtb",
        action="store_true",
        help="Run Finalization validation (formerly RTB)",
    )
    parser.add_argument(
        "--retrospective",
        "--debrief",
        action="store_true",
        help="Run Retrospective validation (formerly Debrief)",
    )
    parser.add_argument(
        "--clean",
        "--cleanup",
        "--pristine",
        action="store_true",
        help="Run Clean State validation (formerly Cleanup)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show full orchestration status",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run type-safe Pydantic validation and output JSON",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "--turbo",
        action="store_true",
        help="Run in Turbo Mode (Turbo Create Protocol - lightweight validation)",
    )

    args = parser.parse_args()

    # Default to status if no option specified
    if not any(
        [
            args.init,
            args.execute,
            args.finalize,
            args.retrospective,
            args.clean,
            args.status,
            args.validate,
        ]
    ):
        parser.print_help()
        sys.exit(0)

    success = True

    if args.validate:
        if validate_initialization:
            result = validate_initialization(Path.cwd())
            print(result.model_dump_json(indent=2))
            success = result.passed
        else:
            print("❌ Pydantic validators not available.")
            success = False
    elif args.init:
        if args.turbo:
            success = run_turbo_initialization(args.verbose)
        else:
            success = run_initialization(args.verbose)
    elif args.execute:
        success = run_execution(args.verbose)
    elif args.finalize:
        if args.turbo:
            success = run_turbo_finalization(args.verbose)
        else:
            success = run_finalization(args.verbose)
    elif args.retrospective:
        success = run_retrospective(args.verbose)
    elif args.clean:
        success = run_clean_state(args.verbose)
    elif args.status:
        success = run_status(args.verbose)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
