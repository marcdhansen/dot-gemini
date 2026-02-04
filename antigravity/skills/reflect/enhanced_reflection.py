#!/usr/bin/env python3
"""
Enhanced Reflect Skill with Protocol Integration
Combines reflection capture with protocol highlights for comprehensive session learning
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


class EnhancedReflection:
    def __init__(self):
        self.workspace_dir = Path.cwd()
        self.agent_dir = self.workspace_dir / ".agent"
        self.reflections_file = self.agent_dir / "reflections.json"

    def run_enhanced_reflection(self):
        """Run enhanced reflection with protocol integration"""

        print("🧪 Enhanced Reflection - Protocol-Integrated Learning Capture")
        print("=" * 60)
        print()

        # 1. Protocol Context
        self._show_protocol_context()

        # 2. Current Session Analysis
        self._analyze_session()

        # 3. Reflection Capture
        reflection_data = self._capture_reflection()

        # 4. Save Reflection
        self._save_reflection(reflection_data)

        print("✅ Enhanced reflection captured successfully!")
        print()

    def _show_protocol_context(self):
        """Show protocol highlights to guide reflection"""
        print("📜 PROTOCOL CONTEXT - Guiding Your Reflection")
        print("-----------------------------------------")
        print("🎯 Quality Gates Status:")
        print("   • Tests: Run before RTB if code changed")
        print("   • Linting: Code quality validation")
        print("   • Type Checking: Type validation")
        print("   • Markdown Duplicates: Must be resolved")
        print("   • SOP Evaluation: PFC compliance check")
        print()
        print("📝 Closure Standards:")
        print("   • File locations with descriptions")
        print("   • Quick start instructions")
        print("   • Documentation references")
        print("   • Integration guidance")
        print("   • Production considerations")
        print()
        print("🔄 Learning Emphasis:")
        print("   • Real-time friction capture (not retrospective)")
        print("   • Exact error messages and solutions")
        print("   • User corrections and preferences")
        print("   • Performance bottlenecks and workarounds")
        print()
        print("🚫 Common RTB Blockers:")
        print("   • Missing closure notes")
        print("   • Duplicate markdown files")
        print("   • Uncommitted changes not pushed")
        print("   • Failed SOP evaluation")
        print()

    def _analyze_session(self):
        """Analyze current session for context"""
        print("🔍 SESSION ANALYSIS")
        print("------------------")

        # Check recent git activity
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", '--since="3 hours ago"', "--oneline"],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
            )
            commits = result.stdout.strip().split("\n") if result.stdout.strip() else []

            if commits:
                print(f"📊 Recent Activity: {len(commits)} commits in last 3 hours")
                for commit in commits[:3]:  # Show last 3
                    print(f"   • {commit}")
            else:
                print("📊 Recent Activity: No recent commits")

        except Exception:
            print("📊 Recent Activity: Unable to determine")

        # Check for friction log
        friction_logs = list(self.workspace_dir.glob(".session_friction_*.md"))
        if friction_logs:
            print(f"📝 Friction Logs: {len(friction_logs)} found")
            for log in friction_logs:
                print(f"   • {log.name}")
        else:
            print("📝 Friction Logs: None found")

        print()

    def _capture_reflection(self):
        """Interactive reflection capture"""
        print("🧪 REFLECTION CAPTURE")
        print("--------------------")
        print("💡 Answer these questions to capture key learnings from your session:")
        print()

        reflection_data = {
            "timestamp": datetime.now().timestamp(),
            "mission_name": self._get_input("Mission/Issue ID or task name: "),
            "outcome": self._get_choice(
                "Session outcome", ["SUCCESS", "PARTIAL", "FAILURE"]
            ),
            "duration_hours": self._get_float("Session duration (hours): "),
            "success_metrics": self._capture_success_metrics(),
            "technical_learnings": self._capture_learnings("Technical learnings"),
            "challenges_overcome": self._capture_learnings("Challenges overcome"),
            "protocol_issues": self._capture_protocol_issues(),
            "process_improvements": self._capture_learnings("Process improvements"),
            "quantitative_results": self._capture_quantitative_results(),
            "next_mission_readiness": self._get_choice(
                "Ready for next mission", [True, False]
            ),
            "status": "COMPLETE",
        }

        return reflection_data

    def _get_input(self, prompt):
        """Get user input with default handling"""
        try:
            response = input(f"   {prompt}").strip()
            return response if response else "Not specified"
        except (EOFError, KeyboardInterrupt):
            return "Not specified"

    def _get_choice(self, prompt, choices):
        """Get choice from options"""
        try:
            choice_input = input(
                f"   {prompt} ({'/'.join(map(str, choices))}): "
            ).strip()
            if choice_input in [str(c) for c in choices]:
                return choices[[str(c) for c in choices].index(choice_input)]
            return choices[0]  # Default to first choice
        except (EOFError, KeyboardInterrupt):
            return choices[0]

    def _get_float(self, prompt):
        """Get float input with validation"""
        try:
            value = input(f"   {prompt}").strip()
            return float(value) if value else 0.0
        except (ValueError, EOFError, KeyboardInterrupt):
            return 0.0

    def _capture_success_metrics(self):
        """Capture success metrics"""
        print("   ✅ Success Metrics (one per line, empty when done):")
        metrics = {}
        while True:
            metric = input("     • ").strip()
            if not metric:
                break
            if ":" in metric:
                key, value = metric.split(":", 1)
                metrics[key.strip()] = value.strip()
            else:
                metrics[metric] = True
        return metrics

    def _capture_learnings(self, title):
        """Capture learning items"""
        print(f"   🧪 {title} (one per line, empty when done):")
        learnings = []
        while True:
            learning = input("     • ").strip()
            if not learning:
                break
            learnings.append(learning)
        return learnings

    def _capture_protocol_issues(self):
        """Capture protocol-related issues"""
        print("   📜 Protocol Issues (one per line, empty when done):")
        issues = []
        while True:
            issue = input("     • ").strip()
            if not issue:
                break
            issues.append(issue)
        return issues

    def _capture_quantitative_results(self):
        """Capture quantitative results"""
        print("   📊 Quantitative Results (key: value, one per line, empty when done):")
        results = {}
        while True:
            result = input("     • ").strip()
            if not result:
                break
            if ":" in result:
                key, value = result.split(":", 1)
                try:
                    # Try to preserve numeric values
                    if value.strip().isdigit():
                        results[key.strip()] = int(value.strip())
                    elif (
                        "." in value.strip()
                        and value.strip().replace(".", "").isdigit()
                    ):
                        results[key.strip()] = float(value.strip())
                    else:
                        results[key.strip()] = value.strip()
                except:
                    results[key.strip()] = value.strip()
            else:
                results[result] = "Not specified"
        return results

    def _save_reflection(self, reflection_data):
        """Save reflection to file"""
        # Load existing reflections
        reflections = []
        if self.reflections_file.exists():
            try:
                with open(self.reflections_file, "r") as f:
                    reflections = json.load(f)
                if not isinstance(reflections, list):
                    reflections = []
            except:
                reflections = []

        # Add new reflection
        reflections.append(reflection_data)

        # Save reflections
        with open(self.reflections_file, "w") as f:
            json.dump(reflections, f, indent=2)

        # Display summary
        print(f"📝 Reflection saved: {reflection_data['mission_name']}")
        print(
            f"📊 Learnings captured: {len(reflection_data['technical_learnings'])} technical, {len(reflection_data['process_improvements'])} process"
        )
        if reflection_data["protocol_issues"]:
            print(f"📜 Protocol issues: {len(reflection_data['protocol_issues'])}")
        print(f"💾 Total reflections: {len(reflections)}")


def main():
    """Main entry point for enhanced reflection"""

    reflection = EnhancedReflection()

    try:
        reflection.run_enhanced_reflection()
    except KeyboardInterrupt:
        print("\n👋 Reflection interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERROR: Enhanced reflection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
