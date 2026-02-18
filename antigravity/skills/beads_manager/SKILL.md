---
name: beads-manager
description: Cross-repository beads issue management from a single context, reducing administrative coordination friction for multi-repo workflows.
version: 1.0.0
priority: 2
type: task
labels: [skill, cross-repo, issue-management, beads]
disable-model-invocation: false
allowed-tools: Bash, Read, Write, Create, Edit
---

# 🔮 Beads Manager Skill

**Purpose**: Manage beads issues across multiple repositories (agent-harness, LightRAG, etc.) from a single context without switching terminals or losing workflow state.

## 🎯 Mission

- Create and manage beads issues across multiple repositories
- Search and filter issues across all tracked repos
- Sync issue state between repos when they're related
- Provide unified view of cross-repo work
- Maintain beads CLI compatibility with zero breaking changes

## 📋 When to Use This Skill

Use this skill when:
- Working on features that span multiple repositories
- Managing cross-repo dependencies (e.g., agent-harness change requires LightRAG update)
- Need to view all open issues across projects
- Coordinating related work in different repos
- Administrative overhead of switching contexts is painful

## 🏗️ Architecture

### Design Principles

1. **Single Source of Truth**: Beads CLI remains authoritative for each repo
2. **Non-Invasive**: Doesn't modify beads internals, works through CLI
3. **Stateless Where Possible**: Uses beads CLI for state, minimal local caching
4. **Graceful Degradation**: Falls back to manual beads commands if automation fails

### Component Overview

```
beads-manager/
├── SKILL.md                      # This file
├── scripts/
│   ├── beads_manager.py          # Main cross-repo orchestrator
│   ├── repo_registry.py          # Repository configuration
│   └── issue_sync.py             # Cross-repo issue synchronization
├── tests/
│   ├── test_beads_manager.py     # Unit tests
│   └── test_integration.py       # Integration tests
├── config/
│   ├── defaults.yaml             # Default configuration
│   └── repos.yaml                # Repository registry
└── README.md                     # Implementation details
```

## 🚀 Quick Start

### Interactive Mode (Recommended)

```bash
# Initialize beads-manager in current workspace
python scripts/beads_manager.py --init

# Create issue in specific repo
python scripts/beads_manager.py create \
  --repo agent-harness \
  --title "Add sandboxing support" \
  --type feature \
  --priority 2

# Create linked issues across repos
python scripts/beads_manager.py create-linked \
  --primary agent-harness:"Add API endpoint" \
  --depends lightrag:"Expose data method" \
  --priority 2

# List all open issues across repos
python scripts/beads_manager.py list --all

# Show issue details (auto-detects repo)
python scripts/beads_manager.py show bd-abc123
```

### Non-Interactive Mode (CI/CD Compatible)

```bash
# Export issues to JSON (for processing)
python scripts/beads_manager.py export \
  --format json \
  --output /tmp/issues.json

# Create from template
python scripts/beads_manager.py create \
  --template feature \
  --repo agent-harness \
  --vars "title=New Feature,priority=2" \
  --non-interactive

# Bulk operations
python scripts/beads_manager.py bulk-update \
  --filter "status=open,repo=agent-harness" \
  --set "priority=1" \
  --non-interactive
```

## 🔧 Core Features

### 1. Multi-Repo Issue Creation

Create issues in any tracked repository without leaving current context:

```bash
# Simple creation
bd-create --repo agent-harness \
  "Add debugging skill" \
  --type task \
  --priority 2

# With full context
bd-create --repo lightrag \
  "Optimize query performance" \
  --type bug \
  --priority 1 \
  --blocks agent-harness:bd-xyz789 \
  --description "Query timeout in production"

# From template
bd-create --template hotfix \
  --repo agent-harness \
  --title "Fix memory leak" \
  --auto-assign
```

**Output:**
```
✅ Created issue in agent-harness: bd-abc123
   Title: Add debugging skill
   Type: task
   Priority: 2
   URL: /path/to/agent-harness/.beads/issues/bd-abc123.md
```

### 2. Cross-Repo Search & Filtering

Search issues across all repositories with powerful filters:

```bash
# Find all high-priority open issues
bd-search --priority "0,1" --status open --all-repos

# Find issues blocking specific work
bd-search --blocks bd-abc123 --all-repos

# Find issues by assignee across repos
bd-search --assigned-to "@current-agent" --all-repos

# Complex query
bd-search \
  --repo "agent-harness,lightrag" \
  --type "bug,hotfix" \
  --created-after "2026-02-01" \
  --status open \
  --sort priority
```

