#!/usr/bin/env python3
"""
Infisical Run Helper Script
Wraps Infisical CLI execution for agentic workflows.
Usage: python3 infisical_run.py -- <command>
"""

import os
import subprocess
import sys
from pathlib import Path

# Common binary locations
PATHS = [
    Path("~/.infisical/bin/infisical").expanduser(),
    Path("/usr/local/bin/infisical"),
    Path("/opt/homebrew/bin/infisical"),
]

def find_infisical():
    """Find the infisical binary"""
    for path in PATHS:
        if path.exists() and os.access(path, os.X_CONTROLLER):
            return str(path)
    
    # Try finding in PATH
    try:
        result = subprocess.run(["which", "infisical"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
        
    return None

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--":
        print("Usage: python3 infisical_run.py -- <command>")
        sys.exit(1)
        
    binary = find_infisical()
    if not binary:
        print("❌ Infisical CLI not found. Please install it using the Infisical skill instructions.")
        sys.exit(1)
        
    command = sys.argv[2:]
    
    # Check if .infisical.json exists in CWD
    if not Path(".infisical.json").exists():
        print("⚠️ Warning: .infisical.json not found in current directory. Project might not be initialized.")
        
    full_command = [binary, "run", "--"] + command
    
    try:
        # Pass stdout/stderr and return code
        result = subprocess.run(full_command)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n👋 Infisical execution interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
