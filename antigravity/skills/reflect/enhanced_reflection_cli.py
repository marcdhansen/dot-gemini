#!/usr/bin/env python3
"""
Enhanced Reflection CLI Wrapper
Provides both interactive and non-interactive reflection modes
"""

import sys
import os
import json
from pathlib import Path

# Add the reflect skill directory to path
reflect_dir = Path(__file__).parent
sys.path.insert(0, str(reflect_dir))

try:
    from enhanced_reflection import EnhancedReflection
except ImportError:
    print("❌ Error: enhanced_reflection.py not found")
    sys.exit(1)


def detect_interactive_mode():
    """Detect if running in interactive mode"""
    # Check for specific environment variables
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        return False

    # Check command line flags
    if "--non-interactive" in sys.argv or "--fallback" in sys.argv:
        return False

    # Check if stdin is a terminal (more reliable check)
    if not sys.stdin.isatty():
        return False

    # Default to interactive if no indicators otherwise
    return True

    # Check for specific environment variables
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        return False

    # Check command line flags
    if "--non-interactive" in sys.argv or "--fallback" in sys.argv:
        return False

    # Default to interactive if no indicators otherwise
    return True


def get_fallback_data():
    """Get fallback data from various sources"""
    fallback_data = {}

    # Try environment variables
    if os.getenv("REFLECTION_MISSION"):
        fallback_data["mission_name"] = os.getenv("REFLECTION_MISSION")
    if os.getenv("REFLECTION_OUTCOME"):
        fallback_data["outcome"] = os.getenv("REFLECTION_OUTCOME")
    if os.getenv("REFLECTION_DURATION"):
        try:
            duration_str = os.getenv("REFLECTION_DURATION")
            if duration_str:
                fallback_data["duration_hours"] = float(duration_str)
        except (ValueError, TypeError):
            pass

    # Try to extract from git history if no data provided
    if not fallback_data:
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", '--since="2 hours ago"', "--oneline"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            recent_commits = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
            if recent_commits:
                for commit in recent_commits[:3]:
                    if "lightrag-" in commit.lower():
                        fallback_data["mission_name"] = f"LightRAG Task: {commit}"
                        break
        except Exception:
            pass

    return fallback_data


def main():
    """Main CLI entry point"""

    print("🧪 Enhanced Reflection - Protocol-Integrated Learning Capture")
    print("=" * 60)
    print()

    # Detect mode
    interactive = detect_interactive_mode()

    if interactive:
        print("📝 Interactive mode detected")
        try:
            reflection = EnhancedReflection(non_interactive=False)
            reflection.run_enhanced_reflection()
        except Exception as e:
            print(f"❌ Interactive mode failed: {e}")
            print("🔄 Attempting non-interactive fallback...")
            fallback_data = get_fallback_data()
            reflection = EnhancedReflection(
                non_interactive=True, fallback_data=fallback_data
            )
            reflection.run_enhanced_reflection()
    else:
        print("🤖 Non-interactive mode detected")
        fallback_data = get_fallback_data()
        reflection = EnhancedReflection(
            non_interactive=True, fallback_data=fallback_data
        )
        reflection.run_enhanced_reflection()

    print()
    print("✅ Reflection process completed!")


if __name__ == "__main__":
    main()