**Output:**
```
Found 5 issues across 2 repositories:

agent-harness (3 issues):
  bd-abc123 [P1] Fix memory leak (bug, open)
  bd-def456 [P2] Add sandboxing (feature, open)
  bd-ghi789 [P0] Production outage (hotfix, open)

lightrag (2 issues):
  bd-jkl012 [P1] Query timeout (bug, open)
  bd-mno345 [P2] Cache optimization (feature, open)
```

### 3. Linked Issue Management

Create and manage dependencies between issues across repos:

```bash
# Create parent-child relationship
bd-link --parent agent-harness:bd-abc123 \
  --child lightrag:bd-def456 \
  --type depends-on

# Create blocker relationship
bd-link --blocks agent-harness:bd-ghi789 \
  --blocked-by lightrag:bd-jkl012

# View dependency graph
bd-graph bd-abc123 --include-cross-repo
```

**Output (dependency graph):**
```
agent-harness:bd-abc123 (Add API endpoint)
├── depends-on → lightrag:bd-def456 (Expose data method)
└── blocks → agent-harness:bd-ghi789 (Complete feature)
    └── depends-on → lightrag:bd-jkl012 (Performance fix)
```

### 4. Unified Issue View

View all issues across repositories in single dashboard:

```bash
# Dashboard view
bd-dashboard

# Filtered dashboard
bd-dashboard --repos agent-harness,lightrag \
  --status open \
  --priority "0,1,2"

# Export dashboard
bd-dashboard --format markdown > /tmp/status.md
```

**Output:**
```
╔═══════════════════════════════════════════════════════════╗
║           Cross-Repo Beads Dashboard                      ║
╚═══════════════════════════════════════════════════════════╝

Summary:
  Total: 15 issues
  Open: 8 issues
  In Progress: 4 issues
  Blocked: 1 issue
  Done: 2 issues

By Repository:
  agent-harness: 8 issues (5 open, 2 in-progress, 1 done)
  lightrag:      5 issues (2 open, 2 in-progress, 1 done)
  other:         2 issues (1 open, 0 in-progress, 1 blocked)

High Priority (P0-P1):
  • agent-harness:bd-ghi789 [P0] Production outage
  • lightrag:bd-jkl012      [P1] Query timeout
  • agent-harness:bd-abc123 [P1] Fix memory leak

Blocked Issues:
  • other:bd-xyz999 [P2] Blocked by lightrag:bd-jkl012
```

### 5. Issue Synchronization

Sync related issues across repositories:

```bash
# Sync linked issues
bd-sync bd-abc123 --sync-linked

# Auto-sync on status change
bd-update bd-abc123 --status in-progress --auto-sync

# Bidirectional sync
bd-sync --bidirectional \
  agent-harness:bd-abc123 \
  lightrag:bd-def456
```

**Sync Behavior:**
```
When agent-harness:bd-abc123 changes status to "done":
  → Check for linked issues
  → Find lightrag:bd-def456 (depends-on)
  → Add comment: "Blocker resolved: agent-harness:bd-abc123"
  → Optionally update status if all blockers resolved
```

### 6. Bulk Operations

Perform operations on multiple issues at once:

```bash
# Bulk status update
bd-bulk-update \
  --filter "repo=agent-harness,status=open,priority=2" \
  --set status=in-progress

# Bulk assignment
bd-bulk-assign \
  --filter "type=bug,status=open" \
  --assignee "@current-agent"

# Bulk close
bd-bulk-close \
  --filter "status=done,updated-before=2026-01-01" \
  --reason "Completed in Q4 2025"
```

## 🔍 Configuration

### Repository Registry (`config/repos.yaml`)

