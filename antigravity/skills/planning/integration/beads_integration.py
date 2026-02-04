#!/usr/bin/env python3
"""
Beads Integration for Planning Skill
Provides task recommendation and creation with user approval workflow
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BeadsIntegration:
    """Integration with Beads task management system"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.agent_dir = repo_path / ".agent"
        self.beads_integration_file = self.agent_dir / "beads_integration.json"

        # Ensure beads is available
        if not self._check_beads_available():
            raise RuntimeError("Beads command 'bd' is not available")

    def _check_beads_available(self) -> bool:
        """Check if beads command is available"""
        try:
            result = subprocess.run(
                ["bd", "--version"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            return False

    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """Get detailed information about a specific task"""
        try:
            result = subprocess.run(
                ["bd", "show", task_id, "--json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return None

        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            FileNotFoundError,
        ):
            return None

    def recommend_tasks_from_planning(self, planning_scope: Dict) -> List[Dict]:
        """Generate task recommendations based on planning scope"""

        recommendations = []
        task_id = planning_scope.get("task_id", "unknown")

        # Extract blast radius analysis
        blast_analysis = planning_scope.get("blast_radius_analysis", {})
        summary = blast_analysis.get("summary", {})
        detailed = blast_analysis.get("detailed", {})

        # Generate testing task recommendation
        testing_rec = self._create_testing_recommendation(task_id, planning_scope)
        if testing_rec:
            recommendations.append(testing_rec)

        # Generate documentation task recommendation
        doc_rec = self._create_documentation_recommendation(task_id, planning_scope)
        if doc_rec:
            recommendations.append(doc_rec)

        # Generate migration task recommendation
        migration_rec = self._create_migration_recommendation(task_id, planning_scope)
        if migration_rec:
            recommendations.append(migration_rec)

        # Generate risk mitigation recommendation
        risk_rec = self._create_risk_recommendation(task_id, planning_scope)
        if risk_rec:
            recommendations.append(risk_rec)

        # Generate performance testing recommendation
        perf_rec = self._create_performance_recommendation(task_id, planning_scope)
        if perf_rec:
            recommendations.append(perf_rec)

        # Generate security review recommendation
        security_rec = self._create_security_recommendation(task_id, planning_scope)
        if security_rec:
            recommendations.append(security_rec)

        return recommendations

    def _create_testing_recommendation(
        self, task_id: str, scope: Dict
    ) -> Optional[Dict]:
        """Create testing task recommendation"""

        changed_files = scope.get("changed_files", [])

        # Check if there are actual code changes
        has_code_changes = any(f.endswith(".py") for f in changed_files)

        if not has_code_changes:
            return None

        # Check test coverage gaps
        blast_analysis = scope.get("blast_radius_analysis", {})
        detailed = blast_analysis.get("detailed", {})
        test_gaps = detailed.get("test_coverage_gaps", [])

        # Determine priority based on risk
        summary = blast_analysis.get("summary", {})
        risk_level = summary.get("risk_level", "LOW")

        priority_map = {"CRITICAL": "P0", "HIGH": "P1", "MEDIUM": "P2", "LOW": "P3"}

        priority = priority_map.get(risk_level, "P3")

        # Estimate effort based on complexity
        file_count = len([f for f in changed_files if f.endswith(".py")])
        if file_count > 5:
            estimate = "1-2 days"
        elif file_count > 2:
            estimate = "4-8 hours"
        else:
            estimate = "2-4 hours"

        return {
            "title": f"Add comprehensive test coverage for {task_id}",
            "description": self._generate_testing_description(task_id, scope),
            "priority": priority,
            "type": "task",
            "estimate": estimate,
            "dependencies": [task_id],
            "tags": ["testing", "quality-assurance"],
            "test_coverage_gaps": test_gaps,
            "changed_files": changed_files,
        }

    def _generate_testing_description(self, task_id: str, scope: Dict) -> str:
        """Generate description for testing task"""

        changed_files = scope.get("changed_files", [])
        py_files = [f for f in changed_files if f.endswith(".py")]

        description = f"Create comprehensive tests for changes in {task_id}.\n\n"
        description += "**Files to test:**\n"

        for py_file in py_files[:10]:  # Limit to first 10 files
            description += f"- {py_file}\n"

        if len(py_files) > 10:
            description += f"- ... and {len(py_files) - 10} additional files\n"

        # Add specific test requirements based on file types
        if any("api" in f or "routes" in f for f in py_files):
            description += "\n**API Testing Requirements:**\n"
            description += "- Endpoint testing with various inputs\n"
            description += "- Error handling validation\n"
            description += "- Authentication/authorization testing\n"

        if any("core" in f for f in py_files):
            description += "\n**Core Functionality Testing:**\n"
            description += "- Unit tests with >90% coverage\n"
            description += "- Integration tests with dependent systems\n"
            description += "- Performance benchmarks\n"

        return description

    def _create_documentation_recommendation(
        self, task_id: str, scope: Dict
    ) -> Optional[Dict]:
        """Create documentation task recommendation"""

        changed_files = scope.get("changed_files", [])

        # Check if documentation changes are needed
        needs_docs = (
            any("api" in f or "routes" in f for f in changed_files)
            or any("config" in f for f in changed_files)
            or any("deployment" in f for f in changed_files)
        )

        if not needs_docs:
            return None

        # Determine priority
        if any("api" in f for f in changed_files):
            priority = "P2"
        else:
            priority = "P3"

        return {
            "title": f"Update documentation for {task_id}",
            "description": self._generate_documentation_description(task_id, scope),
            "priority": priority,
            "type": "task",
            "estimate": "2-4 hours",
            "dependencies": [task_id],
            "tags": ["documentation"],
            "affected_components": [
                f
                for f in changed_files
                if any(
                    keyword in f
                    for keyword in ["api", "routes", "config", "deployment"]
                )
            ],
        }

    def _generate_documentation_description(self, task_id: str, scope: Dict) -> str:
        """Generate description for documentation task"""

        changed_files = scope.get("changed_files", [])
        description = f"Update documentation to reflect changes in {task_id}.\n\n"

        if any("api" in f or "routes" in f for f in changed_files):
            description += "**API Documentation Updates:**\n"
            description += "- Update OpenAPI/Swagger specifications\n"
            description += "- Add new endpoint documentation\n"
            description += "- Update request/response examples\n"
            description += "- Document breaking changes\n\n"

        if any("config" in f for f in changed_files):
            description += "**Configuration Documentation:**\n"
            description += "- Update configuration examples\n"
            description += "- Document new configuration options\n"
            description += "- Add migration guide for config changes\n\n"

        if any("deployment" in f for f in changed_files):
            description += "**Deployment Documentation:**\n"
            description += "- Update deployment procedures\n"
            description += "- Document environment requirements\n"
            description += "- Add troubleshooting sections\n\n"

        return description

    def _create_migration_recommendation(
        self, task_id: str, scope: Dict
    ) -> Optional[Dict]:
        """Create migration task recommendation"""

        changed_files = scope.get("changed_files", [])

        # Check if migrations are needed
        needs_migration = any(
            "database" in f or "schema" in f for f in changed_files
        ) or any("migration" in f for f in changed_files)

        if not needs_migration:
            return None

        # Check blast radius analysis for migration requirements
        blast_analysis = scope.get("blast_radius_analysis", {})
        detailed = blast_analysis.get("detailed", {})
        migration_reqs = detailed.get("migration_requirements", [])

        return {
            "title": f"Database migration for {task_id}",
            "description": self._generate_migration_description(task_id, scope),
            "priority": "P1",  # Migrations are high priority
            "type": "task",
            "estimate": "4-8 hours",
            "dependencies": [task_id],
            "tags": ["database", "migration"],
            "migration_requirements": migration_reqs,
        }

    def _generate_migration_description(self, task_id: str, scope: Dict) -> str:
        """Generate description for migration task"""

        changed_files = scope.get("changed_files", [])
        description = f"Create and test database migration scripts for {task_id}.\n\n"

        # Identify database-related files
        db_files = [
            f
            for f in changed_files
            if any(keyword in f for keyword in ["database", "schema", "migration"])
        ]

        description += "**Database Changes:**\n"
        for db_file in db_files:
            description += f"- {db_file}\n"

        description += "\n**Migration Requirements:**\n"
        description += "- Create forward migration scripts\n"
        description += "- Create rollback migration scripts\n"
        description += "- Test migrations on staging data\n"
        description += "- Document data transformation logic\n"
        description += "- Plan for zero-downtime deployment\n"

        return description

    def _create_risk_recommendation(self, task_id: str, scope: Dict) -> Optional[Dict]:
        """Create risk mitigation task recommendation"""

        blast_analysis = scope.get("blast_radius_analysis", {})
        summary = blast_analysis.get("summary", {})

        # Only recommend risk mitigation for high-risk changes
        if summary.get("risk_level") not in ["HIGH", "CRITICAL"]:
            return None

        return {
            "title": f"Risk mitigation and rollback planning for {task_id}",
            "description": self._generate_risk_description(task_id, scope),
            "priority": "P0" if summary.get("risk_level") == "CRITICAL" else "P1",
            "type": "task",
            "estimate": "4-6 hours",
            "dependencies": [task_id],
            "tags": ["risk-management", "safety"],
            "risk_level": summary.get("risk_level"),
        }

    def _generate_risk_description(self, task_id: str, scope: Dict) -> str:
        """Generate description for risk mitigation task"""

        blast_analysis = scope.get("blast_radius_analysis", {})
        summary = blast_analysis.get("summary", {})
        detailed = blast_analysis.get("detailed", {})

        description = (
            f"Create comprehensive risk mitigation and rollback plan for {task_id}.\n\n"
        )

        description += f"**Risk Level:** {summary.get('risk_level', 'UNKNOWN')}\n"
        description += f"**Files Affected:** {summary.get('affected_files_count', 0)}\n"
        description += (
            f"**Critical Paths:** {', '.join(summary.get('critical_paths', []))}\n\n"
        )

        description += "**Risk Mitigation Activities:**\n"
        description += "- Create detailed rollback procedures\n"
        description += "- Identify key metrics to monitor\n"
        description += "- Create canary deployment plan\n"
        description += "- Prepare emergency response procedures\n"
        description += "- Schedule risk review meeting\n\n"

        if detailed.get("rollback_complexity") == "COMPLEX":
            description += "**Complex Rollback Requirements:**\n"
            description += "- Test rollback procedures in staging\n"
            description += "- Create data consistency validation scripts\n"
            description += "- Plan extended rollback window\n"

        return description

    def _create_performance_recommendation(
        self, task_id: str, scope: Dict
    ) -> Optional[Dict]:
        """Create performance testing task recommendation"""

        changed_files = scope.get("changed_files", [])

        # Check if performance testing is needed
        needs_perf_testing = (
            any("query" in f or "search" in f for f in changed_files)
            or any("cache" in f or "storage" in f for f in changed_files)
            or any("api" in f or "routes" in f for f in changed_files)
        )

        if not needs_perf_testing:
            return None

        return {
            "title": f"Performance testing for {task_id}",
            "description": self._generate_performance_description(task_id, scope),
            "priority": "P2",
            "type": "task",
            "estimate": "4-6 hours",
            "dependencies": [task_id],
            "tags": ["performance", "testing"],
        }

    def _generate_performance_description(self, task_id: str, scope: Dict) -> str:
        """Generate description for performance testing task"""

        changed_files = scope.get("changed_files", [])
        description = f"Create and execute performance tests for {task_id}.\n\n"

        if any("query" in f or "search" in f for f in changed_files):
            description += "**Query Performance Testing:**\n"
            description += "- Measure query response times\n"
            description += "- Test with various data volumes\n"
            description += "- Compare against baseline metrics\n\n"

        if any("cache" in f or "storage" in f for f in changed_files):
            description += "**Cache/Storage Performance:**\n"
            description += "- Measure cache hit rates\n"
            description += "- Test storage I/O performance\n"
            description += "- Validate memory usage patterns\n\n"

        if any("api" in f or "routes" in f for f in changed_files):
            description += "**API Performance:**\n"
            description += "- Load testing with concurrent requests\n"
            description += "- Stress testing to identify limits\n"
            description += "- Monitor resource utilization\n"

        return description

    def _create_security_recommendation(
        self, task_id: str, scope: Dict
    ) -> Optional[Dict]:
        """Create security review task recommendation"""

        changed_files = scope.get("changed_files", [])

        # Check if security review is needed
        needs_security_review = (
            any("auth" in f or "security" in f for f in changed_files)
            or any("api" in f or "routes" in f for f in changed_files)
            or any("config" in f for f in changed_files)
        )

        if not needs_security_review:
            return None

        return {
            "title": f"Security review for {task_id}",
            "description": self._generate_security_description(task_id, scope),
            "priority": "P2",
            "type": "task",
            "estimate": "2-4 hours",
            "dependencies": [task_id],
            "tags": ["security", "review"],
        }

    def _generate_security_description(self, task_id: str, scope: Dict) -> str:
        """Generate description for security review task"""

        changed_files = scope.get("changed_files", [])
        description = f"Conduct security review for changes in {task_id}.\n\n"

        if any("auth" in f or "security" in f for f in changed_files):
            description += "**Authentication/Security Changes:**\n"
            description += "- Review authentication flow changes\n"
            description += "- Validate security controls implementation\n"
            description += "- Test authorization logic\n\n"

        if any("api" in f or "routes" in f for f in changed_files):
            description += "**API Security Review:**\n"
            description += "- Validate input sanitization\n"
            description += "- Review access controls\n"
            description += "- Test for common vulnerabilities\n\n"

        if any("config" in f for f in changed_files):
            description += "**Configuration Security:**\n"
            description += "- Review sensitive data handling\n"
            description += "- Validate secure defaults\n"
            description += "- Check configuration exposure risks\n"

        return description

    def present_recommendations_to_user(self, recommendations: List[Dict]) -> List[str]:
        """Present recommendations to user and get selections"""

        if not recommendations:
            print("ℹ️  No additional tasks recommended based on planning scope.")
            return []

        print(f"\n📋 RECOMMENDED TASKS ({len(recommendations)}):")
        print("=" * 60)

        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['title']} [{rec['priority']}]")
            print(f"   📝 {rec['description'][:100]}...")
            print(f"   ⏱️  Estimate: {rec['estimate']}")
            print(f"   🏷️  Tags: {', '.join(rec['tags'])}")

        print("\n" + "=" * 60)
        print("💡 Enter the numbers of tasks you want to create (comma-separated)")
        print("   Example: 1,3,5")
        print("   Press Enter to skip all tasks")

        try:
            selection = input("Your selection: ").strip()

            if not selection:
                return []

            # Parse selection
            selected_numbers = [
                int(x.strip()) for x in selection.split(",") if x.strip().isdigit()
            ]

            # Get selected recommendations
            selected_recommendations = []
            for num in selected_numbers:
                if 1 <= num <= len(recommendations):
                    selected_recommendations.append(recommendations[num - 1])
                else:
                    print(f"⚠️  Invalid selection: {num}")

            return [rec["title"] for rec in selected_recommendations]

        except (KeyboardInterrupt, ValueError):
            print("\n⚠️  Invalid input. No tasks created.")
            return []

    def create_tasks(self, task_titles: List[str]) -> List[str]:
        """Create tasks in Beads from titles"""

        if not task_titles:
            return []

        created_task_ids = []

        print(f"\n🔧 Creating {len(task_titles)} tasks in Beads...")

        for title in task_titles:
            try:
                # Create task using beads command
                # Note: This would need to be adapted based on actual beads CLI
                result = subprocess.run(
                    ["bd", "create", "--title", title, "--interactive", "false"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    # Extract task ID from output
                    output = result.stdout
                    task_id = self._extract_task_id_from_output(output)

                    if task_id:
                        created_task_ids.append(task_id)
                        print(f"   ✅ Created: {task_id} - {title}")
                    else:
                        print(f"   ⚠️  Created but couldn't extract ID: {title}")
                else:
                    print(f"   ❌ Failed to create: {title}")
                    print(f"      Error: {result.stderr}")

            except (
                subprocess.TimeoutExpired,
                subprocess.CalledProcessError,
                FileNotFoundError,
            ) as e:
                print(f"   ❌ Error creating {title}: {e}")

        if created_task_ids:
            print(f"\n✅ Successfully created {len(created_task_ids)} tasks:")
            for task_id in created_task_ids:
                print(f"   - {task_id}")

        return created_task_ids

    def _extract_task_id_from_output(self, output: str) -> Optional[str]:
        """Extract task ID from beads command output"""

        # Look for pattern like "lightrag-abc123"
        import re

        # Common patterns in beads output
        patterns = [
            r"(lightrag-[a-zA-Z0-9]+)",
            r"Task ID: ([a-zA-Z0-9-]+)",
            r"Created task ([a-zA-Z0-9-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                return match.group(1)

        return None

    def update_task_with_planning_info(self, task_id: str, planning_scope: Dict):
        """Update existing task with planning information"""

        # Add planning information to task description or metadata
        try:
            # This would depend on beads CLI capabilities
            # For now, we'll store the association locally

            integration_data = {}
            if self.beads_integration_file.exists():
                with open(self.beads_integration_file, "r") as f:
                    integration_data = json.load(f)

            if task_id not in integration_data:
                integration_data[task_id] = {}

            integration_data[task_id]["planning_scope"] = planning_scope
            integration_data[task_id]["updated_at"] = datetime.now().isoformat()

            with open(self.beads_integration_file, "w") as f:
                json.dump(integration_data, f, indent=2, default=str)

            print(f"✅ Updated task {task_id} with planning information")

        except Exception as e:
            print(f"⚠️  Could not update task with planning info: {e}")

    def get_planning_recommendations_for_task(self, task_id: str) -> Optional[Dict]:
        """Get planning recommendations for a specific task"""

        if not self.beads_integration_file.exists():
            return None

        with open(self.beads_integration_file, "r") as f:
            integration_data = json.load(f)

        return integration_data.get(task_id, {}).get("planning_scope")


def main():
    """Main entry point for beads integration"""
    if len(sys.argv) < 2:
        print("Usage: python beads_integration.py <command> [options]")
        print("Commands:")
        print("  recommend <scope_file>")
        print("  create-tasks <task1,task2,...>")
        print("  update-task <task_id> <scope_file>")
        print("  get-planning <task_id>")
        sys.exit(1)

    command = sys.argv[1]
    repo_path = Path.cwd()

    try:
        beads = BeadsIntegration(repo_path)
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    if command == "recommend":
        if len(sys.argv) < 3:
            print("Error: Please provide scope_file")
            sys.exit(1)

        scope_file = sys.argv[2]

        with open(scope_file, "r") as f:
            scope = json.load(f)

        recommendations = beads.recommend_tasks_from_planning(scope)
        selected = beads.present_recommendations_to_user(recommendations)

        if selected:
            task_ids = beads.create_tasks(selected)
            print(f"\n🎉 Created {len(task_ids)} tasks from planning recommendations!")

    elif command == "create-tasks":
        if len(sys.argv) < 3:
            print("Error: Please provide comma-separated task titles")
            sys.exit(1)

        task_titles = sys.argv[2].split(",")
        task_ids = beads.create_tasks(task_titles)

        print(f"\n🎉 Created {len(task_ids)} tasks!")

    elif command == "update-task":
        if len(sys.argv) < 4:
            print("Error: Please provide task_id and scope_file")
            sys.exit(1)

        task_id = sys.argv[2]
        scope_file = sys.argv[3]

        with open(scope_file, "r") as f:
            scope = json.load(f)

        beads.update_task_with_planning_info(task_id, scope)

    elif command == "get-planning":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)

        task_id = sys.argv[2]
        planning = beads.get_planning_recommendations_for_task(task_id)

        if planning:
            print(json.dumps(planning, indent=2, default=str))
        else:
            print(f"No planning information found for {task_id}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
