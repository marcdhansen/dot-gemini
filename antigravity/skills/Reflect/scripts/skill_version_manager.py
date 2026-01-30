#!/usr/bin/env python3
"""
Tag-based versioning and rollback system for SKILL.md files.
Provides safe experimentation with skills and easy rollback capabilities.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class SkillVersionManager:
    """Manages versioning and rollback for skill files using Git tags."""

    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = (
            skills_dir or Path.home() / ".gemini" / "antigravity" / "skills"
        )
        self.version_file = (
            Path.home() / ".gemini" / "learnings" / "skill_versions.json"
        )
        self.version_file.parent.mkdir(parents=True, exist_ok=True)

        # Ensure we're in a git repo
        if not self._ensure_git_repo():
            raise RuntimeError("Skills directory is not a Git repository")

    def _ensure_git_repo(self) -> bool:
        """Ensure skills directory is a Git repository."""
        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ["git", "status"], cwd=self.skills_dir, capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _run_git_command(
        self, args: List[str], capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a git command in skills directory."""
        try:
            return subprocess.run(
                ["git"] + args,
                cwd=self.skills_dir,
                capture_output=capture_output,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Git command failed: {' '.join(args)}. Error: {e.stderr}"
            )

    def create_learning_tag(
        self,
        skill_name: str,
        learning_description: str,
        author: str = "enhanced-reflect",
    ) -> str:
        """
        Create a tag-based version for a skill learning.

        Args:
            skill_name: Name of skill being modified
            learning_description: Description of learning applied
            author: Author of the change

        Returns:
            Tag name created
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tag_name = f"learning_{timestamp}_{skill_name.lower().replace('-', '_')}"

        # First ensure changes are committed
        self._commit_changes(skill_name, learning_description, author)

        # Create annotated tag
        tag_message = f"""Learning Update for {skill_name}

Description: {learning_description}
Author: {author}
Timestamp: {datetime.now().isoformat()}
Type: learning_update
"""

        try:
            self._run_git_command(["tag", "-a", tag_name, "-m", tag_message])
            self._record_version(tag_name, skill_name, learning_description, author)
            print(f"✅ Created tag: {tag_name}")
            return tag_name
        except Exception as e:
            raise RuntimeError(f"Failed to create tag {tag_name}: {e}")

    def _commit_changes(self, skill_name: str, description: str, author: str) -> None:
        """Commit any changes to skill file."""
        skill_file = self.skills_dir / skill_name / "SKILL.md"

        if not skill_file.exists():
            return  # No changes to commit

        # Add specific skill file
        try:
            self._run_git_command(["add", str(skill_file.relative_to(self.skills_dir))])

            commit_message = f"docs(skills): Update {skill_name} with learning\\n\\n{description}\\n\\nAuthor: {author}"
            self._run_git_command(["commit", "-m", commit_message])
            print(f"✅ Committed changes to {skill_name}")
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in e.stderr.lower():
                print(f"ℹ️ No changes to commit for {skill_name}")
            else:
                raise

    def _record_version(
        self, tag_name: str, skill_name: str, description: str, author: str
    ) -> None:
        """Record version information in version tracking file."""
        versions = self._load_versions()

        version_entry = {
            "tag": tag_name,
            "skill": skill_name,
            "description": description,
            "author": author,
            "timestamp": datetime.now().isoformat(),
            "type": "learning_update",
        }

        versions.append(version_entry)
        self._save_versions(versions)

    def _load_versions(self) -> List[Dict[str, Any]]:
        """Load version history."""
        try:
            if self.version_file.exists():
                return json.loads(self.version_file.read_text())
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_versions(self, versions: List[Dict[str, Any]]) -> None:
        """Save version history."""
        self.version_file.write_text(json.dumps(versions, indent=2))

    def list_versions(self, skill_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all versions, optionally filtered by skill."""
        versions = self._load_versions()

        if skill_name:
            versions = [v for v in versions if v["skill"] == skill_name]

        # Sort by timestamp (newest first)
        versions.sort(key=lambda x: x["timestamp"], reverse=True)
        return versions

    def rollback_to_tag(self, tag_name: str, create_backup: bool = True) -> bool:
        """
        Rollback to a specific tag.

        Args:
            tag_name: Tag to rollback to
            create_backup: Whether to create a backup tag before rollback

        Returns:
            True if successful, False otherwise
        """
        backup_tag = None
        try:
            # Verify tag exists
            result = self._run_git_command(["tag", "-l", tag_name])
            if tag_name not in result.stdout.split("\\n"):
                print(f"❌ Tag {tag_name} does not exist")
                return False

            # Create backup if requested
            if create_backup:
                backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_tag = f"before_rollback_{backup_timestamp}"

                try:
                    self._run_git_command(["tag", backup_tag, "HEAD"])
                    print(f"✅ Created backup tag: {backup_tag}")
                except Exception as e:
                    print(f"⚠️ Failed to create backup tag: {e}")
                    backup_tag = None

            # Perform rollback
            self._run_git_command(["reset", "--hard", tag_name])
            print(f"✅ Successfully rolled back to {tag_name}")

            # Record rollback
            versions = self._load_versions()
            rollback_entry = {
                "tag": tag_name,
                "backup_tag": backup_tag if create_backup else None,
                "timestamp": datetime.now().isoformat(),
                "type": "rollback",
                "action": f"rolled_back_to_{tag_name}",
            }
            versions.append(rollback_entry)
            self._save_versions(versions)

            return True

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

    def rollback_to_previous(self, skill_name: str, create_backup: bool = True) -> bool:
        """
        Rollback to the previous version of a specific skill.

        Args:
            skill_name: Name of the skill to rollback
            create_backup: Whether to create a backup tag

        Returns:
            True if successful, False otherwise
        """
        versions = self.list_versions(skill_name)

        if len(versions) < 2:
            print(f"❌ No previous version found for {skill_name}")
            return False

        # Find the latest learning tag for this skill
        latest_version = versions[0]
        if latest_version["type"] != "learning_update":
            print(f"❌ Latest version for {skill_name} is not a learning update")
            return False

        return self.rollback_to_tag(latest_version["tag"], create_backup)

    def compare_versions(self, tag1: str, tag2: Optional[str] = None) -> str:
        """Compare two versions (defaults to comparing tag with current HEAD)."""
        try:
            if tag2 is None:
                # Compare with current HEAD
                result = self._run_git_command(
                    ["diff", tag1, "HEAD"], capture_output=False
                )
            else:
                result = self._run_git_command(
                    ["diff", tag2, tag1], capture_output=False
                )

            return result.stdout

        except Exception as e:
            return f"❌ Failed to compare versions: {e}"

    def get_skill_changes(
        self, skill_name: str, since_tag: Optional[str] = None
    ) -> List[str]:
        """Get changes for a specific skill since a given tag."""
        skill_file = f"{skill_name}/SKILL.md"

        try:
            if since_tag:
                result = self._run_git_command(
                    ["log", f"{since_tag}..HEAD", "--oneline", "--", skill_file]
                )
            else:
                result = self._run_git_command(
                    ["log", "--oneline", "-10", "--", skill_file]
                )

            return result.stdout.strip().split("\\n") if result.stdout.strip() else []

        except Exception as e:
            return [f"❌ Failed to get changes: {e}"]

    def cleanup_old_tags(self, keep_count: int = 20) -> int:
        """Clean up old learning tags, keeping only the most recent N."""
        try:
            # Get all learning tags
            result = self._run_git_command(["tag", "-l", "learning_*"])
            learning_tags = [
                tag.strip()
                for tag in result.stdout.split("\\n")
                if tag.strip().startswith("learning_")
            ]

            if len(learning_tags) <= keep_count:
                print(
                    f"✅ No cleanup needed (have {len(learning_tags)}, keeping {keep_count})"
                )
                return 0

            # Sort tags by date (newest first)
            learning_tags.sort(reverse=True)
            tags_to_delete = learning_tags[keep_count:]

            deleted_count = 0
            for tag in tags_to_delete:
                try:
                    self._run_git_command(["tag", "-d", tag])
                    deleted_count += 1
                    print(f"🗑️ Deleted old tag: {tag}")
                except Exception as e:
                    print(f"⚠️ Failed to delete tag {tag}: {e}")

            print(f"✅ Cleaned up {deleted_count} old tags")
            return deleted_count

        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return 0


