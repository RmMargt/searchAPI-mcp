"""
Test event loop cleanup behavior.
Verify that cleanup works in different event loop states.
"""
import asyncio
import os
import sys

# Set test environment
os.environ["SEARCHAPI_API_KEY"] = "test_api_key_123"

from config import APIConfig
from client import SearchAPIClient


def test_cleanup_with_no_loop():
    """Test cleanup when no event loop exists."""
    print("\n" + "="*70)
    print("Test 1: Cleanup with no event loop")
    print("="*70)

    config = APIConfig(api_key="test_key", enable_cache=False, enable_metrics=False)
    client = SearchAPIClient(config)

    # Close all event loops first
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.close()
    except RuntimeError:
        pass

    # Create new loop for cleanup
    asyncio.set_event_loop(asyncio.new_event_loop())

    # Now cleanup - should use asyncio.run()
    try:
        asyncio.run(client.close())
        print("✓ Cleanup succeeded with asyncio.run()")
        return True
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False


def test_cleanup_with_stopped_loop():
    """Test cleanup when event loop exists but is stopped."""
    print("\n" + "="*70)
    print("Test 2: Cleanup with stopped event loop")
    print("="*70)

    config = APIConfig(api_key="test_key", enable_cache=False, enable_metrics=False)
    client = SearchAPIClient(config)

    # Create a new event loop but don't run it
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Cleanup - should use run_until_complete()
    try:
        loop.run_until_complete(client.close())
        print("✓ Cleanup succeeded with run_until_complete()")
        loop.close()
        return True
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False


async def test_cleanup_with_running_loop_async():
    """Test cleanup when called from within a running event loop."""
    print("\n" + "="*70)
    print("Test 3: Cleanup within running event loop")
    print("="*70)

    config = APIConfig(api_key="test_key", enable_cache=False, enable_metrics=False)
    client = SearchAPIClient(config)

    # We're already in a running loop
    # Direct await should work
    try:
        await client.close()
        print("✓ Cleanup succeeded with direct await")
        return True
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False


def test_cleanup_robustness():
    """Test that cleanup doesn't crash on errors."""
    print("\n" + "="*70)
    print("Test 4: Cleanup robustness (error handling)")
    print("="*70)

    config = APIConfig(api_key="test_key", enable_cache=False, enable_metrics=False)
    client = SearchAPIClient(config)

    # Close client first
    asyncio.run(client.close())

    # Try to close again - should handle gracefully
    try:
        asyncio.run(client.close())
        print("✓ Cleanup succeeded even when called twice")
        return True
    except Exception as e:
        print(f"✗ Cleanup failed on second call: {e}")
        return False


def run_all_tests():
    """Run all event loop cleanup tests."""
    print("Testing Event Loop Cleanup Robustness")
    print("="*70)

    results = []

    # Test 1: No loop
    results.append(("No event loop", test_cleanup_with_no_loop()))

    # Test 2: Stopped loop
    results.append(("Stopped event loop", test_cleanup_with_stopped_loop()))

    # Test 3: Running loop
    async def run_async_test():
        return await test_cleanup_with_running_loop_async()

    results.append(("Running event loop", asyncio.run(run_async_test())))

    # Test 4: Robustness
    results.append(("Cleanup robustness", test_cleanup_robustness()))

    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