```yaml
repositories:
  agent-harness:
    path: /path/to/agent-harness
    beads_dir: .beads
    default_assignee: "@agent"
    labels:
      - harness
      - core
    priority_mapping:
      critical: 0
      high: 1
      medium: 2
      low: 3
  
  lightrag:
    path: /path/to/LightRAG
    beads_dir: .beads
    default_assignee: "@agent"
    labels:
      - rag
      - ml
    
  # Add more repos as needed
  other-repo:
    path: ~/projects/other-repo
    beads_dir: .beads
    enabled: false  # Temporarily disabled

# Global settings
sync_settings:
  auto_sync: true
  sync_on_status_change: true
  bidirectional: false
  sync_labels: true

search_settings:
  default_repos: all
  max_results: 100
  sort_by: priority

templates:
  feature:
    type: feature
    priority: 2
    labels: [enhancement]
  
  bug:
    type: bug
    priority: 1
    labels: [bug]
  
  hotfix:
    type: bug
    priority: 0
    labels: [hotfix, emergency]
```

### Defaults (`config/defaults.yaml`)

```yaml
# Default values for issue creation
defaults:
  type: task
  priority: 2
  status: open
  assignee: "@current-agent"

# Display preferences
display:
  format: table  # table, list, json, markdown
  show_repo: true
  show_labels: true
  color: true

# Behavior
behavior:
  auto_cd: true  # Auto-cd to repo when operating on issues
  confirm_bulk: true  # Require confirmation for bulk ops
  cache_duration: 300  # Cache search results for 5 minutes
```

## 📚 Implementation Details

### Core Script: `beads_manager.py`

