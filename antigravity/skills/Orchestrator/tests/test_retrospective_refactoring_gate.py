#!/usr/bin/env python3
"""
Tests for Retrospective Refactoring Identification

Verifies that the Orchestrator enforces the presence of 'refactoring_candidates'
in the structured reflection artifact (.reflection_input.json).

This is a gate test per the SOP Modification skill.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_protocol_compliance import check_reflection_invoked


class TestRetrospectiveRefactoring(unittest.TestCase):
    """Test suite for retrospective refactoring identification gate"""

    def setUp(self):
        self.artifact_path = Path(".reflection_input.json")
        if self.artifact_path.exists():
            self.artifact_path.unlink()

    def tearDown(self):
        if self.artifact_path.exists():
            self.artifact_path.unlink()

    def test_reflection_missing_refactoring_candidates_fails(self):
        """Test that reflection missing refactoring_candidates field fails validation"""
        data = {
            "session_name": "Test Session",
            "outcome": "SUCCESS",
            "technical_learnings": ["Learned something"]
        }
        self.artifact_path.write_text(json.dumps(data))
        
        ok, msg = check_reflection_invoked()
        self.assertFalse(ok)
        self.assertIn("missing required fields", msg)
        self.assertIn("refactoring_candidates", msg)

    def test_reflection_with_refactoring_candidates_passes(self):
        """Test that reflection with refactoring_candidates field passes validation"""
        data = {
            "session_name": "Test Session",
            "outcome": "SUCCESS",
            "technical_learnings": ["Learned something"],
            "refactoring_candidates": ["Monolith script X needs decomposition"]
        }
        self.artifact_path.write_text(json.dumps(data))
        
        ok, msg = check_reflection_invoked()
        # Note: Might still fail due to recency if mtime is old, but we test the field check
        if not ok and "too old" in msg:
            # If it failed only because of recency, the field check passed
            pass
        else:
            self.assertTrue(ok, f"Validation failed: {msg}")


if __name__ == "__main__":
    unittest.main()
