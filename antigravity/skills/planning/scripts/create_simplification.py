#!/usr/bin/env python3
"""
SOP Simplification Proposal Creator

Helps agents create SOP simplification proposals by:
1. Analyzing current task context
2. Suggesting appropriate simplifications based on task type
3. Pre-populating the template with relevant information
4. Guiding through risk assessment
"""

import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from datetime import datetime


class SimplificationCreator:
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize creator with configuration."""
        self.config_path = (
            config_path or Path(__file__).parent.parent / "config" / "planning_config.yaml"
        )
        self.config = self._load_config()
        self.template_path = (
            Path(__file__).parent.parent / "templates" / "simplified_sop_proposal.md"
        )

    def _load_config(self) -> Dict:
        """Load planning configuration."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def create_proposal(self, task_info: Dict, output_path: Optional[Path] = None) -> Path:
        """
        Create a simplification proposal based on task information.

        Args:
            task_info: Dict containing task details
            output_path: Optional output path for the proposal

        Returns:
            Path to the created proposal file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"sop_simplification_{timestamp}.md")

        # Load template
        template_content = self.template_path.read_text()

        # Fill in basic information
        template_content = self._fill_basic_info(template_content, task_info)

        # Suggest simplifications based on task type
        template_content = self._suggest_simplifications(template_content, task_info)

        # Add risk assessment guidance
        template_content = self._add_risk_guidance(template_content, task_info)

        # Write the proposal
        output_path.write_text(template_content)

        print(f"📝 SOP Simplification Proposal created: {output_path}")
        print(f"📋 Task Type: {task_info.get('task_type', 'Unknown')}")
        print(
            f"🎯 Edit the proposal and then validate with: python {Path(__file__).name} {output_path}"
        )

        return output_path

    def _fill_basic_info(self, template: str, task_info: Dict) -> str:
        """Fill in basic task information."""
        replacements = {
            "[Enter task identifier or brief description]": task_info.get(
                "task_id", task_info.get("description", "Unknown Task")
            ),
            "[Bug Fix / Feature Addition / Documentation / Configuration / Security]": task_info.get(
                "task_type", "Unknown"
            ),
            "[Agent name/model]": "Claude Code Agent",
            "[Current date]": datetime.now().strftime("%Y-%m-%d"),
        }

        for old, new in replacements.items():
            template = template.replace(old, new)

        return template

    def _suggest_simplifications(self, template: str, task_info: Dict) -> str:
        """Suggest simplifications based on task type."""
        task_type = task_info.get("task_type", "").lower()

        if task_type == "bug fix":
            return self._suggest_bug_fix_simplifications(template)
        elif task_type == "feature addition":
            return self._suggest_feature_simplifications(template)
        elif task_type == "documentation":
            return self._suggest_documentation_simplifications(template)
        elif task_type == "configuration":
            return self._suggest_configuration_simplifications(template)
        else:
            return template

    def _suggest_bug_fix_simplifications(self, template: str) -> str:
        """Suggest simplifications for bug fixes."""
        # Pre-fill common bug fix simplifications
        suggestions = [
            "Remove performance benchmarking - not relevant for simple bug fixes",
            "Skip integration testing scope expansion - focus on specific bug reproduction",
            "Condense retrospective to key technical learnings only",
        ]

        justifications = [
            "Bug fix has no performance impact, so benchmarking is unnecessary overhead",
            "Integration testing should focus on the specific bug scenario, not full regression",
            "Simple bug fixes generate minimal strategic insights, focus on technical learnings",
        ]

        # Insert suggestions into template
        template = self._insert_simplification_suggestions(template, suggestions, justifications)

        # Set risk level to Low
        template = re.sub(
            r"- \*\*Risk Level\*\*: \[Low / Medium / High / Critical\]",
            "- **Risk Level**: **Low**",
            template,
        )

        return template

    def _suggest_feature_simplifications(self, template: str) -> str:
        """Suggest simplifications for feature additions."""
        # Feature additions typically need full SOP - suggest minimal simplifications
        suggestions = [
            "Streamline documentation to core functionality only",
            "Focus performance testing on critical path",
        ]

        justifications = [
            "Initial feature release can focus on core functionality, comprehensive docs can follow",
            "Performance testing should prioritize critical user workflows initially",
        ]

        template = self._insert_simplification_suggestions(template, suggestions, justifications)

        # Set risk level to Medium
        template = re.sub(
            r"- \*\*Risk Level\*\*: \[Low / Medium / High / Critical\]",
            "- **Risk Level**: **Medium**",
            template,
        )

        return template

    def _suggest_documentation_simplifications(self, template: str) -> str:
        """Suggest simplifications for documentation tasks."""
        suggestions = [
            "Skip TDD for pure documentation changes",
            "Remove performance benchmarking requirements",
            "Simplify finalization to documentation quality checks only",
        ]

        justifications = [
            "Pure documentation changes don't involve code, so TDD process doesn't apply",
            "Documentation changes don't affect system performance",
            "Focus quality gates on documentation integrity rather than code quality",
        ]

        template = self._insert_simplification_suggestions(template, suggestions, justifications)

        # Set risk level to Low
        template = re.sub(
            r"- \*\*Risk Level\*\*: \[Low / Medium / High / Critical\]",
            "- **Risk Level**: **Low**",
            template,
        )

        return template

    def _suggest_configuration_simplifications(self, template: str) -> str:
        """Suggest simplifications for configuration tasks."""
        suggestions = [
            "Focus testing on configuration validation scenarios",
            "Skip comprehensive integration testing if no API changes",
        ]

        justifications = [
            "Configuration changes should focus on validation of new settings",
            "If no API interfaces change, full integration testing may be excessive",
        ]

        template = self._insert_simplification_suggestions(template, suggestions, justifications)

        # Set risk level to Medium
        template = re.sub(
            r"- \*\*Risk Level\*\*: \[Low / Medium / High / Critical\]",
            "- **Risk Level**: **Medium**",
            template,
        )

        return template

    def _insert_simplification_suggestions(
        self, template: str, suggestions: List[str], justifications: List[str]
    ) -> str:
        """Insert suggestions into the template."""
        # Find the modifications section
        mod_section_match = re.search(
            r"(### Steps Being Removed or Modified.*?)(### Steps Being Combined)",
            template,
            re.DOTALL,
        )
        if not mod_section_match:
            return template

        mod_section = mod_section_match.group(1)

        # Add pre-filled suggestions
        for i, (suggestion, justification) in enumerate(zip(suggestions, justifications)):
            checkbox = f"- [x] **Remove/Modify**: {suggestion}\n  - **Justification**: {justification}\n  - **Impact Assessment**: Minimal impact on quality outcomes\n\n"
            mod_section += checkbox

        # Replace the section in template
        return template.replace(mod_section_match.group(1), mod_section)

    def _add_risk_guidance(self, template: str, task_info: Dict) -> str:
        """Add risk assessment guidance based on task type."""
        task_type = task_info.get("task_type", "").lower()

        risk_guidance = {
            "bug fix": {
                "specific_risks": "Fix might introduce regression in related functionality",
                "mitigation": "Focused testing on affected areas, comprehensive regression testing",
            },
            "feature addition": {
                "specific_risks": "New feature might affect existing workflows or performance",
                "mitigation": "Thorough testing, performance monitoring, gradual rollout",
            },
            "documentation": {
                "specific_risks": "Documentation errors might mislead users or developers",
                "mitigation": "Technical review, user testing, cross-reference validation",
            },
            "configuration": {
                "specific_risks": "Configuration changes might break deployments or functionality",
                "mitigation": "Staging validation, rollback procedures, monitoring",
            },
        }

        guidance = risk_guidance.get(task_type, {})
        if not guidance:
            return template

        # Fill in risk assessment section
        template = template.replace(
            "- **Specific Risks**: [What could go wrong with simplification]",
            f"- **Specific Risks**: {guidance['specific_risks']}",
        )

        template = template.replace(
            "- **Mitigation Strategies**: [How each risk will be addressed]",
            f"- **Mitigation Strategies**: {guidance['mitigation']}",
        )

        return template

    def guide_creation(self, task_type: str) -> None:
        """Provide interactive guidance for creating a proposal."""
        print(f"🎯 SOP Simplification Guide for {task_type.title()}")
        print("=" * 50)

        # Task type specific guidance
        guidance = {
            "bug fix": {
                "common_simplifications": [
                    "Skip performance benchmarking for non-performance fixes",
                    "Focus testing on specific bug scenario",
                    "Streamline retrospective to technical learnings",
                ],
                "risk_focus": "Regression risk and fix effectiveness",
            },
            "feature addition": {
                "common_simplifications": [
                    "Phase documentation rollouts",
                    "Focus performance testing on critical paths",
                ],
                "risk_focus": "Integration complexity and user adoption",
            },
            "documentation": {
                "common_simplifications": [
                    "Skip TDD for pure doc changes",
                    "Focus quality gates on doc integrity",
                ],
                "risk_focus": "Accuracy and clarity of information",
            },
        }

        if task_type in guidance:
            guide = guidance[task_type]
            print(f"\n📋 Common Simplifications for {task_type.title()}:")
            for simplification in guide["common_simplifications"]:
                print(f"  • {simplification}")

            print(f"\n⚠️  Risk Focus: {guide['risk_focus']}")

        print(f"\n💡 Remember:")
        print(f"  • TDD is never negotiable for code changes")
        print(f"  • Quality gates must be maintained")
        print(f"  • Justifications must be specific and clear")
        print(f"  • Risk assessment must include mitigation strategies")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python create_simplification.py <task_type> [task_id] [description]")
        print("Task types: bug-fix, feature-addition, documentation, configuration")
        sys.exit(1)

    task_type = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    description = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None

    creator = SimplificationCreator()

    # Provide guidance first
    creator.guide_creation(task_type)

    # Create proposal
    task_info = {
        "task_type": task_type,
        "task_id": task_id or f"{task_type}-{datetime.now().strftime('%Y%m%d')}",
        "description": description or f"SOP simplification for {task_type}",
    }

    proposal_path = creator.create_proposal(task_info)

    print(f"\n📄 Next steps:")
    print(f"1. Edit the proposal: {proposal_path}")
    print(f"2. Validate: python {Path(__file__).name} {proposal_path}")
    print(f"3. Submit for user approval")


if __name__ == "__main__":
    main()
