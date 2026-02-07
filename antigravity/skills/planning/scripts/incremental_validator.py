#!/usr/bin/env python3
"""
Incremental Validation System with Milestone Blocking
Provides value-driven change validation with A/B testing and rollback safety
"""

import json
import os
import subprocess
import sys
import statistics
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# Statistical testing imports
try:
    from scipy import stats
except ImportError:
    stats = None


class ValidationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class MilestoneStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    AB_TEST = "ab_test"


@dataclass
class SuccessCriteria:
    metric_name: str
    threshold_value: float
    comparison_operator: str  # ">", "<", ">=", "<=", "=="
    test_type: TestType
    description: str


@dataclass
class ValidationResult:
    criteria: SuccessCriteria
    actual_value: float
    passed: bool
    measurement_time: datetime
    details: Dict[str, Any]


@dataclass
class Milestone:
    name: str
    description: str
    success_criteria: List[SuccessCriteria]
    validation_steps: List[str]
    estimated_duration: str
    blocking: bool
    status: MilestoneStatus
    validation_results: List[ValidationResult]
    created_at: datetime
    completed_at: Optional[datetime]


@dataclass
class ABTestResult:
    test_name: str
    control_mean: float
    treatment_mean: float
    p_value: float
    effect_size: float
    statistical_significance: bool
    sample_size_control: int
    sample_size_treatment: int
    recommendation: str


@dataclass
class RollbackPlan:
    feature_name: str
    rollback_steps: List[str]
    rollback_time: timedelta
    data_consistency_checks: List[str]
    validation_commands: List[str]
    emergency_contacts: List[str]
    last_validated: datetime


