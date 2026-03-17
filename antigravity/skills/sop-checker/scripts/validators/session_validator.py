import json
from pathlib import Path
from .common import check_mark, Colors


def check_show_next_task_used(*args) -> tuple[bool, str]:
    """
    Verify that the show-next-task skill was used for task discovery.
    This is a MANUAL check - the validator prompts the agent to confirm.
    """
    print()
    print("─" * 50)
    print("🔍 MANUAL VERIFICATION: Task Discovery")
    print("─" * 50)
    print()
    print("When you answered 'what should we work on next?' (or similar),")
    print("did you use the show-next-task skill?")
    print()
    print("Expected response: YES (I used /show-next-task)")
    print()
    print(f"{Colors.YELLOW}NOTE: Always use show-next-task skill for task discovery,")
    print(f"regardless of how the user phrases the question.{Colors.END}")
    print()
    # Returns True by default - creates accountability through the prompt
    # The agent must see this question when running initialization
    return True, "Manual verification - see prompt above"


def check_harness_session(*args) -> tuple[bool, str]:
    """Verify that a harness session is active for the current workspace."""
    session_file = Path.cwd() / ".agent" / "sessions" / "session.lock"

    if not session_file.exists():
        return False, "No active harness session found. Run orchestrator initialization first."

    try:
        with open(session_file, "r") as f:
            data = json.load(f)

        session_id = data.get("id", "unknown")
        issue_id = data.get("issue_id", "unknown")

        return True, f"Active session found: {session_id} (Tracking: {issue_id})"
    except Exception as e:
        return False, f"Error reading session file: {e}"
