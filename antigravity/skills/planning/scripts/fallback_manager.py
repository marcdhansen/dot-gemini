#!/usr/bin/env python3
"""
Fallback Mechanism for Planning Skill
Handles conflicts with existing processes and provides graceful degradation
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class ConflictType(Enum):
    EXISTING_MANUAL_PLAN = "existing_manual_plan"
    BEADS_TASK_ONLY = "beads_task_only"
    EMERGENCY_DEVELOPMENT = "emergency_development"
    LEGACY_PROCESS_CONFLICT = "legacy_process_conflict"
    RESOURCE_CONSTRAINT = "resource_constraint"
    SYSTEM_UNAVAILABLE = "system_unavailable"


class FallbackStrategy(Enum):
    MERGE_WITH_EXISTING = "merge_with_existing"
    ENHANCE_BEADS_TASK = "enhance_beads_task"
    MINIMAL_PLANNING = "minimal_planning"
    MANUAL_PLANNING = "manual_planning"
    DEFER_TO_LATER = "defer_to_later"


class PlanningFallbackManager:
    """Manages fallback mechanisms for planning conflicts"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.agent_dir = repo_path / ".agent"
        self.fallback_file = self.agent_dir / "planning_fallbacks.json"
        self.user_preferences_file = self.agent_dir / "planning_preferences.json"

        # Ensure directories exist
        self.agent_dir.mkdir(exist_ok=True)
        (self.agent_dir / "fallback_logs").mkdir(exist_ok=True)

        # Load user preferences
        self.user_preferences = self._load_user_preferences()

    def _load_user_preferences(self) -> Dict:
        """Load user planning preferences"""
        default_preferences = {
            "auto_fallback": True,
            "preferred_strategies": {
                ConflictType.EXISTING_MANUAL_PLAN: FallbackStrategy.MERGE_WITH_EXISTING,
                ConflictType.BEADS_TASK_ONLY: FallbackStrategy.ENHANCE_BEADS_TASK,
                ConflictType.EMERGENCY_DEVELOPMENT: FallbackStrategy.MINIMAL_PLANNING,
                ConflictType.LEGACY_PROCESS_CONFLICT: FallbackStrategy.MANUAL_PLANNING,
                ConflictType.RESOURCE_CONSTRAINT: FallbackStrategy.DEFER_TO_LATER,
                ConflictType.SYSTEM_UNAVAILABLE: FallbackStrategy.MANUAL_PLANNING,
            },
            "emergency_justification_required": True,
            "fallback_logging": True,
        }

        if self.user_preferences_file.exists():
            try:
                with open(self.user_preferences_file, "r") as f:
                    loaded_prefs = json.load(f)
                # Merge with defaults
                return {**default_preferences, **loaded_prefs}
            except (json.JSONDecodeError, IOError):
                pass

        return default_preferences

    def detect_conflict_type(self, task_id: str) -> Optional[ConflictType]:
        """Detect the type of conflict for a task"""

        # Check for system unavailability first
        if self._is_system_unavailable():
            return ConflictType.SYSTEM_UNAVAILABLE

        # Check for existing manual plan
        if self._has_existing_manual_plan(task_id):
            return ConflictType.EXISTING_MANUAL_PLAN

        # Check if beads task exists but no planning
        if self._has_beads_task_only(task_id):
            return ConflictType.BEADS_TASK_ONLY

        # Check for emergency development needs
        if self._is_emergency_development(task_id):
            return ConflictType.EMERGENCY_DEVELOPMENT

        # Check for legacy process conflicts
        if self._has_legacy_process_conflict(task_id):
            return ConflictType.LEGACY_PROCESS_CONFLICT

        # Check for resource constraints
        if self._has_resource_constraints(task_id):
            return ConflictType.RESOURCE_CONSTRAINT

        return None

    def _has_existing_manual_plan(self, task_id: str) -> bool:
        """Check if there's an existing manual plan"""

        # Look for existing planning documents
        manual_plan_patterns = [
            f"{task_id}_plan.md",
            f"{task_id}_planning.md",
            f"plans/{task_id}.md",
            f".agent/plans/{task_id}_manual.json",
        ]

        for pattern in manual_plan_patterns:
            if (self.repo_path / pattern).exists():
                return True

        return False

    def _has_beads_task_only(self, task_id: str) -> bool:
        """Check if there's only a beads task without planning"""

        # Check if beads task exists
        try:
            result = subprocess.run(
                ["bd", "show", task_id, "--json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Check if planning scope exists
                scope_file = self.agent_dir / "plans" / f"{task_id}_scope.json"
                if not scope_file.exists():
                    return True

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            pass

        return False

    def _is_emergency_development(self, task_id: str) -> bool:
        """Check if this is an emergency development situation"""

        # Check task priority and keywords
        try:
            result = subprocess.run(
                ["bd", "show", task_id, "--json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                task_data = json.loads(result.stdout)

                # Check for emergency indicators
                emergency_indicators = [
                    task_data.get("priority") == "P0",
                    "emergency" in task_data.get("title", "").lower(),
                    "critical" in task_data.get("title", "").lower(),
                    "production" in task_data.get("title", "").lower()
                    and "down" in task_data.get("title", "").lower(),
                    "hotfix" in task_data.get("tags", []),
                    "urgent" in task_data.get("tags", []),
                ]

                return any(emergency_indicators)

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            FileNotFoundError,
        ):
            pass

        return False

    def _has_legacy_process_conflict(self, task_id: str) -> bool:
        """Check for conflicts with existing processes"""

        # Look for legacy process indicators
        legacy_indicators = [
            (self.repo_path / "legacy_planning").exists(),
            (self.repo_path / ".legacy_workflow").exists(),
            (self.agent_dir / "legacy_process.txt").exists(),
        ]

        return any(legacy_indicators)

    def _has_resource_constraints(self, task_id: str) -> bool:
        """Check if there are resource constraints"""

        # Simple check - look for active development sessions
        session_files = list(self.agent_dir.glob("session_locks/*.json"))

        # If many agents are active, resources might be constrained
        return len(session_files) > 5  # Arbitrary threshold

    def _is_system_unavailable(self) -> bool:
        """Check if the planning system is unavailable"""

        # Check if key components are available
        checks = [
            self._check_beads_available(),
            self._check_git_available(),
            self._check_disk_space_available(),
        ]

        return not all(checks)

    def _check_beads_available(self) -> bool:
        """Check if beads command is available"""
        try:
            result = subprocess.run(
                ["bd", "--version"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            return False

    def _check_git_available(self) -> bool:
        """Check if git command is available"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            return False

    def _check_disk_space_available(self) -> bool:
        """Check if disk space is available"""
        try:
            disk_usage = os.statvfs(self.repo_path)
            free_space_mb = (disk_usage.f_frsize * disk_usage.f_bavail) / (1024**2)
            return free_space_mb > 100  # Need at least 100MB
        except Exception:
            return False

    def get_fallback_summary(self) -> Dict:
        """Get summary of fallback activity"""

        log_file = self.agent_dir / "fallback_logs" / "fallback_log.jsonl"

        if not log_file.exists():
            return {"total_conflicts": 0, "resolutions": {}}

        conflicts = []
        resolutions = {}

        with open(log_file, "r") as f:
            for line in f:
                entry = json.loads(line.strip())
                conflicts.append(entry)

                if entry.get("type") == "conflict_resolved":
                    strategy = entry.get("strategy_used")
                    resolutions[strategy] = resolutions.get(strategy, 0) + 1

        return {
            "total_conflicts": len(
                [c for c in conflicts if c.get("type") == "conflict_detected"]
            ),
            "total_resolutions": len(resolutions),
            "resolutions_by_strategy": resolutions,
            "recent_conflicts": conflicts[-10:],  # Last 10 conflicts
        }


def main():
    """Main entry point for fallback mechanism"""
    if len(sys.argv) < 2:
        print("Usage: python fallback_manager.py <command> [options]")
        print("Commands:")
        print("  detect <task_id>                # Detect conflict type")
        print("  resolve <task_id> [strategy]     # Resolve conflict")
        print("  summary                         # Show fallback summary")
        print("  preferences                     # Show user preferences")
        sys.exit(1)

    command = sys.argv[1]
    repo_path = Path.cwd()

    try:
        fallback = PlanningFallbackManager(repo_path)
    except Exception as e:
        print(f"❌ Error initializing fallback manager: {e}")
        sys.exit(1)

    if command == "detect":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)

        task_id = sys.argv[2]
        conflict_type = fallback.detect_conflict_type(task_id)

        if conflict_type:
            print(f"Conflict detected: {conflict_type.value}")
        else:
            print("No conflicts detected")

    elif command == "resolve":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)

        task_id = sys.argv[2]
        strategy = None

        if len(sys.argv) > 3:
            try:
                strategy = FallbackStrategy(sys.argv[3])
            except ValueError:
                print(f"Invalid strategy: {sys.argv[3]}")
                sys.exit(1)

        conflict_type = fallback.detect_conflict_type(task_id)

        if not conflict_type:
            print("No conflicts detected to resolve")
            sys.exit(1)

        print(
            f"Would resolve {conflict_type.value} using {strategy.value if strategy else 'default'}"
        )

    elif command == "summary":
        summary = fallback.get_fallback_summary()

        print("Fallback Mechanism Summary:")
        print(f"  Total Conflicts: {summary['total_conflicts']}")
        print(f"  Total Resolutions: {summary.get('total_resolutions', 0)}")
        print("  Resolutions by Strategy:")
        for strategy, count in summary.get("resolutions_by_strategy", {}).items():
            print(f"    {strategy}: {count}")

    elif command == "preferences":
        import json

        print(json.dumps(fallback.user_preferences, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
