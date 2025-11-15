# SearchAPI MCP Server - Refactoring Notes

## Overview

This codebase has been refactored following **FAST MCP best practices** for production-ready Model Context Protocol servers. The refactoring focuses on:

1. **Configuration Management** - Pydantic-based validation and environment variable handling
2. **Resilient HTTP Client** - Connection pooling, retry logic, and circuit breaker pattern
3. **Performance Optimization** - Multi-level caching with TTL
4. **Error Handling** - Structured error responses with proper classification
5. **Monitoring & Observability** - Metrics collection and health checks
6. **Production Readiness** - Logging, graceful degradation, and fail-safe design

---

## Architecture Changes

### File Structure

```
searchAPI-mcp/
├── config.py                    # NEW: Configuration management with Pydantic
├── client.py                    # NEW: HTTP client with resilience patterns
├── mcp_server_refactored.py     # NEW: Refactored MCP server
├── mcp_server.py                # ORIGINAL: Legacy server (kept for reference)
├── test_refactored.py           # NEW: Test suite
├── requirements.txt             # UPDATED: Added Pydantic dependencies
├── .env.example                 # EXISTING: Environment template
└── README.md                    # EXISTING: Main documentation
```

### Key Components

#### 1. Configuration Module (`config.py`)

**Following FAST MCP Best Practice**: Externalized configuration with startup validation

Features:
- Pydantic models for type-safe configuration
- Environment variable validation at startup
- Configurable timeouts, retries, cache settings
- Prevents invalid API keys (e.g., "your_api_key_here")

```python
from config import load_config

config = load_config()  # Raises ValueError if invalid
```

#### 2. HTTP Client (`client.py`)

**Following FAST MCP Best Practices**: Resilient communication with external APIs

Components:

**a) CacheManager**
- In-memory cache with TTL (default: 1 hour)
- LRU eviction when max size reached
- Reduces API calls and improves latency
- Cache hit rate tracking

**b) CircuitBreaker**
- Prevents cascading failures
- Opens after 5 consecutive failures
- Auto-recovery after 60 seconds
- Half-open state for gradual recovery

**c) MetricsCollector**
- Request count and latency tracking
- P95/P99 latency percentiles
- Cache hit rate monitoring
- Error classification and counting

**d) SearchAPIClient**
- Connection pooling (default: 10 connections)
- Exponential backoff retry (max 3 retries)
- Structured error responses
- Health check endpoint
- Automatic resource cleanup

#### 3. MCP Server (`mcp_server_refactored.py`)

**Following FAST MCP Best Practices**: Production-ready tool design

Improvements:
- **Comprehensive Tool Descriptions**: Each tool has detailed docstrings explaining:
  - Purpose and use cases
  - All parameters with examples
  - Return value structure
  - Usage examples
  - Cross-references to related tools

- **Input Validation**: Validates required parameters before making API calls

- **Better Error Messages**: Structured error responses with type classification

- **Health Check Tool**: New `health_check()` tool for monitoring

- **Enhanced Date Tool**: `get_current_time()` includes travel date suggestions

- **Google AI Mode**: New tool for AI-powered search with overview generation

---

## New Features

### 1. Health Check & Monitoring

```python
# Check service health
await health_check()

# Returns:
{
  "api_status": {
    "status": "healthy",
    "latency_ms": 245.3,
    "circuit_breaker": "closed"
  },
  "cache_stats": {
    "size": 42,
    "max_size": 1000,
    "ttl": 3600
  },
  "metrics": {
    "request_count": 150,
    "error_count": 2,
    "error_rate": 0.013,
    "cache_hit_rate": 0.35,
    "latency": {
      "avg": 0.234,
      "p95": 0.456,
      "p99": 0.678
    }
  }
}
```

### 2. Google AI Mode Search

New tool for AI-powered search with comprehensive overviews:

```python
await search_google_ai_mode(
    q="How does photosynthesis work?",
    location="San Francisco, CA"
)

# Returns:
{
  "text_blocks": [
    {
      "type": "header",
      "answer": "Photosynthesis Overview",
      "reference_indexes": [1, 3]
    },
    {
      "type": "paragraph",
      "answer": "Photosynthesis is the process...",
      "reference_indexes": [1, 2, 3]
    },
    {
      "type": "ordered_list",
      "items": [...]
    }
  ],
  "markdown": "## Photosynthesis Overview\n\nPhotosynthesis...[^1][^2]",
  "reference_links": [
    {
      "index": 1,
      "title": "Photosynthesis - Wikipedia",
      "link": "https://...",
      "source": "Wikipedia"
    }
  ],
  "web_results": [...],
  "local_results": [...]
}
```

### 3. Response Caching

Automatic caching of API responses:
- **Default TTL**: 1 hour (3600 seconds)
- **Cache Size**: 1000 items (LRU eviction)
- **Configurable**: Via environment variables

Benefits:
- Faster response times for repeated queries
- Reduced API costs
- Lower API rate limit impact

### 4. Circuit Breaker

Automatic failure protection:
- **Threshold**: 5 consecutive failures
- **Recovery Time**: 60 seconds
- **States**: Closed → Open → Half-Open → Closed

Prevents wasting resources on unavailable services.

### 5. Retry Logic

Exponential backoff retry:
- **Max Retries**: 3 attempts
- **Backoff**: 1s → 2s → 4s
- **Smart Retry**: Doesn't retry 4xx client errors

---

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Required
SEARCHAPI_API_KEY=your_actual_api_key

