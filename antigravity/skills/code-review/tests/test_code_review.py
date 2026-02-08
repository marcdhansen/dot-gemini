import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os

# Add scripts to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))
from code_review import CodeReviewer

class TestCodeReviewer(unittest.TestCase):
    def setUp(self):
        self.reviewer = CodeReviewer()

    def test_validate_size_pass(self):
        diff = "+\n" * 10
        self.assertTrue(self.reviewer.validate_size(diff))

    def test_validate_size_fail(self):
        self.reviewer.config["max_diff_lines"] = 5
        diff = "+\n" * 10
        self.assertFalse(self.reviewer.validate_size(diff))

    @patch('code_review.is_non_interactive', return_value=True)
    def test_execute_non_interactive_pass(self, mock_non_int):
        with patch.object(CodeReviewer, 'get_diff', return_value="some diff"):
            with patch.object(CodeReviewer, 'validate_size', return_value=True):
                with patch.object(CodeReviewer, 'check_tests', return_value=True):
                    self.assertTrue(self.reviewer.execute())

    @patch('code_review.is_non_interactive', return_value=False)
    @patch('code_review.safe_input', return_value='n')
    def test_execute_interactive_reject(self, mock_input, mock_non_int):
        with patch.object(CodeReviewer, 'get_diff', return_value="some diff"):
            self.reviewer.config["checklist"] = ["Item 1"]
            self.assertFalse(self.reviewer.execute())

if __name__ == "__main__":
    unittest.main()
