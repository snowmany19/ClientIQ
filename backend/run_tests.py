#!/usr/bin/env python3
# run_tests.py
# Test runner script for A.I.ncident

import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage reporting."""
    
    # Ensure we're in the backend directory
    if not os.path.exists('tests'):
        print("❌ Error: No tests directory found. Make sure you're in the backend directory.")
        sys.exit(1)
    
    print("🧪 Running A.I.ncident tests...")
    print("=" * 50)
    
    # Run tests with coverage
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=70"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode

def run_specific_test(test_file):
    """Run a specific test file."""
    if not os.path.exists(f"tests/{test_file}"):
        print(f"❌ Test file tests/{test_file} not found.")
        return 1
    
    print(f"🧪 Running {test_file}...")
    print("=" * 50)
    
    cmd = ["python", "-m", "pytest", f"tests/{test_file}", "-v"]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ {test_file} tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_file} tests failed with exit code {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        exit_code = run_specific_test(test_file)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code) 