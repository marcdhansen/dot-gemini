#!/usr/bin/env python3
"""
Tests for PR Response Protocol validators in check_protocol_compliance.py

These tests verify:
1. check_pr_decomposition_closure() - Ensures decomposed PRs are properly closed
2. check_child_pr_linkage() - Validates child PRs reference their parent Epic/issue
"""

import unittest
from unittest.mock import patch, MagicMock, call
import subprocess
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_protocol_compliance import (
    check_pr_decomposition_closure,
    check_child_pr_linkage,
)


class TestPRDecompositionClosure(unittest.TestCase):
    """Test suite for check_pr_decomposition_closure function"""

    @patch('check_protocol_compliance.check_tool_available')
    def test_missing_tools(self, mock_tool_check):
        """Test when beads or gh are not available"""
        mock_tool_check.side_effect = lambda tool: tool not in ["bd", "gh"]
        
        ok, msg = check_pr_decomposition_closure()
        self.assertTrue(ok)
        self.assertIn("not available", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    def test_no_active_issue(self, mock_get_issue, mock_tool_check):
        """Test when there's no active Beads issue"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = None
        
        ok, msg = check_pr_decomposition_closure()
        self.assertTrue(ok)
        self.assertIn("No active issue", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    @patch('subprocess.run')
    def test_no_child_issues(self, mock_run, mock_get_issue, mock_tool_check):
        """Test when issue has no child issues (not a decomposition)"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = "lightrag-123"
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Simple issue description no children"
        )
        
        ok, msg = check_pr_decomposition_closure()
        self.assertTrue(ok)
        self.assertIn("No child issues detected", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    @patch('subprocess.run')
    def test_decomposition_pr_properly_closed(self, mock_run, mock_get_issue, mock_tool_check):
        """Test when decomposed PR is properly closed"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = "lightrag-epic-001"
        
        # First call: bd show - returns issue with children and PR reference
        # Second call: gh pr view - returns CLOSED status
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Epic with part-of children. Original PR #49 decomposed."),
            MagicMock(returncode=0, stdout="CLOSED")
        ]
        
        ok, msg = check_pr_decomposition_closure()
        self.assertTrue(ok)
        self.assertIn("properly closed", msg)
        self.assertIn("#49", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    @patch('subprocess.run')
    def test_decomposition_pr_still_open_violation(self, mock_run, mock_get_issue, mock_tool_check):
        """Test PROTOCOL VIOLATION: Original PR still open with children"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = "lightrag-epic-001"
        
        # First call: bd show - returns issue with children and PR reference
        # Second call: gh pr view - returns OPEN status (VIOLATION)
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Epic with part-of children. Original PR #49"),
            MagicMock(returncode=0, stdout="OPEN")
        ]
        
        ok, msg = check_pr_decomposition_closure()
        self.assertFalse(ok)
        self.assertIn("PROTOCOL VIOLATION", msg)
        self.assertIn("still OPEN", msg)
        self.assertIn("#49", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    @patch('subprocess.run')
    def test_decomposition_pr_merged_ok(self, mock_run, mock_get_issue, mock_tool_check):
        """Test when original PR was merged (not decomposed, that's fine)"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = "lightrag-epic-001"
        
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Epic with part-of children. Original PR #49"),
            MagicMock(returncode=0, stdout="MERGED")
        ]
        
        ok, msg = check_pr_decomposition_closure()
        self.assertTrue(ok)
        self.assertIn("merged", msg)


class TestChildPRLinkage(unittest.TestCase):
    """Test suite for check_child_pr_linkage function"""

    @patch('check_protocol_compliance.check_tool_available')
    def test_missing_tools(self, mock_tool_check):
        """Test when beads or gh are not available"""
        mock_tool_check.side_effect = lambda tool: tool not in ["bd", "gh"]
        
        ok, msg = check_child_pr_linkage()
        self.assertTrue(ok)
        self.assertIn("not available", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    def test_no_active_issue(self, mock_get_issue, mock_tool_check):
        """Test when there's no active Beads issue"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = None
        
        ok, msg = check_child_pr_linkage()
        self.assertTrue(ok)
        self.assertIn("No active issue", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    @patch('subprocess.run')
    def test_no_parent_issue(self, mock_run, mock_get_issue, mock_tool_check):
        """Test when issue has no parent (not a child PR)"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = "lightrag-123"
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Standalone issue with no parent dependency"
        )
        
        ok, msg = check_child_pr_linkage()
        self.assertTrue(ok)
        self.assertIn("No parent issue detected", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    @patch('check_protocol_compliance.check_branch_info')
    @patch('subprocess.run')
    def test_child_pr_properly_references_parent(self, mock_run, mock_branch, mock_get_issue, mock_tool_check):
        """Test when child PR properly references parent Epic"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = "lightrag-124"
        mock_branch.return_value = ("feature/fix-deps", True)
        
        # First call: bd show - returns issue with parent reference
        # Second call: gh pr view - returns PR body with parent mention
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Part of: lightrag-epic-001\nFix dependency issues"),
            MagicMock(returncode=0, stdout="Part of Epic #lightrag-epic-001\nThis PR addresses dependency resolution.")
        ]
        
        ok, msg = check_child_pr_linkage()
        self.assertTrue(ok)
        self.assertIn("properly references", msg)
        self.assertIn("lightrag-epic-001", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    @patch('check_protocol_compliance.check_branch_info')
    @patch('subprocess.run')
    def test_child_pr_missing_parent_reference_violation(self, mock_run, mock_branch, mock_get_issue, mock_tool_check):
        """Test PROTOCOL VIOLATION: Child PR doesn't reference parent"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = "lightrag-124"
        mock_branch.return_value = ("feature/fix-deps", True)
        
        # First call: bd show - returns issue with parent reference
        # Second call: gh pr view - PR body missing parent reference (VIOLATION)
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Part of: lightrag-epic-001\nFix dependency issues"),
            MagicMock(returncode=0, stdout="Just fixing some dependencies\nNo parent reference")
        ]
        
        ok, msg = check_child_pr_linkage()
        self.assertFalse(ok)
        self.assertIn("PROTOCOL VIOLATION", msg)
        self.assertIn("does not reference parent", msg)
        self.assertIn("lightrag-epic-001", msg)

    @patch('check_protocol_compliance.check_tool_available')
    @patch('check_protocol_compliance.get_active_issue_id')
    @patch('check_protocol_compliance.check_branch_info')
    def test_not_on_feature_branch(self, mock_branch, mock_get_issue, mock_tool_check):
        """Test when not on a feature branch"""
        mock_tool_check.return_value = True
        mock_get_issue.return_value = "lightrag-124"
        mock_branch.return_value = ("main", False)
        
        ok, msg = check_child_pr_linkage()
        self.assertTrue(ok)
        self.assertIn("Not on feature branch", msg)


if __name__ == "__main__":
    unittest.main()
