"""
Test suite for the refactored SearchAPI MCP Server.
Following FAST MCP best practices for testing.
"""
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    print("pytest not installed - running basic tests only")
    print("Install pytest for full test suite: pip install pytest pytest-asyncio\n")

# Set test environment variables before importing modules
os.environ["SEARCHAPI_API_KEY"] = "test_api_key_123"

from config import load_config, APIConfig
from client import SearchAPIClient, CacheManager, MetricsCollector, CircuitBreaker


class TestConfiguration:
    """Test configuration management."""

    def test_config_validation_with_valid_key(self):
        """Test that valid configuration loads successfully."""
        with patch.dict(os.environ, {"SEARCHAPI_API_KEY": "valid_key_123"}):
            config = load_config()
            assert config.api_key == "valid_key_123"
            assert config.timeout == 30.0
            assert config.enable_cache is True

    def test_config_validation_with_invalid_key(self):
        """Test that invalid API keys are rejected."""
        with patch.dict(os.environ, {"SEARCHAPI_API_KEY": "your_api_key_here"}):
            with pytest.raises(ValueError):
                load_config()

    def test_config_defaults(self):
        """Test that configuration defaults are set correctly."""
        with patch.dict(os.environ, {"SEARCHAPI_API_KEY": "test_key"}):
            config = load_config()
            assert config.api_url == "https://www.searchapi.io/api/v1/search"
            assert config.max_retries == 3
            assert config.cache_ttl == 3600
            assert config.pool_connections == 10


class TestCacheManager:
    """Test cache functionality."""

    def test_cache_set_and_get(self):
        """Test basic cache operations."""
        cache = CacheManager(ttl=3600, max_size=100)
        params = {"engine": "google", "q": "test"}
        response = {"results": ["result1", "result2"]}

        cache.set(params, response)
        cached = cache.get(params)

        assert cached == response

    def test_cache_miss(self):
        """Test cache miss scenario."""
        cache = CacheManager(ttl=3600, max_size=100)
        params = {"engine": "google", "q": "test"}

        cached = cache.get(params)
        assert cached is None

    def test_cache_expiration(self):
        """Test cache TTL expiration."""
        cache = CacheManager(ttl=0, max_size=100)  # Immediate expiration
        params = {"engine": "google", "q": "test"}
        response = {"results": ["result1"]}

        cache.set(params, response)
        # Wait for expiration
        import time
        time.sleep(0.1)
        cached = cache.get(params)

        assert cached is None

    def test_cache_max_size_eviction(self):
        """Test that cache evicts oldest items when full."""
        cache = CacheManager(ttl=3600, max_size=2)

        cache.set({"q": "1"}, {"result": "1"})
        cache.set({"q": "2"}, {"result": "2"})
        cache.set({"q": "3"}, {"result": "3"})  # Should evict first item

        assert cache.get({"q": "1"}) is None
        assert cache.get({"q": "2"}) is not None
        assert cache.get({"q": "3"}) is not None