```python
#!/usr/bin/env python3
"""
Beads Manager - Cross-repository issue management

This script provides a unified interface for managing beads issues
across multiple repositories without context switching.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import json

class BeadsManager:
    """Main orchestrator for cross-repo beads management."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.repos = self._load_repos()
        self.defaults = self._load_defaults()
    
    def _load_repos(self) -> Dict:
        """Load repository registry from config."""
        repos_file = self.config_dir / "repos.yaml"
        if not repos_file.exists():
            raise FileNotFoundError(
                f"Repository registry not found: {repos_file}\n"
                f"Run: beads-manager --init"
            )
        
        with open(repos_file) as f:
            config = yaml.safe_load(f)
        
        # Filter enabled repos
        repos = {
            name: info for name, info in config['repositories'].items()
            if info.get('enabled', True)
        }
        
        return repos
    
    def _load_defaults(self) -> Dict:
        """Load default configuration."""
        defaults_file = self.config_dir / "defaults.yaml"
        if defaults_file.exists():
            with open(defaults_file) as f:
                return yaml.safe_load(f)
        return {}
    
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
        """
        if repo not in self.repos:
            raise ValueError(f"Unknown repository: {repo}")
        
        repo_info = self.repos[repo]
        repo_path = Path(repo_info['path'])
        
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
                print(f"   Description: {description[:100]}...")
            
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
            # Assuming bd create outputs: "Created issue: bd-abc123"
            output = result.stdout.strip()
            issue_id = self._extract_issue_id(output)
            
            print(f"✅ Created issue in {repo}: {issue_id}")
            print(f"   Path: {repo_path / repo_info['beads_dir'] / 'issues' / f'{issue_id}.md'}")
            
            return issue_id
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create issue in {repo}")
            print(f"   Error: {e.stderr}")
            raise
    
    def _extract_issue_id(self, output: str) -> str:
        """Extract issue ID from beads command output."""
        import re
        match = re.search(r'bd-[a-z0-9]+', output)
        if match:
            return match.group(0)
        raise ValueError(f"Could not extract issue ID from: {output}")
    
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
        
        # Format output
        if format == 'json':
            print(json.dumps(all_issues, indent=2))
        elif format == 'table':
            self._print_table(all_issues)
        elif format == 'list':
            self._print_list(all_issues)
        
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
        """Print issues in list format."""
        for issue in issues:
            print(f"• {issue['repo']}:{issue['id']} - {issue['title']}")
    
    def show_issue(self, issue_id: str, repo: str = None) -> Dict:
        """
        Show detailed information about an issue.
        
        Args:
            issue_id: Issue ID (e.g., bd-abc123)
            repo: Repository name (auto-detected if None)
        
        Returns:
            Issue details dictionary
        """
        # Auto-detect repo if not specified
        if not repo:
            repo = self._find_issue_repo(issue_id)
            if not repo:
                raise ValueError(f"Issue {issue_id} not found in any repository")
        
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
    
    def _find_issue_repo(self, issue_id: str) -> Optional[str]:
        """Find which repository contains the given issue ID."""
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
        
        print(f"\nPath: {issue['repo_path']}/.beads/issues/{issue['id']}.md")
        print(f"{'='*60}\n")
    
    def create_linked_issues(
        self,
        primary: tuple,  # (repo, title)
        dependencies: List[tuple],  # [(repo, title), ...]
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
            Dictionary mapping repo:title to issue_id
        """
        created_issues = {}
        
        # Create dependency issues first
        for dep_repo, dep_title in dependencies:
            issue_id = self.create_issue(
                repo=dep_repo,
                title=dep_title,
                priority=priority,
                interactive=interactive
            )
            created_issues[f"{dep_repo}:{dep_title}"] = issue_id
        
        # Create primary issue with dependencies
        primary_repo, primary_title = primary
        depends_on = list(created_issues.values())
        
        primary_id = self.create_issue(
            repo=primary_repo,
            title=primary_title,
            priority=priority,
            depends_on=depends_on,
            interactive=interactive
        )
        created_issues[f"{primary_repo}:{primary_title}"] = primary_id
        
        print(f"\n✅ Created linked issue chain:")
        print(f"   Primary: {primary_repo}:{primary_id}")
        print(f"   Dependencies:")
        for dep_key, dep_id in created_issues.items():
            if dep_id != primary_id:
                print(f"     • {dep_key} → {dep_id}")
        
        return created_issues


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Beads Manager - Cross-repository issue management"
    )
    
    parser.add_argument(
        '--config-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'config',
        help="Configuration directory"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize beads-manager')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create issue')
    create_parser.add_argument('--repo', required=True, help='Repository name')
    create_parser.add_argument('--title', required=True, help='Issue title')
    create_parser.add_argument('--type', help='Issue type')
    create_parser.add_argument('--priority', type=int, help='Priority (0-3)')
    create_parser.add_argument('--description', help='Issue description')
    create_parser.add_argument('--non-interactive', action='store_true', help='No prompts')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List issues')
    list_parser.add_argument('--repo', nargs='+', help='Repository names')
    list_parser.add_argument('--all', action='store_true', help='All repositories')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--priority', help='Filter by priority (comma-separated)')
    list_parser.add_argument('--format', choices=['table', 'list', 'json'], default='table')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show issue details')
    show_parser.add_argument('issue_id', help='Issue ID')
    show_parser.add_argument('--repo', help='Repository name (auto-detected if omitted)')
    
    # Create-linked command
    linked_parser = subparsers.add_parser('create-linked', help='Create linked issues')
    linked_parser.add_argument('--primary', required=True, help='Primary issue (repo:title)')
    linked_parser.add_argument('--depends', nargs='+', required=True, help='Dependencies (repo:title)')
    linked_parser.add_argument('--priority', type=int, default=2, help='Priority')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        manager = BeadsManager(args.config_dir)
        
        if args.command == 'create':
            manager.create_issue(
                repo=args.repo,
                title=args.title,
                issue_type=args.type,
                priority=args.priority,
                description=args.description,
                interactive=not args.non_interactive
            )
        
        elif args.command == 'list':
            repos = args.repo if args.repo else (None if args.all else [])
            priority = [int(p) for p in args.priority.split(',')] if args.priority else None
            
            manager.list_issues(
                repos=repos,
                status=args.status,
                priority=priority,
                format=args.format
            )
        
        elif args.command == 'show':
            manager.show_issue(
                issue_id=args.issue_id,
                repo=args.repo
            )
        
        elif args.command == 'create-linked':
            # Parse primary and dependencies
            primary_repo, primary_title = args.primary.split(':', 1)
            dependencies = [dep.split(':', 1) for dep in args.depends]
            
            manager.create_linked_issues(
                primary=(primary_repo, primary_title),
                dependencies=dependencies,
                priority=args.priority
            )
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

## ⚠️ Error Handling & Fallbacks

### Fallback to Manual Commands

If script fails, users can still use standard beads CLI:

```bash
# Fallback examples
cd /path/to/agent-harness
bd create "Add feature" --type feature --priority 2

