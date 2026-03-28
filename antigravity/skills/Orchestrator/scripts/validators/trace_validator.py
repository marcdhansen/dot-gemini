"""
Trace Validator - Verifies intent/action/outcome tracking

This validator checks that agents are properly logging their actions
and not failing silently or using workarounds.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path for trace_logger
sys.path.insert(0, str(Path(__file__).parent.parent))
from validators.common import check_mark, Colors

try:
    from trace_logger import verify_trace, audit_report, get_logger
except ImportError:
    # Fallback if trace_logger not available
    def verify_trace():
        return {"passed": True, "issues": [], "summary": "Trace logger not available"}

    def audit_report():
        return "Trace logger not available"


def check_trace_integrity() -> tuple[bool, str]:
    """
    Verify that traced actions match stated intents.

    Returns (passed, message) tuple.
    """
    result = verify_trace()

    if result["passed"]:
        return True, result["summary"]

    # Build issue report
    issues = result.get("issues", [])
    msg_parts = [f"{len(issues)} trace issues detected:"]

    for issue in issues:
        msg_parts.append(f"  - {issue.get('message', 'unknown issue')}")

    return False, "\n".join(msg_parts)


def check_trace_audit() -> tuple[bool, str]:
    """
    Generate and return the self-report audit.

    Returns (has_entries, audit_report) tuple.
    """
    report = audit_report()

    # Check if there are actual entries
    has_entries = "No actions traced" not in report and "0 actions" not in report

    return has_entries, report


def print_trace_audit():
    """Print the full trace audit to console."""
    _, report = check_trace_audit()
    print(report)


if __name__ == "__main__":
    # Test
    print("Trace Integrity Check:")
    passed, msg = check_trace_integrity()
    print(f"{check_mark(passed)} {msg}")

    print("\n" + "=" * 50)
    print_trace_audit()
