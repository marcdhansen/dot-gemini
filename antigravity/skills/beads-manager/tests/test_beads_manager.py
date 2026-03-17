"""
Unit tests for beads_manager.py

Run with: pytest tests/test_beads_manager.py -v
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from beads_manager import BeadsManager


@pytest.fixture
def temp_config(tmp_path):
    """Create temporary config directory with test configuration."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create test repos.yaml
    repos_yaml = config_dir / "repos.yaml"
    repos_yaml.write_text("""
repositories:
  test-repo:
    path: /tmp/test-repo
    beads_dir: .beads
    enabled: true
    default_assignee: "@test-agent"
  
  test-repo-2:
    path: /tmp/test-repo-2
    beads_dir: .beads
    enabled: true

sync_settings:
  auto_sync: true
  sync_on_status_change: true

search_settings:
  default_repos: all
  max_results: 100
""")
    
    # Create test defaults.yaml
    defaults_yaml = config_dir / "defaults.yaml"
    defaults_yaml.write_text("""
defaults:
  type: task
  priority: 2
  status: open
  assignee: "@current-agent"

display:
  format: table
  color: true

behavior:
  confirm_bulk: true
  cache_duration: 300
""")
    
    return config_dir


@pytest.fixture
def manager(temp_config):
    """Create BeadsManager instance with test config."""
    return BeadsManager(temp_config)


class TestBeadsManagerInit:
    """Test BeadsManager initialization."""
    
    def test_init_loads_repos(self, manager):
        """Test that repos are loaded from config."""
        assert 'test-repo' in manager.repos
        assert 'test-repo-2' in manager.repos
        assert manager.repos['test-repo']['path'] == '/tmp/test-repo'
    
    def test_init_loads_defaults(self, manager):
        """Test that defaults are loaded from config."""
        assert manager.defaults['defaults']['type'] == 'task'
        assert manager.defaults['defaults']['priority'] == 2
    
    def test_init_filters_disabled_repos(self, temp_config):
        """Test that disabled repos are filtered out."""
        # Add disabled repo to config
        repos_yaml = temp_config / "repos.yaml"
        config = repos_yaml.read_text()
        config += """
  disabled-repo:
    path: /tmp/disabled
    beads_dir: .beads
    enabled: false
"""
        repos_yaml.write_text(config)
        
        manager = BeadsManager(temp_config)
        assert 'disabled-repo' not in manager.repos
    
    def test_init_fails_without_config(self, tmp_path):
        """Test that initialization fails without config file."""
        with pytest.raises(FileNotFoundError):
            BeadsManager(tmp_path / "nonexistent")