cd /path/to/LightRAG
bd list --status open
```

### Common Error Scenarios

1. **Repository not configured**:
   ```
   ❌ Error: Unknown repository: unknown-repo
   Available: agent-harness, lightrag
   
   Add to config/repos.yaml:
   unknown-repo:
     path: /path/to/repo
     beads_dir: .beads
   ```

2. **Beads CLI not available**:
   ```
   ❌ Error: beads CLI not found
   Install: pip install beads-cli --break-system-packages
   Or add to PATH: export PATH="$PATH:/path/to/beads"
   ```

3. **Issue not found**:
   ```
   ❌ Error: Issue bd-abc123 not found
   Searched repositories: agent-harness, lightrag
   
   Check:
   - Issue ID is correct
   - Repository is configured
   - Issue file exists in .beads/issues/
   ```

## 🧪 Testing

### Unit Tests (`tests/test_beads_manager.py`)

```python
import pytest
from pathlib import Path
from scripts.beads_manager import BeadsManager

@pytest.fixture
def manager(tmp_path):
    """Create test manager with mock config."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create mock repos.yaml
    repos_yaml = config_dir / "repos.yaml"
    repos_yaml.write_text("""
repositories:
  test-repo:
    path: /tmp/test-repo
    beads_dir: .beads
    enabled: true
""")
    
    return BeadsManager(config_dir)

def test_create_issue(manager, monkeypatch):
    """Test issue creation."""
    # Mock subprocess.run
    def mock_run(*args, **kwargs):
        class Result:
            stdout = "Created issue: bd-test123"
            stderr = ""
            returncode = 0
        return Result()
    
    monkeypatch.setattr('subprocess.run', mock_run)
    
    issue_id = manager.create_issue(
        repo='test-repo',
        title='Test issue',
        interactive=False
    )
    
    assert issue_id == 'bd-test123'

def test_list_issues(manager, monkeypatch):
    """Test issue listing."""
    def mock_run(*args, **kwargs):
        class Result:
            stdout = '[{"id": "bd-test123", "title": "Test", "status": "open"}]'
            stderr = ""
            returncode = 0
        return Result()
    
    monkeypatch.setattr('subprocess.run', mock_run)
    
    issues = manager.list_issues(format='json')
    assert len(issues) == 1
    assert issues[0]['id'] == 'bd-test123'

def test_unknown_repo(manager):
    """Test error on unknown repository."""
    with pytest.raises(ValueError, match="Unknown repository"):
        manager.create_issue(
            repo='unknown',
            title='Test',
            interactive=False
        )
```

### Integration Tests (`tests/test_integration.py`)

```python
import pytest
from pathlib import Path
import subprocess

@pytest.fixture
def test_repos(tmp_path):
    """Create test repository structure."""
    repos = {}
    
    for repo_name in ['repo-a', 'repo-b']:
        repo_path = tmp_path / repo_name
        repo_path.mkdir()
        
        # Initialize beads
        subprocess.run(['bd', 'init'], cwd=repo_path, check=True)
        
        repos[repo_name] = repo_path
    
    return repos

def test_cross_repo_creation(test_repos):
    """Test creating issues across repos."""
    # Create issue in repo-a
    result = subprocess.run(
        ['python', 'scripts/beads_manager.py', 'create',
         '--repo', 'repo-a',
         '--title', 'Test issue',
         '--non-interactive'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert 'bd-' in result.stdout

def test_cross_repo_search(test_repos):
    """Test searching across repos."""
    # Create issues in both repos
    for repo in test_repos:
        subprocess.run(
            ['bd', 'create', 'Test', '--type', 'task'],
            cwd=test_repos[repo],
            check=True
        )
    
    # Search all repos
    result = subprocess.run(
        ['python', 'scripts/beads_manager.py', 'list', '--all'],
        capture_output=True,
        text=True
    )
    
    assert 'repo-a' in result.stdout
    assert 'repo-b' in result.stdout
```

## 📊 Performance Considerations

### Caching Strategy

```python
import time
from functools import lru_cache

class BeadsManager:
    def __init__(self, config_dir: Path):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _get_cached(self, key: str):
        """Get cached value if still valid."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return value
        return None
    
    def _set_cached(self, key: str, value):
        """Cache value with timestamp."""
        self._cache[key] = (value, time.time())
    
    @lru_cache(maxsize=100)
    def _find_issue_repo(self, issue_id: str) -> Optional[str]:
        """Cached repo lookup for issue IDs."""
        # Implementation...
