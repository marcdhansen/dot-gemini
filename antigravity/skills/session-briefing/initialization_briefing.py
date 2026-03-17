#!/usr/bin/env python3
"""
Initialization Briefing Skill - Essential pre-mission information for agents
Provides balanced overview of protocol, current status, and areas to watch

Optimizations:
- Ultra-Lite mode for administrative tasks
- Parallel command execution
- Cached static content
- Optimized git checks
"""

import argparse
import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


ADMIN_KEYWORDS = {
    "beads",
    "bd",
    "issue",
    "task",
    "question",
    "q&a",
    "docs",
    "documentation",
    "research",
    "read",
    "review",
    "explain",
    "help",
    "how",
    "what",
    "why",
    "where",
    "when",
    "which",
    "list",
    "show",
    "get",
    "check",
    "status",
    "metadata",
    "admin",
    "create",
    "update",
    "close",
    "info",
    "info-only",
    "no-code",
    "no code",
    "meta",
}

STATIC_CONTENT_CACHE_TTL = 3600


class InitializationBriefing:
    def __init__(self):
        self.workspace_dir = Path.cwd()
        self.agent_dir = self.workspace_dir / ".agent"
        self.cache_dir = self.agent_dir / ".briefing_cache"
        self._lock = threading.Lock()

    def _get_static_content_cache_path(self) -> Path:
        return self.cache_dir / "static_content.json"

    def _is_admin_task(self, args: Optional[list] = None) -> bool:
        """Detect if current task is administrative/non-implementation"""
        if args:
            args_str = " ".join(args).lower()
            if any(kw in args_str for kw in ADMIN_KEYWORDS):
                return True

        task_desc_file = self.agent_dir / "current_task.txt"
        if task_desc_file.exists():
            try:
                content = task_desc_file.read_text().lower()
                if any(kw in content for kw in ADMIN_KEYWORDS):
                    return True
            except:
                pass

        issue_file = self.agent_dir / "current"
        if issue_file.exists():
            try:
                issue_id = issue_file.read_text().strip()
                if issue_id:
                    result = subprocess.run(
                        ["bd", "show", issue_id],
                        capture_output=True,
                        text=True,
                        cwd=self.workspace_dir,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        issue_info = result.stdout.lower()
                        if any(kw in issue_info for kw in ADMIN_KEYWORDS):
                            return True
            except:
                pass

        return False

    def run_briefing(self, turbo: bool = False, force_full: bool = False):
        """Generate and display initialization briefing (Ultra-Lite, Turbo, or Full)"""

        mode = "turbo" if turbo else "full"

        if not force_full and self._is_admin_task():
            mode = "ultra-lite"
            print("🎯 ADMINISTRATIVE TASK DETECTED - Ultra-Lite Mode")
            print("=" * 60)
            print()

        if mode != "ultra-lite" and turbo:
            is_clean, _ = self._check_for_code_changes_fast()
            if not is_clean:
                print("⚠️ ESCALATION DETECTED: Code changes found. Switching to FULL BRIEFING.")
                mode = "full"

        mode_str = mode.upper()
        print(f"🚀 INITIALIZATION BRIEFING - {mode_str} MODE")
        print("=" * 60)
        print()

        if mode == "ultra-lite":
            self._show_current_status_fast()
        else:
            self._run_full_briefing(mode == "turbo")

    def _run_full_briefing(self, turbo: bool):
        """Run full briefing with parallel execution"""

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_status = executor.submit(self._get_status_data)
            future_prs = executor.submit(self._get_prs_data)
            future_beads = executor.submit(self._get_beads_pr_open_data)

            status_data = future_status.result()
            self._display_status_data(status_data)

            prs_data = future_prs.result()
            if prs_data:
                self._display_prs_data(prs_data)

            beads_data = future_beads.result()
            if beads_data:
                self._display_beads_data(beads_data)

        if turbo:
            print("⚡ TURBO MODE ACTIVE: Minimal protocol required.")
            print("   • Focus: Administrative/Metadata tasks (Beads, Q&A)")
            print("   • Status: Direct execution enabled")
            print("   • Note: ANY code change will require escalation to Full SOP.")
        else:
            static_content = self._get_or_create_static_content()
            self._display_static_content(static_content)

    def _get_status_data(self) -> dict:
        """Gather status data concurrently"""
        data = {"git_clean": True, "branch": "unknown", "in_progress_issues": 0, "active_locks": 0}

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.workspace_dir,
        )
        data["git_clean"] = not bool(result.stdout.strip())

        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=self.workspace_dir,
        )
        data["branch"] = result.stdout.strip()

        if self._command_exists("bd"):
            result = subprocess.run(
                ["bd", "list", "--status", "in_progress", "--limit", "5"],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
            )
            if result.stdout and "No issues found" not in result.stdout:
                data["in_progress_issues"] = len(
                    [l for l in result.stdout.split("\n") if l.strip() and "○" in l]
                )

        session_locks_dir = self.agent_dir / "session_locks"
        if session_locks_dir.exists():
            data["active_locks"] = len(list(session_locks_dir.glob("*.json")))

        return data

    def _get_prs_data(self) -> Optional[list]:
        """Get PR data concurrently"""
        if not self._command_exists("gh"):
            return None

        try:
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--state",
                    "open",
                    "--json",
                    "number,title,headRefName,createdAt,url",
                    "--limit",
                    "30",
                ],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
                timeout=10,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return None

    def _get_beads_pr_open_data(self) -> Optional[list]:
        """Get beads pr:open issues concurrently"""
        if not self._command_exists("bd"):
            return None

        try:
            result = subprocess.run(
                ["bd", "list", "--label", "pr:open"],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
                timeout=15,
            )
            if (
                result.returncode == 0
                and result.stdout.strip()
                and "No issues found" not in result.stdout
            ):
                return [
                    l for l in result.stdout.split("\n") if l.strip() and ("○" in l or "●" in l)
                ]
        except:
            pass
        return None

    def _display_status_data(self, data: dict):
        """Display status data"""
        print("📍 CURRENT STATUS")
        print("-----------------")

        if data["git_clean"]:
            print("✅ Git: Working directory clean")
        else:
            print("📝 Git: Uncommitted changes present")

        print(f"🌿 Branch: {data['branch']}")

        if data["branch"].startswith("agent/") or data["branch"].startswith("feature/"):
            print("🔧 Feature branch detected - extra cleanup required")

        if data["in_progress_issues"] > 0:
            print(f"📋 Active Issues: {data['in_progress_issues']} in progress")
        else:
            print("📋 Active Issues: None in progress")

        if data["active_locks"] > 0:
            print(f"🔒 Active Sessions: {data['active_locks']}")
        else:
            print("🔒 Active Sessions: None")

        print()

    def _display_prs_data(self, prs: list):
        """Display PR data"""
        if not prs:
            print("✅ PRs: No open PRs requiring review")
            print("---------------------------------")
            return

        print(f"🔴 OPEN PRs NEEDING REVIEW ({len(prs)})")
        print("---------------------------------")
        for pr in prs:
            number = pr.get("number", "?")
            title = pr.get("title", "Unknown")
            branch = pr.get("headRefName", "unknown")
            created = pr.get("createdAt", "")
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                now = datetime.now(dt.tzinfo)
                days = (now - dt).days
                age_str = f"{days}d ago"
            except:
                age_str = "..."

            print(f"  • #{number} {title}")
            print(f"     └─ Branch: {branch} | Age: {age_str}")

        print()
        print(
            "💡 PRIORITY ACTION: Open PRs are TOP PRIORITY. Review them before starting new tracks."
        )
        print()

    def _display_beads_data(self, issues: list):
        """Display beads pr:open data"""
        print(f"🔵 BEADS ISSUES WITH 'pr:open' LABEL ({len(issues)})")
        print("---------------------------------")
        for issue in issues[:10]:
            print(f"  {issue.strip()}")

        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")

        print()
        print("💡 These issues have open PRs linked. Review them before starting new work.")
        print()

    def _show_current_status_fast(self):
        """Fast status display for Ultra-Lite mode"""
        data = self._get_status_data()
        self._display_status_data(data)

        print(f"🎯 READY: Ultra-Lite mode - minimal briefing complete!")
        print()

    def _get_or_create_static_content(self) -> dict:
        """Get cached static content or create new"""
        cache_path = self._get_static_content_cache_path()

        try:
            if cache_path.exists():
                stat = cache_path.stat()
                age = datetime.now().timestamp() - stat.st_mtime
                if age < STATIC_CONTENT_CACHE_TTL:
                    return json.loads(cache_path.read_text())
        except:
            pass

        static_content = {
            "protocol_highlights": self._generate_protocol_highlights(),
            "friction_areas": self._generate_friction_areas(),
            "common_pitfalls": self._generate_common_pitfalls(),
            "session_checklist": self._generate_session_checklist(),
            "cached_at": datetime.now().isoformat(),
        }

        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(static_content, indent=2))
        except:
            pass

        return static_content

    def _generate_protocol_highlights(self) -> list:
        return [
            "🧪 Quality Gates:",
            "   1. Tests (pytest) - if test suite exists",
            "   2. Linting (ruff) - code quality checks",
            "   3. Type Checking (mypy) - type validation",
            "   4. Markdown Duplicates - must be resolved before Finalization",
            "   5. SOP Evaluation - Initialization compliance check",
            "",
            "📝 Closure Requirements:",
            "   • File locations and descriptions",
            "   • Quick start instructions",
            "   • Documentation references",
            "   • Integration guidance",
            "   • Production considerations",
            "",
            "🔄 Learning Capture:",
            "   • Real-time friction logging",
            "   • Tool/Process friction points",
            "   • User corrections and preferences",
            "",
            "🚫 Finalization Blockers:",
            "   • Uncommitted changes not pushed",
            "   • Duplicate markdown files",
            "   • Failed SOP evaluation",
            "   • Missing closure notes",
        ]

    def _generate_friction_areas(self) -> list:
        return [
            "🎯 AREAS TO WATCH",
            "---------------",
            "🔧 Tool/Process Friction:",
            "   • Slow or buggy tool execution",
            "   • Inefficient workflows",
            "",
            "📝 Corrections & Preferences:",
            "   • Direct user feedback ('No,' 'Wrong,' 'Actually...')",
            "   • Coding style preferences",
            "",
            "✅ Success Patterns:",
            "   • Approaches that work particularly well",
            "   • Quick solutions to common problems",
            "",
            "🚫 Failures & Challenges:",
            "   • Mistakes and dead ends",
            "   • Misunderstood requirements",
            "",
            "🔄 Workarounds & Performance:",
            "   • Temporary fixes needed",
            "   • Performance bottlenecks",
        ]

    def _generate_common_pitfalls(self) -> list:
        return [
            "⚠️  COMMON PITFALLS",
            "------------------",
            "🚫 Documentation Mistakes:",
            "   • Forgetting closure notes with file locations",
            "   • Missing quick start instructions",
            "",
            "🧪 Quality Gate Issues:",
            "   • Not running tests before Finalization",
            "   • Ignoring linting/type checking errors",
            "",
            "🔧 Git & Workflow:",
            "   • Assuming git push worked without verification",
            "   • Not checking branch cleanup on feature branches",
            "",
            "🧠 Learning & Reflection:",
            "   • Trying to remember friction points retrospectively",
            "   • Not capturing user corrections exactly",
        ]

    def _generate_session_checklist(self) -> list:
        return [
            "📋 SESSION CHECKLIST",
            "-------------------",
            "✅ Pre-Mission:",
            "   □ Review this initialization briefing",
            "   □ Understand task requirements",
            "",
            "🔍 During Mission:",
            "   □ Monitor friction points in real-time",
            "   □ Tag issues with severity: [CRITICAL], [HIGH], [MEDIUM], [LOW]",
            "   □ Record exact error messages",
            "",
            "🏁 Pre-Finalization:",
            "   □ Run quality gates (if code changed)",
            "   □ Add comprehensive closure notes",
            "",
            "🚀 After Finalization:",
            "   □ Verify all changes pushed successfully",
            "   □ Confirm session cleaned up",
        ]

    def _display_static_content(self, content: dict):
        """Display cached static content"""
        print("---------------------")
        for line in content["protocol_highlights"]:
            print(line)

        print()
        for line in content["friction_areas"]:
            print(line)

        print()
        for line in content["common_pitfalls"]:
            print(line)

        print()
        for line in content["session_checklist"]:
            print(line)

        print()
        print("💡 PRO TIP: Create a friction log file and add notes as they happen!")

    def _check_for_code_changes_fast(self) -> Tuple[bool, str]:
        """Fast git check - exit on first code file found"""
        try:
            result = subprocess.run(
                ["git", "diff", "--quiet"],
                capture_output=True,
                cwd=self.workspace_dir,
            )
            if result.returncode == 0:
                return True, "Clean"

            code_exts = {".py", ".sh", ".js", ".ts", ".go", ".c", ".cpp", ".java", ".rs"}
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
            )
            for line in result.stdout.strip().split("\n"):
                if line:
                    filepath = line[3:] if len(line) > 3 else line
                    if any(filepath.endswith(ext) for ext in code_exts):
                        return False, "Code changes detected"
            return True, "No code changes"
        except:
            return True, "Unknown"

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system"""
        try:
            subprocess.run(
                [command, "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return False


def main():
    """Main entry point for initialization briefing"""
    parser = argparse.ArgumentParser(description="Initialization Briefing Skill")
    parser.add_argument("--turbo", action="store_true", help="Run in Turbo Mode (lightweight)")
    parser.add_argument(
        "--force-full", action="store_true", help="Force Full Mode regardless of task type"
    )
    parser.add_argument("--clear-cache", action="store_true", help="Clear static content cache")
    args = parser.parse_args()

    if not Path(".git").exists():
        print("❌ ERROR: Not in a git repository")
        print("💡 Navigate to your LightRAG workspace and try again")
        sys.exit(1)

    briefing = InitializationBriefing()

    if args.clear_cache:
        cache_path = briefing._get_static_content_cache_path()
        if cache_path.exists():
            cache_path.unlink()
            print("✅ Cache cleared")

    try:
        briefing.run_briefing(turbo=args.turbo, force_full=args.force_full)
    except KeyboardInterrupt:
        print("\n👋 Initialization briefing interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERROR: Initialization briefing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
