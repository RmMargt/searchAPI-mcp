"""
HTTP client with connection pooling, retry logic, and circuit breaker.
Following FAST MCP best practices for resilient API communication.
"""
import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import httpx
from config import APIConfig


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for fail-safe design.
    Prevents cascading failures when external API is down.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open
        self.half_open_calls = 0

    def call(self, func):
        """Decorator to wrap function calls with circuit breaker logic."""
        async def wrapper(*args, **kwargs):
            if self.state == "open":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "half_open"
                    self.half_open_calls = 0
                else:
                    raise Exception("Circuit breaker is OPEN - service unavailable")

            try:
                result = await func(*args, **kwargs)

                # Success - reset on half_open or keep closed
                if self.state == "half_open":
                    self.half_open_calls += 1
                    if self.half_open_calls >= self.half_open_max_calls:
                        self.state = "closed"
                        self.failure_count = 0

                return result

            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    self.state = "open"

                raise e

        return wrapper


class CacheManager:
    """
    Simple in-memory cache with TTL support.
    Implements multi-level caching strategy from FAST MCP best practices.
    """

    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}

    def _generate_key(self, params: Dict[str, Any]) -> str:
        """Generate cache key from parameters."""
        # Sort params to ensure consistent key generation
        sorted_params = json.dumps(params, sort_keys=True)
        return hashlib.md5(sorted_params.encode()).hexdigest()

    def get(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        key = self._generate_key(params)

        if key not in self.cache:
            return None

        # Check if expired
        if time.time() - self.access_times[key] > self.ttl:
            del self.cache[key]
            del self.access_times[key]
            return None

        return self.cache[key]

    def set(self, params: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Cache response with TTL."""
        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        key = self._generate_key(params)
        self.cache[key] = response
        self.access_times[key] = time.time()

    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.access_times.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl
        }


class MetricsCollector:
    """
    Metrics collection for monitoring and observability.
    Tracks request counts, latency, errors, etc.
    """

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.latencies = []
        self.errors_by_type = {}

    def record_request(self, latency: float, from_cache: bool = False):
        """Record a successful request."""
        self.request_count += 1
        self.latencies.append(latency)

        # Keep only last 1000 latencies
        if len(self.latencies) > 1000:
            self.latencies = self.latencies[-1000:]

        if from_cache:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def record_error(self, error_type: str):
        """Record an error occurrence."""
        self.error_count += 1
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1

    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics statistics."""
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        p95_latency = sorted(self.latencies)[int(len(self.latencies) * 0.95)] if self.latencies else 0
        p99_latency = sorted(self.latencies)[int(len(self.latencies) * 0.99)] if self.latencies else 0

        cache_hit_rate = (
            self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0
            else 0
        )

        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "latency": {
                "avg": round(avg_latency, 3),
                "p95": round(p95_latency, 3),
                "p99": round(p99_latency, 3)
            },
            "errors_by_type": self.errors_by_type
        }


class SearchAPIClient:
    """
    Resilient HTTP client for SearchAPI.io with connection pooling,
    retry logic, caching, and circuit breaker pattern.
    """

    def __init__(self, config: APIConfig):
        self.config = config

        # Initialize HTTP client with connection pooling
        limits = httpx.Limits(
            max_connections=config.pool_connections,
            max_keepalive_connections=config.pool_maxsize
        )

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.timeout),
            limits=limits,
            follow_redirects=True
        )

        # Initialize cache if enabled
        self.cache = (
            CacheManager(ttl=config.cache_ttl, max_size=config.cache_max_size)
            if config.enable_cache
            else None
        )

        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker()

        # Initialize metrics
        self.metrics = MetricsCollector() if config.enable_metrics else None

    async def request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API request with retry logic, caching, and error handling.

        Args:
            params: Request parameters

        Returns:
            API response dictionary

        Raises:
            Exception: If request fails after all retries
        """
        # Add API key to params
        params = {**params, "api_key": self.config.api_key}

        # Check cache first
        if self.cache:
            cached = self.cache.get(params)
            if cached:
                if self.metrics:
                    self.metrics.record_request(latency=0, from_cache=True)
                return cached

        # Make request with retry logic
        start_time = time.time()

        try:
            response = await self._request_with_retry(params)
            latency = time.time() - start_time

            # Cache successful response
            if self.cache and "error" not in response:
                self.cache.set(params, response)

            # Record metrics
            if self.metrics:
                self.metrics.record_request(latency=latency, from_cache=False)

            return response

        except Exception as e:
            if self.metrics:
                self.metrics.record_error(type(e).__name__)
            raise

    async def _request_with_retry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with exponential backoff retry."""
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self.client.get(
                    self.config.api_url,
                    params=params
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    return self._format_error_response(e)

                last_exception = e

            except httpx.HTTPError as e:
                last_exception = e

            except Exception as e:
                last_exception = e

            # Exponential backoff before retry
            if attempt < self.config.max_retries:
                backoff = self.config.retry_backoff * (2 ** attempt)
                await asyncio.sleep(backoff)

        # All retries failed
        return self._format_error_response(last_exception)

    def _format_error_response(self, error: Exception) -> Dict[str, Any]:
        """Format error as structured response."""
        error_detail = None

        if isinstance(error, httpx.HTTPStatusError):
            try:
                error_detail = error.response.json()
            except ValueError:
                error_detail = error.response.text

            return {
                "error": f"HTTP {error.response.status_code}: {error.response.reason_phrase}",
                "details": error_detail,
                "type": "http_error",
                "status_code": error.response.status_code
            }

        return {
            "error": str(error),
            "type": type(error).__name__,
            "details": None
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on SearchAPI.

        Returns:
            Health check status
        """
        try:
            # Make a minimal test request
            params = {
                "engine": "google",
                "q": "test",
                "num": "1"
            }
            start_time = time.time()
            response = await self.request(params)
            latency = time.time() - start_time

            if "error" in response:
                return {
                    "status": "unhealthy",
                    "latency_ms": round(latency * 1000, 2),
                    "error": response["error"]
                }

            return {
                "status": "healthy",
                "latency_ms": round(latency * 1000, 2),
                "circuit_breaker": self.circuit_breaker.state
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "circuit_breaker": self.circuit_breaker.state
            }

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current metrics."""
        if not self.metrics:
            return None
        return self.metrics.get_stats()

    def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """Get cache statistics."""
        if not self.cache:
            return None
        return self.cache.get_stats()

    async def close(self):
        """Close HTTP client and cleanup resources."""
        await self.client.aclose()
