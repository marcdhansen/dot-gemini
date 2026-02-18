"""
Integration tests for beads-manager

These tests require actual beads CLI to be installed and working.
They create temporary repositories and test real beads operations.

Run with: pytest tests/test_integration.py -v
Skip if slow: pytest tests/test_integration.py -v -m "not slow"
"""

import pytest
from pathlib import Path
import subprocess
import tempfile
import shutil
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from beads_manager import BeadsManager


# Skip all integration tests if beads CLI not available
try:
    subprocess.run(['bd', '--version'], capture_output=True, check=True)
    BEADS_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    BEADS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not BEADS_AVAILABLE,
    reason="Beads CLI not available"
)


@pytest.fixture(scope="function")
def test_workspace(tmp_path):
    """
    Create a temporary workspace with multiple beads repositories.
    
    Returns a dict with:
    - workspace: Path to workspace directory
    - repos: Dict of repo_name -> Path
    - config_dir: Path to beads-manager config
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    repos = {}
    
    # Create two test repositories
    for repo_name in ['repo-a', 'repo-b']:
        repo_path = workspace / repo_name
        repo_path.mkdir()
        
        # Initialize beads
        subprocess.run(
            ['bd', 'init'],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        
        repos[repo_name] = repo_path
    
    # Create beads-manager config
    config_dir = workspace / 'config'
    config_dir.mkdir()
    
    # Write repos.yaml
    repos_yaml = config_dir / 'repos.yaml'
    repos_yaml.write_text(f"""
repositories:
  repo-a:
    path: {repos['repo-a']}
    beads_dir: .beads
    enabled: true
  
  repo-b:
    path: {repos['repo-b']}
    beads_dir: .beads
    enabled: true

sync_settings:
  auto_sync: true

search_settings:
  default_repos: all
  max_results: 100
""")
    
    # Write defaults.yaml
    defaults_yaml = config_dir / 'defaults.yaml'
    defaults_yaml.write_text("""
defaults:
  type: task
  priority: 2
  status: open

display:
  format: table
  color: false

behavior:
  confirm_bulk: false
  cache_duration: 0
