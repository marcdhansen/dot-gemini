#!/usr/bin/env python3
"""
/continue skill — load a prior session handoff into working memory.

Usage:
    python continue.py                           # most recent handoff (any agent)
    python continue.py opencode                  # most recent for a specific agent
    python continue.py opencode-20260314T1504-a3f7  # exact session ID
"""
import json
import pathlib
import sys

HANDOFF_DIR = pathlib.Path.home() / ".agent/handoff"


def all_handoffs():
    """All .json handoffs, newest-modified first, excluding archive subdir."""
    files = [
        f for f in HANDOFF_DIR.glob("*.json")
        if f.is_file()
    ]
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def fmt(data: dict, path: pathlib.Path) -> str:
    agent     = data.get("agent", "unknown")
    ts        = data.get("timestamp", path.stem)[:19].replace("T", " ")
    ctx       = data.get("context", {})
    desc      = ctx.get("description") or "no description"
    completed = data.get("completed", [])
    open_items= data.get("open_items", [])
    blockers  = data.get("blockers", [])
    next_rec  = data.get("next_recommended", "")
    beads     = ctx.get("beads_issue")
    pr        = ctx.get("pr_url")
    branch    = ctx.get("branch")

    lines = [
        f"━━━ Handoff: {path.stem} ━━━",
        f"Agent: {agent}  |  {ts}",
        f"Task:  {desc}",
    ]
    if beads or pr or branch:
        meta = "  ".join(filter(None, [
            f"Beads: {beads}" if beads else None,
            f"PR: {pr}"       if pr    else None,
            f"Branch: {branch}"if branch else None,
        ]))
        lines.append(f"       {meta}")

    if completed:
        lines.append(f"\n✅ Done ({len(completed)}):")
        for c in completed[:5]:
            lines.append(f"  • {c}")
        if len(completed) > 5:
            lines.append(f"  … and {len(completed) - 5} more")

    if open_items:
        lines.append(f"\n🔄 Open ({len(open_items)}):")
        for o in open_items[:5]:
            lines.append(f"  • {o}")
        if len(open_items) > 5:
            lines.append(f"  … and {len(open_items) - 5} more")

    if blockers:
        lines.append(f"\n🚫 Blockers ({len(blockers)}) — DO NOT PROCEED without user sign-off:")
        for b in blockers:
            lines.append(f"  • {b}")
    else:
        lines.append("\n🚫 Blockers: None")

    if next_rec:
        lines.append(f"\n➡️  Next recommended: {next_rec}")

    return "\n".join(lines)


def main():
    if not HANDOFF_DIR.exists():
        print("No handoff directory found (~/.agent/handoff/). Fresh start.")
        return

    arg = sys.argv[1] if len(sys.argv) > 1 else None

    if arg:
        # 1. Try exact session ID
        exact = HANDOFF_DIR / f"{arg}.json"
        if exact.exists():
            print(fmt(load(exact), exact))
            return

        # 2. Try as agent name prefix — load most recent
        matches = sorted(
            HANDOFF_DIR.glob(f"{arg}-*.json"),
            key=lambda f: f.stat().st_mtime, reverse=True
        )
        if matches:
            print(fmt(load(matches[0]), matches[0]))
            return

        print(f"No handoff found for: {arg!r}")
        print(f"Available: {[f.stem for f in all_handoffs()[:5]]}")
        sys.exit(1)

    else:
        # No arg — show recent list, then auto-load the newest
        files = all_handoffs()
        if not files:
            print("No handoffs found. Fresh start — no prior context.")
            return

        if len(files) > 1:
            print(f"Recent handoffs ({min(len(files), 5)} shown):\n")
            for i, f in enumerate(files[:5]):
                try:
                    d = load(f)
                    agent = d.get("agent", "?")
                    ts    = d.get("timestamp", "?")[:16].replace("T", " ")
                    desc  = d.get("context", {}).get("description", "no description")
                    blk   = " 🚫" if d.get("blockers") else ""
                    marker = " ← loading" if i == 0 else ""
                    print(f"  [{i+1}] {f.stem}{blk}{marker}")
                    print(f"       {agent} · {ts} · {desc}")
                except Exception as e:
                    print(f"  [{i+1}] {f.name}  (parse error: {e})")
            print()

        print(fmt(load(files[0]), files[0]))


if __name__ == "__main__":
    main()