```

### Batch Operations

For large-scale operations, batch commands:

```python
def bulk_update(self, filter_spec: Dict, updates: Dict):
    """Update multiple issues in batch."""
    issues = self.list_issues(**filter_spec)
    
    # Group by repo for efficiency
    by_repo = {}
    for issue in issues:
        repo = issue['repo']
        if repo not in by_repo:
            by_repo[repo] = []
        by_repo[repo].append(issue['id'])
    
    # Execute batch updates per repo
    for repo, issue_ids in by_repo.items():
        cmd = ['bd', 'bulk-update'] + issue_ids
        for key, value in updates.items():
            cmd.extend([f'--{key}', str(value)])
        
        subprocess.run(cmd, cwd=self.repos[repo]['path'], check=True)
```

## 🔐 Security Considerations

1. **Path Validation**: Always validate repository paths to prevent directory traversal
2. **Command Injection**: Use subprocess with list arguments, never string concatenation
3. **Access Control**: Respect beads CLI permissions and authentication
4. **Credential Handling**: Never log or cache sensitive data

```python
def _validate_repo_path(self, path: Path) -> bool:
    """Validate repository path is safe."""
    # Must be absolute path
    if not path.is_absolute():
        return False
    
    # Must exist and be directory
    if not path.exists() or not path.is_dir():
        return False
    
    # Must contain .beads directory
    if not (path / '.beads').exists():
        return False
    
    # Must be within allowed base paths
    allowed_bases = [Path.home() / 'projects', Path('/opt/repos')]
    if not any(path.is_relative_to(base) for base in allowed_bases):
        return False
    
    return True
```

## 📖 Usage Examples

### Example 1: Feature Spanning Multiple Repos

```bash
# Scenario: Adding API endpoint requires changes to both repos

# Create issues with dependencies
python scripts/beads_manager.py create-linked \
  --primary agent-harness:"Add /debug endpoint" \
  --depends lightrag:"Expose debug info method" \
  --priority 2

# Output:
# ✅ Created linked issue chain:
#    Primary: agent-harness:bd-abc123
#    Dependencies:
#      • lightrag:Expose debug info method → bd-def456

# Work on dependency first
cd /path/to/LightRAG
bd start bd-def456
# ... implement feature ...
bd close bd-def456

# Then work on primary
cd /path/to/agent-harness
bd start bd-abc123
# ... implement feature ...
bd close bd-abc123
```

### Example 2: Cross-Repo Bug Triage

```bash
# Find all high-priority bugs across repos
python scripts/beads_manager.py list \
  --all \
  --type bug \
  --priority "0,1" \
  --status open

# Output shows bugs from all repos
# Triage and assign
```

### Example 3: Release Planning

```bash
# Get all open issues for release planning
python scripts/beads_manager.py list --all --status open --format json > /tmp/release-issues.json

# Process with jq or other tools
jq '.[] | select(.priority <= 1) | {repo, id, title, priority}' /tmp/release-issues.json
```

## 🚧 Future Enhancements

Potential future features (not in v1.0):

1. **GitHub Integration**: Sync with GitHub issues
2. **Metrics Dashboard**: Visualize issue trends
3. **Smart Scheduling**: Suggest optimal issue order
4. **Team Collaboration**: Multi-agent coordination
5. **Webhook Support**: Real-time notifications
6. **Custom Workflows**: Define repo-specific processes

## 📚 References

- Beads CLI documentation: [Link to beads docs]
- TDD-Beads skill pattern: `~/.config/opencode/skills/tdd-beads/SKILL.md`
- Skill-making patterns: `~/.config/opencode/skills/skill-making/SKILL.md`
- Complete Harness Enforcement: `Complete_Harness_Enforcement_Architecture.md`

## ✅ Checklist for Integration

- [ ] Install dependencies: `pip install pyyaml --break-system-packages`
- [ ] Create config directory: `mkdir -p ~/.gemini/antigravity/skills/beads-manager/config`
- [ ] Copy config templates to config directory
- [ ] Update `repos.yaml` with your repository paths
- [ ] Test basic commands: `python scripts/beads_manager.py list --all`
- [ ] Add aliases to shell (optional): `alias bd-create='python /path/to/beads_manager.py create'`
- [ ] Run tests: `pytest tests/`
- [ ] Document team usage in README

## 🎓 Learning Resources

For agents new to this skill:

1. Start with single-repo operations (create, list, show)
2. Graduate to cross-repo search
3. Practice with linked issues
4. Explore bulk operations
5. Customize for your workflow

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-17  
**Status**: Production Ready  
**Maintainer**: Agent Harness Team
