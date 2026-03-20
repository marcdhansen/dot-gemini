#!/usr/bin/env python3
"""
SOP Consistency Validator

Validates cross-agent SOP compliance across .agent, .gemini, .config, .antigravity directories.
Intended to be run during Return-to-Base (RTB) process to ensure consistency.

Usage:
    python ~/.agent/scripts/validate_sop_consistency.py [--project-dir /path/to/project]

Exit codes:
    0: All checks passed
    1: Warnings found (non-blocking)
    2: Errors found (blocking)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import subprocess
import re


class SOPValidator:
    """Validates SOP consistency across agent directories."""

    def __init__(self, project_dir: Path | None = None):
        self.project_dir = Path.cwd() if project_dir is None else Path(project_dir)
        self.home_dir = Path.home()
        self.errors = []
        self.warnings = []

        # Directory structure expectations
        self.global_agent_dir = self.home_dir / ".agent"
        self.global_gemini_dir = self.home_dir / ".gemini"
        self.global_antigravity_dir = self.home_dir / ".antigravity"
        self.project_agent_dir = self.project_dir / ".agent"

    def log_error(self, message: str):
        """Record an error (blocking)."""
        self.errors.append(f"❌ ERROR: {message}")

    def log_warning(self, message: str):
        """Record a warning (non-blocking)."""
        self.warnings.append(f"⚠️  WARNING: {message}")

    def log_info(self, message: str):
        """Record informational message."""
        print(f"ℹ️  INFO: {message}")

    def check_global_directories_exist(self) -> bool:
        """Verify global directories exist and are accessible."""
        self.log_info("Checking global directory structure...")

        required_dirs = [
            (self.global_agent_dir, "Global agent standards"),
            (self.global_gemini_dir, "Gemini-specific configs"),
            (self.global_antigravity_dir, "Global workflows/skills"),
        ]

        all_exist = True
        for dir_path, description in required_dirs:
            if not dir_path.exists():
                self.log_error(f"Missing {description}: {dir_path}")
                all_exist = False
            elif not dir_path.is_dir():
                self.log_error(f"Not a directory - {description}: {dir_path}")
                all_exist = False
            else:
                self.log_info(f"✓ Found {description}: {dir_path}")

        return all_exist

    def check_project_structure(self) -> bool:
        """Verify project-specific .agent directory structure."""
        self.log_info("Checking project directory structure...")

        if not self.project_agent_dir.exists():
            self.log_warning(
                f"No project .agent directory found: {self.project_agent_dir}"
            )
            return True  # Not blocking - some projects may not have it

        # Expected subdirectories
        expected_subdirs = ["rules", "skills", "docs", "scripts", "session_locks"]

        for subdir in expected_subdirs:
            subdir_path = self.project_agent_dir / subdir
            if subdir_path.exists():
                self.log_info(f"✓ Found project subdir: {subdir_path}")
            else:
                self.log_warning(f"Missing expected project subdir: {subdir_path}")

        return True

    def check_symlink_integrity(self) -> bool:
        """Validate symlinks between global and project directories."""
        self.log_info("Checking symlink integrity...")

        if not self.project_agent_dir.exists():
            self.log_info("No project .agent directory - skipping symlink checks")
            return True

        # Common expected symlinks
        expected_links = [
            ("docs/sop/global-configs", self.global_agent_dir / "docs"),
            ("docs/sop/skills", self.project_agent_dir / "skills"),
            ("BOOTSTRAP.md", self.global_gemini_dir / "AGENT_ONBOARDING.md"),
        ]

        broken_links = []
        for link_path, target_path in expected_links:
            full_link_path = self.project_agent_dir / link_path

            if full_link_path.exists() and full_link_path.is_symlink():
                if not full_link_path.resolve().exists():
                    broken_links.append(f"{link_path} -> {target_path}")
                    self.log_error(f"Broken symlink: {link_path} -> {target_path}")
                else:
                    self.log_info(f"✓ Valid symlink: {link_path}")
            elif full_link_path.is_symlink():
                # Symlink exists but target doesn't
                broken_links.append(f"{link_path} -> {target_path}")
                self.log_error(f"Broken symlink: {link_path} -> {target_path}")
            else:
                self.log_warning(f"Missing expected symlink: {link_path}")

        # Check for circular symlinks
        if self.global_gemini_dir / ".gemini" in Path(self.global_gemini_dir).rglob(
            "*"
        ):
            self.log_error("Circular symlink detected: ~/.gemini/.gemini")

        return len(broken_links) == 0

    def check_file_consistency(self) -> bool:
        """Check consistency of key files across directories."""
        self.log_info("Checking file consistency...")

        consistency_issues = []

        # Check AGENTS.md exists and is accessible
        agents_md = self.global_agent_dir / "AGENTS.md"
        if not agents_md.exists():
            self.log_error("Missing universal entry point: ~/.agent/AGENTS.md")
        else:
            self.log_info("✓ Found universal entry point: ~/.agent/AGENTS.md")

        # Check GLOBAL_INDEX.md consistency
        global_index_candidates = [
            self.global_agent_dir / "docs" / "GLOBAL_INDEX.md",
            self.global_gemini_dir / "GLOBAL_INDEX.md",
        ]

        found_indices = [p for p in global_index_candidates if p.exists()]
        if len(found_indices) > 1:
            self.log_warning(f"Multiple GLOBAL_INDEX.md files found: {found_indices}")
        elif len(found_indices) == 0:
            self.log_error("No GLOBAL_INDEX.md found in expected locations")
        else:
            self.log_info(f"✓ Found GLOBAL_INDEX.md: {found_indices[0]}")

        return len(consistency_issues) == 0

    def check_git_status(self) -> bool:
        """Check git status of global directories."""
        self.log_info("Checking git status of global directories...")

        directories_to_check = [self.global_agent_dir, self.global_gemini_dir]

        for directory in directories_to_check:
            if not directory.exists():
                continue

            try:
                os.chdir(directory)
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.stdout.strip():
                    self.log_warning(f"Uncommitted changes in {directory}:")
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            self.log_warning(f"  {line}")
                else:
                    self.log_info(f"✓ No uncommitted changes in {directory}")

            except subprocess.TimeoutExpired:
                self.log_warning(f"Git status timeout for {directory}")
            except Exception as e:
                self.log_warning(f"Could not check git status for {directory}: {e}")
            finally:
                os.chdir(self.project_dir)

        return True

    def check_markdown_linting(self) -> bool:
        """Run markdown linting on key documentation files."""
        self.log_info("Checking markdown quality...")

        try:
            # Check if markdownlint is available
            result = subprocess.run(
                ["markdownlint", "--version"], capture_output=True, text=True, timeout=5
            )

            if result.returncode != 0:
                self.log_warning(
                    "markdownlint not available - skipping markdown checks"
                )
                return True

        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log_warning("markdownlint not available - skipping markdown checks")
            return True

        # Files to check
        files_to_check = []

        # Global files
        global_files = [
            self.global_agent_dir / "AGENTS.md",
            self.global_agent_dir / "docs" / "GLOBAL_INDEX.md"
            if (self.global_agent_dir / "docs").exists()
            else None,
            self.global_gemini_dir / "AGENT_ONBOARDING.md",
            self.global_gemini_dir / "GEMINI.md",
        ]

        # Project files
        if self.project_agent_dir.exists():
            project_files = [
                self.project_agent_dir / "rules" / "ROADMAP.md",
                self.project_agent_dir / "rules" / "ImplementationPlan.md",
                self.project_agent_dir / "SESSION.md",
            ]
            files_to_check.extend([f for f in project_files if f and f.exists()])

        files_to_check.extend([f for f in global_files if f and f.exists()])

        lint_errors = []
        for file_path in files_to_check:
            if not file_path.exists():
                continue

            try:
                result = subprocess.run(
                    ["markdownlint", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    self.log_warning(f"Markdown issues in {file_path.name}:")
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            self.log_warning(f"  {line}")
                    lint_errors.append(file_path.name)
                else:
                    self.log_info(f"✓ Markdown OK: {file_path.name}")

            except subprocess.TimeoutExpired:
                self.log_warning(f"Markdown lint timeout for {file_path}")
            except Exception as e:
                self.log_warning(f"Could not lint {file_path}: {e}")

        return len(lint_errors) == 0

    def check_file_placement_consistency(self) -> bool:
        """Check that files are in correct directories per SOP."""
        self.log_info("Checking file placement consistency...")

        # Files that should be in ~/.agent (global)
        expected_in_global_agent = {
            "AGENTS.md": "Universal entry point",
            "GLOBAL_INDEX.md": "Global navigation (should be in docs/)",
            "CROSS_COMPATIBILITY.md": "Cross-agent design principles",
            "HOW_TO_USE_BEADS.md": "Beads task management guide",
            "MISSION_NOMENCLATURE.md": "Universal terminology",
            "SELF_EVOLUTION_GLOBAL.md": "Global learning strategy",
        }

        # Files that should be in ~/.gemini (provider-specific)
        expected_in_gemini = {
            "AGENT_ONBOARDING.md": "Gemini-specific onboarding",
            "GEMINI.md": "Gemini-specific configuration",
            "google_accounts.json": "Gemini authentication",
        }

        placement_issues = []

        # Check global agent directory
        for filename, description in expected_in_global_agent.items():
            # Allow for GLOBAL_INDEX.md to be in docs/ subdirectory
            if filename == "GLOBAL_INDEX.md":
                locations = [
                    self.global_agent_dir / filename,
                    self.global_agent_dir / "docs" / filename,
                ]
            else:
                # Allow SOP files to be in docs/sop/ subdirectory
                if filename in [
                    "CROSS_COMPATIBILITY.md",
                    "HOW_TO_USE_BEADS.md",
                    "MISSION_NOMENCLATURE.md",
                    "SELF_EVOLUTION_GLOBAL.md",
                ]:
                    locations = [
                        self.global_agent_dir / filename,
                        self.global_agent_dir / "docs" / filename,
                        self.global_agent_dir / "docs" / "sop" / filename,
                    ]
                else:
                    locations = [self.global_agent_dir / filename]

            if not any(loc.exists() for loc in locations):
                self.log_error(f"Missing {description}: {filename} in ~/.agent/")

        # Check global workflow files in docs/sop/
        expected_global_workflows = {
            "tdd-workflow.md": "Universal TDD workflow",
        }

        for filename, description in expected_global_workflows.items():
            workflow_path = self.global_agent_dir / "docs" / "sop" / filename
            if not workflow_path.exists():
                self.log_error(f"Missing {description}: docs/sop/{filename}")

        # Check global skills directory
        expected_global_skills = [
            "flight-director",
            "reflect",
            "librarian",
            "quality-analyst",
            "javascript",
            "coding-standards",
        ]

        for skill_name in expected_global_skills:
            skill_path = self.global_agent_dir / "skills" / skill_name
            if not skill_path.exists():
                self.log_error(
                    f"Missing global skill: {skill_name} in ~/.agent/skills/"
                )

        # Check gemini directory (provider-specific only)
        for filename, description in expected_in_gemini.items():
            if not (self.global_gemini_dir / filename).exists():
                self.log_warning(f"Missing {description}: {filename} in ~/.gemini/")

        # Check for other provider directories that shouldn't contain universal files
        provider_dirs = [
            (Path.home() / ".config" / "opencode", "Provider-specific configs"),
            (Path.home() / ".claude", "Claude-specific configs"),
        ]

        for provider_dir, description in provider_dirs:
            if provider_dir.exists():
                # Check for incorrectly placed universal files
                for universal_file in [
                    "CROSS_COMPATIBILITY.md",
                    "GLOBAL_INDEX.md",
                    "HOW_TO_USE_BEADS.md",
                ]:
                    if (provider_dir / universal_file).exists():
                        self.log_error(
                            f"Universal file found in wrong provider dir: {description}/{universal_file}"
                        )

                # Check for incorrectly placed global skills
                skills_dir = provider_dir / "skills"
                if skills_dir.exists():
                    for universal_skill in [
                        "flight-director",
                        "reflect",
                        "librarian",
                        "quality-analyst",
                        "javascript",
                        "coding-standards",
                    ]:
                        if (skills_dir / universal_skill).exists():
                            self.log_error(
                                f"Universal skill found in wrong provider dir: {description}/{universal_skill}"
                            )

        return len(placement_issues) == 0

    def validate_all(self) -> Tuple[int, List[str], List[str]]:
        """Run all validation checks."""
        self.log_info(
            f"Starting SOP consistency validation for project: {self.project_dir}"
        )
        print("=" * 60)

        # Run all checks
        checks = [
            self.check_global_directories_exist,
            self.check_project_structure,
            self.check_symlink_integrity,
            self.check_file_consistency,
            self.check_file_placement_consistency,
            self.check_git_status,
            self.check_markdown_linting,
        ]

        for check in checks:
            try:
                check()
                print("-" * 40)
            except Exception as e:
                self.log_error(f"Validation check failed: {e}")
                print("-" * 40)

        # Determine exit code
        exit_code = 0
        if self.errors:
            exit_code = 2
        elif self.warnings:
            exit_code = 1

        return exit_code, self.errors, self.warnings

    def print_summary(self):
        """Print validation summary."""
        print("=" * 60)
        print("SOP CONSISTENCY VALIDATION SUMMARY")
        print("=" * 60)

        if self.errors:
            print(f"\n🚨 BLOCKING ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ ALL CHECKS PASSED - SOP consistency verified!")

        print(f"\nExit code: {self.get_exit_code()}")

    def get_exit_code(self) -> int:
        """Get appropriate exit code based on results."""
        if self.errors:
            return 2
        elif self.warnings:
            return 1
        else:
            return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate SOP consistency")
    parser.add_argument(
        "--project-dir",
        type=str,
        default=None,
        help="Path to project directory (default: current directory)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    validator = SOPValidator(project_dir if project_dir else Path.cwd())

    exit_code, errors, warnings = validator.validate_all()
    validator.print_summary()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
