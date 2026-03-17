#!/usr/bin/env python3
"""
Prune old handoff files. Called automatically by agent-end.sh.

Policy:
  - Keep the most recent MAX_PER_AGENT files per agent in ~/.agent/handoff/
  - Move older files to ~/.agent/handoff/archive/
  - The archive itself is never auto-deleted

Usage:
    python cleanup_handoffs.py [--dry-run] [--max N]
"""
import json
import pathlib
import shutil
import sys
from collections import defaultdict

HANDOFF_DIR = pathlib.Path.home() / ".agent/handoff"
ARCHIVE_DIR = HANDOFF_DIR / "archive"
MAX_PER_AGENT = 20  # default; override with --max N


def main():
    dry_run = "--dry-run" in sys.argv
    max_keep = MAX_PER_AGENT
    if "--max" in sys.argv:
        idx = sys.argv.index("--max")
        max_keep = int(sys.argv[idx + 1])

    if not HANDOFF_DIR.exists():
        print("No handoff directory — nothing to clean.")
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Group handoff files by agent name (prefix before first timestamp segment)
    by_agent: dict[str, list[pathlib.Path]] = defaultdict(list)
    for f in HANDOFF_DIR.glob("*.json"):
        if not f.is_file():
            continue
        # agent name = everything before the first date-segment (8 digits)
        parts = f.stem.split("-")
        agent = parts[0]
        by_agent[agent].append(f)

    archived = 0
    for agent, files in by_agent.items():
        # Sort newest first
        files_sorted = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
        to_archive = files_sorted[max_keep:]
        for f in to_archive:
            dest = ARCHIVE_DIR / f.name
            if dry_run:
                print(f"  [dry-run] would archive: {f.name}")
            else:
                shutil.move(str(f), str(dest))
                archived += 1

    if dry_run:
        print(f"Dry run complete. Would archive files beyond last {max_keep} per agent.")
    else:
        if archived:
            print(f"  ✓ archived {archived} old handoff(s) to {ARCHIVE_DIR}")
        else:
            print(f"  ✓ handoffs clean (≤{max_keep} per agent)")


if __name__ == "__main__":
    main()
