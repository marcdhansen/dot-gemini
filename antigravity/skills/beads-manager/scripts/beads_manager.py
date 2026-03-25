#!/usr/bin/env python3
from __future__ import annotations

"""
Beads Manager - Cross-repository issue management (v1.0.1)

Production-ready version with CI/CD improvements.

Changelog v1.0.1:
- Added safe_input() for non-interactive environments (CI/CD)
- Added require_bd_cli() check at startup with helpful error messages
- Added _validate_repo_path() for security validation
- Implemented SimpleCache class for list operations
- Replaced all input() calls with safe_input()
- Updated version to 1.0.1

Author: Agent Harness Team
Version: 1.0.1
License: Same as agent-harness project
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml --break-system-packages")
    sys.exit(1)


# ===== Helper Functions =====


def safe_input(prompt: str, default: str = "y") -> str:
    """
    Safe input that works in non-interactive environments (CI/CD).

    Handles EOF gracefully and detects CI environments to auto-confirm.

    Args:
        prompt: Prompt to show user
        default: Default value when stdin is not a TTY

    Returns:
        User input or default value
    """
    # Check if running in CI or non-interactive environment
    if not sys.stdin.isatty() or os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        print(f"{prompt}[Auto: {default}]")
        return default

    try:
        return input(prompt).strip().lower()
    except EOFError:
        print(f"[EOF detected, using default: {default}]")
        return default


def check_bd_cli_available() -> bool:
    """
    Check if beads CLI (bd) is installed and accessible.

    Returns:
        True if bd is available, False otherwise
    """
    if shutil.which("bd") is None:
        return False

    try:
        result = subprocess.run(["bd", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def require_bd_cli():
    """
    Require bd CLI to be installed, exit with helpful message if not.

    This ensures early failure with clear instructions rather than
    cryptic errors later when trying to run bd commands.
    """
    if not check_bd_cli_available():
        print("❌ Error: beads CLI (bd) not found")
        print()
        print("Install beads CLI:")
        print("  pip install beads-cli --break-system-packages")
        print()
        print("Or add to PATH:")
        print('  export PATH="$PATH:/path/to/beads"')
        print()
        print("Verify installation:")
        print("  bd --version")
        sys.exit(1)


# ===== Simple Cache Implementation =====


class SimpleCache:
    """Simple TTL-based cache for search results."""

    def __init__(self, ttl: int = 300):
        """
        Initialize cache.

        Args:
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value if still valid.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/missing
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            # Expired
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any):
        """
        Cache a value with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())

    def clear(self):
        """Clear all cached values."""
        self._cache.clear()

    def stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with entries count and TTL
        """
        return {"entries": len(self._cache), "ttl": self._ttl}


# ===== Main BeadsManager Class =====