# Optional - HTTP Client
TIMEOUT=30.0                    # Request timeout (seconds)
MAX_RETRIES=3                   # Retry attempts
RETRY_BACKOFF=1.0              # Backoff multiplier
POOL_CONNECTIONS=10            # Connection pool size
POOL_MAXSIZE=10                # Max connections per pool

# Optional - Cache
ENABLE_CACHE=true              # Enable response caching
CACHE_TTL=3600                 # Cache lifetime (seconds)
CACHE_MAX_SIZE=1000            # Max cached items

# Optional - Monitoring
ENABLE_METRICS=true            # Enable metrics collection
LOG_LEVEL=INFO                 # Logging level

# Optional - Server
MCP_TRANSPORT=stdio            # MCP transport type
```

### Claude Desktop Configuration

**Using Refactored Server:**

```json
{
  "mcpServers": {
    "searchapi": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "/path/to/searchAPI-mcp/mcp_server_refactored.py"
      ],
      "env": {
        "SEARCHAPI_API_KEY": "your_api_key_here",
        "ENABLE_CACHE": "true",
        "CACHE_TTL": "3600",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## Installation

### 1. Install Dependencies

```bash
# Install updated requirements
pip install -r requirements.txt

# Or install individually
pip install httpx>=0.24.0 fastmcp>=0.1.0 python-dotenv>=1.0.0 pydantic>=2.0.0 pydantic-settings>=2.0.0
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your API key
nano .env
```

### 3. Run Server

```bash
# Run refactored server
python mcp_server_refactored.py

# Or with uv
uv run mcp_server_refactored.py
```

---

## Testing

### Run Tests

```bash
# Basic test runner
python test_refactored.py

# Full test suite with pytest
pip install pytest pytest-asyncio
pytest test_refactored.py -v

# With coverage
pytest test_refactored.py --cov=. --cov-report=html
```

### Test Coverage

The test suite includes:
- ✓ Configuration validation
- ✓ Cache operations (set, get, expiration, eviction)
- ✓ Metrics collection (requests, errors, latency)
- ✓ Circuit breaker behavior
- ✓ HTTP client initialization
- ✓ Request caching
- ✓ Health checks
- ✓ Error handling

---

## Performance Improvements

### Benchmarks (Estimated)

| Metric | Original | Refactored | Improvement |
|--------|----------|------------|-------------|
| Cache Hit Response | N/A | <10ms | ∞ |
| Repeated Queries | ~300ms | ~10ms | 30x faster |
| Connection Setup | Per request | Pooled | ~50ms saved |
| Failed Requests | No retry | 3 retries | +resilience |
| Circuit Break | No | Yes | +stability |

### Cache Hit Rate

Expected cache hit rates:
- **Repeated Queries**: ~80-90%
- **Exploratory Use**: ~20-40%
- **Production**: ~50-70%

---

## Migration Guide

### From Original to Refactored

**No Changes Required for:**
- Tool names and parameters
- API responses
- MCP client configuration (except file path)

**Optional Enhancements:**
1. Configure cache TTL based on use case
2. Adjust retry settings for network conditions
3. Enable/disable metrics collection
4. Set custom logging levels

**Breaking Changes:**
- None - fully backward compatible

---

## Best Practices Applied

### 1. Single Responsibility Principle
Each module has one clear purpose:
- `config.py` → Configuration
- `client.py` → HTTP communication
- `mcp_server_refactored.py` → MCP tool definitions

### 2. Defense in Depth
Multiple security layers:
- Input validation (Pydantic)
- API key validation
- Error handling
- Rate limiting (via retry backoff)

### 3. Fail-Safe Design
- Circuit breaker prevents cascading failures
- Cache fallback for degraded service
- Graceful error responses
- No crashes on invalid config

### 4. Performance Optimization
- Connection pooling
- Response caching
- Async/await throughout
- Efficient retry logic

### 5. Observability
- Structured logging
- Metrics collection
- Health checks
- Request timing

---

## Troubleshooting

### Issue: Configuration Error

```
ValueError: Invalid API key. Please set SEARCHAPI_API_KEY environment variable.
```

**Solution**: Set valid API key in `.env` file or environment.

### Issue: Circuit Breaker Open

```
error: "Circuit breaker is OPEN - service unavailable"
```

**Solution**: Wait 60 seconds for auto-recovery or check SearchAPI service status.

### Issue: Cache Not Working

**Check**:
1. `ENABLE_CACHE=true` in environment
2. Queries are identical (parameters must match exactly)
3. Cache hasn't expired (default 1 hour TTL)

### Issue: Slow First Request

**Expected**: First request is slower due to:
1. Connection pool initialization
2. Circuit breaker warmup
3. No cache hit

Subsequent requests will be much faster.

---

## Future Enhancements

Potential improvements:
- [ ] Redis cache backend for multi-instance deployments
- [ ] Prometheus metrics export
- [ ] OpenTelemetry tracing
- [ ] Rate limit handling with backoff
- [ ] Request queue for high-volume scenarios
- [ ] WebSocket transport support
- [ ] OAuth authentication for SearchAPI

---

## References

- [FAST MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/specification/2025-06-18)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [HTTPX Documentation](https://www.python-httpx.org/)

---

## Support

For issues or questions:
1. Check this document first
2. Review test suite for examples
3. Check configuration in `.env`
4. Review logs for error details
5. Open GitHub issue with logs and config (sanitize API keys!)

---

**Last Updated**: 2025-11-15
**Version**: 1.0.0 (Refactored)
