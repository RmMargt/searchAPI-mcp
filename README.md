# SearchAPI MCP Server

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-Latest-green.svg)](https://github.com/jlowin/fastmcp)

A production-ready Model Context Protocol (MCP) server providing comprehensive search capabilities through SearchAPI.io. Enable AI assistants to search Google, Maps, Flights, Hotels, and more with built-in caching, retry logic, and circuit breakers.

一个基于 Model Context Protocol (MCP) 的生产级搜索服务器，通过 SearchAPI.io 提供全面的搜索功能。使 AI 助手能够搜索 Google、地图、航班、酒店等，内置缓存、重试逻辑和熔断器。

[Features](#features) • [Quick Start](#quick-start) • [Installation](#installation) • [Configuration](#configuration) • [Available Tools](#available-tools)

</div>

---

## Features

### 🔍 Search Engines
- **Google Search** - Web results, knowledge graph, answer boxes, related questions
- **Google Videos** - Video search with filtering by duration, source, and upload time
- **Google AI Mode** - AI-generated overviews with cited sources and structured content
- **Google Maps** - Places, businesses, reviews, and location details
- **Google Flights** - Flight search with comprehensive filtering and price calendars
- **Google Hotels** - Accommodation search with amenities, ratings, and price filters

### 🏗️ Production-Ready Architecture
- **Connection Pooling** - Efficient HTTP connection management with httpx
- **Response Caching** - Configurable TTL-based caching with LRU eviction
- **Retry Logic** - Exponential backoff for transient failures
- **Circuit Breaker** - Fail-safe pattern preventing cascading failures
- **Metrics Collection** - Request counts, latencies, cache hit rates, error tracking
- **Health Checks** - Monitor API connectivity and service status

### ⚙️ Configuration & Monitoring
- **Pydantic Validation** - Type-safe configuration with environment variable support
- **Structured Logging** - Configurable log levels with detailed request tracing
- **Resource Management** - Automatic cleanup and graceful shutdown
- **Environment Variables** - Flexible configuration for different deployments

---

## Quick Start

### Prerequisites
- Python 3.10 or higher
- SearchAPI.io API key ([Get one here](https://www.searchapi.io/))

### Installation with UV (Recommended)

The fastest way to get started is using `uvx`:

```bash
# Set your API key
export SEARCHAPI_API_KEY="your_api_key_here"

# Run directly with uvx (no installation needed)
uvx --from git+https://github.com/RmMargt/searchAPI-mcp.git mcp-server-searchapi
```

---

## Installation

### Method 1: UV (Recommended)

UV is the fastest and most convenient method:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/RmMargt/searchAPI-mcp.git
cd searchAPI-mcp

# Install dependencies
uv pip install -r requirements.txt
```

### Method 2: pip

```bash
# Clone the repository
git clone https://github.com/RmMargt/searchAPI-mcp.git
cd searchAPI-mcp

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Method 3: From Source

```bash
git clone https://github.com/RmMargt/searchAPI-mcp.git
cd searchAPI-mcp

# Using uv
uv pip install httpx fastmcp python-dotenv pydantic pydantic-settings

# Or using pip
pip install httpx fastmcp python-dotenv pydantic pydantic-settings
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
SEARCHAPI_API_KEY=your_api_key_here

# Optional - API Configuration
SEARCHAPI_API_URL=https://www.searchapi.io/api/v1/search
TIMEOUT=30.0
MAX_RETRIES=3
RETRY_BACKOFF=1.0

# Optional - Cache Configuration
ENABLE_CACHE=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Optional - Connection Pool
POOL_CONNECTIONS=10
POOL_MAXSIZE=10

# Optional - Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

### MCP Client Configuration

#### Claude Desktop

Add to your Claude Desktop configuration file:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Using UV (Recommended):**
```json
{
  "mcpServers": {
    "searchapi": {
      "command": "uvx",
      "args": [
        "--directory",
        "/absolute/path/to/searchAPI-mcp",
        "python",
        "mcp_server_refactored.py"
      ],
      "env": {
        "SEARCHAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Using Python directly:**
```json
{
  "mcpServers": {
    "searchapi": {
      "command": "python",
      "args": [
        "/absolute/path/to/searchAPI-mcp/mcp_server_refactored.py"
      ],
      "env": {
        "SEARCHAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Using virtual environment:**
```json
{
  "mcpServers": {
    "searchapi": {
      "command": "/absolute/path/to/searchAPI-mcp/venv/bin/python",
      "args": [
        "/absolute/path/to/searchAPI-mcp/mcp_server_refactored.py"
      ],
      "env": {
        "SEARCHAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### VS Code (Continue, Cline)

Add to `.vscode/mcp.json` in your workspace or use the "MCP: Open User Configuration" command:

```json
{
  "servers": {
    "searchapi": {
      "command": "python",
      "args": [
        "/absolute/path/to/searchAPI-mcp/mcp_server_refactored.py"
      ],
      "env": {
        "SEARCHAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**With UV:**
```json
{
  "servers": {
    "searchapi": {
      "command": "uvx",
      "args": [
        "--directory",
        "/absolute/path/to/searchAPI-mcp",
        "python",
        "mcp_server_refactored.py"
      ],
      "env": {
        "SEARCHAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Zed Editor

Add to `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "searchapi": {
      "command": {
        "path": "python",
        "args": [
          "/absolute/path/to/searchAPI-mcp/mcp_server_refactored.py"
        ],
        "env": {
          "SEARCHAPI_API_KEY": "your_api_key_here"
        }
      }
    }
  }
}
```

#### Cline (VS Code Extension)

In Cline settings, add to MCP Servers:

```json
{
  "mcpServers": {
    "searchapi": {
      "command": "python",
      "args": [
        "/absolute/path/to/searchAPI-mcp/mcp_server_refactored.py"
      ],
      "env": {
        "SEARCHAPI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Generic MCP Client

For any MCP-compatible client:

```bash
# Using stdio transport (default)
python /path/to/searchAPI-mcp/mcp_server_refactored.py

# With environment variable
SEARCHAPI_API_KEY=your_key python mcp_server_refactored.py
```

---

## Available Tools

### Health & Monitoring

#### `health_check`
Check the health and performance of the SearchAPI service.

**Returns:**
- API connectivity status
- Response latency
- Circuit breaker state
- Cache statistics
- Request metrics

**Example:**
```json
{
  "api_status": {
    "status": "healthy",
    "latency_ms": 145.23,
    "circuit_breaker": "closed"
  },
  "cache_stats": {
    "size": 42,
    "max_size": 1000,
    "ttl": 3600
  },
  "metrics": {
    "request_count": 156,
    "error_count": 2,
    "cache_hit_rate": 0.67
  }
}
```

---

### Time & Date Utilities

#### `get_current_time`
Get current time and travel date suggestions. Essential for flight and hotel bookings.

**Parameters:**
- `format` - Date format: "iso", "slash", "chinese", "timestamp", "full"
- `days_offset` - Days from today (can be negative)
- `return_future_dates` - Return array of future dates
- `future_days` - Number of future dates (if return_future_dates=true)

**Example:**
```python
# Get today's date in ISO format
get_current_time(format="iso")
# Returns: {"date": "2025-11-16", "now": {...}, "travel_dates": {...}}

# Get date 7 days from now with future dates array
get_current_time(days_offset=7, return_future_dates=True, future_days=30)
```

---

### Google Search

#### `search_google`
Search Google for web results, knowledge graphs, and answer boxes.

**Parameters:**
- `q` (required) - Search query
- `location` - Location name (e.g., "New York, NY")
- `gl` - Country code (default: "us")
- `hl` - Language code (default: "en")
- `time_period` - Time filter: "last_hour", "last_day", "last_week", "last_month", "last_year"
- `num` - Results per page (default: "10")
- `safe` - Safe search: "off", "active"

**Example:**
```python
search_google(
    q="Python programming tutorials",
    location="San Francisco, CA",
    time_period="last_month",
    num="20"
)
```

#### `search_google_videos`
Search Google Videos for video content.

**Parameters:** Similar to `search_google` with video-specific filters
- `q` (required) - Search query
- `time_period` - Filter by upload time
- `device` - "desktop" or "mobile"

**Example:**
```python
search_google_videos(
    q="machine learning tutorial",
    time_period="last_week",
    num="10"
)
```

#### `search_google_ai_mode`
Search with AI-generated overviews and cited sources.

**Parameters:**
- `q` - Search query (required unless url provided)
- `url` - Image URL to search
- `location` - Location for localized results

**Returns:**
- AI-generated overview with citations
- Structured content blocks (paragraphs, lists, tables, code)
- Reference links
- Web results

**Example:**
```python
search_google_ai_mode(
    q="How does machine learning work?",
    location="United States"
)
```

---

### Google Maps

#### `search_google_maps`
Search for places, businesses, and services.

**Parameters:**
- `query` (required) - Search query
- `location_ll` - Lat/lng coordinates (format: "@lat,lng,zoom")

**Example:**
```python
search_google_maps(
    query="coffee shops near Central Park",
    location_ll="@40.7829,-73.9654,15z"
)
```

#### `search_google_maps_reviews`
Get reviews for a specific place.

**Parameters:**
- `place_id` (required if no data_id) - Google Maps place ID
- `data_id` - Alternative place identifier
- `sort_by` - "most_relevant", "newest", "highest_rating", "lowest_rating"
- `rating` - Filter by rating: "1"-"5"

**Example:**
```python
search_google_maps_reviews(
    place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
    sort_by="newest",
    rating="5"
)
```

---

### Google Flights

#### `search_google_flights`
Search for flights with comprehensive filtering.

**Parameters:**
- `departure_id` (required) - Airport code (e.g., "JFK")
- `arrival_id` (required) - Airport code (e.g., "LAX")
- `outbound_date` (required) - Departure date (YYYY-MM-DD)
- `flight_type` - "one_way", "round_trip", "multi_city"
- `return_date` - Return date (required for round_trip)
- `travel_class` - "economy", "premium_economy", "business", "first"
- `stops` - "0" (nonstop), "1", "2"
- `adults` - Number of adults
- `currency` - Currency code (e.g., "USD")

**Example:**
```python
search_google_flights(
    departure_id="JFK",
    arrival_id="LAX",
    outbound_date="2025-12-15",
    return_date="2025-12-22",
    flight_type="round_trip",
    travel_class="economy",
    stops="0",
    adults="2"
)
```

#### `search_google_flights_calendar`
Get price calendar for flexible date planning.

**Parameters:**
- `flight_type` (required) - "one_way" or "round_trip"
- `departure_id` (required) - Airport code
- `arrival_id` (required) - Airport code
- `outbound_date` (required) - Reference date
- `return_date` - Required for round_trip

**Example:**
```python
search_google_flights_calendar(
    flight_type="round_trip",
    departure_id="SFO",
    arrival_id="NYC",
    outbound_date="2025-12-01",
    return_date="2025-12-08"
)
```

---

### Google Hotels

#### `search_google_hotels`
Search for hotels and accommodation.

**Parameters:**
- `q` (required) - Location query
- `check_in_date` (required) - Check-in date (YYYY-MM-DD)
- `check_out_date` (required) - Check-out date (YYYY-MM-DD)
- `adults` - Number of adults (default: "2")
- `rating` - Minimum rating: "3", "4", "5"
- `hotel_class` - Star rating: "2"-"5"
- `price_min` / `price_max` - Price range
- `amenities` - Filter by amenities (e.g., "pool,wifi,parking")
- `free_cancellation` - "true" or "false"

**Example:**
```python
search_google_hotels(
    q="hotels in Paris",
    check_in_date="2025-12-20",
    check_out_date="2025-12-25",
    adults="2",
    rating="4",
    amenities="wifi,pool",
    price_max="300",
    free_cancellation="true"
)
```

#### `search_google_hotels_property`
Get detailed information for a specific hotel.

**Parameters:**
- `property_token` (required) - Property ID from search results
- `check_in_date` (required) - Check-in date
- `check_out_date` (required) - Check-out date
- `adults` - Number of adults

**Example:**
```python
search_google_hotels_property(
    property_token="ChIJd8BlQ2BZwokRAFUEcm_qrcA",
    check_in_date="2025-12-20",
    check_out_date="2025-12-25",
    adults="2"
)
```

---

## Usage Examples

### Example 1: Plan a Trip

```python
# 1. Get current date and travel dates
dates = get_current_time(return_future_dates=True, future_days=30)
check_in = dates["travel_dates"]["next_week"]
check_out = dates["travel_dates"]["next_month"]

# 2. Search for flights
flights = search_google_flights(
    departure_id="JFK",
    arrival_id="CDG",
    outbound_date=check_in,
    return_date=check_out,
    flight_type="round_trip",
    travel_class="economy",
    adults="2"
)

# 3. Search for hotels
hotels = search_google_hotels(
    q="hotels in Paris",
    check_in_date=check_in,
    check_out_date=check_out,
    adults="2",
    rating="4",
    amenities="wifi,breakfast"
)

# 4. Find nearby restaurants
restaurants = search_google_maps(
    query="restaurants near Eiffel Tower"
)
```

### Example 2: Research with AI Mode

```python
# Get AI-generated overview with sources
result = search_google_ai_mode(
    q="What are the health benefits of Mediterranean diet?",
    location="United States"
)

# Result includes:
# - result["markdown"] - AI overview in markdown format
# - result["text_blocks"] - Structured content blocks
# - result["reference_links"] - Cited sources
# - result["web_results"] - Traditional search results
```

### Example 3: Monitor Service Health

```python
# Check API health and metrics
health = health_check()

print(f"Status: {health['api_status']['status']}")
print(f"Latency: {health['api_status']['latency_ms']}ms")
print(f"Cache hit rate: {health['metrics']['cache_hit_rate']:.2%}")
print(f"Total requests: {health['metrics']['request_count']}")
```

---

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python test_refactored.py
```

### Code Structure

```
searchAPI-mcp/
├── mcp_server_refactored.py  # Main MCP server with FastMCP
├── config.py                  # Configuration with Pydantic validation
├── client.py                  # HTTP client with pooling, retry, caching
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment variables
└── tests/                    # Test files
```

### Key Components

- **mcp_server_refactored.py** - MCP server implementation using FastMCP
  - Tool definitions with comprehensive docstrings
  - Health checks and monitoring endpoints
  - Clean shutdown and resource management

- **config.py** - Configuration management
  - Pydantic models for type-safe configuration
  - Environment variable validation
  - Sensible defaults with override options

- **client.py** - Production-ready HTTP client
  - Connection pooling with httpx
  - Exponential backoff retry logic
  - TTL-based response caching
  - Circuit breaker pattern
  - Metrics collection

### Debugging

Use the MCP Inspector to test tools:

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
npx @modelcontextprotocol/inspector python mcp_server_refactored.py
```

Set environment variable for verbose logging:

```bash
LOG_LEVEL=DEBUG python mcp_server_refactored.py
```

---

## Troubleshooting

### Common Issues

**Issue: "Invalid API key" error**
- Solution: Ensure `SEARCHAPI_API_KEY` is set correctly in environment or .env file
- Get an API key at https://www.searchapi.io/

**Issue: "Circuit breaker is OPEN" error**
- Cause: Too many consecutive API failures
- Solution: Check your internet connection and API key. Wait 60 seconds for circuit to reset, or restart the server

**Issue: Connection timeouts**
- Solution: Increase timeout in .env: `TIMEOUT=60.0`
- Check network connectivity to SearchAPI.io

**Issue: High latency**
- Solution: Enable caching if disabled: `ENABLE_CACHE=true`
- Increase cache size: `CACHE_MAX_SIZE=5000`
- Check `health_check` tool for metrics

**Issue: Windows encoding errors**
- Solution: Set environment variable in your MCP client config:
  ```json
  "env": {
    "PYTHONIOENCODING": "utf-8",
    "SEARCHAPI_API_KEY": "your_key"
  }
  ```

### Getting Help

- Check the [MCP Documentation](https://modelcontextprotocol.io/)
- Review [SearchAPI.io Documentation](https://www.searchapi.io/docs)
- Open an issue on [GitHub](https://github.com/RmMargt/searchAPI-mcp/issues)

---

## Performance Tuning

### Cache Configuration

For higher cache hit rates:
```bash
CACHE_TTL=7200        # 2 hours
CACHE_MAX_SIZE=5000   # Store more results
```

For memory-constrained environments:
```bash
CACHE_TTL=1800        # 30 minutes
CACHE_MAX_SIZE=100    # Smaller cache
```

### Connection Pool

For high-traffic scenarios:
```bash
POOL_CONNECTIONS=50
POOL_MAXSIZE=50
```

For low-traffic scenarios:
```bash
POOL_CONNECTIONS=5
POOL_MAXSIZE=5
```

---

## Security Considerations

⚠️ **Important Security Notes:**

1. **API Key Protection**
   - Never commit `.env` file to version control
   - Use environment variables in production
   - Rotate API keys regularly

2. **Rate Limiting**
   - SearchAPI.io has rate limits based on your plan
   - Built-in retry logic respects rate limits
   - Monitor usage with `health_check` tool

3. **Data Privacy**
   - Search queries are sent to SearchAPI.io
   - Responses are cached locally (configurable)
   - Review SearchAPI.io privacy policy

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Protocol specification by Anthropic
- **[FastMCP](https://github.com/jlowin/fastmcp)** - Python MCP framework
- **[SearchAPI.io](https://www.searchapi.io/)** - Search API service provider
- **[httpx](https://www.python-httpx.org/)** - Modern HTTP client for Python
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation framework

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Changelog

### v1.0.0 (Current)
- ✅ Production-ready architecture with FastMCP
- ✅ Connection pooling and retry logic
- ✅ Response caching with TTL
- ✅ Circuit breaker pattern
- ✅ Comprehensive health checks and metrics
- ✅ Google Search, Videos, AI Mode
- ✅ Google Maps and Reviews
- ✅ Google Flights and Calendar
- ✅ Google Hotels and Property details
- ✅ Time utilities for travel planning

---

<div align="center">

**[⬆ Back to Top](#searchapi-mcp-server)**

Made with ❤️ for the MCP community

</div>
