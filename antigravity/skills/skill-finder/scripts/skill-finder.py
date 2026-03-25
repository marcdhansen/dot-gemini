#!/usr/bin/env python3
"""Find existing skills before creating new ones."""

import argparse
import subprocess
import sys
from pathlib import Path


SKILL_MARKETPLACES = [
    ("Anthropic Official", "https://github.com/anthropics/skills", "Document, PDF, PPT, Excel"),
    (
        "Alireza Rezvan",
        "https://github.com/alirezarezvani/claude-skills",
        "183+ skills, 11 platforms",
    ),
    ("LobeHub", "https://lobehub.com/skills", "100,000+ skills"),
    ("MCP Market", "https://mcpmarket.com/tools/skills", "MCP-compatible skills"),
    ("skillsmp.com", "https://skillsmp.com", "Community skills"),
]

LOCAL_SKILL_DIRS = [
    Path.home() / ".config" / "opencode" / "skills",
    Path.home() / ".claude" / "skills",
]


def search_local(task: str) -> list[str]:
    """Search locally installed skills."""
    found = []
    task_lower = task.lower()

    for skill_dir in LOCAL_SKILL_DIRS:
        if not skill_dir.exists():
            continue
        for skill_path in skill_dir.iterdir():
            if skill_path.is_dir() and task_lower in skill_path.name.lower():
                found.append(str(skill_path))

    return found


def search_github(task: str) -> list[str]:
    """Search GitHub for skill repositories."""
    try:
        result = subprocess.run(
            ["gh", "search", "repos", f"claude skill {task}", "--limit", "5", "--json", "name,url"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            import json

            repos = json.loads(result.stdout)
            return [f"{r['name']}: {r['url']}" for r in repos]
    except Exception:
        pass
    return []


def main():
    parser = argparse.ArgumentParser(description="Find existing skills before creating new ones")
    parser.add_argument("task", nargs="?", help="Task description to search for")
    parser.add_argument("--local-only", action="store_true", help="Only check local skills")
    args = parser.parse_args()

    if not args.task:
        print("Usage: skill-finder.py <task description>")
        print("\nExample: skill-finder.py testing")
        print("\nSearching local skills...")
        args.task = ""

    print("🔍 SKILL FINDER")
    print("=" * 50)

    if args.task:
        print(f"\nTask: {args.task}\n")

    # Search local
    print("📂 Local Skills:")
    local_found = search_local(args.task) if args.task else []
    if local_found:
        for skill in local_found:
            print(f"   ✅ {Path(skill).name}")
    else:
        print("   ❌ None found")

    if args.local_only:
        return

    # GitHub search
    if args.task:
        print("\n🐙 GitHub Search:")
        gh_found = search_github(args.task)
        if gh_found:
            for repo in gh_found:
                print(f"   ⚡ {repo}")
        else:
            print("   ❌ None found")

    # Marketplaces
    print("\n🌐 Skill Marketplaces:")
    for name, url, desc in SKILL_MARKETPLACES:
        print(f"   📦 {name}: {url}")
        print(f"      {desc}")

    print("\n" + "=" * 50)
    print("\n💡 Next Steps:")
    print("   1. Search marketplaces manually if needed")
    print("   2. If found: Use/adapt existing skill")
    print("   3. If not found: Create new skill with /skill-making")


if __name__ == "__main__":
    main()
