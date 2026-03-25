#!/usr/bin/env python3
"""Continue a session by reading the handoff file."""

import subprocess
import sys
from pathlib import Path


def run(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode == 0
    except Exception as e:
        return str(e), False


def find_session_handoff():
    """Find the most recent session handoff file."""
    handoffs_dir = Path(".agent/handoffs")
    if not handoffs_dir.exists():
        return None

    session_files = list(handoffs_dir.glob("*-session.md"))
    if not session_files:
        return None

    return max(session_files, key=lambda p: p.stat().st_mtime)


def main():
    print("📋 SESSION CONTINUE")
    print("=" * 40)

    # Git pull
    print("\n🔄 Pulling latest changes...")
    output, ok = run("git pull --rebase 2>&1")
    if ok:
        print(f"   ✅ {output}" if output else "   ✅ Already up to date")
    else:
        print(f"   ⚠️ {output}")

    # Find and read handoff
    handoff = find_session_handoff()
    if handoff:
        print(f"\n📄 Reading: {handoff.name}")
        print("-" * 40)
        content = handoff.read_text()
        print(content)
    else:
        print("\n⚠️ No session handoff file found")
        print("   (This is normal for first session)")

    # Check inbox
    print("\n📬 Checking inbox...")
    if Path("src/agent_harness/scripts/poll_inbox.py").exists():
        output, ok = run("python3 src/agent_harness/scripts/poll_inbox.py 2>&1")
        print(f"   {output}")
    else:
        print("   (Poll script not found)")

    print("\n" + "=" * 40)
    print("Ready to continue! 🎯")


if __name__ == "__main__":
    main()
