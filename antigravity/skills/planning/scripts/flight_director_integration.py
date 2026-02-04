#!/usr/bin/env python3
"""
Flight Director Integration for Planning Skill
Provides post-task-selection planning prompts and workflow integration
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add the planning skill to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.blast_radius_analyzer import ChangeDetector, AnalysisLevel


class FlightDirectorPlanningIntegration:
    """Integration with Flight Director for post-task-selection planning"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.agent_dir = repo_path / ".agent"
        self.session_file = self.agent_dir / "session_state.json"
        self.planning_prompts_file = self.agent_dir / "planning_prompts.json"

    def detect_task_selection_and_prompt_planning(self) -> bool:
        """Detect when agent selects a task and prompt for planning"""

        # Check if we have a selected task that needs planning
        selected_task = self._get_selected_task()

        if selected_task and not self._has_planning_scope(selected_task):
            return self._prompt_for_planning(selected_task)

        return False

    def _get_selected_task(self) -> Optional[str]:
        """Get the currently selected task"""
        # Try to read from session state
        if self.session_file.exists():
            try:
                with open(self.session_file, "r") as f:
                    session_data = json.load(f)
                return session_data.get("selected_task")
            except (json.JSONDecodeError, KeyError):
                pass

        # Try to detect from git branch
        git_branch = self._get_current_git_branch()
        if git_branch and "task/" in git_branch:
            # Extract task ID from branch name
            task_match = re.search(r"(lightrag-[a-zA-Z0-9]+)", git_branch)
            if task_match:
                return task_match.group(1)

        return None

    def _has_planning_scope(self, task_id: str) -> bool:
        """Check if task has been scoped for planning"""
        planning_file = self.agent_dir / "plans" / f"{task_id}_scope.json"
        return planning_file.exists()

    def _prompt_for_planning(self, task_id: str) -> bool:
        """Display planning prompt to user"""

        print("\n" + "=" * 60)
        print("🎯 TASK SELECTED - PLANNING REQUIRED")
        print("=" * 60)
        print(f"📋 Selected Task: {task_id}")
        print()
        print("🚀 RECOMMENDED NEXT STEP:")
        print(f"   /plan scope {task_id}")
        print()
        print("📊 This will:")
        print("   • Analyze blast radius and impact")
        print("   • Create implementation milestones")
        print("   • Generate risk assessment")
        print("   • Recommend development approach")
        print()
        print("⚡ OPTIONS:")
        print(f"   /plan scope {task_id}     # Scope the task")
        print(f"   /plan analyze {task_id}    # Detailed analysis")
        print(f"   /next                     # Choose different task")
        print()
        print("💡 After scoping, you can choose to:")
        print("   • Proceed with implementation")
        print("   • Table the task with saved scoping")
        print("   • Modify the plan as needed")
        print("=" * 60)

        return True

    def _get_current_git_branch(self) -> Optional[str]:
        """Get current git branch name"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            pass

        return None

    def create_task_scope(
        self,
        task_id: str,
        changed_files: List[str],
        analysis_level: AnalysisLevel = AnalysisLevel.DETAILED,
    ) -> Dict:
        """Create planning scope for a task"""

        # Run blast radius analysis
        detector = ChangeDetector(self.repo_path)
        analysis_result = detector.analyze_changes(changed_files, analysis_level)

        # Get task details from beads
        task_details = self._get_task_details(task_id)

        # Create scope document
        scope = {
            "task_id": task_id,
            "created_at": datetime.now().isoformat(),
            "task_details": task_details,
            "blast_radius_analysis": analysis_result,
            "changed_files": changed_files,
            "analysis_level": analysis_level.value,
            "planning_status": "scoped",
        }

        # Save scope to file
        plans_dir = self.agent_dir / "plans"
        plans_dir.mkdir(exist_ok=True)

        scope_file = plans_dir / f"{task_id}_scope.json"
        with open(scope_file, "w") as f:
            json.dump(scope, f, indent=2, default=str)

        return scope

    def _get_task_details(self, task_id: str) -> Dict:
        """Get task details from beads"""
        try:
            # Try to get task details from beads
            result = subprocess.run(
                ["bd", "show", task_id, "--json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            FileNotFoundError,
        ):
            pass

        # Fallback basic details
        return {
            "id": task_id,
            "title": f"Task {task_id}",
            "status": "unknown",
            "priority": "unknown",
        }

    def recommend_tasks_from_scope(self, task_id: str) -> List[Dict]:
        """Create task recommendations based on planning scope"""

        scope_file = self.agent_dir / "plans" / f"{task_id}_scope.json"
        if not scope_file.exists():
            return []

        with open(scope_file, "r") as f:
            scope = json.load(f)

        blast_analysis = scope["blast_radius_analysis"]
        recommendations = []

        # Create tasks based on blast radius analysis
        if blast_analysis["summary"]:
            summary = blast_analysis["summary"]

            # Testing task
            if summary["estimated_testing_effort"] != "NONE":
                test_task = {
                    "title": f"Add test coverage for {task_id}",
                    "description": f"Create comprehensive tests for {scope['task_details']['title']}",
                    "priority": "P2"
                    if summary["risk_level"] in ["HIGH", "CRITICAL"]
                    else "P3",
                    "type": "task",
                    "estimate": self._estimate_test_effort(
                        summary["estimated_testing_effort"]
                    ),
                    "dependencies": [task_id],
                }
                recommendations.append(test_task)

            # Documentation task
            if any("api" in f for f in scope["changed_files"]):
                doc_task = {
                    "title": f"Update documentation for {task_id}",
                    "description": f"Update API documentation and examples for {scope['task_details']['title']}",
                    "priority": "P3",
                    "type": "task",
                    "estimate": "2-4 hours",
                    "dependencies": [task_id],
                }
                recommendations.append(doc_task)

            # Migration task
            if (
                blast_analysis["detailed"]
                and blast_analysis["detailed"]["migration_requirements"]
            ):
                migration_task = {
                    "title": f"Database migration for {task_id}",
                    "description": f"Create and test migration scripts for {scope['task_details']['title']}",
                    "priority": "P1",
                    "type": "task",
                    "estimate": "4-8 hours",
                    "dependencies": [task_id],
                }
                recommendations.append(migration_task)

        # Risk mitigation tasks
        if summary["risk_level"] == "CRITICAL":
            risk_task = {
                "title": f"Risk mitigation planning for {task_id}",
                "description": f"Create detailed risk mitigation and rollback plan for {scope['task_details']['title']}",
                "priority": "P0",
                "type": "task",
                "estimate": "4-6 hours",
                "dependencies": [task_id],
            }
            recommendations.append(risk_task)

        return recommendations

    def _estimate_test_effort(self, testing_effort: str) -> str:
        """Convert testing effort description to estimate"""
        effort_map = {
            "2-4 hours": "2-4 hours",
            "1-2 days": "1-2 days",
            "2-4 days": "2-3 days",
            "3-5 days": "3-4 days",
        }
        return effort_map.get(testing_effort, "2-4 hours")

    def create_implementation_plan(
        self, task_id: str, user_approvals: List[str]
    ) -> Dict:
        """Create implementation plan from scope with user-approved tasks"""

        scope_file = self.agent_dir / "plans" / f"{task_id}_scope.json"
        if not scope_file.exists():
            raise ValueError(f"No planning scope found for {task_id}")

        with open(scope_file, "r") as f:
            scope = json.load(f)

        # Get recommended tasks
        all_recommendations = self.recommend_tasks_from_scope(task_id)

        # Filter by user approvals
        approved_tasks = []
        for rec in all_recommendations:
            if rec["title"] in user_approvals:
                approved_tasks.append(rec)

        # Create implementation plan with milestones
        plan = {
            "task_id": task_id,
            "created_at": datetime.now().isoformat(),
            "original_scope": scope,
            "approved_tasks": approved_tasks,
            "milestones": self._create_milestones(scope, approved_tasks),
            "plan_status": "approved",
        }

        # Save implementation plan
        plans_dir = self.agent_dir / "plans"
        plan_file = plans_dir / f"{task_id}_implementation.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2, default=str)

        # Update session state
        self._update_session_state(task_id, "planned")

        return plan

    def _create_milestones(self, scope: Dict, approved_tasks: List[Dict]) -> List[Dict]:
        """Create implementation milestones"""
        milestones = []

        # Milestone 1: Core Development
        core_milestone = {
            "name": "Core Development",
            "description": f"Implement core functionality for {scope['task_details']['title']}",
            "success_criteria": [
                "All core functions implemented",
                "Unit tests passing with >80% coverage",
                "Code review completed",
            ],
            "estimated_duration": self._estimate_core_duration(scope),
            "blocking": True,
        }
        milestones.append(core_milestone)

        # Milestone 2: Integration
        if scope["blast_radius_analysis"]["summary"]["deployment_impact"] != "NONE":
            integration_milestone = {
                "name": "Integration Testing",
                "description": "Test integration with existing systems",
                "success_criteria": [
                    "All integration tests passing",
                    "API compatibility verified",
                    "No breaking changes detected",
                ],
                "estimated_duration": "1-2 days",
                "blocking": True,
            }
            milestones.append(integration_milestone)

        # Milestone 3: Additional Tasks
        if approved_tasks:
            additional_milestone = {
                "name": "Additional Requirements",
                "description": "Complete approved additional tasks",
                "success_criteria": [
                    f"All {len(approved_tasks)} approved tasks completed",
                    "Documentation updated",
                    "Final validation completed",
                ],
                "estimated_duration": self._estimate_additional_duration(
                    approved_tasks
                ),
                "blocking": True,
            }
            milestones.append(additional_milestone)

        return milestones

    def _estimate_core_duration(self, scope: Dict) -> str:
        """Estimate duration for core development"""
        risk_level = scope["blast_radius_analysis"]["summary"]["risk_level"]
        file_count = len(scope["changed_files"])

        if risk_level == "CRITICAL" or file_count > 10:
            return "5-7 days"
        elif risk_level == "HIGH" or file_count > 5:
            return "3-5 days"
        elif file_count > 2:
            return "2-3 days"
        else:
            return "1-2 days"

    def _estimate_additional_duration(self, approved_tasks: List[Dict]) -> str:
        """Estimate duration for additional tasks"""
        total_hours = 0

        for task in approved_tasks:
            estimate = task.get("estimate", "2-4 hours")
            # Extract numeric range and take average
            if "-" in estimate:
                try:
                    start, end = estimate.split("-")
                    start_num = int("".join(filter(str.isdigit, start)))
                    end_num = int("".join(filter(str.isdigit, end)))
                    total_hours += (start_num + end_num) / 2
                except (ValueError, AttributeError):
                    total_hours += 4  # Default
            else:
                total_hours += 4

        days = total_hours / 8  # Convert to workdays
        if days <= 1:
            return "1 day"
        elif days <= 3:
            return "2-3 days"
        else:
            return f"{int(days)} days"

    def _update_session_state(self, task_id: str, status: str):
        """Update session state with planning status"""
        session_data = {
            "selected_task": task_id,
            "planning_status": status,
            "updated_at": datetime.now().isoformat(),
        }

        with open(self.session_file, "w") as f:
            json.dump(session_data, f, indent=2)

    def table_task_with_scoping(self, task_id: str, reason: str = "") -> Dict:
        """Save scoping information and table the task for later"""

        scope_file = self.agent_dir / "plans" / f"{task_id}_scope.json"
        if not scope_file.exists():
            raise ValueError(f"No planning scope found for {task_id}")

        # Load existing scope
        with open(scope_file, "r") as f:
            scope = json.load(f)

        # Mark as tabled
        scope["planning_status"] = "tabled"
        scope["tabled_at"] = datetime.now().isoformat()
        scope["tabled_reason"] = reason

        # Save updated scope
        with open(scope_file, "w") as f:
            json.dump(scope, f, indent=2, default=str)

        # Create tabled summary
        summary = {
            "task_id": task_id,
            "status": "tabled",
            "reason": reason,
            "blast_radius_summary": scope["blast_radius_analysis"]["summary"],
            "recommendations": scope["blast_radius_analysis"]["recommendations"],
            "tabled_at": scope["tabled_at"],
        }

        # Save to tabled tasks list
        tabled_file = self.agent_dir / "plans" / "tabled_tasks.json"
        tabled_tasks = []

        if tabled_file.exists():
            with open(tabled_file, "r") as f:
                tabled_tasks = json.load(f)

        tabled_tasks.append(summary)

        with open(tabled_file, "w") as f:
            json.dump(tabled_tasks, f, indent=2, default=str)

        # Clear session state
        if self.session_file.exists():
            self.session_file.unlink()

        return summary

    def check_milestone_completion(self, task_id: str) -> Dict:
        """Check completion status of implementation milestones"""

        plan_file = self.agent_dir / "plans" / f"{task_id}_implementation.json"
        if not plan_file.exists():
            return {"status": "no_plan", "milestones": []}

        with open(plan_file, "r") as f:
            plan = json.load(f)

        milestones = plan.get("milestones", [])
        completed_milestones = []
        blocked_milestones = []

        for milestone in milestones:
            if self._is_milestone_completed(milestone):
                completed_milestones.append(milestone["name"])
            elif milestone.get("blocking", True):
                blocked_milestones.append(milestone["name"])

        return {
            "status": "completed"
            if len(completed_milestones) == len(milestones)
            else "in_progress",
            "completed_milestones": completed_milestones,
            "blocked_milestones": blocked_milestones,
            "total_milestones": len(milestones),
            "progress_percentage": (len(completed_milestones) / len(milestones)) * 100
            if milestones
            else 0,
        }

    def _is_milestone_completed(self, milestone: Dict) -> bool:
        """Check if a milestone is completed"""
        # This would integrate with actual completion tracking
        # For now, check if completion file exists
        milestone_id = milestone["name"].lower().replace(" ", "_")
        completion_file = (
            self.agent_dir / "milestones" / f"{milestone_id}_completed.json"
        )
        return completion_file.exists()


def main():
    """Main entry point for Flight Director integration"""
    if len(sys.argv) < 2:
        print("Usage: python flight_director_integration.py <command> [options]")
        print("Commands:")
        print("  check-task-selection    # Check for selected task and prompt planning")
        print("  create-scope <task_id> <files>")
        print("  recommend-tasks <task_id>")
        print("  create-plan <task_id> <task1,task2,...>")
        print("  table-task <task_id> [reason]")
        print("  check-milestones <task_id>")
        sys.exit(1)

    command = sys.argv[1]
    repo_path = Path.cwd()
    integration = FlightDirectorPlanningIntegration(repo_path)

    if command == "check-task-selection":
        prompted = integration.detect_task_selection_and_prompt_planning()
        sys.exit(0 if prompted else 1)

    elif command == "create-scope":
        if len(sys.argv) < 4:
            print("Error: Please provide task_id and comma-separated files")
            sys.exit(1)

        task_id = sys.argv[2]
        files = sys.argv[3].split(",")
        scope = integration.create_task_scope(task_id, files)

        print(f"✅ Planning scope created for {task_id}")
        print(
            f"📊 Risk Level: {scope['blast_radius_analysis']['summary']['risk_level']}"
        )
        print(f"📁 Files Affected: {len(files)}")

    elif command == "recommend-tasks":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)

        task_id = sys.argv[2]
        recommendations = integration.recommend_tasks_from_scope(task_id)

        print(f"📋 Recommended tasks for {task_id}:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['title']} ({rec['priority']})")
            print(f"     {rec['description']}")
            print(f"     Estimate: {rec['estimate']}")
            print()

    elif command == "create-plan":
        if len(sys.argv) < 4:
            print(
                "Error: Please provide task_id and comma-separated approved task titles"
            )
            sys.exit(1)

        task_id = sys.argv[2]
        approved_tasks = sys.argv[3].split(",")
        plan = integration.create_implementation_plan(task_id, approved_tasks)

        print(f"✅ Implementation plan created for {task_id}")
        print(f"🎯 Milestones: {len(plan['milestones'])}")
        print(f"📋 Approved Tasks: {len(plan['approved_tasks'])}")

    elif command == "table-task":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)

        task_id = sys.argv[2]
        reason = (
            sys.argv[3] if len(sys.argv) > 3 else "Deferred for later consideration"
        )

        summary = integration.table_task_with_scoping(task_id, reason)
        print(f"📋 Task {task_id} tabled with scoping saved")
        print(f"📊 Risk Level: {summary['blast_radius_summary']['risk_level']}")
        print(f"💭 Reason: {reason}")

    elif command == "check-milestones":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)

        task_id = sys.argv[2]
        status = integration.check_milestone_completion(task_id)

        print(f"🎯 Milestone Status for {task_id}:")
        print(f"📊 Overall Status: {status['status']}")
        print(f"📈 Progress: {status['progress_percentage']:.1f}%")
        print(f"✅ Completed: {', '.join(status['completed_milestones'])}")
        if status["blocked_milestones"]:
            print(f"🚫 Blocked: {', '.join(status['blocked_milestones'])}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    # Add missing import
    import subprocess

    main()