class TestMetricsCollector:
    """Test metrics collection."""

    def test_record_request(self):
        """Test request metrics recording."""
        metrics = MetricsCollector()

        metrics.record_request(latency=0.5, from_cache=False)
        metrics.record_request(latency=0.3, from_cache=True)

        stats = metrics.get_stats()
        assert stats["request_count"] == 2
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1

    def test_record_error(self):
        """Test error metrics recording."""
        metrics = MetricsCollector()

        metrics.record_error("HTTPError")
        metrics.record_error("HTTPError")
        metrics.record_error("TimeoutError")

        stats = metrics.get_stats()
        assert stats["error_count"] == 3
        assert stats["errors_by_type"]["HTTPError"] == 2
        assert stats["errors_by_type"]["TimeoutError"] == 1

    def test_latency_percentiles(self):
        """Test latency percentile calculations."""
        metrics = MetricsCollector()

        for i in range(100):
            metrics.record_request(latency=i / 100.0)

        stats = metrics.get_stats()
        assert "latency" in stats
        assert "avg" in stats["latency"]
        assert "p95" in stats["latency"]
        assert "p99" in stats["latency"]


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    async def test_circuit_breaker_opens_on_failures(self):
        """Test that circuit breaker opens after threshold failures."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        async def failing_function():
            raise Exception("Test failure")

        wrapped = cb.call(failing_function)

        # Cause failures to open circuit
        for _ in range(3):
            try:
                await wrapped()
            except Exception:
                pass

        assert cb.state == "open"

        # Next call should fail immediately
        if PYTEST_AVAILABLE:
            with pytest.raises(Exception, match="Circuit breaker is OPEN"):
                await wrapped()
        else:
            # Manual check when pytest not available
            try:
                await wrapped()
                assert False, "Should have raised exception when circuit is OPEN"
            except Exception as e:
                assert "Circuit breaker is OPEN" in str(e)


class TestSearchAPIClient:
    """Test SearchAPI client functionality."""

    async def test_circuit_breaker_integration(self):
        """Test that circuit breaker is wired into request path."""
        config = APIConfig(api_key="test_key", enable_cache=False, enable_metrics=False)
        client = SearchAPIClient(config)

        # Initially circuit should be closed
        assert client.circuit_breaker.state == "closed"

        # Mock to always fail
        async def failing_request(*args, **kwargs):
            raise Exception("API Error")

        with patch.object(client, '_request_with_retry', new=failing_request):
            # Make 5 failing requests to open circuit
            for _ in range(5):
                try:
                    await client.request({"engine": "google", "q": "test"})
                except Exception:
                    pass

            # Circuit should now be open
            assert client.circuit_breaker.state == "open"

            # Next request should fail immediately without hitting API
            try:
                await client.request({"engine": "google", "q": "test"})
                assert False, "Should have raised circuit breaker exception"
            except Exception as e:
                assert "Circuit breaker is OPEN" in str(e)

        await client.close()

    async def test_client_initialization(self):
        """Test client initializes with correct configuration."""
        config = APIConfig(
            api_key="test_key",
            enable_cache=True,
            enable_metrics=True
        )
        client = SearchAPIClient(config)

        assert client.cache is not None
        assert client.metrics is not None
        assert client.config.api_key == "test_key"

        await client.close()

    async def test_request_caching(self):
        """Test that responses are cached correctly."""
        config = APIConfig(api_key="test_key", enable_cache=True)
        client = SearchAPIClient(config)

        params = {"engine": "google", "q": "test"}
        mock_response = {"results": ["test"]}

        # Mock the HTTP request
        with patch.object(client, '_request_with_retry', new=AsyncMock(return_value=mock_response)):
            # First request - should hit API
            result1 = await client.request(params)
            # Second request - should hit cache
            result2 = await client.request(params)

            assert result1 == result2
            # _request_with_retry should only be called once due to caching
            assert client._request_with_retry.call_count == 1

        await client.close()

    async def test_health_check(self):
        """Test health check functionality."""
        config = APIConfig(api_key="test_key")
        client = SearchAPIClient(config)

        mock_response = {"organic_results": []}

        with patch.object(client, 'request', new=AsyncMock(return_value=mock_response)):
            health = await client.health_check()

            assert "status" in health
            assert health["status"] == "healthy"
            assert "latency_ms" in health

        await client.close()

    async def test_error_handling(self):
        """Test error response formatting."""
        config = APIConfig(api_key="test_key", enable_cache=False)
        client = SearchAPIClient(config)

        # Mock HTTP error
        mock_error = Exception("Test error")

        with patch.object(client, '_request_with_retry', new=AsyncMock(side_effect=mock_error)):
            with pytest.raises(Exception):
                await client.request({"engine": "google", "q": "test"})

        await client.close()


async def run_async_tests():
    """Run async tests."""
    print("\n" + "="*70)
    print("Testing Circuit Breaker Integration")
    print("="*70)

    try:
        test_client = TestSearchAPIClient()
        await test_client.test_circuit_breaker_integration()
        print("✓ Circuit breaker integration test passed")
    except Exception as e:
        print(f"✗ Circuit breaker integration test failed: {e}")
        import traceback
        traceback.print_exc()


def run_tests():
    """Run all tests."""
    print("Running SearchAPI MCP Server Tests...")
    print("\n" + "="*70)
    print("Testing Configuration Management")
    print("="*70)

    # Test configuration
    try:
        test_config = TestConfiguration()
        test_config.test_config_defaults()
        print("✓ Configuration defaults test passed")
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")

    print("\n" + "="*70)
    print("Testing Cache Manager")
    print("="*70)

    # Test cache
    try:
        test_cache = TestCacheManager()
        test_cache.test_cache_set_and_get()
        print("✓ Cache set/get test passed")

        test_cache.test_cache_miss()
        print("✓ Cache miss test passed")

        test_cache.test_cache_max_size_eviction()
        print("✓ Cache eviction test passed")
    except Exception as e:
        print(f"✗ Cache test failed: {e}")

    print("\n" + "="*70)
    print("Testing Metrics Collector")
    print("="*70)

    # Test metrics
    try:
        test_metrics = TestMetricsCollector()
        test_metrics.test_record_request()
        print("✓ Metrics request recording test passed")

        test_metrics.test_record_error()
        print("✓ Metrics error recording test passed")

        test_metrics.test_latency_percentiles()
        print("✓ Metrics latency percentiles test passed")
    except Exception as e:
        print(f"✗ Metrics test failed: {e}")

    # Run async tests
    try:
        asyncio.run(run_async_tests())
    except Exception as e:
        print(f"✗ Async tests failed: {e}")

    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print("All basic tests completed. Run with pytest for full async tests.")
    print("\nTo run full test suite with pytest:")
    print("  pip install pytest pytest-asyncio")
    print("  pytest test_refactored.py -v")


if __name__ == "__main__":
    run_tests()