class TestCreateIssue:
    """Test issue creation functionality."""
    
    def test_create_issue_basic(self, manager, monkeypatch):
        """Test basic issue creation."""
        # Mock subprocess.run
        mock_result = Mock()
        mock_result.stdout = "Created issue: bd-test123"
        mock_result.stderr = ""
        mock_result.returncode = 0
        
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        issue_id = manager.create_issue(
            repo='test-repo',
            title='Test issue',
            interactive=False
        )
        
        assert issue_id == 'bd-test123'
        
        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['bd', 'create', 'Test issue', '--type=task', '--priority=2']
        assert call_args[1]['cwd'] == Path('/tmp/test-repo')
    
    def test_create_issue_with_all_params(self, manager, monkeypatch):
        """Test issue creation with all parameters."""
        mock_result = Mock()
        mock_result.stdout = "Created issue: bd-test456"
        mock_result.stderr = ""
        
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        issue_id = manager.create_issue(
            repo='test-repo',
            title='Complex issue',
            issue_type='bug',
            priority=1,
            description='Test description',
            blocks=['bd-abc123'],
            depends_on=['bd-def456'],
            labels=['urgent', 'critical'],
            interactive=False
        )
        
        assert issue_id == 'bd-test456'
        
        # Verify all parameters were passed
        call_args = mock_run.call_args[0][0]
        assert '--type=bug' in call_args
        assert '--priority=1' in call_args
        assert '--description' in call_args
        assert 'Test description' in call_args
        assert '--blocks' in call_args
        assert '--labels' in call_args
    
    def test_create_issue_unknown_repo(self, manager):
        """Test error handling for unknown repository."""
        with pytest.raises(ValueError, match="Unknown repository"):
            manager.create_issue(
                repo='unknown-repo',
                title='Test',
                interactive=False
            )
    
    def test_create_issue_applies_defaults(self, manager, monkeypatch):
        """Test that defaults are applied when not specified."""
        mock_result = Mock()
        mock_result.stdout = "Created issue: bd-test789"
        
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        manager.create_issue(
            repo='test-repo',
            title='Test defaults',
            interactive=False
        )
        
        # Check that defaults were used
        call_args = mock_run.call_args[0][0]
        assert '--type=task' in call_args  # Default type
        assert '--priority=2' in call_args  # Default priority
    
    def test_create_issue_subprocess_error(self, manager, monkeypatch):
        """Test error handling when subprocess fails."""
        mock_run = Mock(side_effect=subprocess.CalledProcessError(
            returncode=1,
            cmd=['bd', 'create'],
            stderr="Error: Invalid parameters"
        ))
        monkeypatch.setattr('subprocess.run', mock_run)
        
        with pytest.raises(subprocess.CalledProcessError):
            manager.create_issue(
                repo='test-repo',
                title='Test',
                interactive=False
            )


class TestListIssues:
    """Test issue listing functionality."""
    
    def test_list_issues_basic(self, manager, monkeypatch):
        """Test basic issue listing."""
        mock_result = Mock()
        mock_result.stdout = json.dumps([
            {
                "id": "bd-test123",
                "title": "Test issue 1",
                "status": "open",
                "priority": 2,
                "type": "task"
            },
            {
                "id": "bd-test456",
                "title": "Test issue 2",
                "status": "in-progress",
                "priority": 1,
                "type": "bug"
            }
        ])
        mock_result.stderr = ""
        
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        issues = manager.list_issues(format='json')
        
        assert len(issues) == 2
        assert issues[0]['id'] == 'bd-test123'
        assert issues[0]['repo'] == 'test-repo'
        assert issues[1]['id'] == 'bd-test456'
    
    def test_list_issues_with_filters(self, manager, monkeypatch):
        """Test issue listing with filters."""
        mock_result = Mock()
        mock_result.stdout = json.dumps([])
        
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        manager.list_issues(
            repos=['test-repo'],
            status='open',
            priority=[1, 2],
            issue_type='bug',
            format='json'
        )
        
        # Verify filters were passed to subprocess
        call_args = mock_run.call_args[0][0]
        assert '--status' in call_args
        assert 'open' in call_args
        assert '--priority' in call_args
        assert '--type' in call_args
        assert 'bug' in call_args
    
    def test_list_issues_multiple_repos(self, manager, monkeypatch):
        """Test listing issues across multiple repos."""
        call_count = 0
        
        def mock_run_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            result = Mock()
            result.stderr = ""
            
            if call_count == 1:  # First repo
                result.stdout = json.dumps([{"id": "bd-1", "title": "Issue 1"}])
            else:  # Second repo
                result.stdout = json.dumps([{"id": "bd-2", "title": "Issue 2"}])
            
            return result
        
        mock_run = Mock(side_effect=mock_run_side_effect)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        issues = manager.list_issues(format='json')
        
        assert len(issues) == 2
        assert issues[0]['repo'] == 'test-repo'
        assert issues[1]['repo'] == 'test-repo-2'
    
    def test_list_issues_handles_repo_errors(self, manager, monkeypatch, capsys):
        """Test that errors in one repo don't break the entire listing."""
        call_count = 0
        
        def mock_run_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:  # First repo fails
                raise subprocess.CalledProcessError(
                    returncode=1,
                    cmd=['bd', 'list'],
                    stderr="Error in test-repo"
                )
            else:  # Second repo succeeds
                result = Mock()
                result.stdout = json.dumps([{"id": "bd-2", "title": "Issue 2"}])
                result.stderr = ""
                return result
        
        mock_run = Mock(side_effect=mock_run_side_effect)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        issues = manager.list_issues(format='json')
        
        # Should still get issues from second repo
        assert len(issues) == 1
        assert issues[0]['repo'] == 'test-repo-2'
        
        # Should print warning
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "test-repo" in captured.out


