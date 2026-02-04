#!/usr/bin/env python3
"""Browser Manager - Playwright browser process lifecycle management."""

import argparse
import json
import os
import psutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    import requests
except ImportError:
    print("⚠️ Warning: 'requests' package not available, some features may be limited")
    requests = None


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output."""
        cls.GREEN = ""
        cls.RED = ""
        cls.YELLOW = ""
        cls.BLUE = ""
        cls.BOLD = ""
        cls.END = ""


class BrowserManager:
    """Manages Playwright browser processes with tab tracking and cleanup."""

    def __init__(self, config_path: Optional[Path] = None):
        self.home_dir = Path.home()
        self.config_path = config_path or (
            Path(__file__).parent.parent / "config" / "limits.yaml"
        )
        self.session_file = self.home_dir / ".gemini" / "browser_sessions.json"
        self.audit_log = self.home_dir / ".gemini" / "browser_audit.log"

        # Get current agent ID from environment or create one
        self.agent_id = (
            os.environ.get("AGENT_ID") or os.environ.get("USER") or "unknown-agent"
        )

        self.config = self._load_config()
        self._ensure_session_dir()

        # Disable colors if not in terminal
        if not sys.stdout.isatty():
            Colors.disable()

    def _ensure_session_dir(self):
        """Ensure session data directory exists."""
        session_dir = self.session_file.parent
        session_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        import yaml

        if not self.config_path.exists():
            # Create default config if it doesn't exist
            return self._create_default_config()

        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Warning: Could not load config: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict:
        """Create default configuration with no limits."""
        return {
            "limits": {
                "max_tabs_per_agent": None,
                "max_browser_age_minutes": None,
                "max_memory_mb": None,
                "max_browsers_total": None,
            },
            "admin": {
                "require_permission_for_others": True,
                "permission_timeout_seconds": 30,
                "audit_log_enabled": True,
                "force_cleanup_confirmation": True,
            },
            "tracking": {
                "delete_on_mission_end": True,
                "session_retention_hours": 24,
                "tab_detection_timeout": 5,
                "process_scan_interval": 2,
            },
            "tab_detection": {
                "preferred_method": "devtools",
                "enable_fallback": True,
                "show_incognito_counts": True,
                "truncate_length": 50,
            },
            "display": {
                "show_tabs_in_status": True,
                "show_memory_usage": True,
                "show_age_info": True,
                "use_colors": True,
                "verbose_mode": False,
            },
            "cleanup": {
                "graceful_shutdown_timeout": 10,
                "enable_force_kill": True,
                "cleanup_user_data_dirs": False,
                "confirm_own_cleanup": False,
                "show_cleanup_summary": True,
            },
        }

    def detect_playwright_browsers(self) -> List[Dict]:
        """Detect all Playwright-managed browser processes."""
        browsers = []

        for proc in psutil.process_iter(
            ["pid", "name", "cmdline", "create_time", "memory_info", "username"]
        ):
            try:
                cmdline = " ".join(proc.info["cmdline"] or [])

                if self._is_playwright_browser(proc, cmdline):
                    browser_info = {
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "cmdline": cmdline,
                        "start_time": datetime.fromtimestamp(proc.info["create_time"]),
                        "memory_mb": proc.info["memory_info"].rss / 1024 / 1024,
                        "user_data_dir": self._extract_user_data_dir(cmdline),
                        "debug_port": self._find_debugging_port(cmdline),
                        "agent_id": self._get_agent_for_pid(proc.info["pid"]),
                        "username": proc.info["username"],
                    }

                    # Detect tabs for this browser
                    browser_info["tabs"] = self.detect_browser_tabs(browser_info)

                    browsers.append(browser_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return browsers

    def _is_playwright_browser(self, proc, cmdline: str) -> bool:
        """Check if process is a Playwright-managed browser."""
        # Check for Chrome/Chromium with Playwright indicators
        if "chrome" not in proc.info["name"].lower():
            return False

        # Skip renderer and helper processes (they have --type=renderer, --type=gpu-process, etc.)
        if "--type=" in cmdline and "renderer" in cmdline:
            return False

        playwright_indicators = [
            "--remote-debugging-port",
            "--user-data-dir",
            "playwright",
            "--no-first-run",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
        ]

        # Must have user-data-dir (Playwright typical)
        if "--user-data-dir" not in cmdline:
            return False

        # Must have remote debugging (for tab detection)
        if "--remote-debugging-port" not in cmdline:
            return False

        return any(indicator in cmdline for indicator in playwright_indicators)

    def _extract_user_data_dir(self, cmdline: str) -> Optional[str]:
        """Extract user data directory from command line."""
        for part in cmdline.split():
            if part.startswith("--user-data-dir="):
                return part.split("=", 1)[1]
        return None

    def _find_debugging_port(self, cmdline: str) -> Optional[int]:
        """Find remote debugging port from command line."""
        for part in cmdline.split():
            if part.startswith("--remote-debugging-port="):
                try:
                    return int(part.split("=", 1)[1])
                except ValueError:
                    pass
        return None

    def _get_agent_for_pid(self, pid: int) -> str:
        """Get agent ID that owns this browser process."""
        if not self.session_file.exists():
            return "unknown"

        try:
            sessions = self._load_sessions()
            for session_data in sessions.values():
                if session_data.get("browser_info", {}).get("pid") == pid:
                    return session_data.get("agent_id", "unknown")
        except Exception:
            pass

        return "unknown"

    def detect_browser_tabs(self, browser_info: Dict) -> List[Dict]:
        """Detect tabs for a browser using Chrome DevTools Protocol."""
        if not requests or not browser_info.get("debug_port"):
            # Fallback: estimate tab count from process info
            return self._estimate_tab_count(browser_info)

        debug_port = browser_info["debug_port"]
        try:
            response = requests.get(
                f"http://localhost:{debug_port}/json",
                timeout=self.config.get("tab_detection", {}).get(
                    "tab_detection_timeout", 5
                ),
            )
            if response.status_code == 200:
                tabs_data = response.json()
                tabs = []

                for tab in tabs_data:
                    # Skip devtools and background pages
                    if tab.get("type") in [
                        "devtools",
                        "background_page",
                        "service_worker",
                    ]:
                        continue

                    tab_info = {
                        "id": tab.get("id"),
                        "url": tab.get("url", "about:blank"),
                        "title": tab.get("title", "Untitled"),
                        "type": tab.get("type", "page"),
                        "browser_pid": browser_info["pid"],
                        "agent_id": browser_info["agent_id"],
                    }

                    # Truncate for privacy in logs
                    truncate_len = self.config["tab_detection"]["truncate_length"]
                    if len(tab_info["title"]) > truncate_len:
                        tab_info["title"] = tab_info["title"][:truncate_len] + "..."
                    if len(tab_info["url"]) > truncate_len:
                        tab_info["url"] = tab_info["url"][:truncate_len] + "..."

                    tabs.append(tab_info)

                return tabs
        except Exception as e:
            if self.config["display"]["verbose_mode"]:
                print(f"⚠️ Tab detection failed for PID {browser_info['pid']}: {e}")

        # Fallback to estimation
        return self._estimate_tab_count(browser_info)

    def _estimate_tab_count(self, browser_info: Dict) -> List[Dict]:
        """Estimate tab count from process information."""
        # Very basic estimation - in future could analyze window handles
        estimated_count = 1  # Assume at least 1 tab

        return [
            {
                "id": "estimated",
                "url": "about:blank",
                "title": f"Estimated {estimated_count} tab(s)",
                "type": "estimated",
                "browser_pid": browser_info["pid"],
                "agent_id": browser_info["agent_id"],
            }
            for _ in range(estimated_count)
        ]

    def check_resource_limits(self) -> Tuple[bool, List[str]]:
        """Check if browser usage exceeds configured limits (soft warnings only)."""
        browsers = self.detect_playwright_browsers()
        agent_browsers = [b for b in browsers if b["agent_id"] == self.agent_id]

        warnings = []
        limits = self.config["limits"]

        # Tab count warning
        if limits["max_tabs_per_agent"]:
            total_tabs = sum(len(b["tabs"]) for b in agent_browsers)
            if total_tabs >= limits["max_tabs_per_agent"]:
                warnings.append(
                    f"High tab count: {total_tabs} >= {limits['max_tabs_per_agent']}"
                )

        # Memory warning
        if limits["max_memory_mb"]:
            total_memory = sum(b["memory_mb"] for b in agent_browsers)
            if total_memory >= limits["max_memory_mb"]:
                warnings.append(
                    f"High memory usage: {total_memory:.0f}MB >= {limits['max_memory_mb']}MB"
                )

        # Age warning
        if limits["max_browser_age_minutes"]:
            for browser in agent_browsers:
                age = datetime.now() - browser["start_time"]
                if age >= timedelta(minutes=limits["max_browser_age_minutes"]):
                    warnings.append(
                        f"Old browser: PID {browser['pid']} running for {age}"
                    )

        # Global browser count warning
        if limits["max_browsers_total"]:
            if len(browsers) >= limits["max_browsers_total"]:
                warnings.append(
                    f"High global browser count: {len(browsers)} >= {limits['max_browsers_total']}"
                )

        return len(warnings) == 0, warnings

def request_cleanup_permission(
        self, target_agent: str, browsers: List[Dict]
    ) -> bool:
        """Request user permission before cleaning other agents' browsers."""
        if not self.config["admin"]["require_permission_for_others"]:
            return True

        # Check for non-interactive environment
        import sys
        import os
        
        is_non_interactive = (
            not sys.stdin.isatty() or
            os.getenv("CI") or 
            os.getenv("GITHUB_ACTIONS") or
            os.getenv("AUTOMATED_MODE")
        )
        
        if is_non_interactive:
            print(f"\n{Colors.YELLOW}🤖 Non-interactive mode detected - Auto-approving cleanup{Colors.END}")
            print(
                f"Auto-cleaning {len(browsers)} browser(s) from agent '{target_agent}' (CI/automated environment)"
            )
            return True

        print(f"\n{Colors.YELLOW}🔒 Admin Permission Required{Colors.END}")
        print(
            f"Attempting to clean up {len(browsers)} browser(s) from agent '{target_agent}'"
        )
        print()

        total_tabs = 0
        for browser in browsers:
            tabs = browser.get("tabs", [])
            total_tabs += len(tabs)
            age = datetime.now() - browser["start_time"]

            print(
                f"  • PID {browser['pid']}: {len(tabs)} tabs, {browser['memory_mb']:.0f}MB, running {age}"
            )

            if self.config["display"]["show_tabs_in_status"] and tabs:
                for tab in tabs[:3]:  # Show first 3 tabs
                    print(f"    - {tab['title']}")
                if len(tabs) > 3:
                    print(f"    ... and {len(tabs) - 3} more tabs")
        print()

        try:
            timeout = self.config["admin"]["permission_timeout_seconds"]
            prompt = f"Clean up {target_agent}'s {len(browsers)} browser(s) with {total_tabs} tabs? [y/N] "
            print(f"Timeout: {timeout} seconds")

            start_time = time.time()
            while True:
                if time.time() - start_time > timeout:
                    print(f"\n⏰ Permission timeout - operation cancelled")
                    return False

                # Check for non-interactive environment
                import sys
                import os
                is_non_interactive = (
                    not sys.stdin.isatty() or
                    os.getenv("CI") or 
                    os.getenv("GITHUB_ACTIONS") or
                    os.getenv("AUTOMATED_MODE")
                )
                
                if is_non_interactive:
                    print(f"\n{Colors.YELLOW}🤖 Non-interactive mode - Auto-approving cleanup{Colors.END}")
                    response = "y"  # Auto-approve
                else:
                    try:
                        response = input(prompt).strip().lower()
                    except EOFError:
                        print(f"\n⏰ Permission timeout - operation cancelled")
                        return False
                    except KeyboardInterrupt:
                        print(f"\n❌ Operation cancelled by user")
                        return False
                break

            if response in ["y", "yes"]:
                print(f"✅ Permission granted")
                return True
            else:
                print(f"❌ Permission denied")
                return False

        except Exception as e:
            print(f"❌ Error requesting permission: {e}")
            return False

                try:
                    response = input(prompt).strip().lower()
                    break
                except EOFError:
                    print(f"\n⏰ Permission timeout - operation cancelled")
                    return False
                except KeyboardInterrupt:
                    print(f"\n❌ Operation cancelled by user")
                    return False

            return response in ["y", "yes"]

        except Exception as e:
            print(f"⚠️ Error getting permission: {e}")
            return False

    def cleanup_browsers(
        self, target_agent: Optional[str] = None, force: bool = False
    ) -> Dict:
        """Cleanup browser processes with permission system."""
        browsers = self.detect_playwright_browsers()

        # Determine targets
        if target_agent:
            targets = [b for b in browsers if b["agent_id"] == target_agent]
        elif force or target_agent == "all":
            targets = browsers
        else:
            targets = [b for b in browsers if b["agent_id"] == self.agent_id]

        # Check permission for other agents' browsers
        other_agent_browsers = [b for b in targets if b["agent_id"] != self.agent_id]
        if other_agent_browsers and not force:
            # Group by agent for permission requests
            agents = {}
            for browser in other_agent_browsers:
                agent = browser["agent_id"]
                if agent not in agents:
                    agents[agent] = []
                agents[agent].append(browser)

            for agent_id, agent_browsers in agents.items():
                if not self.request_cleanup_permission(agent_id, agent_browsers):
                    # Remove this agent's browsers from targets
                    targets = [b for b in targets if b["agent_id"] != agent_id]

        # Confirm own cleanup if required
        own_browsers = [b for b in targets if b["agent_id"] == self.agent_id]
        if own_browsers and self.config["cleanup"]["confirm_own_cleanup"] and not force:
            total_tabs = sum(len(b.get("tabs", [])) for b in own_browsers)
            if not self.request_cleanup_permission(self.agent_id, own_browsers):
                targets = [b for b in targets if b["agent_id"] != self.agent_id]

        # Execute cleanup
        return self._execute_cleanup(targets)

    def _execute_cleanup(self, targets: List[Dict]) -> Dict:
        """Execute the actual cleanup operation."""
        stats = {"attempted": 0, "success": 0, "failed": 0, "skipped": 0}

        for browser in targets:
            stats["attempted"] += 1

            pid = browser["pid"]
            try:
                # Try graceful shutdown first
                proc = psutil.Process(pid)

                # Send SIGTERM for graceful shutdown
                proc.terminate()

                # Wait for graceful shutdown
                timeout = self.config["cleanup"]["graceful_shutdown_timeout"]
                try:
                    proc.wait(timeout=timeout)
                    stats["success"] += 1

                    # Log audit entry
                    self._log_audit("cleanup_success", browser)

                except psutil.TimeoutExpired:
                    if self.config["cleanup"]["enable_force_kill"]:
                        # Force kill if graceful shutdown fails
                        proc.kill()
                        proc.wait(timeout=5)
                        stats["success"] += 1
                        self._log_audit("cleanup_force_kill", browser)
                    else:
                        stats["failed"] += 1
                        self._log_audit(
                            "cleanup_failed",
                            browser,
                            "Graceful shutdown timeout, force kill disabled",
                        )

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                stats["skipped"] += 1
                self._log_audit("cleanup_skipped", browser, str(e))

        # Clean up session tracking
        self._update_session_tracking(targets)

        if self.config["cleanup"]["show_cleanup_summary"]:
            print(
                f"🧹 Cleanup Summary: {stats['success']}/{stats['attempted']} successful"
            )
            if stats["failed"] > 0:
                print(f"  ⚠️ {stats['failed']} failed")
            if stats["skipped"] > 0:
                print(f"  ℹ️ {stats['skipped']} skipped")

        return stats

    def _log_audit(self, action: str, browser: Dict, details: Optional[str] = None):
        """Log audit entry for cross-agent operations."""
        if not self.config["admin"]["audit_log_enabled"]:
            return

        try:
            timestamp = datetime.now().isoformat()
            entry = {
                "timestamp": timestamp,
                "action": action,
                "agent_id": self.agent_id,
                "target_agent_id": browser.get("agent_id"),
                "browser_pid": browser["pid"],
                "memory_mb": browser.get("memory_mb"),
                "tab_count": len(browser.get("tabs", [])),
                "details": details,
            }

            with open(self.audit_log, "a") as f:
                f.write(json.dumps(entry) + "\n")

        except Exception as e:
            print(f"⚠️ Failed to write audit log: {e}")

    def show_status(self, detailed: bool = False, refresh: bool = False):
        """Display current browser usage status."""
        browsers = self.detect_playwright_browsers()
        agent_browsers = [b for b in browsers if b["agent_id"] == self.agent_id]

        print(
            f"{Colors.BOLD}🌐 Browser Manager Status - Agent: {self.agent_id}{Colors.END}"
        )
        print("=" * 50)
        print()

        # Global stats
        total_tabs = sum(len(b.get("tabs", [])) for b in browsers)
        agent_tabs = sum(len(b.get("tabs", [])) for b in agent_browsers)
        total_memory = sum(b["memory_mb"] for b in browsers)
        agent_memory = sum(b["memory_mb"] for b in agent_browsers)

        agents = list(set(b["agent_id"] for b in browsers))

        print(f"📊 Global Stats:")
        print(f"  • Total agents: {len(agents)}")
        print(f"  • Total browsers: {len(browsers)}")
        print(f"  • Total tabs: {total_tabs}")
        if self.config["display"]["show_memory_usage"]:
            print(f"  • Total memory: {total_memory:.0f}MB")
        print()

        print(f"🖥️  Your Browser Sessions:")
        print(f"  • Browsers: {len(agent_browsers)}")
        print(f"  • Tabs: {agent_tabs}")
        if self.config["display"]["show_memory_usage"]:
            print(f"  • Memory: {agent_memory:.0f}MB")
        print()

        # Detailed browser info
        if agent_browsers and (
            detailed or self.config["display"]["show_tabs_in_status"]
        ):
            for browser in agent_browsers:
                age = datetime.now() - browser["start_time"]
                tabs = browser.get("tabs", [])

                print(
                    f"  📍 PID {browser['pid']}: {browser['name']} ({len(tabs)} tabs)"
                )

                if self.config["display"]["show_memory_usage"]:
                    print(f"     💾 Memory: {browser['memory_mb']:.0f}MB")
                if self.config["display"]["show_age_info"]:
                    print(f"     ⏰ Age: {age}")

                if detailed and tabs:
                    for tab in tabs[:5]:  # Show more tabs in detailed mode
                        print(f"     📄 {tab['title']}")
                    if len(tabs) > 5:
                        print(f"     ... and {len(tabs) - 5} more tabs")
                print()

        # Check limits
        limits_ok, warnings = self.check_resource_limits()
        if warnings:
            print(f"{Colors.YELLOW}⚠️ Resource Warnings:{Colors.END}")
            for warning in warnings:
                print(f"  • {warning}")
            print()

        # Configuration summary
        print(f"{Colors.BLUE}⚙️  Configuration:{Colors.END}")
        limits = self.config["limits"]
        active_limits = [k for k, v in limits.items() if v is not None]
        if active_limits:
            print(f"  • Active limits: {', '.join(active_limits)}")
        else:
            print(f"  • Limits: None configured (unlimited)")
        print()

        # Commands
        print(f"{Colors.GREEN}🔧 Commands:{Colors.END}")
        print(f"  • browser-manager status --detailed    # Detailed status")
        print(f"  • browser-manager tabs                 # Show all tabs")
        print(f"  • browser-manager cleanup              # Clean your browsers")
        print(f"  • browser-manager cleanup --all         # Clean all browsers")
        print(f"  • browser-manager config               # Show configuration")

    def rtb_cleanup(self):
        """RTB integration with automatic session cleanup."""
        print(f"{Colors.BLUE}🌐 Browser Manager RTB Cleanup{Colors.END}")
        print("=" * 40)

        # Clean up current agent's browsers
        stats = self.cleanup_browsers()
        print(f"  • Cleaned {stats['success']}/{stats['attempted']} browsers")

        # Clean up session data
        self.cleanup_session_data()
        print(f"  • Session data deleted")

        print(f"{Colors.GREEN}✅ Browser cleanup complete{Colors.END}")

    def cleanup_session_data(self):
        """Delete browser session tracking data at mission end."""
        if not self.config["tracking"]["delete_on_mission_end"]:
            return

        try:
            # Remove current agent's session data
            sessions = self._load_sessions()
            agent_sessions = {
                k: v for k, v in sessions.items() if v.get("agent_id") != self.agent_id
            }

            if agent_sessions:
                self.session_file.write_text(json.dumps(agent_sessions, indent=2))
            elif self.session_file.exists():
                self.session_file.unlink()

            if self.config["display"]["verbose_mode"]:
                print(f"🧹 Cleaned up browser session data for agent {self.agent_id}")

        except Exception as e:
            print(f"⚠️ Error cleaning session data: {e}")

    def _load_sessions(self) -> Dict:
        """Load browser session tracking data."""
        if not self.session_file.exists():
            return {}

        try:
            with open(self.session_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_sessions(self, sessions: Dict):
        """Save browser session tracking data."""
        try:
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.session_file, "w") as f:
                json.dump(sessions, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving sessions: {e}")

    def _update_session_tracking(self, cleaned_browsers: List[Dict]):
        """Update session tracking after cleanup."""
        sessions = self._load_sessions()

        # Remove cleaned browsers from tracking
        cleaned_pids = {b["pid"] for b in cleaned_browsers}
        sessions = {
            k: v
            for k, v in sessions.items()
            if v.get("browser_info", {}).get("pid") not in cleaned_pids
        }

        self._save_sessions(sessions)


def main():
    """Main CLI interface."""
    manager = BrowserManager()

    parser = argparse.ArgumentParser(
        description="Browser Manager - Playwright browser process lifecycle management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    browser-manager status              # Show browser usage
    browser-manager cleanup              # Clean your browsers  
    browser-manager cleanup --agent agent-42  # Clean specific agent's browsers
    browser-manager cleanup --all         # Clean all browsers
    browser-manager config               # Show configuration
        """,
    )

    parser.add_argument(
        "command",
        choices=[
            "status",
            "cleanup",
            "config",
            "sessions",
            "tabs",
            "rtb-cleanup",
            "check-limits",
        ],
        help="Command to execute",
    )

    parser.add_argument("--agent", help="Target specific agent ID for cleanup")

    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Apply to all agents (requires permission)",
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force cleanup without permission prompts",
    )

    parser.add_argument(
        "--detailed", "-d", action="store_true", help="Show detailed output"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose debugging output"
    )

    parser.add_argument(
        "--refresh",
        "-r",
        action="store_true",
        help="Force refresh of browser detection",
    )

    args = parser.parse_args()

    # Enable verbose mode if requested
    if args.verbose:
        manager.config["display"]["verbose_mode"] = True

    try:
        if args.command == "status":
            manager.show_status(detailed=args.detailed, refresh=args.refresh)

        elif args.command == "cleanup":
            target_agent = args.agent
            if args.all:
                target_agent = "all"

            stats = manager.cleanup_browsers(
                target_agent=target_agent, force=args.force
            )
            if not manager.config["cleanup"]["show_cleanup_summary"]:
                print(
                    f"Cleanup completed: {stats['success']}/{stats['attempted']} successful"
                )

        elif args.command == "rtb-cleanup":
            manager.rtb_cleanup()

        elif args.command == "check-limits":
            limits_ok, warnings = manager.check_resource_limits()
            if limits_ok:
                print(f"{Colors.GREEN}✅ No resource warnings{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️ Resource warnings detected:{Colors.END}")
                for warning in warnings:
                    print(f"  • {warning}")

        elif args.command == "config":
            print(f"{Colors.BLUE}⚙️ Current Configuration:{Colors.END}")
            print(json.dumps(manager.config, indent=2))

        elif args.command == "sessions":
            sessions = manager._load_sessions()
            if sessions:
                print(f"{Colors.BLUE}📋 Browser Sessions:{Colors.END}")
                print(json.dumps(sessions, indent=2))
            else:
                print(f"{Colors.GREEN}No active browser sessions tracked{Colors.END}")

        elif args.command == "tabs":
            browsers = manager.detect_playwright_browsers()
            if browsers:
                print(f"{Colors.BLUE}📄 All Browser Tabs:{Colors.END}")
                for browser in browsers:
                    tabs = browser.get("tabs", [])
                    print(
                        f"\n📍 PID {browser['pid']} ({browser['agent_id']}): {len(tabs)} tabs"
                    )
                    for tab in tabs:
                        print(f"  📄 {tab['title']}")
                        if args.verbose:
                            print(f"     {tab['url']}")
            else:
                print(f"{Colors.GREEN}No browsers found{Colors.END}")

    except KeyboardInterrupt:
        print(f"\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
