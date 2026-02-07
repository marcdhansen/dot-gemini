#!/usr/bin/env python3
"""
TDD Gate Enhancement for Planning Skill
Integrates planning requirements with existing TDD gate system
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class TDDGateEnhancement:
    """Enhanced TDD gate integration with planning requirements"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.agent_dir = repo_path / ".agent"
        self.tdd_config_file = self.agent_dir / "tdd_gate_config.json"
        self.planning_integration_file = (
            self.agent_dir / "planning_tdd_integration.json"
        )

        # Ensure directories exist
        self.agent_dir.mkdir(exist_ok=True)
        (self.agent_dir / "tdd_reports").mkdir(exist_ok=True)

        # Load configuration
        self.tdd_config = self._load_tdd_config()
        self.integration_config = self._load_integration_config()

    def _load_tdd_config(self) -> Dict:
        """Load TDD gate configuration"""
        default_config = {
            "enabled_gates": [
                "pytest",
                "linting",
                "type_checking",
                "markdown_duplicates",
            ],
            "pytest": {
                "required_coverage": 80,
                "high_risk_coverage": 90,
                "critical_risk_coverage": 95,
                "fail_on_missing": True,
                "test_patterns": ["tests/test_*.py", "*_test.py", "test_*.py"],
            },
            "linting": {
                "tool": "ruff",
                "fail_on_error": True,
                "exclude_patterns": ["venv/", ".venv/", "build/"],
            },
            "type_checking": {
                "tool": "mypy",
                "fail_on_error": False,  # Usually warning-only
                "exclude_patterns": ["tests/", "venv/"],
            },
            "markdown_duplicates": {"enabled": True, "fail_on_duplicates": True},
        }

        if self.tdd_config_file.exists():
            try:
                with open(self.tdd_config_file, "r") as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                return {**default_config, **loaded_config}
            except (json.JSONDecodeError, IOError):
                pass

        return default_config

    def _load_integration_config(self) -> Dict:
        """Load planning-TDD integration configuration"""
        default_config = {
            "planning_required": True,
            "adaptive_thresholds": True,
            "planning_based_gates": {
                "blast_radius_review": True,
                "milestone_validation": True,
                "rollback_verification": True,
            },
            "threshold_adjustments": {
                "LOW": {"coverage": 75, "linting_strictness": "relaxed"},
                "MEDIUM": {"coverage": 80, "linting_strictness": "standard"},
                "HIGH": {"coverage": 85, "linting_strictness": "strict"},
                "CRITICAL": {"coverage": 90, "linting_strictness": "strict"},
            },
        }

        if self.planning_integration_file.exists():
            try:
                with open(self.planning_integration_file, "r") as f:
                    loaded_config = json.load(f)
                return {**default_config, **loaded_config}
            except (json.JSONDecodeError, IOError):
                pass

        return default_config

    def validate_planning_requirements(self, task_id: Optional[str] = None) -> Dict:
        """Validate planning requirements before TDD gates"""

        result = {"passed": True, "errors": [], "warnings": [], "planning_status": {}}

        # Check if planning is required
        if not self.integration_config.get("planning_required", True):
            result["planning_status"]["planning_required"] = False
            return result

        # Get task context
        task_context = self._get_task_context(task_id)

        # Validate planning scope exists
        if task_context.get("task_id"):
            scope_validation = self._validate_planning_scope(task_context["task_id"])
            result["planning_status"]["scope_validation"] = scope_validation

            if not scope_validation.get("exists", False):
                result["passed"] = False
                result["errors"].append(
                    f"No planning scope found for task {task_context['task_id']}"
                )
                result["warnings"].append(
                    "Run `/plan scope <task-id>` to create planning scope"
                )
            else:
                result["planning_status"]["scope_valid"] = True
                result["warnings"].append(
                    f"Planning scope found for {task_context['task_id']}"
                )

        # Validate milestone completion
        if task_context.get("task_id"):
            milestone_validation = self._validate_milestones(task_context["task_id"])
            result["planning_status"]["milestone_validation"] = milestone_validation

            if milestone_validation.get("blocked", False):
                result["passed"] = False
                result["errors"].append(
                    f"Task {task_context['task_id']} is blocked by incomplete milestones"
                )
                result["warnings"].append(
                    "Complete required milestones before proceeding"
                )

        # Validate rollback capability for high-risk changes
        blast_analysis = task_context.get("blast_radius_analysis")
        if blast_analysis and blast_analysis.get("summary", {}).get("risk_level") in [
            "HIGH",
            "CRITICAL",
        ]:
            rollback_validation = self._validate_rollback_capability(
                task_context["task_id"]
            )
            result["planning_status"]["rollback_validation"] = rollback_validation

            if not rollback_validation.get("valid", False):
                result["passed"] = False
                result["errors"].append(
                    "Rollback procedures not validated for high-risk changes"
                )
                result["warnings"].append(
                    "Run `/plan validate-rollback <feature>` to validate rollback procedures"
                )

        return result

    def _get_task_context(self, task_id: Optional[str] = None) -> Dict:
        """Get current task context"""

        context = {"task_id": task_id}

        if task_id:
            # Try to get planning scope
            scope_file = self.agent_dir / "plans" / f"{task_id}_scope.json"
            if scope_file.exists():
                with open(scope_file, "r") as f:
                    context.update(json.load(f))

            # Try to get implementation plan
            plan_file = self.agent_dir / "plans" / f"{task_id}_implementation.json"
            if plan_file.exists():
                with open(plan_file, "r") as f:
                    context["implementation_plan"] = json.load(f)

        return context

    def _validate_planning_scope(self, task_id: str) -> Dict:
        """Validate planning scope exists and is recent"""

        scope_file = self.agent_dir / "plans" / f"{task_id}_scope.json"

        if not scope_file.exists():
            return {"exists": False}

        try:
            with open(scope_file, "r") as f:
                scope = json.load(f)

            created_at = scope.get("created_at", "")
            if created_at:
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                age_days = (datetime.now() - created_dt).days

                if age_days > 30:  # Scope is old
                    return {"exists": True, "fresh": False, "age_days": age_days}

            return {"exists": True, "fresh": True}

        except (json.JSONDecodeError, ValueError, IOError):
            return {"exists": False, "error": "Invalid scope file"}

    def _validate_milestones(self, task_id: str) -> Dict:
        """Validate milestone completion status"""

        # Try to use incremental validator
        validator_file = self.agent_dir / "validation" / f"{task_id}_blocked.json"

        if validator_file.exists():
            return {"blocked": True, "block_file": str(validator_file)}

        # Check milestone completion
        milestones_dir = self.agent_dir / "validation" / "milestones"
        if milestones_dir.exists():
            milestone_files = list(milestones_dir.glob(f"{task_id}_*.json"))

            completed = 0
            for milestone_file in milestone_files:
                try:
                    with open(milestone_file, "r") as f:
                        milestone = json.load(f)

                    if milestone.get("status") == "completed":
                        completed += 1
                except (json.JSONDecodeError, IOError):
                    continue

            if milestone_files:
                return {
                    "blocked": False,
                    "total_milestones": len(milestone_files),
                    "completed_milestones": completed,
                }

        return {"blocked": False, "no_milestones": True}

    def _validate_rollback_capability(self, task_id: str) -> Dict:
        """Validate rollback procedures are in place"""

        # Look for rollback plans
        rollback_dir = self.agent_dir / "validation" / "rollbacks"
        if rollback_dir.exists():
            rollback_files = list(rollback_dir.glob(f"{task_id}_*.json"))

            for rollback_file in rollback_files:
                try:
                    with open(rollback_file, "r") as f:
                        rollback = json.load(f)

                    # Check if rollback was recently validated
                    last_validated = rollback.get("last_validated", "")
                    if last_validated:
                        validated_dt = datetime.fromisoformat(
                            last_validated.replace("Z", "+00:00")
                        )
                        age_days = (datetime.now() - validated_dt).days

                        if age_days <= 7:  # Validated within last week
                            return {"valid": True, "rollback_file": str(rollback_file)}

                except (json.JSONDecodeError, ValueError, IOError):
                    continue

        return {"valid": False, "no_rollback_plan": True}

    def run_enhanced_tdd_gates(self, task_id: Optional[str] = None) -> Dict:
        """Run enhanced TDD gates with planning integration"""

        # First validate planning requirements
        planning_result = self.validate_planning_requirements(task_id)

        if not planning_result["passed"]:
            return {
                "passed": False,
                "stage": "planning_validation",
                "planning_result": planning_result,
                "tdd_results": {},
            }

        # Get adaptive thresholds based on planning
        adaptive_thresholds = self._get_adaptive_thresholds(task_id)

        # Run standard TDD gates with adaptive thresholds
        tdd_results = {}

        for gate in self.tdd_config["enabled_gates"]:
            if gate == "pytest":
                tdd_results["pytest"] = self._run_pytest_gate(
                    adaptive_thresholds.get("coverage")
                )
            elif gate == "linting":
                tdd_results["linting"] = self._run_linting_gate(
                    adaptive_thresholds.get("linting_strictness", "standard")
                )
            elif gate == "type_checking":
                tdd_results["type_checking"] = self._run_type_checking_gate()
            elif gate == "markdown_duplicates":
                tdd_results["markdown_duplicates"] = (
                    self._run_markdown_duplicates_gate()
                )

        # Combine results
        all_passed = all(result.get("passed", False) for result in tdd_results.values())

        return {
            "passed": all_passed,
            "stage": "tdd_gates",
            "planning_result": planning_result,
            "tdd_results": tdd_results,
            "adaptive_thresholds": adaptive_thresholds,
        }

    def _get_adaptive_thresholds(self, task_id: Optional[str] = None) -> Dict:
        """Get adaptive thresholds based on planning risk assessment"""

        if not self.integration_config.get("adaptive_thresholds", True):
            return {"coverage": self.tdd_config["pytest"]["required_coverage"]}

        # Get task context to determine risk level
        task_context = self._get_task_context(task_id)
        blast_analysis = task_context.get("blast_radius_analysis", {})
        risk_level = blast_analysis.get("summary", {}).get("risk_level", "MEDIUM")

        # Get thresholds for risk level
        thresholds = self.integration_config["threshold_adjustments"].get(
            risk_level, {}
        )

        return {
            "coverage": thresholds.get(
                "coverage", self.tdd_config["pytest"]["required_coverage"]
            ),
            "linting_strictness": thresholds.get("linting_strictness", "standard"),
            "risk_level": risk_level,
        }

    def _run_pytest_gate(self, coverage_threshold: Optional[int] = None) -> Dict:
        """Run pytest gate with coverage requirements"""

        if coverage_threshold is None:
            coverage_threshold = self.tdd_config["pytest"]["required_coverage"]

        try:
            # Run pytest with coverage
            cmd = [
                "python",
                "-m",
                "pytest",
                "--cov=lightrag",
                "--cov-report=json",
                "--cov-report=term-missing",
            ]

            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            # Parse coverage from JSON report
            coverage_file = self.repo_path / "coverage.json"
            coverage_percentage = 0.0

            if coverage_file.exists():
                try:
                    with open(coverage_file, "r") as f:
                        coverage_data = json.load(f)

                    total_coverage = coverage_data.get("totals", {}).get(
                        "percent_covered", 0.0
                    )
                    coverage_percentage = float(total_coverage)

                except (json.JSONDecodeError, KeyError, ValueError):
                    pass

            passed = (
                result.returncode == 0 and coverage_percentage >= coverage_threshold
            )

            return {
                "passed": passed,
                "exit_code": result.returncode,
                "coverage_percentage": coverage_percentage,
                "required_coverage": coverage_threshold,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "pytest timeout after 5 minutes",
                "coverage_percentage": 0.0,
            }
        except Exception as e:
            return {
                "passed": False,
                "error": f"pytest execution failed: {e}",
                "coverage_percentage": 0.0,
            }

    def _run_linting_gate(self, strictness: str = "standard") -> Dict:
        """Run linting gate with configurable strictness"""

        try:
            # Determine ruff command based on strictness
            if strictness == "relaxed":
                cmd = ["ruff", "check", "--exit-zero"]  # Don't fail on errors
            elif strictness == "strict":
                cmd = ["ruff", "check", "--fix", "--exit-non-zero-on-fix"]
            else:  # standard
                cmd = ["ruff", "check"]

            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutes
            )

            passed = result.returncode == 0

            return {
                "passed": passed,
                "exit_code": result.returncode,
                "strictness": strictness,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "ruff timeout after 2 minutes",
                "strictness": strictness,
            }
        except Exception as e:
            return {
                "passed": False,
                "error": f"ruff execution failed: {e}",
                "strictness": strictness,
            }

    def _run_type_checking_gate(self) -> Dict:
        """Run type checking gate"""

        try:
            cmd = ["mypy", "lightrag/", "--no-error-summary"]

            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minutes
            )

            passed = (
                result.returncode == 0
                or not self.tdd_config["type_checking"]["fail_on_error"]
            )

            return {
                "passed": passed,
                "exit_code": result.returncode,
                "fail_on_error": self.tdd_config["type_checking"]["fail_on_error"],
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "mypy timeout after 3 minutes"}
        except Exception as e:
            return {"passed": False, "error": f"mypy execution failed: {e}"}

    def _run_markdown_duplicates_gate(self) -> Dict:
        """Run markdown duplicates gate"""

        if not self.tdd_config["markdown_duplicates"]["enabled"]:
            return {"passed": True, "skipped": True}

        try:
            # Check for duplicate markdown files
            script_path = self.agent_dir / "scripts" / "verify_markdown_duplicates.sh"

            if not script_path.exists():
                return {
                    "passed": True,
                    "skipped": True,
                    "error": "Duplicate check script not found",
                }

            cmd = ["bash", str(script_path)]

            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,  # 1 minute
            )

            passed = result.returncode == 0

            if (
                not passed
                and self.tdd_config["markdown_duplicates"]["fail_on_duplicates"]
            ):
                passed = False
            else:
                passed = True  # Don't fail the gate unless configured to do so

            return {
                "passed": passed,
                "exit_code": result.returncode,
                "fail_on_duplicates": self.tdd_config["markdown_duplicates"][
                    "fail_on_duplicates"
                ],
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "markdown duplicates check timeout"}
        except Exception as e:
            return {"passed": False, "error": f"markdown duplicates check failed: {e}"}

    def generate_tdd_report(self, results: Dict) -> str:
        """Generate comprehensive TDD report"""

        report_lines = []
        report_lines.append("# TDD Gate Report")
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("")

        # Overall status
        passed = results.get("passed", False)
        status = "✅ PASSED" if passed else "❌ FAILED"
        report_lines.append(f"Overall Status: {status}")
        report_lines.append("")

        # Planning validation results
        if "planning_result" in results:
            planning = results["planning_result"]
            report_lines.append("## Planning Validation")
            report_lines.append(
                f"Status: {'✅ PASSED' if planning.get('passed', False) else '❌ FAILED'}"
            )

            if not planning.get("passed", False):
                for error in planning.get("errors", []):
                    report_lines.append(f"- ❌ {error}")

            for warning in planning.get("warnings", []):
                report_lines.append(f"- ⚠️  {warning}")

            report_lines.append("")

        # TDD gate results
        if "tdd_results" in results:
            tdd = results["tdd_results"]
            report_lines.append("## TDD Gates")

            for gate_name, gate_result in tdd.items():
                gate_passed = gate_result.get("passed", False)
                gate_status = "✅ PASSED" if gate_passed else "❌ FAILED"
                report_lines.append(f"### {gate_name.title()}: {gate_status}")

                if gate_passed:
                    if gate_name == "pytest":
                        coverage = gate_result.get("coverage_percentage", 0)
                        required = gate_result.get("required_coverage", 0)
                        report_lines.append(
                            f"- Coverage: {coverage:.1f}% (required: {required}%)"
                        )
                    elif gate_name == "linting":
                        strictness = gate_result.get("strictness", "standard")
                        report_lines.append(f"- Strictness: {strictness}")
                else:
                    error = gate_result.get("error", "")
                    if error:
                        report_lines.append(f"- Error: {error}")
                    else:
                        report_lines.append("- Check output for details")

                report_lines.append("")

        # Adaptive thresholds
        if "adaptive_thresholds" in results:
            thresholds = results["adaptive_thresholds"]
            report_lines.append("## Adaptive Thresholds")
            report_lines.append(
                f"- Coverage Requirement: {thresholds.get('coverage', 80)}%"
            )
            report_lines.append(
                f"- Linting Strictness: {thresholds.get('linting_strictness', 'standard')}"
            )
            if "risk_level" in thresholds:
                report_lines.append(f"- Risk Level: {thresholds['risk_level']}")
            report_lines.append("")

        return "\n".join(report_lines)

    def save_tdd_report(self, results: Dict, filename: Optional[str] = None) -> str:
        """Save TDD report to file"""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tdd_report_{timestamp}.md"

        report_content = self.generate_tdd_report(results)
        report_file = self.agent_dir / "tdd_reports" / filename

        with open(report_file, "w") as f:
            f.write(report_content)

        return str(report_file)


