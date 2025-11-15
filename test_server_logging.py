"""
Test that the server properly applies logging configuration on startup.
"""
import os
import sys
import logging
from io import StringIO


def test_server_logging_initialization():
    """Test that server applies log level from config on initialization."""
    print("\n" + "="*70)
    print("Testing Server Logging Initialization")
    print("="*70)

    # Set DEBUG level
    os.environ["SEARCHAPI_API_KEY"] = "test_key_for_logging_test"
    os.environ["LOG_LEVEL"] = "DEBUG"

    # Capture logging output
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

    # Import server module (this triggers config load and logging setup)
    # We can't run the full server, but we can verify the module initializes correctly
    print("\nImporting server module with DEBUG level...")

    # Save original handlers to restore later
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]

    try:
        # Clear existing handlers and add our test handler
        root_logger.handlers.clear()
        root_logger.addHandler(handler)

        # Import the server module - this will load config and set logging level
        import mcp_server_refactored

        # Check that config was loaded with DEBUG level
        assert mcp_server_refactored.config.log_level == "DEBUG", \
            f"Expected DEBUG, got {mcp_server_refactored.config.log_level}"

        # Check that root logger level was updated
        current_level = logging.getLogger().level
        expected_level = logging.DEBUG
        assert current_level == expected_level, \
            f"Root logger level should be {expected_level} (DEBUG), got {current_level}"

        # Test that DEBUG messages are actually logged
        test_logger = logging.getLogger("test_server")
        test_logger.debug("Test DEBUG message")
        test_logger.info("Test INFO message")

        output = log_capture.getvalue()
        assert "Test DEBUG message" in output, "DEBUG messages should be logged"
        assert "Test INFO message" in output, "INFO messages should be logged"

        print("✓ Server correctly initialized with DEBUG level")
        print(f"✓ Root logger level: {logging.getLevelName(current_level)}")
        print(f"✓ Config log_level: {mcp_server_refactored.config.log_level}")

    finally:
        # Restore original handlers
        root_logger.handlers.clear()
        for h in original_handlers:
            root_logger.addHandler(h)

    # Test 2: Verify INFO level (default)
    print("\nTest 2: Default INFO level")
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]

    # Reload the module
    import importlib
    importlib.reload(mcp_server_refactored)

    assert mcp_server_refactored.config.log_level == "INFO", \
        f"Expected INFO as default, got {mcp_server_refactored.config.log_level}"

    print("✓ Server correctly uses INFO as default level")

    print("\n" + "="*70)
    print("Server logging initialization tests passed!")
    print("="*70)


if __name__ == "__main__":
    try:
        test_server_logging_initialization()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