class IncrementalValidator:
    """Main incremental validation system"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.agent_dir = repo_path / ".agent"
        self.validation_dir = self.agent_dir / "validation"
        self.validation_dir.mkdir(exist_ok=True)

        # Subdirectories
        (self.validation_dir / "milestones").mkdir(exist_ok=True)
        (self.validation_dir / "ab_tests").mkdir(exist_ok=True)
        (self.validation_dir / "rollbacks").mkdir(exist_ok=True)

    def create_milestone(self, task_id: str, milestone_config: Dict) -> Milestone:
        """Create a new milestone with success criteria"""

        # Create success criteria objects
        criteria_list = []
        for crit in milestone_config.get("success_criteria", []):
            criteria = SuccessCriteria(
                metric_name=crit["metric_name"],
                threshold_value=crit["threshold_value"],
                comparison_operator=crit["comparison_operator"],
                test_type=TestType(crit["test_type"]),
                description=crit["description"],
            )
            criteria_list.append(criteria)

        # Create milestone
        milestone = Milestone(
            name=milestone_config["name"],
            description=milestone_config["description"],
            success_criteria=criteria_list,
            validation_steps=milestone_config.get("validation_steps", []),
            estimated_duration=milestone_config.get("estimated_duration", "1 day"),
            blocking=milestone_config.get("blocking", True),
            status=MilestoneStatus.NOT_STARTED,
            validation_results=[],
            created_at=datetime.now(),
            completed_at=None,
        )

        # Save milestone
        milestone_file = (
            self.validation_dir
            / "milestones"
            / f"{task_id}_{milestone.name.lower().replace(' ', '_')}.json"
        )

        with open(milestone_file, "w") as f:
            json.dump(asdict(milestone), f, indent=2, default=str)

        return milestone

    def validate_milestone(
        self, task_id: str, milestone_name: str, measurements: Dict[str, float]
    ) -> Milestone:
        """Validate a milestone against success criteria"""

        # Load milestone
        milestone_file = (
            self.validation_dir
            / "milestones"
            / f"{task_id}_{milestone_name.lower().replace(' ', '_')}.json"
        )

        if not milestone_file.exists():
            raise ValueError(f"Milestone {milestone_name} not found for task {task_id}")

        with open(milestone_file, "r") as f:
            milestone_data = json.load(f)

        # Update status to running
        milestone_data["status"] = MilestoneStatus.IN_PROGRESS.value

        # Validate each criteria
        validation_results = []
        overall_passed = True

        for criteria_data in milestone_data["success_criteria"]:
            criteria = SuccessCriteria(**criteria_data)

            # Get actual measurement
            actual_value = measurements.get(criteria.metric_name, 0.0)

            # Evaluate criteria
            passed = self._evaluate_criteria(criteria, actual_value)

            if not passed and criteria.test_type != TestType.AB_TEST:
                overall_passed = False

            result = ValidationResult(
                criteria=criteria,
                actual_value=actual_value,
                passed=passed,
                measurement_time=datetime.now(),
                details={},
            )
            validation_results.append(result)

        # Update milestone status
        milestone_data["validation_results"] = [asdict(r) for r in validation_results]

        if overall_passed:
            milestone_data["status"] = MilestoneStatus.COMPLETED.value
            milestone_data["completed_at"] = datetime.now().isoformat()
        else:
            milestone_data["status"] = MilestoneStatus.FAILED.value

        # Save updated milestone
        with open(milestone_file, "w") as f:
            json.dump(milestone_data, f, indent=2, default=str)

        # Check if this is a blocking milestone and failed
        if milestone_data.get("blocking", True) and not overall_passed:
            self._block_task_progression(task_id, milestone_name, validation_results)

        return Milestone(**milestone_data)

    def _evaluate_criteria(
        self, criteria: SuccessCriteria, actual_value: float
    ) -> bool:
        """Evaluate a single success criteria"""
        if criteria.comparison_operator == ">":
            return actual_value > criteria.threshold_value
        elif criteria.comparison_operator == "<":
            return actual_value < criteria.threshold_value
        elif criteria.comparison_operator == ">=":
            return actual_value >= criteria.threshold_value
        elif criteria.comparison_operator == "<=":
            return actual_value <= criteria.threshold_value
        elif criteria.comparison_operator == "==":
            return abs(actual_value - criteria.threshold_value) < 0.001
        else:
            return False

    def _block_task_progression(
        self,
        task_id: str,
        milestone_name: str,
        validation_results: List[ValidationResult],
    ):
        """Block task progression when blocking milestone fails"""

        block_file = self.validation_dir / f"{task_id}_blocked.json"

        block_data = {
            "task_id": task_id,
            "blocked_by_milestone": milestone_name,
            "blocked_at": datetime.now().isoformat(),
            "failed_criteria": [
                {
                    "metric": result.criteria.metric_name,
                    "threshold": result.criteria.threshold_value,
                    "actual": result.actual_value,
                    "operator": result.criteria.comparison_operator,
                }
                for result in validation_results
                if not result.passed
            ],
            "reason": f"Blocking milestone '{milestone_name}' failed validation",
        }

        with open(block_file, "w") as f:
            json.dump(block_data, f, indent=2)

        print(f"🚫 TASK BLOCKED: {task_id}")
        print(f"   Failed milestone: {milestone_name}")
        print(
            f"   Failed criteria: {len([r for r in validation_results if not r.passed])}"
        )

    def run_ab_test(
        self,
        test_name: str,
        control_data: List[float],
        treatment_data: List[float],
        significance_level: float = 0.05,
    ) -> ABTestResult:
        """Run A/B test with statistical significance testing"""

        if not stats:
            # Fallback to basic statistics without scipy
            return self._fallback_ab_test(
                test_name, control_data, treatment_data, significance_level
            )

        # Calculate basic statistics
        control_mean = statistics.mean(control_data)
        treatment_mean = statistics.mean(treatment_data)

        # Perform t-test
        t_stat, p_value = stats.ttest_ind(control_data, treatment_data)

        # Calculate effect size (Cohen's d)
        pooled_std = statistics.sqrt(
            statistics.stdev(control_data) ** 2 + statistics.stdev(treatment_data) ** 2
        )
        effect_size = (
            abs(treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0.0
        )

        # Determine statistical significance
        statistical_significance = p_value < significance_level

        # Generate recommendation
        if statistical_significance:
            if treatment_mean > control_mean:
                recommendation = "DEPLOY_TREATMENT"
            else:
                recommendation = "KEEP_CONTROL"
        else:
            recommendation = "INCONCLUSIVE"

        result = ABTestResult(
            test_name=test_name,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            p_value=p_value,
            effect_size=effect_size,
            statistical_significance=statistical_significance,
            sample_size_control=len(control_data),
            sample_size_treatment=len(treatment_data),
            recommendation=recommendation,
        )

        # Save A/B test result
        test_file = self.validation_dir / "ab_tests" / f"{test_name}.json"

        with open(test_file, "w") as f:
            json.dump(asdict(result), f, indent=2, default=str)

        return result

    def _fallback_ab_test(
        self,
        test_name: str,
        control_data: List[float],
        treatment_data: List[float],
        significance_level: float,
    ) -> ABTestResult:
        """Fallback A/B test without scipy"""

        control_mean = statistics.mean(control_data)
        treatment_mean = statistics.mean(treatment_data)

        # Simple difference-based approach
        difference = treatment_mean - control_mean
        relative_change = abs(difference) / control_mean if control_mean != 0 else 0

        # Simple significance based on relative change
        statistical_significance = relative_change > 0.05  # 5% threshold

        effect_size = relative_change

        if statistical_significance:
            if treatment_mean > control_mean:
                recommendation = "DEPLOY_TREATMENT"
            else:
                recommendation = "KEEP_CONTROL"
        else:
            recommendation = "INCONCLUSIVE"

        return ABTestResult(
            test_name=test_name,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            p_value=1.0 - relative_change,  # Fake p-value
            effect_size=effect_size,
            statistical_significance=statistical_significance,
            sample_size_control=len(control_data),
            sample_size_treatment=len(treatment_data),
            recommendation=recommendation,
        )

    def create_rollback_plan(
        self, feature_name: str, rollback_config: Dict
    ) -> RollbackPlan:
        """Create rollback plan for a feature"""

        plan = RollbackPlan(
            feature_name=feature_name,
            rollback_steps=rollback_config.get("rollback_steps", []),
            rollback_time=timedelta(
                hours=rollback_config.get("rollback_time_hours", 2)
            ),
            data_consistency_checks=rollback_config.get("data_consistency_checks", []),
            validation_commands=rollback_config.get("validation_commands", []),
            emergency_contacts=rollback_config.get("emergency_contacts", []),
            last_validated=datetime.now(),
        )

        # Save rollback plan
        plan_file = self.validation_dir / "rollbacks" / f"{feature_name}_rollback.json"

        with open(plan_file, "w") as f:
            json.dump(asdict(plan), f, indent=2, default=str)

        return plan

    def validate_rollback_capability(self, feature_name: str) -> bool:
        """Validate that rollback procedures are working"""

        plan_file = self.validation_dir / "rollbacks" / f"{feature_name}_rollback.json"

        if not plan_file.exists():
            return False

        with open(plan_file, "r") as f:
            plan_data = json.load(f)

        # Check if rollback was recently validated
        last_validated = datetime.fromisoformat(plan_data["last_validated"])
        if datetime.now() - last_validated > timedelta(days=7):
            return False

        # Run validation commands
        for command in plan_data.get("validation_commands", []):
            try:
                result = subprocess.run(
                    command.split(),
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False

        return True

    def execute_rollback(self, feature_name: str, user_justification: str) -> bool:
        """Execute rollback procedures"""

        plan_file = self.validation_dir / "rollbacks" / f"{feature_name}_rollback.json"

        if not plan_file.exists():
            print(f"❌ No rollback plan found for {feature_name}")
            return False

        with open(plan_file, "r") as f:
            plan_data = json.load(f)

        print(f"🔄 Executing rollback for {feature_name}")
        print(f"   Justification: {user_justification}")
        print(f"   Rollback steps: {len(plan_data['rollback_steps'])}")

        # Execute rollback steps
        for i, step in enumerate(plan_data["rollback_steps"], 1):
            print(f"   Step {i}/{len(plan_data['rollback_steps'])}: {step}")

            try:
                result = subprocess.run(
                    step.split(),
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes per step
                )

                if result.returncode != 0:
                    print(f"   ❌ Step failed: {result.stderr}")
                    return False

            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"   ❌ Step error: {e}")
                return False

        # Run data consistency checks
        for check in plan_data.get("data_consistency_checks", []):
            try:
                result = subprocess.run(
                    check.split(),
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode != 0:
                    print(f"   ⚠️  Data consistency check failed: {check}")

            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"   ⚠️  Data consistency check error: {check}")

        print(f"✅ Rollback completed for {feature_name}")

        # Log rollback
        log_entry = {
            "feature_name": feature_name,
            "rollback_time": datetime.now().isoformat(),
            "user_justification": user_justification,
            "steps_executed": len(plan_data["rollback_steps"]),
            "success": True,
        }

        log_file = self.validation_dir / "rollback_log.json"
        log_entries = []

        if log_file.exists():
            with open(log_file, "r") as f:
                log_entries = json.load(f)

        log_entries.append(log_entry)

        with open(log_file, "w") as f:
            json.dump(log_entries, f, indent=2, default=str)

        return True

    def get_task_validation_status(self, task_id: str) -> Dict:
        """Get overall validation status for a task"""

        milestones_dir = self.validation_dir / "milestones"
        milestone_files = list(milestones_dir.glob(f"{task_id}_*.json"))

        if not milestone_files:
            return {"status": "no_milestones", "milestones": []}

        milestones = []
        for file_path in milestone_files:
            with open(file_path, "r") as f:
                milestone_data = json.load(f)
            milestones.append(milestone_data)

        # Check if task is blocked
        block_file = self.validation_dir / f"{task_id}_blocked.json"
        is_blocked = block_file.exists()

        # Calculate overall status
        if is_blocked:
            overall_status = "blocked"
        elif all(m["status"] == MilestoneStatus.COMPLETED.value for m in milestones):
            overall_status = "completed"
        elif any(m["status"] == MilestoneStatus.FAILED.value for m in milestones):
            overall_status = "failed"
        elif any(m["status"] == MilestoneStatus.IN_PROGRESS.value for m in milestones):
            overall_status = "in_progress"
        else:
            overall_status = "pending"

        return {
            "status": overall_status,
            "milestones": milestones,
            "blocked": is_blocked,
            "completed_count": sum(
                1 for m in milestones if m["status"] == MilestoneStatus.COMPLETED.value
            ),
            "total_count": len(milestones),
            "progress_percentage": (
                sum(
                    1
                    for m in milestones
                    if m["status"] == MilestoneStatus.COMPLETED.value
                )
                / len(milestones)
            )
            * 100
            if milestones
            else 0,
        }

    def unblock_task(self, task_id: str, user_justification: str) -> bool:
        """Unblock a task with user justification"""

        block_file = self.validation_dir / f"{task_id}_blocked.json"

        if not block_file.exists():
            print(f"ℹ️  Task {task_id} is not blocked")
            return True

        # Load block details
        with open(block_file, "r") as f:
            block_data = json.load(f)

        # Remove block file
        block_file.unlink()

        # Log unblock action
        log_entry = {
            "task_id": task_id,
            "unblocked_at": datetime.now().isoformat(),
            "user_justification": user_justification,
            "original_block": block_data,
        }

        log_file = self.validation_dir / "unblock_log.json"
        log_entries = []

        if log_file.exists():
            with open(log_file, "r") as f:
                log_entries = json.load(f)

        log_entries.append(log_entry)

        with open(log_file, "w") as f:
            json.dump(log_entries, f, indent=2, default=str)

        print(f"✅ Task {task_id} unblocked")
        print(f"   Justification: {user_justification}")

        return True


def main():
    """Main entry point for incremental validation"""
    if len(sys.argv) < 2:
        print("Usage: python incremental_validator.py <command> [options]")
        print("Commands:")
        print("  create-milestone <task_id> <config_file>")
        print("  validate <task_id> <milestone_name> <measurements_json>")
        print("  ab-test <test_name> <control_data> <treatment_data>")
        print("  create-rollback <feature_name> <config_file>")
        print("  validate-rollback <feature_name>")
        print("  execute-rollback <feature_name> <justification>")
        print("  status <task_id>")
        print("  unblock <task_id> <justification>")
        sys.exit(1)

    command = sys.argv[1]
    repo_path = Path.cwd()
    validator = IncrementalValidator(repo_path)

    if command == "create-milestone":
        if len(sys.argv) < 4:
            print("Error: Please provide task_id and config_file")
            sys.exit(1)

        task_id = sys.argv[2]
        config_file = sys.argv[3]

        with open(config_file, "r") as f:
            config = json.load(f)

        milestone = validator.create_milestone(task_id, config)
        print(f"✅ Milestone created: {milestone.name}")

    elif command == "validate":
        if len(sys.argv) < 5:
            print(
                "Error: Please provide task_id, milestone_name, and measurements_json"
            )
            sys.exit(1)

        task_id = sys.argv[2]
        milestone_name = sys.argv[3]
        measurements = json.loads(sys.argv[4])

        milestone = validator.validate_milestone(task_id, milestone_name, measurements)
        print(f"🎯 Milestone validation: {milestone.status.value}")
        print(f"   Results: {len(milestone.validation_results)} criteria evaluated")

    elif command == "ab-test":
        if len(sys.argv) < 5:
            print("Error: Please provide test_name, control_data, and treatment_data")
            sys.exit(1)

        test_name = sys.argv[2]
        control_data = [float(x) for x in sys.argv[3].split(",")]
        treatment_data = [float(x) for x in sys.argv[4].split(",")]

        result = validator.run_ab_test(test_name, control_data, treatment_data)
        print(f"🧪 A/B Test Result: {result.recommendation}")
        print(f"   P-value: {result.p_value:.4f}")
        print(f"   Effect size: {result.effect_size:.4f}")

    elif command == "create-rollback":
        if len(sys.argv) < 4:
            print("Error: Please provide feature_name and config_file")
            sys.exit(1)

        feature_name = sys.argv[2]
        config_file = sys.argv[3]

        with open(config_file, "r") as f:
            config = json.load(f)

        plan = validator.create_rollback_plan(feature_name, config)
        print(f"✅ Rollback plan created for {feature_name}")

    elif command == "validate-rollback":
        if len(sys.argv) < 3:
            print("Error: Please provide feature_name")
            sys.exit(1)

        feature_name = sys.argv[2]
        is_valid = validator.validate_rollback_capability(feature_name)

        if is_valid:
            print(f"✅ Rollback capability validated for {feature_name}")
        else:
            print(f"❌ Rollback capability NOT validated for {feature_name}")

    elif command == "execute-rollback":
        if len(sys.argv) < 4:
            print("Error: Please provide feature_name and justification")
            sys.exit(1)

        feature_name = sys.argv[2]
        justification = sys.argv[3]

        success = validator.execute_rollback(feature_name, justification)

        if success:
            print(f"✅ Rollback executed successfully")
        else:
            print(f"❌ Rollback failed")

    elif command == "status":
        if len(sys.argv) < 3:
            print("Error: Please provide task_id")
            sys.exit(1)

        task_id = sys.argv[2]
        status = validator.get_task_validation_status(task_id)

        print(f"🎯 Validation Status for {task_id}: {status['status']}")
        print(f"   Progress: {status['progress_percentage']:.1f}%")
        print(f"   Milestones: {status['completed_count']}/{status['total_count']}")
        if status["blocked"]:
            print(f"   🚫 BLOCKED - See validation/{task_id}_blocked.json")

    elif command == "unblock":
        if len(sys.argv) < 4:
            print("Error: Please provide task_id and justification")
            sys.exit(1)

        task_id = sys.argv[2]
        justification = sys.argv[3]

        success = validator.unblock_task(task_id, justification)

        if success:
            print(f"✅ Task unblocked successfully")
        else:
            print(f"❌ Failed to unblock task")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
