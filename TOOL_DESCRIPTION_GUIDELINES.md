# MCP Tool Description Guidelines

## FastMCP Best Practices for Context Optimization

### Core Principles

1. **Concise Summary** - 1-2 sentences maximum for the main description
2. **Lean Args** - One-line parameter descriptions, rely on type hints
3. **Minimal Examples** - 1-2 most common use cases only
4. **Remove Verbose Returns** - Let the actual response speak for itself
5. **No Redundant Notes** - Include only critical warnings

### Before vs After Example

#### ❌ BEFORE (Verbose - ~70 lines)

```python
@mcp.tool()
async def search_google_videos(
    q: str,
    device: str = "desktop",
    # ... many parameters
) -> Dict[str, Any]:
    """
    Search Google Videos for video content.

    Returns video search results including:
    - Video list results
    - Video carousel (featured videos)
    - Short video content (Shorts)
    - Video metadata (duration, source, upload date)

    Args:
        q: Search query (required)
        device: Device type ("desktop" or "mobile") - affects result format
        location: Location for localized results
        uule: Google's encoded location parameter
        google_domain: Google domain (default: "google.com")
        gl: Country code (default: "us")
        hl: Language code (default: "en")
        lr: Language restriction
        cr: Country restriction
        nfpr: Personalization ("0" = off, "1" = on)
        filter: Duplicate filter ("0" = off, "1" = on)
        safe: Safe search ("off", "active")
        time_period: Time filter (e.g., "last_hour", "last_day", "last_week", "last_month", "last_year")
        time_period_min: Custom start timestamp
        time_period_max: Custom end timestamp
        num: Results per page (default: "10")
        page: Page number (default: "1")

    Returns:
        Video search results with metadata

    Examples:
        - search_google_videos(q="Python tutorial")
        - search_google_videos(q="cooking recipes", time_period="last_week")
        - search_google_videos(q="news", device="mobile", num="20")
    """
```

**Context Cost**: ~500-600 tokens

#### ✅ AFTER (Optimized - ~20 lines)

```python
@mcp.tool()
async def search_google_videos(
    q: str,
    device: str = "desktop",
    location: Optional[str] = None,
    google_domain: str = "google.com",
    gl: str = "us",
    hl: str = "en",
    time_period: Optional[str] = None,
    num: str = "10",
    page: str = "1"
) -> Dict[str, Any]:
    """
    Search Google Videos for video content with metadata.

    Args:
        q: Search query
        device: "desktop" or "mobile"
        location: Location name for localized results
        time_period: Time filter (e.g., "last_hour", "last_day", "last_week")
        num: Results per page (default: 10)
        page: Page number

    Example: search_google_videos(q="Python tutorial", time_period="last_week")
    """
```

**Context Cost**: ~150-200 tokens
**Savings**: ~70% reduction in context usage

---

## Optimization Checklist

When writing tool descriptions:

- [ ] Main description is 1-2 sentences
- [ ] Args are one-line each (except when critical detail needed)
- [ ] Only 1-2 examples shown (most common use cases)
- [ ] No detailed Returns section (structure is self-explanatory from API)
- [ ] Notes only if there's a critical warning or gotcha
- [ ] Parameters use type hints and defaults to convey constraints
- [ ] Description uses active voice: "Search X for Y" not "This tool searches..."

## When to Include More Detail

Keep detailed descriptions for:

1. **Complex validation** - Multi-parameter dependencies (e.g., flight_type requirements)
2. **Non-obvious behavior** - Unexpected side effects or special modes
3. **Critical warnings** - Data loss, security implications, rate limits

## Parameter Description Patterns

### ✅ Good (Concise)
```
q: Search query
location: Location for localized results
time_period: Time filter ("last_hour", "last_day", "last_week")
```

### ❌ Too Verbose
```
q: The search query string that you want to use to search for videos on Google. This is a required parameter and must be provided.
location: The location name that will be used to provide localized search results. For example, you can use "New York, NY" or "San Francisco, CA". This parameter is optional.
```

## Real-World Examples from This MCP

### Tool: `health_check`

**Before**: 19 lines (268 tokens)
```python
"""
Check health status of the SearchAPI service.

Returns comprehensive health metrics including:
- API connectivity status
- Response latency
- Circuit breaker state
- Cache statistics
- Request metrics

Use this tool to diagnose connectivity issues or monitor service health.
"""
```

**After**: 3 lines (45 tokens)
```python
"""
Check SearchAPI service health including API status, latency, cache stats, and metrics.
"""
```

**Savings**: 83% reduction

---

### Tool: `get_current_time`

**Before**: 97 lines (1,500+ tokens)
```python
"""
Get current system time and travel date suggestions.

Essential for travel booking tools (flights, hotels) that require dates.
Provides formatted dates, travel suggestions, and hotel stay recommendations.

Args:
    format: Date format ("iso", "slash", "chinese", "timestamp", "full")
    days_offset: Number of days to offset from today (can be negative)
    return_future_dates: Whether to return an array of future dates
    future_days: Number of future dates to return if return_future_dates=True

Returns:
    Dictionary containing:
    - now: Current date/time in various formats
    - target_date: Calculated date based on days_offset
    - travel_dates: Common travel date shortcuts (today, tomorrow, next_week, etc.)
    - hotel_stay_suggestions: Recommended check-in/check-out date pairs
    - future_dates: Array of future dates (if requested)

Examples:
    - get_current_time(format="iso") → "2025-11-15"
    - get_current_time(days_offset=7) → Date 7 days from now
    - get_current_time(return_future_dates=True, future_days=30) → Next 30 dates
"""
```

**After**: 12 lines (180 tokens)
```python
"""
Get current time and travel date suggestions for booking tools.

Args:
    format: Output format ("iso", "slash", "chinese", "timestamp", "full")
    days_offset: Days from today (positive or negative)
    return_future_dates: Include array of future dates
    future_days: Number of future dates to include

Example: get_current_time(format="iso", days_offset=7)
"""
```

**Savings**: 88% reduction

---

## Implementation Strategy

1. **Phase 1**: Update utility tools (health_check, get_current_time)
2. **Phase 2**: Update simple search tools (search_google, search_google_videos)
3. **Phase 3**: Update complex tools (flights, hotels with many parameters)
4. **Phase 4**: Test and validate no functionality is lost

## Expected Impact

- **Total context reduction**: 60-75% for tool descriptions
- **Agent performance**: Faster tool selection, more context for actual work
- **Maintainability**: Easier to update and keep synchronized
- **Readability**: Clearer at-a-glance understanding of tool purpose

---

## References

- FastMCP Documentation: https://github.com/jlowin/fastmcp
- MCP Specification: Tool annotations (2025-03-26)
- Best Practice: Pythonic simplicity - "Show, don't tell"