def main():
    """Main entry point for TDD gate enhancement"""
    if len(sys.argv) < 2:
        print("Usage: python tdd_gate_enhancement.py <command> [options]")
        print("Commands:")
        print("  validate [task_id]              # Validate planning requirements")
        print("  run-gates [task_id]             # Run enhanced TDD gates")
        print("  report <results_file>            # Generate report from results")
        print("  config                          # Show current configuration")
        sys.exit(1)

    command = sys.argv[1]
    repo_path = Path.cwd()

    try:
        tdd_enhancement = TDDGateEnhancement(repo_path)
    except Exception as e:
        print(f"❌ Error initializing TDD gate enhancement: {e}")
        sys.exit(1)

    if command == "validate":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = tdd_enhancement.validate_planning_requirements(task_id)

        print("Planning Validation Results:")
        print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")

        if not result["passed"]:
            for error in result.get("errors", []):
                print(f"❌ {error}")

        for warning in result.get("warnings", []):
            print(f"⚠️  {warning}")

    elif command == "run-gates":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = tdd_enhancement.run_enhanced_tdd_gates(task_id)

        print("Enhanced TDD Gate Results:")
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        stage = result.get("stage", "unknown")
        print(f"Overall Status: {status} (failed at: {stage})")

        # Save report
        report_file = tdd_enhancement.save_tdd_report(result)
        print(f"Detailed report saved to: {report_file}")

    elif command == "report":
        if len(sys.argv) < 3:
            print("Error: Please provide results file")
            sys.exit(1)

        results_file = sys.argv[2]

        with open(results_file, "r") as f:
            results = json.load(f)

        report_content = tdd_enhancement.generate_tdd_report(results)
        print(report_content)

    elif command == "config":
        import json

        print("TDD Gate Configuration:")
        print(json.dumps(tdd_enhancement.tdd_config, indent=2))
        print("\nPlanning Integration Configuration:")
        print(json.dumps(tdd_enhancement.integration_config, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
