#!/usr/bin/env python3
"""Test cases for Browser Manager functionality."""

import json
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the scripts directory to the path and import directly
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

os.environ["AGENT_ID"] = "test-agent"  # Set test agent ID

# Import the module directly
import importlib.util

spec = importlib.util.spec_from_file_location(
    "browser_manager", Path(__file__).parent.parent / "scripts" / "browser_manager.py"
)
browser_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(browser_manager)

BrowserManager = browser_manager.BrowserManager


class TestBrowserManager(unittest.TestCase):
    """Test cases for Browser Manager core functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "test_config.yaml"
        self.session_file = self.temp_dir / "test_sessions.json"

        # Create test configuration
        test_config = {
            "limits": {
                "max_tabs_per_agent": 3,
                "max_browser_age_minutes": 30,
                "max_memory_mb": 500,
                "max_browsers_total": 5,
            },
            "admin": {
                "require_permission_for_others": True,
                "permission_timeout_seconds": 5,
                "audit_log_enabled": True,
            },
            "tracking": {"delete_on_mission_end": True, "tab_detection_timeout": 2},
            "display": {"show_tabs_in_status": True, "verbose_mode": True},
        }

        import yaml

        with open(self.config_file, "w") as f:
            yaml.dump(test_config, f)

        self.manager = BrowserManager(config_path=self.config_file)
        self.manager.session_file = self.session_file

    def test_config_loading(self):
        """Test configuration loading."""
        self.assertEqual(self.manager.config["limits"]["max_tabs_per_agent"], 3)
        self.assertEqual(self.manager.config["admin"]["permission_timeout_seconds"], 5)
        self.assertTrue(self.manager.config["tracking"]["delete_on_mission_end"])

    def test_process_detection_criteria(self):
        """Test browser process detection criteria."""
        # Test valid Playwright browser
        valid_cmdline = (
            "--remote-debugging-port=9222 --user-data-dir=/tmp/test --no-first-run"
        )
        self.assertTrue(
            self.manager._is_playwright_browser(
                MagicMock(info={"name": "Google Chrome"}), valid_cmdline
            )
        )

        # Test invalid process (no remote debugging)
        invalid_cmdline = "--user-data-dir=/tmp/test --no-first-run"
        self.assertFalse(
            self.manager._is_playwright_browser(
                MagicMock(info={"name": "Google Chrome"}), invalid_cmdline
            )
        )

        # Test renderer process (should be excluded)
        renderer_cmdline = (
            "--type=renderer --remote-debugging-port=9222 --user-data-dir=/tmp/test"
        )
        self.assertFalse(
            self.manager._is_playwright_browser(
                MagicMock(info={"name": "Google Chrome Helper"}), renderer_cmdline
            )
        )

    def test_user_data_dir_extraction(self):
        """Test user data directory extraction."""
        cmdline = "--user-data-dir=/path/to/profile --remote-debugging-port=9222"
        self.assertEqual(
            self.manager._extract_user_data_dir(cmdline), "/path/to/profile"
        )

        cmdline_no_dir = "--remote-debugging-port=9222"
        self.assertIsNone(self.manager._extract_user_data_dir(cmdline_no_dir))

    def test_debug_port_extraction(self):
        """Test debugging port extraction."""
        cmdline = "--remote-debugging-port=9222 --user-data-dir=/tmp/test"
        self.assertEqual(self.manager._find_debugging_port(cmdline), 9222)

        cmdline_no_port = "--user-data-dir=/tmp/test"
        self.assertIsNone(self.manager._find_debugging_port(cmdline_no_port))

    @patch("browser_manager.requests.get")
    def test_tab_detection_with_devtools(self, mock_get):
        """Test tab detection using Chrome DevTools Protocol."""
        # Mock successful DevTools response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "tab1",
                "url": "https://example.com",
                "title": "Example Page",
                "type": "page",
            },
            {
                "id": "tab2",
                "url": "chrome://newtab/",
                "title": "New Tab",
                "type": "page",
            },
            {
                "id": "devtools1",
                "url": "chrome-devtools://...",
                "title": "DevTools",
                "type": "devtools",
            },
        ]
        mock_get.return_value = mock_response

        browser_info = {"pid": 1234, "debug_port": 9222, "agent_id": "test-agent"}

        tabs = self.manager.detect_browser_tabs(browser_info)

        # Should detect 2 tabs (skip devtools)
        self.assertEqual(len(tabs), 2)
        self.assertEqual(tabs[0]["title"], "Example Page")
        self.assertEqual(tabs[0]["url"], "https://example.com")
        self.assertEqual(tabs[1]["title"], "New Tab")
        self.assertEqual(tabs[1]["type"], "page")

    def test_tab_detection_fallback(self):
        """Test tab detection fallback when DevTools fails."""
        browser_info = {
            "pid": 1234,
            "debug_port": None,  # No debug port
            "agent_id": "test-agent",
        }

        tabs = self.manager.detect_browser_tabs(browser_info)

        # Should fall back to estimated tab
        self.assertEqual(len(tabs), 1)
        self.assertEqual(tabs[0]["type"], "estimated")

    def test_resource_limits_check(self):
        """Test resource limits checking."""
        # Mock browser data that exceeds limits
        mock_browsers = [
            {
                "agent_id": "test-agent",
                "memory_mb": 300,
                "start_time": time.time() - 3600,  # 1 hour ago
                "tabs": [
                    {"id": "tab1"},
                    {"id": "tab2"},
                    {"id": "tab3"},
                    {"id": "tab4"},
                ],  # 4 tabs
            }
        ]

        with patch.object(
            self.manager, "detect_playwright_browsers", return_value=mock_browsers
        ):
            limits_ok, warnings = self.manager.check_resource_limits()

            # Should have warnings for tab count and age
            self.assertFalse(limits_ok)
            self.assertTrue(any("tab count" in w.lower() for w in warnings))
            self.assertTrue(any("old browser" in w.lower() for w in warnings))

    def test_session_tracking(self):
        """Test browser session tracking."""
        # Test saving sessions
        test_sessions = {
            "1234": {
                "agent_id": "test-agent",
                "start_time": "2026-02-04T10:00:00",
                "browser_info": {"pid": 1234, "name": "Chrome"},
            }
        }

        self.manager._save_sessions(test_sessions)
        loaded_sessions = self.manager._load_sessions()

        self.assertEqual(loaded_sessions, test_sessions)

    @patch("browser_manager.psutil.Process")
    def test_browser_cleanup(self, mock_process_class):
        """Test browser cleanup functionality."""
        # Mock browser process
        mock_process = MagicMock()
        mock_process_class.return_value = mock_process

        # Mock successful graceful shutdown
        mock_process.wait.return_value = None

        browser = {"pid": 1234, "agent_id": "test-agent", "memory_mb": 100, "tabs": []}

        stats = self.manager._execute_cleanup([browser])

        # Should call terminate and wait
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()

        # Should report success
        self.assertEqual(stats["success"], 1)
        self.assertEqual(stats["attempted"], 1)

    def test_audit_logging(self):
        """Test audit logging for cross-agent operations."""
        browser = {"pid": 1234, "agent_id": "other-agent", "memory_mb": 100, "tabs": []}

        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            self.manager._log_audit("cleanup_success", browser)

            # Should log audit entry
            mock_open.assert_called_once()
            written_data = mock_file.write.call_args[0][0]
            audit_entry = json.loads(written_data)

            self.assertEqual(audit_entry["action"], "cleanup_success")
            self.assertEqual(audit_entry["agent_id"], self.manager.agent_id)
            self.assertEqual(audit_entry["target_agent_id"], "other-agent")
            self.assertEqual(audit_entry["browser_pid"], 1234)

    def test_rtb_cleanup(self):
        """Test RTB cleanup integration."""
        with patch.object(
            self.manager,
            "cleanup_browsers",
            return_value={"success": 2, "attempted": 2},
        ) as mock_cleanup:
            with patch.object(
                self.manager, "cleanup_session_data"
            ) as mock_cleanup_data:
                with patch("builtins.print") as mock_print:
                    self.manager.rtb_cleanup()

                    # Should call cleanup methods
                    mock_cleanup.assert_called_once()
                    mock_cleanup_data.assert_called_once()

                    # Should print summary
                    print_calls = [call[0][0] for call in mock_print.call_args_list]
                    self.assertTrue(
                        any("Cleaned 2/2 browsers" in call for call in print_calls)
                    )


class TestBrowserManagerIntegration(unittest.TestCase):
    """Integration tests for Browser Manager."""

    def setUp(self):
        """Set up integration test environment."""
        self.manager = BrowserManager()

    @unittest.skipUnless(sys.stdout.isatty(), "Requires interactive terminal")
    def test_real_browser_detection(self):
        """Test detection of real browsers (if available)."""
        browsers = self.manager.detect_playwright_browsers()

        # Should not crash and return a list
        self.assertIsInstance(browsers, list)

        if browsers:
            browser = browsers[0]
            self.assertIn("pid", browser)
            self.assertIn("agent_id", browser)
            self.assertIn("tabs", browser)
            self.assertIsInstance(browser["tabs"], list)

    def test_configuration_creation(self):
        """Test creation of default configuration."""
        # Remove any existing config
        if self.manager.config_path.exists():
            self.manager.config_path.unlink()

        # Create new manager (should create default config)
        new_manager = BrowserManager(config_path=self.manager.config_path)

        # Should have default values
        self.assertIsNone(new_manager.config["limits"]["max_tabs_per_agent"])
        self.assertTrue(new_manager.config["admin"]["require_permission_for_others"])
        self.assertTrue(new_manager.config["tracking"]["delete_on_mission_end"])


if __name__ == "__main__":
    # Configure test output
    unittest.main(verbosity=2)
