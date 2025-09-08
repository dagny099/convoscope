#!/usr/bin/env python3
"""
Convoscope Test Runner

Convenient script to run different types of tests for the Convoscope project.
"""
import subprocess
import sys
import argparse

def run_command(cmd, description):
    """Run a command and return success/failure."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run Convoscope tests")
    parser.add_argument(
        "test_type", 
        choices=["unit", "integration", "all", "setup"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--headed", 
        action="store_true",
        help="Run integration tests in headed mode (visible browser)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Run tests in verbose mode"
    )
    
    args = parser.parse_args()
    
    verbose_flag = "-v" if args.verbose else ""
    headed_flag = "--headed" if args.headed else ""
    
    success = True
    
    if args.test_type == "setup":
        # Test basic integration setup
        success = run_command(
            "python test_integration_setup.py",
            "Testing Integration Setup"
        )
    
    elif args.test_type == "unit":
        # Run only unit tests
        success = run_command(
            f'pytest tests/ -m "not integration" {verbose_flag}',
            "Running Unit Tests (56 tests)"
        )
    
    elif args.test_type == "integration":
        # Run only integration tests
        success = run_command(
            f"pytest tests/integration/ {verbose_flag} {headed_flag}",
            "Running Integration Tests (20 tests)"
        )
    
    elif args.test_type == "all":
        # Run all tests
        print("🚀 Running Complete Test Suite")
        
        # Unit tests first
        unit_success = run_command(
            f'pytest tests/ -m "not integration" {verbose_flag}',
            "Running Unit Tests (56 tests)"
        )
        
        # Integration tests
        integration_success = run_command(
            f"pytest tests/integration/ {verbose_flag} {headed_flag}",
            "Running Integration Tests (20 tests)"
        )
        
        success = unit_success and integration_success
        
        if success:
            print(f"\n🎉 All tests passed! Total: 76 tests")
        else:
            print(f"\n⚠️  Some tests failed. Check output above for details.")
    
    print(f"\n{'='*60}")
    if success:
        print("✅ Test run completed successfully!")
    else:
        print("❌ Test run completed with failures!")
    print(f"{'='*60}\n")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()