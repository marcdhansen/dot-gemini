#!/usr/bin/env python3
"""
SOP Simplification Proposal Validator

Validates SOP simplification proposals to ensure:
1. Quality gates are preserved
2. Justifications are adequate
3. Risk assessments are thorough
4. Non-negotiable requirements are maintained
"""

import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml
from datetime import datetime


class SimplificationValidator:
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize validator with configuration."""
        self.config_path = (
            config_path or Path(__file__).parent.parent / "config" / "planning_config.yaml"
        )
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load planning configuration."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default configuration if file not found
            return {
                "sop_simplification": {
                    "validation": {
                        "blocked_modifications": [
                            "skip_tdd",
                            "skip_code_quality_gates",
                            "skip_git_isolation",
                        ],
                        "require_justification_for": [
                            "remove_quality_gates",
                            "combine_steps",
                            "modify_documentation_requirements",
                        ],
                        "risk_thresholds": {
                            "max_allowed_risk": "medium",
                            "require_mitigation_for": ["high", "critical"],
                        },
                    }
                }
            }

    def validate_proposal(self, proposal_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a simplification proposal.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        if not proposal_path.exists():
            return False, [f"Proposal file not found: {proposal_path}"], []

        content = proposal_path.read_text()
        errors = []
        warnings = []

        # 1. Check for blocked modifications
        blocked_mods = self.config["sop_simplification"]["validation"]["blocked_modifications"]
        for blocked_mod in blocked_mods:
            if re.search(rf"\[x\].*{blocked_mod}", content, re.IGNORECASE):
                errors.append(f"BLOCKED: Cannot waive {blocked_mod.replace('_', ' ').title()}")

        # 2. Check justifications for required modifications
        required_justifications = self.config["sop_simplification"]["validation"][
            "require_justification_for"
        ]
        for req_just in required_justifications:
            if re.search(rf"\[x\].*{req_just}", content, re.IGNORECASE):
                if not self._has_justification(content, req_just):
                    errors.append(
                        f"Missing justification for: {req_just.replace('_', ' ').title()}"
                    )

        # 3. Check risk assessment completeness
        if not self._has_risk_assessment(content):
            errors.append("Missing comprehensive risk assessment")

        # 4. Check quality gates section
        if not self._has_quality_gates_section(content):
            errors.append("Missing quality gates maintenance section")

        # 5. Check for non-negotiable items
        non_negotiable = ["TDD Process", "Code Quality Gates", "Git Isolation"]
        for item in non_negotiable:
            if not re.search(rf"\[x\].*{item}", content, re.IGNORECASE):
                errors.append(f"Non-negotiable requirement not checked: {item}")

        # 6. Warnings for potentially problematic proposals
        if self._has_too_many_removals(content):
            warnings.append("High number of removals - consider if this is too aggressive")

        if self._lacks_success_criteria(content):
            warnings.append("Success criteria should be clearly defined")

        return len(errors) == 0, errors, warnings

    def _has_justification(self, content: str, modification_type: str) -> bool:
        """Check if justification is provided for a modification."""
        mod_section = re.search(
            rf"{modification_type.replace('_', ' ').title()}.*?Justification.*?(?=\n\n|\n##|\Z)",
            content,
            re.IGNORECASE | re.DOTALL,
        )
        if not mod_section:
            return False

        justification = mod_section.group()
        return len(justification.strip()) > 50  # Require substantive justification

    def _has_risk_assessment(self, content: str) -> bool:
        """Check if comprehensive risk assessment is present."""
        risk_section = re.search(r"##\s*Risk Assessment.*?##", content, re.IGNORECASE | re.DOTALL)
        if not risk_section:
            return False

        risk_content = risk_section.group()
        # Check for key risk assessment components
        required_elements = ["risk level", "specific risks", "mitigation", "fallback"]
        return all(re.search(elem, risk_content, re.IGNORECASE) for elem in required_elements)

    def _has_quality_gates_section(self, content: str) -> bool:
        """Check if quality gates maintenance section exists."""
        return bool(re.search(r"##\s*Quality Gates Maintained", content, re.IGNORECASE))

    def _has_too_many_removals(self, content: str) -> bool:
        """Check if too many items are being removed."""
        removal_count = len(re.findall(r"\[x\].*(remove|skip|eliminate)", content, re.IGNORECASE))
        return removal_count > 3

    def _lacks_success_criteria(self, content: str) -> bool:
        """Check if success criteria are missing or unclear."""
        return not re.search(r"success criteria|definition of success", content, re.IGNORECASE)

    def generate_approval_prompt(self, proposal_path: Path) -> str:
        """Generate user approval prompt for a valid proposal."""
        content = proposal_path.read_text()

        # Extract key information
        task_id = self._extract_field(content, "Task ID")
        task_type = self._extract_field(content, "Task Type")

        # Extract proposed modifications
        modifications = self._extract_modifications(content)

        # Extract primary benefit
        primary_benefit = self._extract_field(content, "Primary Benefit")
        if not primary_benefit:
            primary_benefit_match = re.search(r"Primary Benefit.*?([^\n]+)", content, re.IGNORECASE)
            primary_benefit = (
                primary_benefit_match.group(1).strip() if primary_benefit_match else "Not specified"
            )

        prompt = f"""
