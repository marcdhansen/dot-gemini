#!/usr/bin/env python3
"""
Flight Director - Agent Orchestrator

Verifies SOP compliance at each phase (PFC, RTB) and validates that agents
complete each step adequately and invoke appropriate skills.

Usage:
    python check_flight_readiness.py --pfc     # Pre-Flight Check validation
    python check_flight_readiness.py --rtb     # Return To Base validation
    python check_flight_readiness.py --status  # Full orchestration status
    python check_flight_readiness.py --help    # Show help
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


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


def check_git_status() -> tuple[bool, str]:
    """Check if git working directory is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            if result.stdout.strip():
                return False, f"Uncommitted changes:\n{result.stdout.strip()}"
            return True, "Working directory clean"
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
        return True, "No blocking issues"  # Not having issues isn't a blocker
    except subprocess.TimeoutExpired:
        return False, "beads command timed out"
    except Exception as e:
        return False, f"beads check failed: {e}"


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
                        return False, f"Plan approval is {hours_ago:.1f} hours old (stale)"
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
                    return True, f"Reflection captured {age.total_seconds() / 60:.0f} minutes ago"
            except Exception:
                pass
    
    return False, "No recent reflection found"


def check_debriefing_invoked() -> tuple[bool, str]:
    """Check if mission debriefing was recently invoked."""
    # Check for recent debrief files in brain directory
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    
    if brain_dir.exists():
        # Sort by modification time, most recent first
        session_dirs = sorted(
            [d for d in brain_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:5]
        
        for session_dir in session_dirs:
            debrief_path = session_dir / "debrief.md"
            if debrief_path.exists():
                try:
                    mtime = datetime.fromtimestamp(debrief_path.stat().st_mtime)
                    age = datetime.now() - mtime
                    if age < timedelta(hours=2):
                        return True, f"Debrief generated {age.total_seconds() / 60:.0f} minutes ago"
                except Exception:
                    pass
    
    return False, "No recent debrief found"


def run_pfc(verbose: bool = False) -> bool:
    """Run Pre-Flight Check validation."""
    print(f"{Colors.BOLD}🛫 PRE-FLIGHT CHECK{Colors.END}")
    print("=" * 40)
    print()
    
    blockers = []
    warnings = []
    
    # Tool Check
    required_tools = ["git", "bd"]
    optional_tools = ["uv", "python3"]
    
    tools_ok = True
    for tool in required_tools:
        if not check_tool_available(tool):
            tools_ok = False
            blockers.append(f"Required tool '{tool}' not available")
    
    print(f"├── Tools: {check_mark(tools_ok)} ", end="")
    if tools_ok:
        print("All required tools available")
    else:
        print(f"Missing: {[t for t in required_tools if not check_tool_available(t)]}")
    
    # Context Check
    docs_ok, missing_docs = check_planning_docs()
    print(f"├── Context: {check_mark(docs_ok)} ", end="")
    if docs_ok:
        print("Planning documents accessible")
    else:
        print(f"Missing: {missing_docs}")
        warnings.append(f"Planning documents missing: {missing_docs}")
    
    # Issue Check
    issues_ok, issues_msg = check_beads_issue()
    print(f"├── Issues: {check_mark(issues_ok)} {issues_msg}")
    if not issues_ok:
        warnings.append(issues_msg)
    
    # Plan Approval Check
    approval_ok, approval_msg = check_plan_approval()
    print(f"└── Approval: {check_mark(approval_ok)} {approval_msg}")
    if not approval_ok:
        warnings.append(approval_msg)
    
    print()
    
    # Summary
    if blockers:
        print(f"{Colors.RED}{Colors.BOLD}❌ PFC BLOCKED{Colors.END}")
        print()
        print("BLOCKERS:")
        for i, blocker in enumerate(blockers, 1):
            print(f"  {i}. {blocker}")
        return False
    elif warnings:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ PFC PASSED WITH WARNINGS{Colors.END}")
        print()
        print("WARNINGS:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()
        print("Ready for takeoff (address warnings when possible)")
        return True
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ PFC COMPLETE{Colors.END}")
        print()
        print("Ready for takeoff!")
        return True


def run_ifo(verbose: bool = False) -> bool:
    """Run In-Flight Operations status check."""
    print(f"{Colors.BOLD}✈️ IN-FLIGHT OPERATIONS{Colors.END}")
    print("=" * 40)
    print()
    print("IFO: Active work phase - executing the task.")
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
            reverse=True
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
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ IFO SETUP INCOMPLETE{Colors.END}")
        print()
        print("SETUP NEEDED:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ IFO ACTIVE{Colors.END}")
        print()
        print("Execute the mission. Run --rtb when ready to land.")
        return True

def run_rtb(verbose: bool = False) -> bool:
    """Run Return To Base validation (safe landing checks only)."""
    print(f"{Colors.BOLD}🛬 RETURN TO BASE CHECK{Colors.END}")
    print("=" * 40)
    print()
    print("RTB focuses on safe landing: code quality, clean git, successful push.")
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
    print(f"└── Branch: {branch_icon} {branch}")
    if not is_feature and branch not in ["main", "master"]:
        warnings.append(f"Not on a feature branch: {branch}")
    
    print()
    
    # Summary
    if blockers:
        print(f"{Colors.RED}{Colors.BOLD}❌ RTB BLOCKED{Colors.END}")
        print()
        print("BLOCKERS:")
        for i, blocker in enumerate(blockers, 1):
            print(f"  {i}. {blocker}")
        print()
        print("Resolve blockers before completing RTB.")
        return False
    elif warnings:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ RTB PASSED WITH WARNINGS{Colors.END}")
        print()
        print("WARNINGS:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()
        print("Safe landing! Now proceed to Mission Debrief.")
        return True
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ RTB COMPLETE{Colors.END}")
        print()
        print("Safe landing! Now proceed to Mission Debrief.")
        return True


def run_debrief(verbose: bool = False) -> bool:
    """Run Mission Debrief validation."""
    print(f"{Colors.BOLD}🎖️ MISSION DEBRIEF CHECK{Colors.END}")
    print("=" * 40)
    print()
    print("Mission Debrief: strategic learning and session closure.")
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
    print(f"└── Plan Cleared: {check_mark(approval_cleared)} ", end="")
    if approval_cleared:
        print("Plan approval cleared or stale")
    else:
        print(f"Plan still active: {approval_msg}")
        warnings.append("Clear the ## Approval marker in task.md")
    
    print()
    
    # Summary
    if blockers:
        print(f"{Colors.RED}{Colors.BOLD}❌ DEBRIEF INCOMPLETE{Colors.END}")
        print()
        print("BLOCKERS:")
        for i, blocker in enumerate(blockers, 1):
            print(f"  {i}. {blocker}")
        return False
    elif warnings:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ DEBRIEF INCOMPLETE{Colors.END}")
        print()
        print("MISSING:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()
        print("Complete these steps, then run --cleanup for final check.")
        return False
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ MISSION DEBRIEF COMPLETE{Colors.END}")
        print()
        print("Now run --cleanup for final repo verification.")
        return True


def run_cleanup(verbose: bool = False) -> bool:
    """Run Cleanup Repo verification (final phase after debrief)."""
    print(f"{Colors.BOLD}✨ CLEANUP REPO CHECK{Colors.END}")
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
    print(f"{Colors.BOLD}📊 FLIGHT DIRECTOR STATUS{Colors.END}")
    print("=" * 40)
    print()
    
    # Current state
    branch, is_feature = check_branch_info()
    git_ok, _ = check_git_status()
    
    print(f"🌿 Branch: {branch}")
    print(f"📁 Git Clean: {'Yes' if git_ok else 'No'}")
    print()
    
    # Recent activity
    print("Recent Skills Status:")
    
    reflect_ok, reflect_msg = check_reflection_invoked()
    print(f"  - Reflect: {check_mark(reflect_ok)} {reflect_msg}")
    
    debrief_ok, debrief_msg = check_debriefing_invoked()
    print(f"  - Debrief: {check_mark(debrief_ok)} {debrief_msg}")
    
    approval_ok, approval_msg = check_plan_approval()
    print(f"  - Plan Approval: {check_mark(approval_ok)} {approval_msg}")
    
    print()
    print("Run --pfc, --rtb, or --debrief for detailed phase checks.")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Flight Director - Agent Orchestrator for SOP Compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run Pre-Flight Check
    python check_flight_readiness.py --pfc
    
    # Run Return To Base check  
    python check_flight_readiness.py --rtb
    
    # Show current status
    python check_flight_readiness.py --status
        """,
    )
    
    parser.add_argument(
        "--pfc",
        action="store_true",
        help="Run Pre-Flight Check validation",
    )
    parser.add_argument(
        "--ifo",
        action="store_true",
        help="Run In-Flight Operations status check",
    )
    parser.add_argument(
        "--rtb",
        action="store_true",
        help="Run Return To Base validation (safe landing)",
    )
    parser.add_argument(
        "--debrief",
        action="store_true",
        help="Run Mission Debrief validation (strategic learning)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Run Cleanup Repo verification (final phase after PR merge)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show full orchestration status",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )
    
    args = parser.parse_args()
    
    # Default to status if no option specified
    if not any([args.pfc, args.ifo, args.rtb, args.debrief, args.cleanup, args.status]):
        parser.print_help()
        sys.exit(0)
    
    success = True
    
    if args.pfc:
        success = run_pfc(args.verbose)
    elif args.ifo:
        success = run_ifo(args.verbose)
    elif args.rtb:
        success = run_rtb(args.verbose)
    elif args.debrief:
        success = run_debrief(args.verbose)
    elif args.cleanup:
        success = run_cleanup(args.verbose)
    elif args.status:
        success = run_status(args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
