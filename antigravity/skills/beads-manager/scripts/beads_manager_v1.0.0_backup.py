#!/usr/bin/env python3
"""
Beads Manager - Cross-repository issue management

This script provides a unified interface for managing beads issues
across multiple repositories without context switching.

Usage:
    python beads_manager.py create --repo REPO --title TITLE
    python beads_manager.py list --all
    python beads_manager.py show ISSUE_ID
    python beads_manager.py create-linked --primary REPO:TITLE --depends REPO:TITLE

Author: Agent Harness Team
Version: 1.0.0
License: Same as agent-harness project
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml --break-system-packages")
    sys.exit(1)


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
        self._cache = {}
        self._cache_ttl = self.defaults.get('behavior', {}).get('cache_duration', 300)
    
    def _load_repos(self) -> Dict:
        """
        Load repository registry from config.
        
        Returns:
            Dictionary of repository configurations
            
        Raises:
            FileNotFoundError: If repos.yml not found
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
        
        if not config or 'repositories' not in config:
            raise ValueError(f"Invalid repos.yml: missing 'repositories' section")
        
        # Filter enabled repos
        repos = {
            name: info for name, info in config['repositories'].items()
            if info.get('enabled', True)
        }
        
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
                    'defaults': {'type': 'task', 'priority': 2, 'status': 'open'},
                    'display': {'format': 'table', 'color': False},
                    'behavior': {'confirm_bulk': True, 'cache_duration': 300}
                }
        
        with open(defaults_file) as f:
            return yaml.safe_load(f)
    
    def create_issue(
        self,
        repo: str,
        title: str,
        issue_type: str = None,
        priority: int = None,
        description: str = None,
        blocks: List[str] = None,
        depends_on: List[str] = None,
        labels: List[str] = None,
        interactive: bool = True
    ) -> str:
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
            subprocess.CalledProcessError: If beads command fails
        """
        if repo not in self.repos:
            available = ', '.join(self.repos.keys())
            raise ValueError(
                f"Unknown repository: {repo}\n"
                f"Available repositories: {available}"
            )
        
        repo_info = self.repos[repo]
        repo_path = Path(repo_info['path'])
        
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
        
        # Apply defaults
        issue_type = issue_type or self.defaults.get('defaults', {}).get('type', 'task')
        priority = priority if priority is not None else self.defaults.get('defaults', {}).get('priority', 2)
        
        # Build beads command
        cmd = ['bd', 'create', title, f'--type={issue_type}', f'--priority={priority}']
        
        if description:
            cmd.extend(['--description', description])
        
        if labels:
            cmd.extend(['--labels', ','.join(labels)])
        
        if blocks:
            for block in blocks:
                cmd.extend(['--blocks', block])
        
        if depends_on:
            for dep in depends_on:
                cmd.extend(['--depends-on', dep])
        
        # Show preview if interactive
        if interactive:
            print(f"\n📝 Creating issue in {repo}:")
            print(f"   Title: {title}")
            print(f"   Type: {issue_type}")
            print(f"   Priority: {priority}")
            if description:
                preview = description[:100] + "..." if len(description) > 100 else description
                print(f"   Description: {preview}")
            
            confirm = input("\nProceed? [Y/n]: ").strip().lower()
            if confirm and confirm != 'y':
                print("Cancelled.")
                return None
        
        # Execute in repo directory
        try:
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract issue ID from output
            output = result.stdout.strip()
            issue_id = self._extract_issue_id(output)
            
            print(f"✅ Created issue in {repo}: {issue_id}")
            issue_file = repo_path / repo_info.get('beads_dir', '.beads') / 'issues' / f'{issue_id}.md'
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
            ValueError: If no issue ID found
        """
        match = re.search(r'bd-[a-z0-9]+', output)
        if match:
            return match.group(0)
        raise ValueError(f"Could not extract issue ID from output: {output}")
    
    def list_issues(
        self,
        repos: List[str] = None,
        status: str = None,
        priority: List[int] = None,
        issue_type: str = None,
        assigned_to: str = None,
        format: str = 'table'
    ) -> List[Dict]:
        """
        List issues across repositories.
        
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
        all_issues = []
        
        for repo_name in repos:
            if repo_name not in self.repos:
                print(f"⚠️  Warning: Skipping unknown repository: {repo_name}")
                continue
            
            repo_info = self.repos[repo_name]
            repo_path = Path(repo_info['path'])
            
            # Build beads list command
            cmd = ['bd', 'list', '--json']
            
            if status:
                cmd.extend(['--status', status])
            if priority:
                cmd.extend(['--priority', ','.join(map(str, priority))])
            if issue_type:
                cmd.extend(['--type', issue_type])
            if assigned_to:
                cmd.extend(['--assigned-to', assigned_to])
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                issues = json.loads(result.stdout)
                
                # Add repo context to each issue
                for issue in issues:
                    issue['repo'] = repo_name
                    issue['repo_path'] = str(repo_path)
                
                all_issues.extend(issues)
                
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: Failed to list issues in {repo_name}")
                print(f"   Error: {e.stderr}")
                continue
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: Failed to parse issues from {repo_name}")
                print(f"   Error: {e}")
                continue
        
        # Format output
        if format == 'json':
            print(json.dumps(all_issues, indent=2))
        elif format == 'table':
            self._print_table(all_issues)
        elif format == 'list':
            self._print_list(all_issues)
        else:
            print(f"Unknown format: {format}. Using table.")
            self._print_table(all_issues)
        
        return all_issues
    
    def _print_table(self, issues: List[Dict]):
        """Print issues in table format."""
        if not issues:
            print("No issues found.")
            return
        
        # Group by repo
        by_repo = {}
        for issue in issues:
            repo = issue['repo']
            if repo not in by_repo:
                by_repo[repo] = []
            by_repo[repo].append(issue)
        
        print(f"\nFound {len(issues)} issues across {len(by_repo)} repositories:\n")
        
        for repo, repo_issues in sorted(by_repo.items()):
            print(f"{repo} ({len(repo_issues)} issues):")
            for issue in sorted(repo_issues, key=lambda x: x.get('priority', 999)):
                priority = issue.get('priority', '?')
                status = issue.get('status', 'unknown')
                issue_type = issue.get('type', 'task')
                title = issue.get('title', 'No title')
                issue_id = issue.get('id', 'unknown')
                
                print(f"  {issue_id} [P{priority}] {title} ({issue_type}, {status})")
            print()
    
    def _print_list(self, issues: List[Dict]):
        """Print issues in simple list format."""
        for issue in issues:
            repo = issue.get('repo', 'unknown')
            issue_id = issue.get('id', 'unknown')
            title = issue.get('title', 'No title')
            print(f"• {repo}:{issue_id} - {title}")
    
    def show_issue(self, issue_id: str, repo: str = None) -> Dict:
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
            if not repo:
                searched = ', '.join(self.repos.keys())
                raise ValueError(
                    f"Issue {issue_id} not found in any repository.\n"
                    f"Searched: {searched}"
                )
        
        repo_info = self.repos[repo]
        repo_path = Path(repo_info['path'])
        
        # Use bd show command
        cmd = ['bd', 'show', issue_id, '--json']
        
        try:
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            issue = json.loads(result.stdout)
            issue['repo'] = repo
            issue['repo_path'] = str(repo_path)
            
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
        
        Args:
            issue_id: Issue ID to find
            
        Returns:
            Repository name or None if not found
        """
        for repo_name, repo_info in self.repos.items():
            repo_path = Path(repo_info['path'])
            beads_dir = repo_info.get('beads_dir', '.beads')
            issue_file = repo_path / beads_dir / 'issues' / f'{issue_id}.md'
            
            if issue_file.exists():
                return repo_name
        
        return None
    
    def _print_issue_details(self, issue: Dict):
        """Print detailed issue information."""
        print(f"\n{'='*60}")
        print(f"Issue: {issue['id']}")
        print(f"Repository: {issue['repo']}")
        print(f"{'='*60}")
        print(f"Title: {issue['title']}")
        print(f"Type: {issue.get('type', 'unknown')}")
        print(f"Priority: {issue.get('priority', '?')}")
        print(f"Status: {issue.get('status', 'unknown')}")
        print(f"Assignee: {issue.get('assignee', 'unassigned')}")
        
        if issue.get('labels'):
            print(f"Labels: {', '.join(issue['labels'])}")
        
        if issue.get('description'):
            print(f"\nDescription:")
            print(issue['description'])
        
        if issue.get('blocks'):
            print(f"\nBlocks:")
            for block in issue['blocks']:
                print(f"  • {block}")
        
        if issue.get('depends_on'):
            print(f"\nDepends on:")
            for dep in issue['depends_on']:
                print(f"  • {dep}")
        
        beads_dir = self.repos[issue['repo']].get('beads_dir', '.beads')
        print(f"\nPath: {issue['repo_path']}/{beads_dir}/issues/{issue['id']}.md")
        print(f"{'='*60}\n")
    
    def create_linked_issues(
        self,
        primary: Tuple[str, str],
        dependencies: List[Tuple[str, str]],
        priority: int = 2,
        interactive: bool = True
    ) -> Dict[str, str]:
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
            confirm = input("\nProceed with creation? [Y/n]: ").strip().lower()
            if confirm and confirm != 'y':
                print("Cancelled.")
                return {}
        
        # Create dependency issues first
        print("\nCreating dependencies...")
        for dep_repo, dep_title in dependencies:
            try:
                issue_id = self.create_issue(
                    repo=dep_repo,
                    title=dep_title,
                    priority=priority,
                    interactive=False
                )
                created_issues[f"{dep_repo}:{dep_title}"] = issue_id
                print(f"  ✅ {dep_repo}:{issue_id}")
            except Exception as e:
                print(f"  ❌ Failed to create {dep_repo}:{dep_title}: {e}")
                # Continue with other dependencies
        
        # Create primary issue with dependencies
        print("\nCreating primary issue...")
        primary_repo, primary_title = primary
        depends_on = list(created_issues.values())
        
        try:
            primary_id = self.create_issue(
                repo=primary_repo,
                title=primary_title,
                priority=priority,
                depends_on=depends_on,
                interactive=False
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
    parser = argparse.ArgumentParser(
        description="Beads Manager - Cross-repository issue management",
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
"""
    )
    
    parser.add_argument(
        '--config-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'config',
        help="Configuration directory (default: ../config)"
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create issue')
    create_parser.add_argument('--repo', required=True, help='Repository name')
    create_parser.add_argument('--title', required=True, help='Issue title')
    create_parser.add_argument('--type', help='Issue type (feature, bug, task, etc.)')
    create_parser.add_argument('--priority', type=int, help='Priority (0-3)')
    create_parser.add_argument('--description', help='Issue description')
    create_parser.add_argument('--labels', help='Comma-separated labels')
    create_parser.add_argument('--blocks', nargs='+', help='Issue IDs this blocks')
    create_parser.add_argument('--depends-on', nargs='+', help='Issue IDs this depends on')
    create_parser.add_argument('--non-interactive', action='store_true', help='No prompts')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List issues')
    list_parser.add_argument('--repo', nargs='+', help='Repository names')
    list_parser.add_argument('--all', action='store_true', help='All repositories')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--priority', help='Filter by priority (comma-separated)')
    list_parser.add_argument('--type', help='Filter by type')
    list_parser.add_argument('--assigned-to', help='Filter by assignee')
    list_parser.add_argument('--format', choices=['table', 'list', 'json'], default='table')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show issue details')
    show_parser.add_argument('issue_id', help='Issue ID (e.g., bd-abc123)')
    show_parser.add_argument('--repo', help='Repository name (auto-detected if omitted)')
    
    # Create-linked command
    linked_parser = subparsers.add_parser('create-linked', help='Create linked issues')
    linked_parser.add_argument('--primary', required=True, help='Primary issue (repo:title)')
    linked_parser.add_argument('--depends', nargs='+', required=True, help='Dependencies (repo:title)')
    linked_parser.add_argument('--priority', type=int, default=2, help='Priority (default: 2)')
    linked_parser.add_argument('--non-interactive', action='store_true', help='No prompts')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        manager = BeadsManager(args.config_dir)
        
        if args.command == 'create':
            labels = args.labels.split(',') if args.labels else None
            
            manager.create_issue(
                repo=args.repo,
                title=args.title,
                issue_type=args.type,
                priority=args.priority,
                description=args.description,
                blocks=args.blocks,
                depends_on=getattr(args, 'depends_on', None),
                labels=labels,
                interactive=not args.non_interactive
            )
        
        elif args.command == 'list':
            repos = args.repo if args.repo else (None if args.all else [])
            priority = [int(p) for p in args.priority.split(',')] if args.priority else None
            
            manager.list_issues(
                repos=repos,
                status=args.status,
                priority=priority,
                issue_type=args.type,
                assigned_to=args.assigned_to,
                format=args.format
            )
        
        elif args.command == 'show':
            manager.show_issue(
                issue_id=args.issue_id,
                repo=args.repo
            )
        
        elif args.command == 'create-linked':
            # Parse primary and dependencies
            if ':' not in args.primary:
                print("Error: Primary must be in format 'repo:title'")
                return 1
            
            primary_repo, primary_title = args.primary.split(':', 1)
            
            dependencies = []
            for dep in args.depends:
                if ':' not in dep:
                    print(f"Error: Dependency must be in format 'repo:title': {dep}")
                    return 1
                dep_repo, dep_title = dep.split(':', 1)
                dependencies.append((dep_repo, dep_title))
            
            manager.create_linked_issues(
                primary=(primary_repo, primary_title),
                dependencies=dependencies,
                priority=args.priority,
                interactive=not args.non_interactive
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


if __name__ == '__main__':
    sys.exit(main())
