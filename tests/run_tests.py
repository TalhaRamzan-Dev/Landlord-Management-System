#!/usr/bin/env python3
"""
Simple test runner for the Property Management System
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with pytest"""
    print("🧪 Running Property Management System Tests")
    print("=" * 50)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest is not installed. Please install it with:")
        print("   pip install -r requirements.txt")
        return False
    
    # Run tests
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--verbose",
        "--tb=short"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False

def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"🧪 Running {test_file}")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/{test_file}",
        "--verbose",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ {test_file} tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_file} tests failed with exit code {e.returncode}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if test_file.endswith('.py'):
            success = run_specific_test(test_file)
        else:
            print(f"❌ Invalid test file: {test_file}")
            success = False
    else:
        success = run_tests()
    
    if success:
        print("\n🎉 Test execution completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test execution failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()