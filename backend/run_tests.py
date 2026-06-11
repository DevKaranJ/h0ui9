import unittest
import sys
import logging

if __name__ == "__main__":
    # Configure root logger to output to stdout with specific format
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout
    )

    print("="*60)
    print("🚀 RUNNING ORDER FLOW TRADING TERMINAL TESTS")
    print("="*60)

    # Discover and run all tests in the backend folder
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='.', pattern='test_*.py')

    # Run with verbosity 2 to show each individual test method clearly
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the logs above.")
        sys.exit(1)
