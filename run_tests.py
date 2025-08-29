#!/usr/bin/env python3
"""
Script to run tests with proper PYTHONPATH setup.
"""

import subprocess
import sys
import os

def run_tests():
    """Run tests with proper PYTHONPATH setup."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(project_root, "src")
    
    # Set up the environment with proper PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = src_path
    
    # Run pytest with the proper environment
    cmd = [sys.executable, "-m", "pytest"] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, env=env)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()