""")
    
    yield {
        'workspace': workspace,
        'repos': repos,
        'config_dir': config_dir
    }
    
    # Cleanup handled by tmp_path fixture


@pytest.fixture
def manager(test_workspace):
    """Create BeadsManager instance with test workspace."""
    return BeadsManager(test_workspace['config_dir'])


@pytest.mark.slow
class TestRealIssueCreation:
    """Test issue creation with real beads CLI."""
    
    def test_create_issue_in_single_repo(self, manager, test_workspace):
        """Test creating a real issue in one repository."""
        issue_id = manager.create_issue(
            repo='repo-a',
            title='Test issue from integration test',
            issue_type='task',
            priority=2,
            interactive=False
        )
        
        assert issue_id.startswith('bd-')
        
        # Verify issue file exists
        repo_path = test_workspace['repos']['repo-a']
        issue_file = repo_path / '.beads' / 'issues' / f'{issue_id}.md'
        assert issue_file.exists()
        
        # Verify issue content
        content = issue_file.read_text()
        assert 'Test issue from integration test' in content
    
    def test_create_issues_in_multiple_repos(self, manager, test_workspace):
        """Test creating issues in different repositories."""
        issue_a = manager.create_issue(
            repo='repo-a',
            title='Issue in repo A',
            interactive=False
        )
        
        issue_b = manager.create_issue(
            repo='repo-b',
            title='Issue in repo B',
            interactive=False
        )
        
        # Verify both issues exist
        assert issue_a.startswith('bd-')
        assert issue_b.startswith('bd-')
        
        file_a = test_workspace['repos']['repo-a'] / '.beads' / 'issues' / f'{issue_a}.md'
        file_b = test_workspace['repos']['repo-b'] / '.beads' / 'issues' / f'{issue_b}.md'
        
        assert file_a.exists()
        assert file_b.exists()


@pytest.mark.slow
class TestRealIssueListing:
    """Test issue listing with real beads CLI."""
    
    def test_list_issues_empty_repos(self, manager):
        """Test listing issues when repos are empty."""
        issues = manager.list_issues(format='json')
        assert len(issues) == 0
    
    def test_list_issues_with_data(self, manager, test_workspace):
        """Test listing issues after creating some."""
        # Create test issues
        manager.create_issue(
            repo='repo-a',
            title='Issue 1',
            priority=1,
            interactive=False
        )
        manager.create_issue(
            repo='repo-a',
            title='Issue 2',
            priority=2,
            interactive=False
        )
        manager.create_issue(
            repo='repo-b',
            title='Issue 3',
            priority=1,
            interactive=False
        )
        
        # List all issues
        issues = manager.list_issues(format='json')
        
        assert len(issues) == 3
        
        # Verify repo attribution
        repo_a_issues = [i for i in issues if i['repo'] == 'repo-a']
        repo_b_issues = [i for i in issues if i['repo'] == 'repo-b']
        
        assert len(repo_a_issues) == 2
        assert len(repo_b_issues) == 1
    
    def test_list_issues_with_filters(self, manager):
        """Test listing issues with priority filter."""
        # Create issues with different priorities
        manager.create_issue(
            repo='repo-a',
            title='High priority',
            priority=1,
            interactive=False
        )
        manager.create_issue(
            repo='repo-a',
            title='Low priority',
            priority=3,
            interactive=False
        )
        
        # Filter for high priority only
        issues = manager.list_issues(
            priority=[1],
            format='json'
        )
        
        assert len(issues) == 1
        assert issues[0]['priority'] == 1


@pytest.mark.slow
class TestRealIssueShow:
    """Test showing issue details with real beads CLI."""
    
    def test_show_issue_with_repo(self, manager):
        """Test showing issue when repo is specified."""
        # Create test issue
        issue_id = manager.create_issue(
            repo='repo-a',
            title='Test show issue',
            description='Detailed description',
            interactive=False
        )
        
        # Show issue
        issue = manager.show_issue(issue_id, repo='repo-a')
        
        assert issue['id'] == issue_id
        assert issue['title'] == 'Test show issue'
        assert 'description' in issue
    
    def test_show_issue_auto_detect(self, manager, test_workspace):
        """Test showing issue with automatic repo detection."""
        # Create test issue
        issue_id = manager.create_issue(
            repo='repo-b',
            title='Auto detect test',
            interactive=False
        )
        
        # Show without specifying repo
        issue = manager.show_issue(issue_id)
        
        assert issue['id'] == issue_id
        assert issue['repo'] == 'repo-b'


@pytest.mark.slow
class TestRealLinkedIssues:
    """Test creating linked issues with real beads CLI."""
    
    def test_create_linked_issues(self, manager, test_workspace):
        """Test creating linked issues across repositories."""
        created = manager.create_linked_issues(
            primary=('repo-a', 'Primary feature'),
            dependencies=[
                ('repo-b', 'Dependency 1'),
                ('repo-a', 'Dependency 2')
            ],
            priority=2,
            interactive=False
        )
        
        assert len(created) == 3
        
        # Verify all issues were created
        for issue_id in created.values():
            assert issue_id.startswith('bd-')
        
        # Verify primary has dependencies
        primary_id = created['repo-a:Primary feature']
        primary = manager.show_issue(primary_id, repo='repo-a')
        
        assert 'depends_on' in primary or 'dependencies' in primary


@pytest.mark.slow
class TestRealCrossRepoWorkflow:
    """Test complete cross-repo workflow."""
    
    def test_end_to_end_workflow(self, manager, test_workspace):
        """Test a complete workflow: create, list, update, show."""
        # 1. Create issues in both repos
        issue_a1 = manager.create_issue(
            repo='repo-a',
            title='Implement API endpoint',
            priority=1,
            interactive=False
        )
        
        issue_b1 = manager.create_issue(
            repo='repo-b',
            title='Add data model',
            priority=1,
            interactive=False
        )
        
        # 2. List all open issues
        all_issues = manager.list_issues(status='open', format='json')
        assert len(all_issues) == 2
        
        # 3. Show details of specific issue
        detail = manager.show_issue(issue_a1, repo='repo-a')
        assert detail['title'] == 'Implement API endpoint'
        
        # 4. Verify cross-repo visibility
        repos_with_issues = set(i['repo'] for i in all_issues)
        assert 'repo-a' in repos_with_issues
        assert 'repo-b' in repos_with_issues


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
