#!/usr/bin/env python3
"""
Tests for SOP Infrastructure Change Detection

Verifies that code changes to SOP infrastructure (Orchestrator scripts, skill scripts, SKILL.md files)
trigger Full Mode escalation per the SOP Modification workflow.

This is a gate test per the SOP Modification skill.
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_protocol_compliance import check_sop_infrastructure_changes


class TestSOPInfrastructureEscalation(unittest.TestCase):
    """Test suite for SOP infrastructure change detection"""

    @patch('subprocess.run')
    def test_no_changes_no_escalation(self, mock_run):
        """Test that no changes means no escalation"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        requires_full_mode, msg = check_sop_infrastructure_changes()
        self.assertFalse(requires_full_mode)
        self.assertIn("No SOP infrastructure changes", msg)

    @patch('subprocess.run')
    def test_orchestrator_script_change_triggers_escalation(self, mock_run):
        """Test that changes to Orchestrator scripts trigger Full Mode"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=".gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py"
        )
        
        requires_full_mode, msg = check_sop_infrastructure_changes()
        self.assertTrue(requires_full_mode)
        self.assertIn("SOP infrastructure changes detected", msg)
        self.assertIn("check_protocol_compliance.py", msg)

    @patch('subprocess.run')
    def test_skill_script_change_triggers_escalation(self, mock_run):
        """Test that changes to skill scripts trigger Full Mode"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=".gemini/antigravity/skills/reflect/scripts/enhanced_reflection.py"
        )
        
        requires_full_mode, msg = check_sop_infrastructure_changes()
        self.assertTrue(requires_full_mode)
        self.assertIn("SOP infrastructure changes detected", msg)

    @patch('subprocess.run')
    def test_skill_md_change_triggers_escalation(self, mock_run):
        """Test that changes to SKILL.md files trigger Full Mode"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=".gemini/antigravity/skills/planning/SKILL.md"
        )
        
        requires_full_mode, msg = check_sop_infrastructure_changes()
        self.assertTrue(requires_full_mode)
        self.assertIn("SOP infrastructure changes detected", msg)

    @patch('subprocess.run')
    def test_sop_doc_change_triggers_escalation(self, mock_run):
        """Test that changes to SOP documentation trigger Full Mode"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=".agent/docs/SOP_COMPLIANCE_CHECKLIST.md"
        )
        
        requires_full_mode, msg = check_sop_infrastructure_changes()
        self.assertTrue(requires_full_mode)
        self.assertIn("SOP infrastructure changes detected", msg)

    @patch('subprocess.run')
    def test_regular_code_change_no_escalation(self, mock_run):
        """Test that regular code changes don't trigger SOP infrastructure escalation"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="src/lightrag/core/engine.py\nsrc/lightrag/utils/helpers.py"
        )
        
        requires_full_mode, msg = check_sop_infrastructure_changes()
        self.assertFalse(requires_full_mode)
        self.assertIn("No SOP infrastructure changes", msg)

    @patch('subprocess.run')
    def test_mixed_changes_triggers_escalation(self, mock_run):
        """Test that mixed changes (SOP + regular) trigger escalation"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="""src/lightrag/core/engine.py
.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py
src/lightrag/utils/helpers.py"""
        )
        
        requires_full_mode, msg = check_sop_infrastructure_changes()
        self.assertTrue(requires_full_mode)
        self.assertIn("SOP infrastructure changes detected", msg)


if __name__ == "__main__":
    unittest.main()