class TestShowIssue:
    """Test showing issue details."""
    
    def test_show_issue_with_repo(self, manager, monkeypatch):
        """Test showing issue when repo is specified."""
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "id": "bd-test123",
            "title": "Test issue",
            "status": "open",
            "priority": 2,
            "type": "task",
            "description": "Test description"
        })
        mock_result.stderr = ""
        
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        issue = manager.show_issue('bd-test123', repo='test-repo')
        
        assert issue['id'] == 'bd-test123'
        assert issue['repo'] == 'test-repo'
    
    def test_show_issue_auto_detect_repo(self, manager, monkeypatch, tmp_path):
        """Test auto-detecting which repo contains the issue."""
        # Create mock repo structure
        repo_path = tmp_path / 'test-repo'
        repo_path.mkdir()
        beads_dir = repo_path / '.beads' / 'issues'
        beads_dir.mkdir(parents=True)
        
        # Create issue file
        issue_file = beads_dir / 'bd-test123.md'
        issue_file.write_text('# Test issue')
        
        # Update manager's repo path to temp path
        manager.repos['test-repo']['path'] = str(repo_path)
        
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "id": "bd-test123",
            "title": "Test issue"
        })
        mock_result.stderr = ""
        
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        issue = manager.show_issue('bd-test123')
        
        assert issue['repo'] == 'test-repo'
    
    def test_show_issue_not_found(self, manager):
        """Test error when issue is not found in any repo."""
        with pytest.raises(ValueError, match="not found"):
            manager.show_issue('bd-nonexistent')


class TestCreateLinkedIssues:
    """Test creating linked issues across repositories."""
    
    def test_create_linked_basic(self, manager, monkeypatch):
        """Test creating linked issues."""
        issue_ids = ['bd-dep1', 'bd-dep2', 'bd-primary']
        call_count = 0
        
        def mock_run_side_effect(*args, **kwargs):
            nonlocal call_count
            result = Mock()
            result.stdout = f"Created issue: {issue_ids[call_count]}"
            result.stderr = ""
            call_count += 1
            return result
        
        mock_run = Mock(side_effect=mock_run_side_effect)
        monkeypatch.setattr('subprocess.run', mock_run)
        
        created = manager.create_linked_issues(
            primary=('test-repo', 'Primary issue'),
            dependencies=[
                ('test-repo-2', 'Dependency 1'),
                ('test-repo', 'Dependency 2')
            ],
            priority=1,
            interactive=False
        )
        
        assert len(created) == 3
        assert 'test-repo:Primary issue' in created
        assert created['test-repo:Primary issue'] == 'bd-primary'


class TestExtractIssueId:
    """Test issue ID extraction."""
    
    def test_extract_issue_id_standard(self, manager):
        """Test extracting issue ID from standard output."""
        output = "Created issue: bd-abc123"
        issue_id = manager._extract_issue_id(output)
        assert issue_id == 'bd-abc123'
    
    def test_extract_issue_id_with_path(self, manager):
        """Test extracting issue ID when path is included."""
        output = "Created issue bd-xyz789 at /path/to/.beads/issues/bd-xyz789.md"
        issue_id = manager._extract_issue_id(output)
        assert issue_id == 'bd-xyz789'
    
    def test_extract_issue_id_fails(self, manager):
        """Test error when no issue ID found."""
        with pytest.raises(ValueError):
            manager._extract_issue_id("No issue ID here")


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