class BeadsManager:
    """Main orchestrator for cross-repo beads management."""

    def __init__(self, config_dir: Path):
        """
        Initialize BeadsManager with configuration directory.

        Args:
            config_dir: Path to configuration directory containing repos.yml and defaults.yml
        """
        self.config_dir = config_dir
        self.repos = self._load_repos()
        self.defaults = self._load_defaults()
        self._cache = SimpleCache(ttl=self.defaults.get("behavior", {}).get("cache_duration", 300))

    def _load_repos(self) -> Dict:
        """
        Load repository registry from config.

        Returns:
            Dictionary of repository configurations

        Raises:
            FileNotFoundError: If repos.yml not found
            ValueError: If no valid repositories found
        """
        repos_file = self.config_dir / "repos.yml"
        if not repos_file.exists():
            # Try .yaml extension as fallback
            repos_file = self.config_dir / "repos.yaml"
            if not repos_file.exists():
                raise FileNotFoundError(
                    f"Repository registry not found: {self.config_dir}/repos.yml\n"
                    f"Create it from template: cp config/repos.yml.template config/repos.yml"
                )

        with open(repos_file) as f:
            config = yaml.safe_load(f)

        if not config or "repositories" not in config:
            raise ValueError(f"Invalid repos.yml: missing 'repositories' section")

        # Filter enabled repos AND validate paths
        repos = {}
        for name, info in config["repositories"].items():
            if not info.get("enabled", True):
                continue

            repo_path = Path(info["path"])
            if not self._validate_repo_path(repo_path):
                print(f"⚠️  Warning: Invalid repository path: {name} at {repo_path}")
                continue

            repos[name] = info

        if not repos:
            raise ValueError("No enabled repositories found in repos.yml")

        return repos

    def _load_defaults(self) -> Dict:
        """
        Load default configuration.

        Returns:
            Dictionary of default settings
        """
        defaults_file = self.config_dir / "defaults.yml"
        if not defaults_file.exists():
            # Try .yaml extension as fallback
            defaults_file = self.config_dir / "defaults.yaml"
            if not defaults_file.exists():
                # Return minimal defaults if file not found
                return {
                    "defaults": {"type": "task", "priority": 2, "status": "open"},
                    "display": {"format": "table", "color": False},
                    "behavior": {"confirm_bulk": True, "cache_duration": 300},
                }

        with open(defaults_file) as f:
            return yaml.safe_load(f)

    def _validate_repo_path(self, path: Path) -> bool:
        """
        Validate repository path is safe and accessible.

        Security checks:
        - Must be absolute path
        - Must exist and be a directory
        - Must contain .beads directory
        - Resolves symlinks and verifies result

        Args:
            path: Repository path to validate

        Returns:
            True if path is valid, False otherwise
        """
        # Must be absolute path
        if not path.is_absolute():
            return False

        # Must exist and be directory
        if not path.exists() or not path.is_dir():
            return False

        # Must contain .beads directory
        if not (path / ".beads").exists():
            return False

        # Security: Resolve symlinks and verify result
        try:
            resolved = path.resolve(strict=True)
            # Additional security checks could be added here
            # e.g., checking against allowed base paths
            return True
        except (OSError, RuntimeError):
            return False

    def create_issue(
        self,
        repo: str,
        title: str,
        issue_type: str | None = None,
        priority: int | None = None,
        description: str | None = None,
        blocks: List[str] | None = None,
        depends_on: List[str] | None = None,
        labels: List[str] | None = None,
        interactive: bool = True,
    ) -> str | None:
        """
        Create issue in specified repository.

        Args:
            repo: Repository name from registry
            title: Issue title
            issue_type: Type (feature, bug, task, etc.)
            priority: Priority level (0-3)
            description: Issue description
            blocks: List of issue IDs this blocks
            depends_on: List of issue IDs this depends on
            labels: Additional labels
            interactive: Whether to prompt for confirmation

        Returns:
            Created issue ID

        Raises:
            ValueError: If repo is unknown
            FileNotFoundError: If repo path doesn't exist
            subprocess.CalledProcessError: If beads command fails
        """
        if repo not in self.repos:
            available = ", ".join(self.repos.keys())
            raise ValueError(f"Unknown repository: {repo}\nAvailable repositories: {available}")

        repo_info = self.repos[repo]
        repo_path = Path(repo_info["path"])

        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

        # Apply defaults
        issue_type = issue_type or self.defaults.get("defaults", {}).get("type", "task")
        priority = (
            priority
            if priority is not None
            else self.defaults.get("defaults", {}).get("priority", 2)
        )

        # Build beads command
        cmd = ["bd", "create", title, f"--type={issue_type}", f"--priority={priority}"]

        if description:
            cmd.extend(["--description", description])

        if labels:
            cmd.extend(["--labels", ",".join(labels)])

        if blocks:
            for block in blocks:
                cmd.extend(["--blocks", block])

        if depends_on:
            for dep in depends_on:
                cmd.extend(["--depends-on", dep])

        # Show preview if interactive
        if interactive:
            print(f"\n📝 Creating issue in {repo}:")
            print(f"   Title: {title}")
            print(f"   Type: {issue_type}")
            print(f"   Priority: {priority}")
            if description:
                preview = description[:100] + "..." if len(description) > 100 else description
                print(f"   Description: {preview}")

            # Use safe_input instead of input for CI/CD compatibility
            confirm = safe_input("\nProceed? [Y/n]: ", default="y")
            if confirm and confirm != "y":
                print("Cancelled.")
                return None

        # Execute in repo directory
        try:
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)

            # Extract issue ID from output
            output = result.stdout.strip()
            issue_id = self._extract_issue_id(output)

            print(f"✅ Created issue in {repo}: {issue_id}")
            issue_file = (
                repo_path / repo_info.get("beads_dir", ".beads") / "issues" / f"{issue_id}.md"
            )
            print(f"   Path: {issue_file}")

            return issue_id

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create issue in {repo}")
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Error: {e.stderr}")
            raise

    def _extract_issue_id(self, output: str) -> str:
        """
        Extract issue ID from beads command output.

        Args:
            output: Command output string

        Returns:
            Issue ID (e.g., 'bd-abc123')

        Raises:
            ValueError: If no issue ID found in output
        """
        match = re.search(r"(?:bd|agent)-[a-z0-9]+", output)
        if match:
            return match.group(0)
        raise ValueError(f"Could not extract issue ID from output: {output}")

    def list_issues(
        self,
        repos: List[str] | None = None,
        status: str | None = None,
        priority: List[int] | None = None,
        issue_type: str | None = None,
        assigned_to: str | None = None,
        format: str = "table",
    ) -> List[Dict]:
        """
        List issues across repositories with caching support.

        Args:
            repos: List of repo names (None = all repos)
            status: Filter by status
            priority: Filter by priority levels
            issue_type: Filter by type
            assigned_to: Filter by assignee
            format: Output format (table, list, json)

        Returns:
            List of issue dictionaries
        """
        repos = repos or list(self.repos.keys())

        # Check cache
        cache_key = f"list:{','.join(sorted(repos))}:{status}:{priority}:{issue_type}:{assigned_to}"
        cached = self._cache.get(cache_key)

        if cached is not None:
            all_issues = cached
        else:
            all_issues = []

            for repo_name in repos:
                if repo_name not in self.repos:
                    print(f"⚠️  Warning: Skipping unknown repository: {repo_name}")
                    continue

                repo_info = self.repos[repo_name]
                repo_path = Path(repo_info["path"])

                # Build beads list command
                cmd = ["bd", "list", "--json"]

                if status:
                    cmd.extend(["--status", status])
                if priority:
                    cmd.extend(["--priority", ",".join(map(str, priority))])
                if issue_type:
                    cmd.extend(["--type", issue_type])
                if assigned_to:
                    cmd.extend(["--assigned-to", assigned_to])

                try:
                    result = subprocess.run(
                        cmd, cwd=repo_path, capture_output=True, text=True, check=True
                    )

                    issues = json.loads(result.stdout)

                    # Add repo context to each issue
                    for issue in issues:
                        issue["repo"] = repo_name
                        issue["repo_path"] = str(repo_path)

                    all_issues.extend(issues)

                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Warning: Failed to list issues in {repo_name}")
                    print(f"   Error: {e.stderr}")
                    continue
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Failed to parse issues from {repo_name}")
                    print(f"   Error: {e}")
                    continue

            # Cache results
            self._cache.set(cache_key, all_issues)

        # Format output
        if format == "json":
            print(json.dumps(all_issues, indent=2))
        elif format == "table":
            self._print_table(all_issues)
        elif format == "list":
            self._print_list(all_issues)
        else:
            print(f"Unknown format: {format}. Using table.")
            self._print_table(all_issues)

        return all_issues

    def _print_table(self, issues: List[Dict]):
        """Print issues in table format grouped by repository."""
        if not issues:
            print("No issues found.")
            return

        # Group by repo
        by_repo: dict[str, list[Dict]] = {}
        for issue in issues:
            repo = issue["repo"]
            if repo not in by_repo:
                by_repo[repo] = []
            by_repo[repo].append(issue)

        print(f"\nFound {len(issues)} issues across {len(by_repo)} repositories:\n")

        for repo, repo_issues in sorted(by_repo.items()):
            print(f"{repo} ({len(repo_issues)} issues):")
            for issue in sorted(repo_issues, key=lambda x: x.get("priority", 999)):
                priority = issue.get("priority", "?")
                status = issue.get("status", "unknown")
                issue_type = issue.get("type", "task")
                title = issue.get("title", "No title")
                issue_id = issue.get("id", "unknown")

                print(f"  {issue_id} [P{priority}] {title} ({issue_type}, {status})")
            print()

    def _print_list(self, issues: List[Dict]):
        """Print issues in simple list format."""
        for issue in issues:
            repo = issue.get("repo", "unknown")
            issue_id = issue.get("id", "unknown")
            title = issue.get("title", "No title")
            print(f"• {repo}:{issue_id} - {title}")

    def show_issue(self, issue_id: str, repo: str | None = None) -> Dict:
        """
        Show detailed information about an issue.

        Args:
            issue_id: Issue ID (e.g., bd-abc123)
            repo: Repository name (auto-detected if None)

        Returns:
            Issue details dictionary

        Raises:
            ValueError: If issue not found
        """
        # Auto-detect repo if not specified
        if not repo:
            repo = self._find_issue_repo(issue_id)
            if repo is None:
                searched = ", ".join(self.repos.keys())
                raise ValueError(
                    f"Issue {issue_id} not found in any repository.\nSearched: {searched}"
                )

        repo_info = self.repos[repo]
        repo_path = Path(repo_info["path"])

        # Use bd show command
        cmd = ["bd", "show", issue_id, "--json"]

        try:
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)

            issues = json.loads(result.stdout)
            # bd show returns a list, take first element
            if isinstance(issues, list):
                issue = issues[0] if issues else {}
            else:
                issue = issues

            issue["repo"] = repo
            issue["repo_path"] = str(repo_path)

            # Print formatted output
            self._print_issue_details(issue)

            return issue

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to show issue {issue_id} in {repo}")
            print(f"   Error: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse issue {issue_id}")
            print(f"   Error: {e}")
            raise

    def _find_issue_repo(self, issue_id: str) -> Optional[str]:
        """
        Find which repository contains the given issue ID.
        Checks both .md files (legacy) and SQLite database (current).

        Args:
            issue_id: Issue ID to find

        Returns:
            Repository name or None if not found
        """
        import sqlite3

        for repo_name, repo_info in self.repos.items():
            repo_path = Path(repo_info["path"])
            beads_dir = repo_info.get("beads_dir", ".beads")

            # Check for .md file first (legacy beads)
            issue_file = repo_path / beads_dir / "issues" / f"{issue_id}.md"
            if issue_file.exists():
                return repo_name

            # Check SQLite database (current beads)
            db_file = repo_path / beads_dir / "beads.db"
            if db_file.exists():
                try:
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM issues WHERE id = ?", (issue_id,))
                    if cursor.fetchone():
                        conn.close()
                        return repo_name
                    conn.close()
                except Exception:
                    pass

        return None

    def _print_issue_details(self, issue: Dict):
        """Print detailed issue information in formatted output."""
        print(f"\n{'=' * 60}")
        print(f"Issue: {issue['id']}")
        print(f"Repository: {issue['repo']}")
        print(f"{'=' * 60}")
        print(f"Title: {issue['title']}")
        print(f"Type: {issue.get('type', 'unknown')}")
        print(f"Priority: {issue.get('priority', '?')}")
        print(f"Status: {issue.get('status', 'unknown')}")
        print(f"Assignee: {issue.get('assignee', 'unassigned')}")

        if issue.get("labels"):
            print(f"Labels: {', '.join(issue['labels'])}")

        if issue.get("description"):
            print(f"\nDescription:")
            print(issue["description"])

        if issue.get("blocks"):
            print(f"\nBlocks:")
            for block in issue["blocks"]:
                print(f"  • {block}")

        if issue.get("depends_on"):
            print(f"\nDepends on:")
            for dep in issue["depends_on"]:
                print(f"  • {dep}")

        beads_dir = self.repos[issue["repo"]].get("beads_dir", ".beads")
        print(f"\nPath: {issue['repo_path']}/{beads_dir}/issues/{issue['id']}.md")
        print(f"{'=' * 60}\n")

    def create_linked_issues(
        self,
        primary: Tuple[str, str],
        dependencies: List[Tuple[str, str]],
        priority: int = 2,
        interactive: bool = True,
    ) -> Dict[str, str | None]:
        """
        Create multiple linked issues across repositories.

        Args:
            primary: (repo, title) for primary issue
            dependencies: List of (repo, title) for dependency issues
            priority: Priority for all issues
            interactive: Whether to prompt for confirmation

        Returns:
            Dictionary mapping "repo:title" to issue_id
        """
        created_issues = {}

        print(f"\n🔗 Creating linked issue chain...")
        print(f"Primary: {primary[0]}:{primary[1]}")
        print(f"Dependencies:")
        for dep_repo, dep_title in dependencies:
            print(f"  • {dep_repo}:{dep_title}")

        if interactive:
            # Use safe_input instead of input for CI/CD compatibility
            confirm = safe_input("\nProceed with creation? [Y/n]: ", default="y")
            if confirm and confirm != "y":
                print("Cancelled.")
                return {}

        # Create dependency issues first
        print("\nCreating dependencies...")
        for dep_repo, dep_title in dependencies:
            try:
                issue_id = self.create_issue(
                    repo=dep_repo, title=dep_title, priority=priority, interactive=False
                )
                created_issues[f"{dep_repo}:{dep_title}"] = issue_id
                print(f"  ✅ {dep_repo}:{issue_id}")
            except Exception as e:
                print(f"  ❌ Failed to create {dep_repo}:{dep_title}: {e}")
                # Continue with other dependencies

        # Create primary issue with dependencies
        print("\nCreating primary issue...")
        primary_repo, primary_title = primary
        depends_on = [x for x in created_issues.values() if x is not None]

        try:
            primary_id = self.create_issue(
                repo=primary_repo,
                title=primary_title,
                priority=priority,
                depends_on=depends_on,
                interactive=False,
            )
            created_issues[f"{primary_repo}:{primary_title}"] = primary_id
            print(f"  ✅ {primary_repo}:{primary_id}")
        except Exception as e:
            print(f"  ❌ Failed to create primary issue: {e}")
            raise

        print(f"\n✅ Created {len(created_issues)} linked issues")

        return created_issues


