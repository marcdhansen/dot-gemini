"""Tests for check_beads_github_sync validator."""
import json
import os
import tempfile
from pathlib import Path
import pytest
import sys

# Add the scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validators.finalization_validator import check_beads_github_sync


class TestBeadsGithubSync:
    """Tests for the beads GitHub sync validator."""

    def test_no_session_file_returns_false(self, tmp_path):
        """Test that missing session file returns False."""
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = check_beads_github_sync()
            assert result[0] is False
            assert "No active session found" in result[1]
        finally:
            os.chdir(old_cwd)

    def test_inactive_session_returns_false(self, tmp_path):
        """Test that inactive session returns False."""
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            session_file = tmp_path / ".agent" / "session_state.json"
            session_file.parent.mkdir(parents=True, exist_ok=True)
            
            session_data = {
                "status": "closed",
                "commands": []
            }
            session_file.write_text(json.dumps(session_data))
            
            result = check_beads_github_sync()
            assert result[0] is False
            assert "No active session" in result[1]
        finally:
            os.chdir(old_cwd)

    def test_active_session_without_sync_returns_false(self, tmp_path):
        """Test that active session without sync command returns False."""
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            session_file = tmp_path / ".agent" / "session_state.json"
            session_file.parent.mkdir(parents=True, exist_ok=True)
            
            session_data = {
                "status": "active",
                "commands": [
                    {"command": "git commit -m 'test'", "timestamp": 1234567890}
                ]
            }
            session_file.write_text(json.dumps(session_data))
            
            result = check_beads_github_sync()
            assert result[0] is False
            assert "Beads GitHub sync not recorded" in result[1]
        finally:
            os.chdir(old_cwd)

    def test_active_session_with_sync_returns_true(self, tmp_path):
        """Test that active session with sync command returns True."""
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            session_file = tmp_path / ".agent" / "session_state.json"
            session_file.parent.mkdir(parents=True, exist_ok=True)
            
            session_data = {
                "status": "active",
                "commands": [
                    {"command": "git commit -m 'test'", "timestamp": 1234567890},
                    {"command": "bd github sync --push-only", "timestamp": 1234567891}
                ]
            }
            session_file.write_text(json.dumps(session_data))
            
            result = check_beads_github_sync()
            assert result[0] is True
            assert "recorded during session" in result[1]
        finally:
            os.chdir(old_cwd)

    def test_malformed_json_returns_false(self, tmp_path):
        """Test that malformed JSON returns False."""
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            session_file = tmp_path / ".agent" / "session_state.json"
            session_file.parent.mkdir(parents=True, exist_ok=True)
            
            session_file.write_text("not valid json")
            
            result = check_beads_github_sync()
            assert result[0] is False
            assert "malformed" in result[1]
        finally:
            os.chdir(old_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
