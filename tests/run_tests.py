import os
import sys

import pytest

if __name__ == "__main__":
    # Ensure the tests directory exists
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    if not os.path.exists(test_dir):
        print("❌ Tests directory not found!")
        sys.exit(1)

    # Define default pytest options
    pytest_args = [
        "-v",  # Verbose mode
        "--tb=short",  # Show short tracebacks for failed tests
        "--log-cli-level=INFO",  # Enable logging in CLI
        "--disable-warnings",  # Suppress warnings
        f"--rootdir={test_dir}",  # Set root directory for tests
    ]

    # Allow additional arguments to be passed via CLI
    pytest_args.extend(sys.argv[1:])

    # Run pytest and capture the exit code
    exit_code = pytest.main(pytest_args)

    # Exit with the pytest exit code (useful for CI/CD)
    sys.exit(exit_code)