def main():
    parser = argparse.ArgumentParser(
        description="Skill versioning and rollback management"
    )
    parser.add_argument(
        "command",
        choices=[
            "tag",
            "rollback",
            "rollback-previous",
            "list",
            "compare",
            "changes",
            "cleanup",
        ],
        help="Command to execute",
    )

    parser.add_argument("--skill", help="Skill name")
    parser.add_argument("--description", help="Learning description (for tag command)")
    parser.add_argument("--tag", help="Tag name (for rollback/compare)")
    parser.add_argument("--tag2", help="Second tag name (for compare)")
    parser.add_argument("--since", help="Since tag (for changes)")
    parser.add_argument("--author", default="enhanced-reflect", help="Author of change")
    parser.add_argument(
        "--no-backup", action="store_true", help="Don't create backup before rollback"
    )
    parser.add_argument(
        "--keep", type=int, default=20, help="Number of tags to keep during cleanup"
    )

    args = parser.parse_args()

    try:
        manager = SkillVersionManager()

        if args.command == "tag":
            if not args.skill or not args.description:
                print("❌ --skill and --description required for tag command")
                return 1

            tag = manager.create_learning_tag(args.skill, args.description, args.author)
            print(f"🏷️ Created tag: {tag}")

        elif args.command == "rollback":
            if not args.tag:
                print("❌ --tag required for rollback command")
                return 1

            success = manager.rollback_to_tag(args.tag, not args.no_backup)
            return 0 if success else 1

        elif args.command == "rollback-previous":
            if not args.skill:
                print("❌ --skill required for rollback-previous command")
                return 1

            success = manager.rollback_to_previous(args.skill, not args.no_backup)
            return 0 if success else 1

        elif args.command == "list":
            versions = manager.list_versions(args.skill)
            print(f"📋 Version History ({len(versions)} versions)")
            for version in versions:
                icon = "🏷️" if version["type"] == "learning_update" else "🔄"
                print(f"  {icon} {version['tag']} - {version['skill']}")
                print(f"     {version['description'][:80]}...")
                print(f"     {version['timestamp']}")
                print()

        elif args.command == "compare":
            if not args.tag:
                print("❌ --tag required for compare command")
                return 1

            diff = manager.compare_versions(args.tag, args.tag2)
            print(f"📊 Version comparison:")
            print(diff)

        elif args.command == "changes":
            if not args.skill:
                print("❌ --skill required for changes command")
                return 1

            changes = manager.get_skill_changes(args.skill, args.since)
            print(f"📝 Changes for {args.skill}:")
            for change in changes:
                if change:
                    print(f"  {change}")

        elif args.command == "cleanup":
            deleted = manager.cleanup_old_tags(args.keep)
            print(f"🧹 Cleanup complete: {deleted} tags deleted")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
