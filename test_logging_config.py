"""
Test that logging level configuration is properly applied.
"""
import os
import sys
import logging
from io import StringIO


def test_logging_level_configuration():
    """Test that LOG_LEVEL environment variable configures logging correctly."""
    print("\n" + "="*70)
    print("Testing Logging Level Configuration")
    print("="*70)

    # Test 1: Default INFO level
    print("\nTest 1: Default INFO level")
    os.environ["SEARCHAPI_API_KEY"] = "test_key_123"
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]

    # Capture log output
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)

    from config import load_config
    config = load_config()

    # Create logger and apply config level
    test_logger = logging.getLogger("test_default")
    test_logger.handlers.clear()
    test_logger.addHandler(handler)
    test_logger.setLevel(getattr(logging, config.log_level))

    # Default should be INFO
    assert config.log_level == "INFO", f"Expected INFO, got {config.log_level}"

    # INFO and higher should be logged
    test_logger.debug("This should NOT appear")
    test_logger.info("This SHOULD appear")
    test_logger.warning("This SHOULD appear")

    output = log_capture.getvalue()
    assert "This SHOULD appear" in output, "INFO messages should be logged"
    assert "This should NOT appear" not in output, "DEBUG messages should not be logged"
    print("✓ Default INFO level works correctly")

    # Test 2: DEBUG level
    print("\nTest 2: DEBUG level from environment")
    os.environ["LOG_LEVEL"] = "DEBUG"

    # Need to reload config module to pick up new env var
    import importlib
    import config as config_module
    importlib.reload(config_module)
    from config import load_config

    config = load_config()
    assert config.log_level == "DEBUG", f"Expected DEBUG, got {config.log_level}"

    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)

    test_logger = logging.getLogger("test_debug")
    test_logger.handlers.clear()
    test_logger.addHandler(handler)
    test_logger.setLevel(getattr(logging, config.log_level))

    # DEBUG and higher should all be logged
    test_logger.debug("DEBUG message")
    test_logger.info("INFO message")

    output = log_capture.getvalue()
    assert "DEBUG message" in output, "DEBUG messages should be logged when level=DEBUG"
    assert "INFO message" in output, "INFO messages should be logged when level=DEBUG"
    print("✓ DEBUG level from environment works correctly")

    # Test 3: ERROR level
    print("\nTest 3: ERROR level from environment")
    os.environ["LOG_LEVEL"] = "ERROR"

    importlib.reload(config_module)
    from config import load_config

    config = load_config()
    assert config.log_level == "ERROR", f"Expected ERROR, got {config.log_level}"

    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)

    test_logger = logging.getLogger("test_error")
    test_logger.handlers.clear()
    test_logger.addHandler(handler)
    test_logger.setLevel(getattr(logging, config.log_level))

    # Only ERROR and higher should be logged
    test_logger.debug("DEBUG should NOT appear")
    test_logger.info("INFO should NOT appear")
    test_logger.warning("WARNING should NOT appear")
    test_logger.error("ERROR SHOULD appear")

    output = log_capture.getvalue()
    assert "ERROR SHOULD appear" in output, "ERROR messages should be logged when level=ERROR"
    assert "DEBUG should NOT appear" not in output, "DEBUG should be filtered at ERROR level"
    assert "INFO should NOT appear" not in output, "INFO should be filtered at ERROR level"
    assert "WARNING should NOT appear" not in output, "WARNING should be filtered at ERROR level"
    print("✓ ERROR level from environment works correctly")

    print("\n" + "="*70)
    print("All logging configuration tests passed!")
    print("="*70)


if __name__ == "__main__":
    try:
        test_logging_level_configuration()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
