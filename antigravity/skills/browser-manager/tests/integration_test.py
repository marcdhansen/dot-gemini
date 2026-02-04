#!/usr/bin/env python3
"""Simple integration test for Browser Manager."""

import sys
import os
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import browser manager
import importlib.util

spec = importlib.util.spec_from_file_location(
    "browser_manager", Path(__file__).parent.parent / "scripts" / "browser_manager.py"
)
browser_manager = importlib.util.module_from_spec(spec)
sys.modules["browser_manager"] = browser_manager
spec.loader.exec_module(browser_manager)


def test_browser_detection():
    """Test basic browser detection and configuration."""
    print("🧪 Testing Browser Manager Integration")
    print("=" * 50)

    # Create manager
    manager = browser_manager.BrowserManager()
    print(f"✅ Browser Manager created")
    print(f"   Agent ID: {manager.agent_id}")
    print(f"   Config loaded: {'Yes' if manager.config else 'No'}")

    # Test browser detection
    browsers = manager.detect_playwright_browsers()
    print(f"✅ Browser detection completed")
    print(f"   Found {len(browsers)} Playwright browsers")

    if browsers:
        total_tabs = sum(len(b.get("tabs", [])) for b in browsers)
        total_memory = sum(b["memory_mb"] for b in browsers)
        print(f"   Total tabs: {total_tabs}")
        print(f"   Total memory: {total_memory:.0f}MB")

        # Show first browser details
        browser = browsers[0]
        print(
            f"   Sample browser: PID {browser['pid']}, {len(browser.get('tabs', []))} tabs"
        )

    # Test configuration limits
    manager.config["limits"]["max_tabs_per_agent"] = 3
    limits_ok, warnings = manager.check_resource_limits()
    print(f"✅ Resource limits check")
    print(f"   Limits OK: {limits_ok}")
    if warnings:
        for warning in warnings:
            print(f"   Warning: {warning}")

    # Test tab detection
    if browsers:
        browser = browsers[0]
        if browser.get("debug_port"):
            tabs = manager.detect_browser_tabs(browser)
            print(f"✅ Tab detection for PID {browser['pid']}")
            print(f"   Detected {len(tabs)} tabs")
            if tabs and tabs[0].get("title"):
                print(f"   Sample tab: {tabs[0]['title']}")
        else:
            print(f"ℹ️  No debug port for PID {browser['pid']}")

    print(f"\n🎉 All tests completed successfully!")
    return True


if __name__ == "__main__":
    try:
        success = test_browser_detection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
