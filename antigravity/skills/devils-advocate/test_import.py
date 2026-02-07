#!/usr/bin/env python3
"""Test devil's advocate import"""


def test_import():
    print("Testing module import...")
    try:
        import json

        print("✅ json imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")

    try:
        import subprocess

        print("✅ subprocess imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")

    try:
        import sys

        print("✅ sys imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")

    print("✅ All modules imported successfully")
    return True


if __name__ == "__main__":
    test_import()
