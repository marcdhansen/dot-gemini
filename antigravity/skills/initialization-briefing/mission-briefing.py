#!/usr/bin/env python3
"""
Mission Briefing Skill - Essential pre-mission information for agents
Provides balanced overview of protocol, current status, and areas to watch
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class MissionBriefing:
    def __init__(self):
        self.workspace_dir = Path.cwd()
        self.agent_dir = self.workspace_dir / ".agent"

    def run_briefing(self):
        """Generate and display comprehensive mission briefing"""

        print("🚀 MISSION BRIEFING - Essential Pre-Mission Information")
        print("=" * 60)
        print()

        # 1. Current Status Check
        self._show_current_status()

        # 2. Protocol Highlights
        self._show_protocol_highlights()

        # 3. Areas to Watch
        self._show_friction_areas()

        # 4. Common Pitfalls
        self._show_common_pitfalls()

        # 5. Session Checklist
        self._show_session_checklist()

        print()
        print("🎯 READY TO START: Mission briefing complete!")
        print("💡 Save friction points as they happen - don't wait until RTB!")
        print()

    def _show_current_status(self):
        """Display current workspace and session status"""
        print("📍 CURRENT STATUS")
        print("-----------------")

        try:
            # Git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
            )
            git_changes = result.stdout.strip()

            if not git_changes:
                print("✅ Git: Working directory clean")
            else:
                lines = len(git_changes.split("\n")) if git_changes else 0
                print(f"📝 Git: {lines} uncommitted changes")

            # Current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
            )
            current_branch = result.stdout.strip()
            print(f"🌿 Branch: {current_branch}")

            # Check if on feature/agent branch
            if current_branch.startswith("agent/") or current_branch.startswith(
                "feature/"
            ):
                print("🔧 Feature branch detected - extra cleanup required")

        except Exception as e:
            print("⚠️  Git status unavailable")

        # Check for active issues (beads)
        if self._command_exists("bd"):
            try:
                result = subprocess.run(
                    ["bd", "list", "--status", "in_progress", "--limit", "5"],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace_dir,
                )
                in_progress = result.stdout.strip()

                if in_progress and "No issues found" not in in_progress:
                    lines = len(
                        [
                            line
                            for line in in_progress.split("\n")
                            if line.strip() and "○" in line
                        ]
                    )
                    print(f"📋 Active Issues: {lines} in progress")
                else:
                    print("📋 Active Issues: None in progress")

            except Exception:
                print("📋 Active Issues: Unable to check")
        else:
            print("📋 Active Issues: Beads not available")

        # Session locks
        session_locks_dir = self.agent_dir / "session_locks"
        if session_locks_dir.exists():
            lock_files = list(session_locks_dir.glob("*.json"))
            active_locks = []

            for lock_file in lock_files:
                try:
                    with open(lock_file, "r") as f:
                        lock_data = json.load(f)
                    active_locks.append(
                        f"Agent: {lock_data.get('agent', 'unknown')} - {lock_data.get('task_id', 'no task')}"
                    )
                except:
                    pass

            if active_locks:
                print(f"🔒 Active Sessions: {len(active_locks)}")
                for lock in active_locks[:2]:  # Show first 2
                    print(f"    • {lock}")
            else:
                print("🔒 Active Sessions: None")
        else:
            print("🔒 Active Sessions: No session locks directory")

        print()

    def _show_protocol_highlights(self):
        """Display key protocol requirements"""
        print("📜 PROTOCOL HIGHLIGHTS")
        print("---------------------")
        print("🧪 Quality Gates:")
        print("   1. Tests (pytest) - if test suite exists")
        print("   2. Linting (ruff) - code quality checks")
        print("   3. Type Checking (mypy) - type validation")
        print("   4. Markdown Duplicates - must be resolved before RTB")
        print("   5. SOP Evaluation - PFC compliance check")
        print()
        print("📝 Closure Requirements:")
        print("   • File locations and descriptions")
        print("   • Quick start instructions")
        print("   • Documentation references")
        print("   • Integration guidance")
        print("   • Production considerations")
        print()
        print("🔄 Learning Capture:")
        print("   • Real-time friction logging")
        print("   • Tool/Process friction points")
        print("   • User corrections and preferences")
        print("   • Success patterns and failures")
        print()
        print("🚫 RTB Blockers:")
        print("   • Uncommitted changes not pushed")
        print("   • Duplicate markdown files")
        print("   • Failed SOP evaluation")
        print("   • Missing closure notes")
        print()

    def _show_friction_areas(self):
        """Show areas to monitor for learning capture"""
        print("🎯 AREAS TO WATCH")
        print("---------------")
        print("🔧 Tool/Process Friction:")
        print("   • Slow or buggy tool execution")
        print("   • Inefficient workflows")
        print("   • Missing dependencies")
        print("   • Version conflicts")
        print()
        print("📝 Corrections & Preferences:")
        print("   • Direct user feedback ('No,' 'Wrong,' 'Actually...')")
        print("   • Coding style preferences")
        print("   • Architectural guidance")
        print("   • Naming conventions")
        print()
        print("✅ Success Patterns:")
        print("   • Approaches that work particularly well")
        print("   • Quick solutions to common problems")
        print("   • Effective tool combinations")
        print("   • Productive workflows")
        print()
        print("🚫 Failures & Challenges:")
        print("   • Mistakes and dead ends")
        print("   • Misunderstood requirements")
        print("   • Failed approaches")
        print("   • Configuration issues")
        print()
        print("🔄 Workarounds & Performance:")
        print("   • Temporary fixes needed")
        print("   • Performance bottlenecks")
        print("   • Memory/resource issues")
        print("   • Timeout or slowness problems")
        print()

    def _show_common_pitfalls(self):
        """Display common mistakes to avoid"""
        print("⚠️  COMMON PITFALLS")
        print("------------------")
        print("🚫 Documentation Mistakes:")
        print("   • Forgetting closure notes with file locations")
        print("   • Missing quick start instructions")
        print("   • No integration guidance provided")
        print("   • No production considerations")
        print()
        print("🧪 Quality Gate Issues:")
        print("   • Not running tests before RTB")
        print("   • Ignoring linting/type checking errors")
        print("   • Duplicate markdown files blocking RTB")
        print("   • Failed SOP evaluation")
        print()
        print("🔧 Git & Workflow:")
        print("   • Assuming git push worked without verification")
        print("   • Not checking branch cleanup on feature branches")
        print("   • Leaving temporary files and artifacts")
        print("   • Forgetting to sync beads database")
        print()
        print("🧠 Learning & Reflection:")
        print("   • Trying to remember friction points retrospectively")
        print("   • Not capturing user corrections exactly")
        print("   • Missing severity levels for issues")
        print("   • Not noting time spent on approaches")
        print()
        print("💡 PRO TIP: Create a friction log file and add notes as they happen!")
        print()

    def _show_session_checklist(self):
        """Show quick reference checklist"""
        print("📋 SESSION CHECKLIST")
        print("-------------------")
        print("✅ Pre-Mission:")
        print("   □ Review this mission briefing")
        print("   □ Understand task requirements")
        print("   □ Note any special instructions")
        print()
        print("🔍 During Mission:")
        print("   □ Monitor friction points in real-time")
        print("   □ Tag issues with severity: [CRITICAL], [HIGH], [MEDIUM], [LOW]")
        print("   □ Record exact error messages")
        print("   □ Note user corrections exactly")
        print("   □ Track time spent on approaches")
        print()
        print("🏁 Pre-RTB:")
        print("   □ Run quality gates (if code changed)")
        print("   □ Add comprehensive closure notes")
        print("   □ Resolve duplicate markdown files")
        print("   □ Complete reflection capture")
        print()
        print("🚀 After RTB:")
        print("   □ Verify all changes pushed successfully")
        print("   □ Confirm session cleaned up")
        print("   □ Check next agent has proper context")
        print()

    def _command_exists(self, command):
        """Check if a command exists in the system"""
        try:
            subprocess.run(
                [command, "--version"], capture_output=True, check=True, timeout=5
            )
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return False


def main():
    """Main entry point for mission briefing"""

    # Check if we're in a valid workspace
    if not Path(".git").exists():
        print("❌ ERROR: Not in a git repository")
        print("💡 Navigate to your LightRAG workspace and try again")
        sys.exit(1)

    briefing = MissionBriefing()

    try:
        briefing.run_briefing()
    except KeyboardInterrupt:
        print("\n👋 Mission briefing interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERROR: Mission briefing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