# SOP Simplification Approval Request

## Task Information
- **Task ID**: {task_id}
- **Task Type**: {task_type}

## Proposed Modifications
{modifications}

## Primary Benefit
{primary_benefit}

## Approval Options

Please choose one of the following:

**[A] Approve Standard SOP** - Follow full standard procedures with all quality gates

**[B] Approve Simplified SOP** - Use the proposed streamlined approach as detailed in the proposal

**[C] Reject** - Require agent to revise the proposal or use standard SOP approach

## Quality Gates Preserved
✅ TDD Process (Red-Green-Refactor cycle required)
✅ Code Quality Gates (linting, formatting, security scanning)  
✅ Git Isolation (feature branch and clean working directory)
✅ Documentation Updates (changes documented appropriately)

## Risk Mitigation
The proposal includes risk assessment and mitigation strategies. Review these carefully before approving.

To make your decision, reply with:
- "Approve Standard" for option A
- "Approve Simplified" for option B  
- "Reject" for option C

Your decision will be recorded in task.md for compliance tracking.
"""
        return prompt

    def _extract_field(self, content: str, field: str) -> str:
        """Extract a field value from proposal content."""
        pattern = rf"- \*\*{field}\*\*:\s*([^\n]+)"
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else "Not specified"

    def _extract_modifications(self, content: str) -> str:
        """Extract proposed modifications as a formatted list."""
        mod_section = re.search(
            r"##\s*Standard SOP Requirements Being Modified.*?(?=\n##|\Z)",
            content,
            re.IGNORECASE | re.DOTALL,
        )
        if not mod_section:
            return "No modifications found"

        # Extract checked items
        modifications = []
        for line in mod_section.group().split("\n"):
            if re.match(r"-\s*\[x\]", line.strip()):
                modifications.append(f"• {line.strip()[3:].strip()}")

        return "\n".join(modifications) if modifications else "No modifications specified"


def main():
    """Main validation function."""
    if len(sys.argv) != 2:
        print("Usage: python validate_simplification.py <proposal_path>")
        sys.exit(1)

    proposal_path = Path(sys.argv[1])
    validator = SimplificationValidator()

    print(f"🔍 Validating SOP Simplification Proposal: {proposal_path.name}")
    print("=" * 60)

    is_valid, errors, warnings = validator.validate_proposal(proposal_path)

    # Display results
    if errors:
        print("❌ VALIDATION ERRORS:")
        for error in errors:
            print(f"  • {error}")

    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")

    if is_valid:
        print("✅ PROPOSAL VALID - Ready for user approval")
        print()
        print(validator.generate_approval_prompt(proposal_path))
    else:
        print("❌ PROPOSAL INVALID - Fix errors before submission")
        sys.exit(1)


if __name__ == "__main__":
    main()