def main():
    """Main CLI entry point."""
    # Check bd CLI is available (early failure with helpful message)
    require_bd_cli()

    parser = argparse.ArgumentParser(
        description="Beads Manager - Cross-repository issue management (v1.0.1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create issue
  %(prog)s create --repo agent-harness --title "Add feature" --type feature --priority 2
  
  # List all issues
  %(prog)s list --all
  
  # Show issue details
  %(prog)s show bd-abc123
  
  # Create linked issues
  %(prog)s create-linked --primary agent-harness:"Add API" --depends lightrag:"Add method"
""",
    )

    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(__file__).parent.parent / "config",
        help="Configuration directory (default: ../config)",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.1")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create issue")
    create_parser.add_argument("--repo", required=True, help="Repository name")
    create_parser.add_argument("--title", required=True, help="Issue title")
    create_parser.add_argument("--type", help="Issue type (feature, bug, task, etc.)")
    create_parser.add_argument("--priority", type=int, help="Priority (0-3)")
    create_parser.add_argument("--description", help="Issue description")
    create_parser.add_argument("--labels", help="Comma-separated labels")
    create_parser.add_argument("--blocks", nargs="+", help="Issue IDs this blocks")
    create_parser.add_argument("--depends-on", nargs="+", help="Issue IDs this depends on")
    create_parser.add_argument("--non-interactive", action="store_true", help="No prompts")

    # List command
    list_parser = subparsers.add_parser("list", help="List issues")
    list_parser.add_argument("--repo", nargs="+", help="Repository names")
    list_parser.add_argument("--all", action="store_true", help="All repositories")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--priority", help="Filter by priority (comma-separated)")
    list_parser.add_argument("--type", help="Filter by type")
    list_parser.add_argument("--assigned-to", help="Filter by assignee")
    list_parser.add_argument("--format", choices=["table", "list", "json"], default="table")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show issue details")
    show_parser.add_argument("issue_id", help="Issue ID (e.g., bd-abc123)")
    show_parser.add_argument("--repo", help="Repository name (auto-detected if omitted)")

    # Create-linked command
    linked_parser = subparsers.add_parser("create-linked", help="Create linked issues")
    linked_parser.add_argument("--primary", required=True, help="Primary issue (repo:title)")
    linked_parser.add_argument(
        "--depends", nargs="+", required=True, help="Dependencies (repo:title)"
    )
    linked_parser.add_argument("--priority", type=int, default=2, help="Priority (default: 2)")
    linked_parser.add_argument("--non-interactive", action="store_true", help="No prompts")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        manager = BeadsManager(args.config_dir)

        if args.command == "create":
            labels = args.labels.split(",") if args.labels else None

            manager.create_issue(
                repo=args.repo,
                title=args.title,
                issue_type=args.type,
                priority=args.priority,
                description=args.description,
                blocks=args.blocks,
                depends_on=getattr(args, "depends_on", None),
                labels=labels,
                interactive=not args.non_interactive,
            )

        elif args.command == "list":
            repos = args.repo if args.repo else (None if args.all else [])
            priority = [int(p) for p in args.priority.split(",")] if args.priority else None

            manager.list_issues(
                repos=repos,
                status=args.status,
                priority=priority,
                issue_type=args.type,
                assigned_to=args.assigned_to,
                format=args.format,
            )

        elif args.command == "show":
            manager.show_issue(issue_id=args.issue_id, repo=args.repo)

        elif args.command == "create-linked":
            # Parse primary and dependencies
            if ":" not in args.primary:
                print("Error: Primary must be in format 'repo:title'")
                return 1

            primary_repo, primary_title = args.primary.split(":", 1)

            dependencies = []
            for dep in args.depends:
                if ":" not in dep:
                    print(f"Error: Dependency must be in format 'repo:title': {dep}")
                    return 1
                dep_repo, dep_title = dep.split(":", 1)
                dependencies.append((dep_repo, dep_title))

            manager.create_linked_issues(
                primary=(primary_repo, primary_title),
                dependencies=dependencies,
                priority=args.priority,
                interactive=not args.non_interactive,
            )

        return 0

    except FileNotFoundError as e:
        print(f"❌ Configuration Error: {e}")
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
