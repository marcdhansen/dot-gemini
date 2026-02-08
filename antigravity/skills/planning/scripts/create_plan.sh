#!/usr/bin/env python3
"""
Main Planning Orchestrator - Entry point for the planning skill
Provides the primary interface for all planning operations
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add planning skill to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.blast_radius_analyzer import ChangeDetector, AnalysisLevel
from scripts.orchestrator_integration import OrchestratorPlanningIntegration
from scripts.incremental_validator import IncrementalValidator
from integration.beads_integration import BeadsIntegration


class PlanningOrchestrator:
    """Main orchestrator for the planning skill"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.agent_dir = repo_path / ".agent"
        
        # Initialize components
        self.blast_detector = ChangeDetector(repo_path)
        self.orchestrator = OrchestratorPlanningIntegration(repo_path)
        self.validator = IncrementalValidator(repo_path)
        self.beads = BeadsIntegration(repo_path)
    
    def handle_scope_command(self, task_id: str, changed_files: Optional[List[str]] = None,
                           analysis_level: AnalysisLevel = AnalysisLevel.DETAILED) -> Dict:
        """Handle /plan scope command"""
        
        print(f"\n🎯 SCOPING TASK: {task_id}")
        print("=" * 50)
        
        # If no files provided, try to detect them
        if not changed_files:
            changed_files = self._detect_changed_files()
        
        if not changed_files:
            print("❌ No changed files detected. Please provide file list manually.")
            return {}
        
        print(f"📁 Analyzing {len(changed_files)} files...")
        
        # Create planning scope
        try:
            scope = self.orchestrator.create_task_scope(
                task_id, changed_files, analysis_level
            )
            
            # Display results
            self._display_scope_results(scope)
            
            return scope
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Error creating scope: {e}")
            return {}
    
    def handle_analyze_command(self, task_id: str) -> Dict:
        """Handle /plan analyze command"""
        
        print(f"\n🔍 DETAILED ANALYSIS: {task_id}")
        print("=" * 50)
        
        # Check if scope exists
        scope_file = self.agent_dir / "plans" / f"{task_id}_scope.json"
        if not scope_file.exists():
            print(f"❌ No planning scope found for {task_id}")
            print(f"   Run `/plan scope {task_id}` first")
            return {}
        
        # Load scope
        with open(scope_file, 'r') as f:
            scope = json.load(f)
        
        # Run detailed analysis
        self._display_detailed_analysis(scope)
        
        # Get task recommendations
        recommendations = self.beads.recommend_tasks_from_planning(scope)
        if recommendations:
            print(f"\n📋 RECOMMENDED TASKS ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec['title']} [{rec['priority']}]")
                print(f"      {rec['estimate']} - {', '.join(rec['tags'])}")
        
        return scope
    
    def handle_proceed_command(self, task_id: str) -> Dict:
        """Handle /plan proceed command"""
        
        print(f"\n🚀 PROCEEDING WITH IMPLEMENTATION: {task_id}")
        print("=" * 60)
        
        # Check if scope exists
        scope_file = self.agent_dir / "plans" / f"{task_id}_scope.json"
        if not scope_file.exists():
            print(f"❌ No planning scope found for {task_id}")
            print(f"   Run `/plan scope {task_id}` first")
            return {}
        
        # Load scope
        with open(scope_file, 'r') as f:
            scope = json.load(f)
        
        # Get recommendations
        recommendations = self.beads.recommend_tasks_from_planning(scope)
        
        if not recommendations:
            print("ℹ️  No additional tasks recommended.")
            # Create implementation plan with just the main task
            plan = self.orchestrator.create_implementation_plan(task_id, [])
            self._display_implementation_plan(plan)
            return plan
        
        # Present recommendations to user
        selected_titles = self.beads.present_recommendations_to_user(recommendations)
        
        # Create implementation plan
        plan = self.orchestrator.create_implementation_plan(task_id, selected_titles)
        
        # Create selected tasks in beads
        if selected_titles:
            task_ids = self.beads.create_tasks(selected_titles)
            print(f"\n✅ Created {len(task_ids)} additional tasks in Beads")
        
        # Display implementation plan
        self._display_implementation_plan(plan)
        
        # Create validation milestones
        self._create_default_milestones(task_id, scope)
        
        return plan
    
    def handle_table_command(self, task_id: str, reason: str = "") -> Dict:
        """Handle /plan table command"""
        
        print(f"\n📋 TABLED TASK: {task_id}")
        print("=" * 40)
        
        if not reason:
            reason = input("Reason for tabling (optional): ").strip()
        
        try:
            summary = self.orchestrator.table_task_with_scoping(task_id, reason)
            
            print(f"✅ Task tabled with scoping saved")
            print(f"   Risk Level: {summary['blast_radius_summary']['risk_level']}")
            print(f"   Files: {summary['blast_radius_summary']['affected_files_count']}")
            
            return summary
            
        except Exception as e:
            print(f"❌ Error tabling task: {e}")
            return {}
    
    def handle_blast_radius_command(self, files: List[str], 
                                   level: AnalysisLevel = AnalysisLevel.SUMMARY) -> Dict:
        """Handle /plan blast-radius command"""
        
        print(f"\n💥 BLAST RADIUS ANALYSIS")
        print("=" * 40)
        print(f"Files: {len(files)}")
        print(f"Level: {level.value}")
        
        try:
            result = self.blast_detector.analyze_changes(files, level)
            self._display_blast_radius_results(result)
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing blast radius: {e}")
            return {}
    
    def handle_validate_command(self, plan_id: str) -> Dict:
        """Handle /plan validate command"""
        
        print(f"\n✅ VALIDATING PLAN: {plan_id}")
        print("=" * 40)
        
        # Get validation status
        status = self.validator.get_task_validation_status(plan_id)
        
        self._display_validation_status(status)
        
        return status
    
    def handle_track_command(self, task_id: str) -> Dict:
        """Handle /plan track command"""
        
        print(f"\n📊 TRACKING PROGRESS: {task_id}")
        print("=" * 40)
        
        # Check milestone completion
        milestone_status = self.orchestrator.check_milestone_completion(task_id)
        
        # Check validation status
        validation_status = self.validator.get_task_validation_status(task_id)
        
        # Display combined status
        self._display_tracking_status(task_id, milestone_status, validation_status)
        
        return {
            "milestones": milestone_status,
            "validation": validation_status
        }
    
    def handle_rollback_command(self, feature_name: str, justification: str = "") -> bool:
        """Handle /plan rollback command"""
        
        print(f"\n🔄 ROLLBACK: {feature_name}")
        print("=" * 40)
        
        if not justification:
            justification = input("Justification for rollback: ").strip()
        
        if not justification:
            print("❌ Justification required for rollback")
            return False
        
        try:
            success = self.validator.execute_rollback(feature_name, justification)
            return success
            
        except Exception as e:
            print(f"❌ Error executing rollback: {e}")
            return False
    
    def _detect_changed_files(self) -> List[str]:
        """Detect changed files from git status"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            
        except Exception:
            pass
        
        return []
    
    def _display_scope_results(self, scope: Dict):
        """Display planning scope results"""
        
        blast_analysis = scope.get("blast_radius_analysis", {})
        summary = blast_analysis.get("summary", {})
        
        print(f"\n📊 BLAST RADIUS SUMMARY:")
        print(f"   Risk Level: {summary.get('risk_level', 'UNKNOWN')}")
        print(f"   Files Affected: {summary.get('affected_files_count', 0)}")
        print(f"   Testing Effort: {summary.get('estimated_testing_effort', 'UNKNOWN')}")
        print(f"   Deployment Impact: {summary.get('deployment_impact', 'UNKNOWN')}")
        print(f"   Timeline Impact: {summary.get('timeline_impact', 'UNKNOWN')}")
        
        # Display recommendations
        recommendations = blast_analysis.get("recommendations", [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):  # Limit to first 5
                print(f"   {i}. {rec}")
    
    def _display_detailed_analysis(self, scope: Dict):
        """Display detailed analysis results"""
        
        blast_analysis = scope.get("blast_radius_analysis", {})
        
        # Display summary
        summary = blast_analysis.get("summary", {})
        print(f"\n📊 SUMMARY ANALYSIS:")
        print(f"   Risk Level: {summary.get('risk_level', 'UNKNOWN')}")
        print(f"   Critical Paths: {', '.join(summary.get('critical_paths', []))}")
        print(f"   Estimated Testing: {summary.get('estimated_testing_effort', 'UNKNOWN')}")
        
        # Display detailed impacts if available
        detailed = blast_analysis.get("detailed", {})
        if detailed:
            print(f"\n🔍 DETAILED IMPACTS:")
            file_impacts = detailed.get("file_impacts", {})
            
            for file_path, impact in list(file_impacts.items())[:5]:  # Limit to first 5
                print(f"   📁 {file_path}")
                print(f"      Risk: {impact.get('risk_level', 'UNKNOWN')}")
                print(f"      Complexity: {impact.get('complexity_score', 0):.1f}")
                print(f"      Test Coverage: {impact.get('test_coverage', 0):.1%}")
    
    def _display_implementation_plan(self, plan: Dict):
        """Display implementation plan"""
        
        print(f"\n🎯 IMPLEMENTATION PLAN CREATED")
        print(f"   Task: {plan.get('task_id', 'unknown')}")
        print(f"   Milestones: {len(plan.get('milestones', []))}")
        print(f"   Approved Tasks: {len(plan.get('approved_tasks', []))}")
        
        # Display milestones
        milestones = plan.get('milestones', [])
        if milestones:
            print(f"\n🎯 MILESTONES:")
            for i, milestone in enumerate(milestones, 1):
                status = milestone.get('status', 'NOT_STARTED')
                duration = milestone.get('estimated_duration', 'unknown')
                blocking = "🚫" if milestone.get('blocking', False) else "✅"
                
                print(f"   {i}. {milestone.get('name', 'Unknown')} [{status}] {blocking}")
                print(f"      Duration: {duration}")
                print(f"      Criteria: {len(milestone.get('success_criteria', []))}")
    
    def _display_blast_radius_results(self, result):
        """Display blast radius analysis results"""
        
        if result.summary:
            summary = result.summary
            print(f"\n📊 SUMMARY:")
            print(f"   Risk Level: {summary.risk_level.value}")
            print(f"   Files Affected: {summary.affected_files_count}")
            print(f"   Critical Paths: {', '.join(summary.critical_paths)}")
            print(f"   Testing Effort: {summary.estimated_testing_effort}")
            print(f"   Deployment Impact: {summary.deployment_impact}")
            print(f"   Timeline Impact: {summary.timeline_impact}")
        
        if result.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"   {i}. {rec}")
    
    def _display_validation_status(self, status: Dict):
        """Display validation status"""
        
        print(f"\n🎯 VALIDATION STATUS: {status['status']}")
        print(f"   Progress: {status['progress_percentage']:.1f}%")
        print(f"   Milestones: {status['completed_count']}/{status['total_count']}")
        
        if status['blocked']:
            print(f"   🚫 BLOCKED - See validation/{status['task_id']}_blocked.json")
        
        # Display milestone details
        for milestone in status['milestones']:
            name = milestone.get('name', 'Unknown')
            milestone_status = milestone.get('status', 'UNKNOWN')
            print(f"   • {name}: {milestone_status}")
    
    def _display_tracking_status(self, task_id: str, milestone_status: Dict, validation_status: Dict):
        """Display combined tracking status"""
        
        print(f"\n📊 OVERALL STATUS:")
        print(f"   Task: {task_id}")
        
        # Implementation milestones
        impl_progress = milestone_status.get('progress_percentage', 0)
        print(f"   Implementation: {impl_progress:.1f}%")
        
        # Validation milestones
        val_progress = validation_status.get('progress_percentage', 0)
        print(f"   Validation: {val_progress:.1f}%")
        
        # Overall progress
        overall_progress = (impl_progress + val_progress) / 2
        print(f"   Overall: {overall_progress:.1f}%")
        
        # Status indicators
        if validation_status.get('blocked'):
            print(f"   🚫 BLOCKED by validation requirements")
        elif impl_progress == 100 and val_progress == 100:
            print(f"   ✅ COMPLETED")
        elif impl_progress > 0 or val_progress > 0:
            print(f"   🔄 IN PROGRESS")
        else:
            print(f"   ⏸️  NOT STARTED")
    
    def _create_default_milestones(self, task_id: str, scope: Dict):
        """Create default validation milestones for a task"""
        
        # Create development milestone
        dev_milestone = {
            "name": "Development",
            "description": f"Complete core development for {task_id}",
            "success_criteria": [
                {
                    "metric_name": "test_coverage",
                    "threshold_value": 80.0,
                    "comparison_operator": ">=",
                    "test_type": "unit",
                    "description": "Unit test coverage >= 80%"
                },
                {
                    "metric_name": "code_review",
                    "threshold_value": 1.0,
                    "comparison_operator": "==",
                    "test_type": "integration",
                    "description": "Code review completed"
                }
            ],
            "validation_steps": [
                "Run unit tests",
                "Check test coverage",
                "Complete code review",
                "Verify coding standards"
            ],
            "estimated_duration": "2-3 days",
            "blocking": True
        }
        
        # Create integration milestone if needed
        blast_analysis = scope.get("blast_radius_analysis", {})
        summary = blast_analysis.get("summary", {})
        
        if summary.get("deployment_impact") != "NONE":
            integration_milestone = {
                "name": "Integration",
                "description": f"Test integration for {task_id}",
                "success_criteria": [
                    {
                        "metric_name": "integration_tests",
                        "threshold_value": 0.0,
                        "comparison_operator": "==",
                        "test_type": "integration",
                        "description": "All integration tests passing"
                    }
                ],
                "validation_steps": [
                    "Run integration tests",
                    "Verify API compatibility",
                    "Test with dependent systems"
                ],
                "estimated_duration": "1-2 days",
                "blocking": True
            }
            
            self.validator.create_milestone(task_id, integration_milestone)
        
        # Always create development milestone
        self.validator.create_milestone(task_id, dev_milestone)


def main():
    """Main entry point for planning orchestrator"""
    if len(sys.argv) < 3:
        print("Usage: python create_plan.sh <command> [options]")
        print("\nCommands:")
        print("  scope <task_id> [files...]     # Scope task with blast radius analysis")
        print("  analyze <task_id>              # Detailed analysis and recommendations")
        print("  proceed <task_id>              # Create implementation plan")
        print("  table <task_id> [reason]       # Table task with scoping")
        print("  blast-radius <files...>        # Quick blast radius analysis")
        print("  validate <task_id>             # Check validation status")
        print("  track <task_id>                # Track progress")
        print("  rollback <feature> <justification>  # Execute rollback")
        print("  help                          # Show this help")
        sys.exit(1)
    
    command = sys.argv[1]
    repo_path = Path.cwd()
    
    try:
        orchestrator = PlanningOrchestrator(repo_path)
    except Exception as e:
        print(f"❌ Error initializing planning orchestrator: {e}")
        sys.exit(1)
    
    if command == "help":
        print("Planning Skill - Comprehensive planning and validation system")
        print("=" * 60)
        print("\nThis skill provides integrated planning capabilities including:")
        print("• Blast radius analysis with progressive disclosure")
        print("• Incremental validation with milestone blocking")
        print("• A/B testing and rollback procedures")
        print("• Beads task integration")
        print("• Orchestrator workflow integration")
        print("\nExample workflows:")
        print("  /plan scope lightrag-abc              # Scope selected task")
        print("  /plan analyze lightrag-abc            # Detailed analysis")
        print("  /plan proceed lightrag-abc            # Create implementation plan")
        print("  /plan track lightrag-abc              # Track progress")
        return
    
    elif command == "scope":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)
        
        task_id = sys.argv[2]
        files = sys.argv[3:] if len(sys.argv) > 3 else None
        
        result = orchestrator.handle_scope_command(task_id, files)
        if result:
            print(f"\n✅ Task {task_id} scoped successfully")
            print(f"💡 Next: /plan analyze {task_id} or /plan proceed {task_id}")
    
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)
        
        task_id = sys.argv[2]
        result = orchestrator.handle_analyze_command(task_id)
        if result:
            print(f"\n💡 Next: /plan proceed {task_id} to create implementation plan")
    
    elif command == "proceed":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)
        
        task_id = sys.argv[2]
        result = orchestrator.handle_proceed_command(task_id)
        if result:
            print(f"\n🎉 Implementation plan ready!")
            print(f"💡 Track progress with: /plan track {task_id}")
    
    elif command == "table":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)
        
        task_id = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else ""
        
        result = orchestrator.handle_table_command(task_id, reason)
        if result:
            print(f"\n💡 Use /next to select a different task")
    
    elif command == "blast-radius":
        if len(sys.argv) < 3:
            print("Error: Please provide files to analyze")
            sys.exit(1)
        
        files = sys.argv[2:]
        result = orchestrator.handle_blast_radius_command(files)
        
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)
        
        task_id = sys.argv[2]
        result = orchestrator.handle_validate_command(task_id)
        
    elif command == "track":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)
        
        task_id = sys.argv[2]
        result = orchestrator.handle_track_command(task_id)
        
    elif command == "rollback":
        if len(sys.argv) < 3:
            print("Error: Please provide feature_name")
            sys.exit(1)
        
        feature_name = sys.argv[2]
        justification = sys.argv[3] if len(sys.argv) > 3 else ""
        
        success = orchestrator.handle_rollback_command(feature_name, justification)
        
        if success:
            print(f"\n✅ Rollback completed successfully")
        else:
            print(f"\n❌ Rollback failed")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'help' to see available commands")
        sys.exit(1)


if __name__ == "__main__":
    main()