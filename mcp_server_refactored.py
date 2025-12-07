"""
SearchAPI MCP Server - Refactored following FAST MCP best practices.

This implementation follows production-ready patterns including:
- Configuration management with Pydantic validation
- Connection pooling and retry logic
- Response caching with TTL
- Circuit breaker pattern for resilience
- Structured error handling
- Metrics collection and monitoring
- Health checks
"""
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP
from config import load_config, get_transport, ServerConfig
from client import SearchAPIClient


# Configure logging with default level (will be updated after config loads)
logging.basicConfig(
    level=logging.INFO,  # Default until config loads
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Load configuration
try:
    config = load_config()

    # Update logging level from config
    log_level = getattr(logging, config.log_level)
    logging.getLogger().setLevel(log_level)
    logger.setLevel(log_level)

    logger.info(f"Configuration loaded successfully (log_level: {config.log_level})")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise


# Initialize FastMCP server
server_config = ServerConfig()
mcp = FastMCP(server_config.name)


# Initialize SearchAPI client
api_client = SearchAPIClient(config)
logger.info("SearchAPI client initialized with connection pooling and caching")


# ============================================================================
# Health Check & Monitoring Tools
# ============================================================================

@mcp.tool()
async def health_check() -> Dict[str, Any]:
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
    health = await api_client.health_check()

    return {
        "api_status": health,
        "cache_stats": api_client.get_cache_stats(),
        "metrics": api_client.get_metrics(),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Time & Date Utilities
# ============================================================================

@mcp.tool()
async def get_current_time(
    format: str = "iso",
    days_offset: int = 0,
    return_future_dates: bool = False,
    future_days: int = 7
) -> Dict[str, Any]:
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
    now = datetime.now()
    target_date = now + timedelta(days=days_offset)

    result = {
        "now": {
            "iso": now.strftime("%Y-%m-%d"),
            "slash": now.strftime("%d/%m/%Y"),
            "chinese": now.strftime("%Y年%m月%d日"),
            "timestamp": int(now.timestamp()),
            "full": now.strftime("%Y-%m-%d %H:%M:%S"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A"),
            "weekday_short": now.strftime("%a"),
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second
        },
        "target_date": {
            "iso": target_date.strftime("%Y-%m-%d"),
            "slash": target_date.strftime("%d/%m/%Y"),
            "chinese": target_date.strftime("%Y年%m月%d日"),
            "timestamp": int(target_date.timestamp()),
            "full": target_date.strftime("%Y-%m-%d %H:%M:%S"),
            "weekday": target_date.strftime("%A"),
            "weekday_short": target_date.strftime("%a"),
            "year": target_date.year,
            "month": target_date.month,
            "day": target_date.day
        },
        "travel_dates": {
            "today": now.strftime("%Y-%m-%d"),
            "tomorrow": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
            "next_week": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
            "next_month": (now + timedelta(days=30)).strftime("%Y-%m-%d"),
            # Next Friday: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
            # Days to Friday: (4 - current_day) % 7
            "weekend": (now + timedelta(days=(4 - now.weekday()) % 7)).strftime("%Y-%m-%d"),
            # Next Sunday: Days to Sunday: (6 - current_day) % 7
            "weekend_end": (now + timedelta(days=(6 - now.weekday()) % 7)).strftime("%Y-%m-%d"),
        },
        "hotel_stay_suggestions": [
            {
                "check_in": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "check_out": (now + timedelta(days=3)).strftime("%Y-%m-%d"),
                "nights": 2,
                "description": "Weekend getaway"
            },
            {
                "check_in": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "check_out": (now + timedelta(days=8)).strftime("%Y-%m-%d"),
                "nights": 7,
                "description": "Week-long vacation"
            },
            {
                "check_in": (now + timedelta(days=30)).strftime("%Y-%m-%d"),
                "check_out": (now + timedelta(days=32)).strftime("%Y-%m-%d"),
                "nights": 2,
                "description": "Next month short trip"
            }
        ]
    }

    if return_future_dates:
        future_dates = []
        for i in range(future_days):
            future_date = now + timedelta(days=i)
            future_dates.append({
                "iso": future_date.strftime("%Y-%m-%d"),
                "slash": future_date.strftime("%d/%m/%Y"),
                "chinese": future_date.strftime("%Y年%m月%d日"),
                "weekday": future_date.strftime("%A"),
                "weekday_short": future_date.strftime("%a"),
                "days_from_now": i
            })
        result["future_dates"] = future_dates

    # Set main date field based on format
    format_map = {
        "iso": target_date.strftime("%Y-%m-%d"),
        "slash": target_date.strftime("%d/%m/%Y"),
        "chinese": target_date.strftime("%Y年%m月%d日"),
        "timestamp": int(target_date.timestamp()),
        "full": target_date.strftime("%Y-%m-%d %H:%M:%S")
    }
    result["date"] = format_map.get(format, target_date.strftime("%Y-%m-%d"))

    return result


# ============================================================================
# Google Search Tools
# ============================================================================

@mcp.tool()
async def search_google(
    q: str,
    device: str = "desktop",
    location: Optional[str] = None,
    uule: Optional[str] = None,
    google_domain: str = "google.com",
    gl: str = "us",
    hl: str = "en",
    lr: Optional[str] = None,
    cr: Optional[str] = None,
    nfpr: str = "0",
    filter: str = "1",
    safe: str = "off",
    time_period: Optional[str] = None,
    time_period_min: Optional[str] = None,
    time_period_max: Optional[str] = None,
    num: str = "10",
    page: str = "1"
) -> Dict[str, Any]:
    """
    Search Google for web results, knowledge graphs, answer boxes, and related questions.

    Comprehensive Google search with support for:
    - Organic web results
    - Knowledge graph information
    - Answer boxes and featured snippets
    - Related questions (People Also Ask)
    - Search suggestions
    - Ads (if present)

    Args:
        q: Search query (required)
        device: Device type ("desktop" or "mobile")
        location: Location name for localized results (e.g., "New York, NY")
        uule: Google's encoded location parameter (auto-generated if location provided)
        google_domain: Google domain to use (default: "google.com")
        gl: Country code for results (default: "us")
        hl: Language code (default: "en")
        lr: Language restriction
        cr: Country restriction
        nfpr: Personalization level ("0" = off, "1" = on)
        filter: Duplicate filter ("0" = off, "1" = on)
        safe: Safe search ("off", "active")
        time_period: Time period filter (e.g., "last_hour", "last_day", "last_week")
        time_period_min: Custom time period start (Unix timestamp)
        time_period_max: Custom time period end (Unix timestamp)
        num: Number of results per page (default: "10")
        page: Page number (default: "1")

    Returns:
        Search results including organic results, knowledge graph, answer boxes, etc.

    Examples:
        - search_google(q="Python programming")
        - search_google(q="weather", location="San Francisco, CA")
        - search_google(q="news", time_period="last_day", num="20")
    """
    params = {
        "engine": "google",
        "q": q,
        "device": device,
        "google_domain": google_domain,
        "gl": gl,
        "hl": hl,
        "nfpr": nfpr,
        "filter": filter,
        "safe": safe,
        "num": num,
        "page": page
    }

    # Add optional parameters
    optional_params = {
        "location": location,
        "uule": uule,
        "lr": lr,
        "cr": cr,
        "time_period": time_period,
        "time_period_min": time_period_min,
        "time_period_max": time_period_max
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


@mcp.tool()
async def search_google_videos(
    q: str,
    device: str = "desktop",
    location: Optional[str] = None,
    uule: Optional[str] = None,
    google_domain: str = "google.com",
    gl: str = "us",
    hl: str = "en",
    lr: Optional[str] = None,
    cr: Optional[str] = None,
    nfpr: str = "0",
    filter: str = "1",
    safe: str = "off",
    time_period: Optional[str] = None,
    time_period_min: Optional[str] = None,
    time_period_max: Optional[str] = None,
    num: str = "10",
    page: str = "1"
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
    params = {
        "engine": "google_videos",
        "q": q,
        "device": device,
        "google_domain": google_domain,
        "gl": gl,
        "hl": hl,
        "nfpr": nfpr,
        "filter": filter,
        "safe": safe,
        "num": num,
        "page": page
    }

    optional_params = {
        "location": location,
        "uule": uule,
        "lr": lr,
        "cr": cr,
        "time_period": time_period,
        "time_period_min": time_period_min,
        "time_period_max": time_period_max
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


@mcp.tool()
async def search_google_ai_mode(
    q: Optional[str] = None,
    url: Optional[str] = None,
    location: Optional[str] = None,
    uule: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search Google with AI-powered overview mode.

    Returns AI-generated overviews along with comprehensive search results:
    - AI-generated content blocks (paragraphs, lists, tables, code)
    - Markdown-formatted AI overview with reference links
    - Reference links cited in the AI content
    - Web results
    - Local results (for location-based searches)
    - Inline shopping results

    Args:
        q: Search query (required unless url is provided)
        url: Image URL to search (required unless q is provided)
        location: Location for localized results (e.g., "New York, NY")
        uule: Google's encoded location parameter (auto-generated if location provided)

    Returns:
        Dictionary containing:
        - text_blocks: AI-generated content structured by type (header, paragraph, list, table, code)
        - markdown: Markdown-formatted AI overview with reference links
        - reference_links: Array of sources cited in the AI content
        - web_results: Traditional web search results
        - local_results: Local business results (if applicable)
        - inline_shopping: Shopping results (if applicable)
        - search_metadata: Request metadata and timing
        - search_parameters: Parameters used for the search

    Examples:
        - search_google_ai_mode(q="How does photosynthesis work?")
        - search_google_ai_mode(q="best restaurants", location="San Francisco, CA")
        - search_google_ai_mode(url="https://example.com/image.jpg")

    Notes:
        - Either 'q' or 'url' must be provided
        - AI mode provides comprehensive answers with cited sources
        - Results include structured data in multiple formats (JSON, Markdown)
        - Reference indexes in text_blocks correspond to reference_links array
    """
    if not q and not url:
        return {
            "error": "Either 'q' (search query) or 'url' (image URL) parameter must be provided",
            "type": "validation_error"
        }

    params = {
        "engine": "google_ai_mode"
    }

    # Add required parameter
    if q:
        params["q"] = q
    if url:
        params["url"] = url

    # Add optional parameters
    if location:
        params["location"] = location
    if uule:
        params["uule"] = uule

    return await api_client.request(params)


# ============================================================================
# Google Maps Tools
# ============================================================================

@mcp.tool()
async def search_google_maps(
    query: str,
    location_ll: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search Google Maps for places, businesses, and services.

    Find locations, businesses, restaurants, hotels, and points of interest.
    Returns detailed place information including ratings, reviews, and coordinates.

    Args:
        query: Search query (e.g., "coffee shops", "hotels in Manhattan", "Eiffel Tower")
        location_ll: Latitude/longitude for centering search (format: "@lat,lng,zoom")
                     Example: "@40.7128,-74.0060,12z" (New York City)

    Returns:
        Dictionary containing:
        - local_results: Array of places with details (name, rating, address, etc.)
        - place_results: Detailed information for specific places
        - search_metadata: Request metadata
        - search_information: Search context and parameters

    Examples:
        - search_google_maps(query="coffee shops near Central Park")
        - search_google_maps(query="restaurants", location_ll="@40.7128,-74.0060,12z")
        - search_google_maps(query="Statue of Liberty")
    """
    params = {
        "engine": "google_maps",
        "q": query
    }

    if location_ll:
        params["ll"] = location_ll

    return await api_client.request(params)


@mcp.tool()
async def search_google_maps_place(
    place_id: Optional[str] = None,
    data_id: Optional[str] = None,
    google_domain: str = "google.com",
    hl: str = "en"
) -> Dict[str, Any]:
    """
    Get detailed information for a specific Google Maps place.

    Retrieve comprehensive place data including:
    - Basic information (name, address, phone, website)
    - Ratings and reviews summary
    - Photos and images
    - Opening hours
    - Amenities and features
    - Popular times
    - User questions and answers
    - Nearby places

    Args:
        place_id: Google Maps place ID (required if data_id not provided)
        data_id: Alternative place identifier (required if place_id not provided)
        google_domain: Google domain to use (default: "google.com")
        hl: Language code for results (default: "en")

    Returns:
        Dictionary containing:
        - place_info: Complete place details
        - ratings: Review statistics and histogram
        - photos: Image gallery
        - hours: Opening hours and popular times
        - amenities: Features and services
        - reviews_link: Link to full reviews

    Examples:
        - search_google_maps_place(place_id="ChIJN1t_tDeuEmsRUsoyG83frY4")
        - search_google_maps_place(data_id="0x89c259a9b3117469:0xd134e199a405a163")

    Notes:
        - Either place_id or data_id must be provided
        - Get place_id from search_google_maps results
    """
    if not place_id and not data_id:
        return {
            "error": "Either 'place_id' or 'data_id' must be provided",
            "type": "validation_error"
        }

    params = {
        "engine": "google_maps_place",
        "google_domain": google_domain,
        "hl": hl
    }

    if place_id:
        params["place_id"] = place_id
    elif data_id:
        params["data_id"] = data_id

    return await api_client.request(params)


@mcp.tool()
async def search_google_maps_reviews(
    place_id: Optional[str] = None,
    data_id: Optional[str] = None,
    topic_id: Optional[str] = None,
    next_page_token: Optional[str] = None,
    sort_by: Optional[str] = None,
    rating: Optional[str] = None,
    hl: Optional[str] = None,
    gl: Optional[str] = None,
    reviews_limit: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get reviews for a Google Maps place.

    Retrieve user reviews, ratings, and feedback for a specific location.
    Supports filtering, sorting, and pagination.

    Args:
        place_id: Google Maps place ID (required if data_id not provided)
        data_id: Alternative place identifier (required if place_id not provided)
        topic_id: Filter reviews by topic
        next_page_token: Token for pagination
        sort_by: Sort order ("most_relevant", "newest", "highest_rating", "lowest_rating")
        rating: Filter by rating ("1", "2", "3", "4", "5")
        hl: Language code for reviews (default: "en")
        gl: Country code (default: "us")
        reviews_limit: Maximum number of reviews to return

    Returns:
        Dictionary containing:
        - reviews: Array of review objects with text, rating, date, user info
        - place_info: Basic place information
        - pagination: Next page token if more reviews available

    Examples:
        - search_google_maps_reviews(place_id="ChIJN1t_tDeuEmsRUsoyG83frY4")
        - search_google_maps_reviews(place_id="...", sort_by="newest", rating="5")
        - search_google_maps_reviews(data_id="0x...")

    Notes:
        - Either place_id or data_id must be provided
        - Use place_id from search_google_maps results
    """
    if not place_id and not data_id:
        return {
            "error": "Either 'place_id' or 'data_id' must be provided",
            "type": "validation_error"
        }

    params = {
        "engine": "google_maps_reviews"
    }

    if place_id:
        params["place_id"] = place_id
    elif data_id:
        params["data_id"] = data_id

    optional_params = {
        "topic_id": topic_id,
        "next_page_token": next_page_token,
        "sort_by": sort_by,
        "rating": rating,
        "hl": hl,
        "gl": gl,
        "reviews_limit": reviews_limit
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


# ============================================================================
# Google Events Tools
# ============================================================================

@mcp.tool()
async def search_google_events(
    q: str,
    location: Optional[str] = None,
    uule: Optional[str] = None,
    google_domain: str = "google.com",
    gl: str = "us",
    hl: str = "en",
    chips: Optional[str] = None,
    page: str = "1"
) -> Dict[str, Any]:
    """
    Search Google Events for concerts, conferences, festivals, and activities.

    Find local and global events including:
    - Concerts and music events
    - Conferences and meetups
    - Sports events
    - Festivals and celebrations
    - Virtual events
    - Exhibitions and shows

    Args:
        q: Search query (e.g., "concerts tonight", "tech conferences in San Francisco") - required
        location: Location name for localized results (e.g., "New York, NY")
        uule: Google's encoded location parameter
        google_domain: Google domain to use (default: "google.com")
        gl: Country code (default: "us")
        hl: Language code (default: "en")
        chips: Event filters - date ("today", "tomorrow", "week", "weekend", "month")
               or type (e.g., "Virtual-Event")
        page: Page number for pagination (default: "1")

    Returns:
        Dictionary containing:
        - events: Array of event objects with details
        - search_metadata: Request metadata
        - search_parameters: Parameters used

    Event object includes:
        - title: Event name
        - date: Event date/time information
        - duration: Event duration
        - address: Event location address
        - location_name: Venue name
        - description: Event description
        - thumbnail: Event image
        - link: Event details URL
        - venue: Venue details with rating and reviews
        - offers: Ticket purchasing options

    Examples:
        - search_google_events(q="concerts in New York")
        - search_google_events(q="tech conferences", location="San Francisco, CA")
        - search_google_events(q="music festivals", chips="weekend")
        - search_google_events(q="virtual events", chips="Virtual-Event")

    Notes:
        - Use chips parameter to filter by date or event type
        - Results include both physical and virtual events
        - Venue information includes ratings and review counts
    """
    params = {
        "engine": "google_events",
        "q": q,
        "google_domain": google_domain,
        "gl": gl,
        "hl": hl,
        "page": page
    }

    optional_params = {
        "location": location,
        "uule": uule,
        "chips": chips
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


# ============================================================================
# Google Flights Tools
# ============================================================================

@mcp.tool()
async def search_google_flights(
    departure_id: Optional[str] = None,
    arrival_id: Optional[str] = None,
    outbound_date: Optional[str] = None,
    flight_type: str = "round_trip",
    return_date: Optional[str] = None,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    currency: Optional[str] = None,
    travel_class: Optional[str] = None,
    stops: Optional[str] = None,
    sort_by: Optional[str] = None,
    adults: Optional[str] = None,
    children: Optional[str] = None,
    multi_city_json: Optional[str] = None,
    show_cheapest_flights: Optional[str] = None,
    show_hidden_flights: Optional[str] = None,
    max_price: Optional[str] = None,
    carry_on_bags: Optional[str] = None,
    checked_bags: Optional[str] = None,
    included_airlines: Optional[str] = None,
    excluded_airlines: Optional[str] = None,
    outbound_times: Optional[str] = None,
    return_times: Optional[str] = None,
    emissions: Optional[str] = None,
    included_connecting_airports: Optional[str] = None,
    excluded_connecting_airports: Optional[str] = None,
    layover_duration_min: Optional[str] = None,
    layover_duration_max: Optional[str] = None,
    max_flight_duration: Optional[str] = None,
    separate_tickets: Optional[str] = None,
    infants_in_seat: Optional[str] = None,
    infants_on_lap: Optional[str] = None,
    departure_token: Optional[str] = None,
    booking_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search Google Flights for flight options and prices.

    Find flights with comprehensive filtering options including:
    - One-way, round-trip, and multi-city itineraries
    - Airline preferences and exclusions
    - Baggage requirements
    - Time and duration filters
    - Price limits
    - Passenger counts

    Args:
        departure_id: Departure airport code (e.g., "JFK", "LAX") - required for one-way/round-trip
        arrival_id: Arrival airport code - required for one-way/round-trip
        outbound_date: Departure date in YYYY-MM-DD format - required for one-way/round-trip
        flight_type: Trip type ("one_way", "round_trip", "multi_city")
        return_date: Return date in YYYY-MM-DD format - required for round_trip
        gl: Country code (default: "us")
        hl: Language code (default: "en")
        currency: Currency code (e.g., "USD", "EUR")
        travel_class: Class of service ("economy", "premium_economy", "business", "first")
        stops: Number of stops ("0" = nonstop, "1" = 1 stop, "2" = 2+ stops)
        sort_by: Sort order ("best", "price", "duration", "departure_time", "arrival_time")
        adults: Number of adult passengers (default: "1")
        children: Number of children
        multi_city_json: JSON string for multi-city itinerary (required if flight_type="multi_city")
        show_cheapest_flights: Show cheapest alternative dates ("true", "false")
        show_hidden_flights: Show hidden/budget airlines ("true", "false")
        max_price: Maximum price filter
        carry_on_bags: Number of carry-on bags
        checked_bags: Number of checked bags
        included_airlines: Comma-separated airline codes to include
        excluded_airlines: Comma-separated airline codes to exclude
        outbound_times: Departure time filter (e.g., "1" = morning)
        return_times: Return time filter
        emissions: Emissions filter ("low", "medium", "high")
        included_connecting_airports: Allowed connection airports
        excluded_connecting_airports: Excluded connection airports
        layover_duration_min: Minimum layover in minutes
        layover_duration_max: Maximum layover in minutes
        max_flight_duration: Maximum total flight duration in minutes
        separate_tickets: Allow separate tickets ("true", "false")
        infants_in_seat: Number of infants in seat
        infants_on_lap: Number of infants on lap
        departure_token: Token for specific departure flight
        booking_token: Token for booking

    Returns:
        Dictionary containing:
        - best_flights: Recommended flights
        - other_flights: Additional flight options
        - price_insights: Price trends and predictions
        - airports: Airport information
        - search_metadata: Request metadata

    Examples:
        - search_google_flights(departure_id="JFK", arrival_id="LAX", outbound_date="2025-12-01", flight_type="one_way")
        - search_google_flights(departure_id="SFO", arrival_id="NYC", outbound_date="2025-12-15", return_date="2025-12-22", travel_class="business", stops="0")
        - search_google_flights(multi_city_json='[{"departure_id":"JFK","arrival_id":"LAX","date":"2025-12-01"},{"departure_id":"LAX","arrival_id":"SFO","date":"2025-12-05"}]', flight_type="multi_city")

    Notes:
        - Use get_current_time() tool to get properly formatted dates
        - For multi-city, only multi_city_json is required
        - Dates must be in YYYY-MM-DD format
    """
    params = {
        "engine": "google_flights",
        "flight_type": flight_type
    }

    # Validate and add required parameters based on flight type
    if flight_type == "multi_city":
        if not multi_city_json:
            return {
                "error": "multi_city_json parameter is required for multi-city flights",
                "type": "validation_error"
            }
        params["multi_city_json"] = multi_city_json
    else:
        if not all([departure_id, arrival_id, outbound_date]):
            return {
                "error": "departure_id, arrival_id, and outbound_date are required for one-way/round-trip flights",
                "type": "validation_error"
            }
        params["departure_id"] = departure_id
        params["arrival_id"] = arrival_id
        params["outbound_date"] = outbound_date

        if flight_type == "round_trip":
            if not return_date:
                return {
                    "error": "return_date is required for round-trip flights",
                    "type": "validation_error"
                }
            params["return_date"] = return_date

    # Add all optional parameters
    optional_params = {
        "gl": gl, "hl": hl, "currency": currency, "travel_class": travel_class,
        "stops": stops, "sort_by": sort_by, "adults": adults, "children": children,
        "show_cheapest_flights": show_cheapest_flights, "show_hidden_flights": show_hidden_flights,
        "max_price": max_price, "carry_on_bags": carry_on_bags, "checked_bags": checked_bags,
        "included_airlines": included_airlines, "excluded_airlines": excluded_airlines,
        "outbound_times": outbound_times, "return_times": return_times, "emissions": emissions,
        "included_connecting_airports": included_connecting_airports,
        "excluded_connecting_airports": excluded_connecting_airports,
        "layover_duration_min": layover_duration_min, "layover_duration_max": layover_duration_max,
        "max_flight_duration": max_flight_duration, "separate_tickets": separate_tickets,
        "infants_in_seat": infants_in_seat, "infants_on_lap": infants_on_lap,
        "departure_token": departure_token, "booking_token": booking_token
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


@mcp.tool()
async def search_google_flights_calendar(
    flight_type: str,
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    outbound_date_start: Optional[str] = None,
    outbound_date_end: Optional[str] = None,
    return_date_start: Optional[str] = None,
    return_date_end: Optional[str] = None,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    currency: Optional[str] = None,
    adults: Optional[str] = None,
    children: Optional[str] = None,
    travel_class: Optional[str] = None,
    stops: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get Google Flights price calendar showing prices across dates.

    Visualize flight prices across a date range to find the cheapest days to fly.
    Useful for flexible travel planning.

    Args:
        flight_type: Trip type ("one_way" or "round_trip")
        departure_id: Departure airport code (required)
        arrival_id: Arrival airport code (required)
        outbound_date: Reference outbound date in YYYY-MM-DD format (required)
        return_date: Reference return date (required for round_trip)
        outbound_date_start: Calendar start date for outbound
        outbound_date_end: Calendar end date for outbound
        return_date_start: Calendar start date for return
        return_date_end: Calendar end date for return
        gl: Country code
        hl: Language code
        currency: Currency code
        adults: Number of adults
        children: Number of children
        travel_class: Class of service
        stops: Number of stops filter

    Returns:
        Dictionary containing:
        - price_grid: Matrix of prices by date combinations
        - best_prices: Cheapest options found
        - search_metadata: Request metadata

    Examples:
        - search_google_flights_calendar(flight_type="one_way", departure_id="JFK", arrival_id="LAX", outbound_date="2025-12-01")
        - search_google_flights_calendar(flight_type="round_trip", departure_id="SFO", arrival_id="NYC", outbound_date="2025-12-15", return_date="2025-12-22")
    """
    params = {
        "engine": "google_flights_calendar",
        "flight_type": flight_type,
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date
    }

    if flight_type == "round_trip":
        if not return_date:
            return {
                "error": "return_date is required for round-trip flights",
                "type": "validation_error"
            }
        params["return_date"] = return_date

    optional_params = {
        "outbound_date_start": outbound_date_start,
        "outbound_date_end": outbound_date_end,
        "return_date_start": return_date_start,
        "return_date_end": return_date_end,
        "gl": gl, "hl": hl, "currency": currency,
        "adults": adults, "children": children,
        "travel_class": travel_class, "stops": stops
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


@mcp.tool()
async def search_google_flights_location_search(
    q: str,
    gl: str = "us",
    hl: str = "en"
) -> Dict[str, Any]:
    """
    Search for airport codes and locations for flight booking.

    Provides autocomplete suggestions for airports and cities based on partial input.
    Useful for finding correct airport codes before searching for flights.

    Args:
        q: Search query - partial airport name, city name, or airport code (required)
           Examples: "New York", "JFK", "Los Angeles International"
        gl: Country code (default: "us")
        hl: Language code (default: "en")

    Returns:
        Dictionary containing:
        - results: Array of location suggestions
        - search_metadata: Request metadata

    Result object includes:
        - airport_code: IATA airport code (e.g., "JFK")
        - title: Airport and city name
        - context: Geographic context (state, country)
        - kgmid: Knowledge Graph ID for precise location

    Examples:
        - search_google_flights_location_search(q="New York")
        - search_google_flights_location_search(q="JFK")
        - search_google_flights_location_search(q="Tokyo")
        - search_google_flights_location_search(q="Heathrow")

    Notes:
        - Returns multiple matching airports/cities
        - Use airport_code in search_google_flights
        - Use kgmid for precise location identification
    """
    params = {
        "engine": "google_flights_location_search",
        "q": q,
        "gl": gl,
        "hl": hl
    }

    return await api_client.request(params)


@mcp.tool()
async def search_google_travel_explore(
    departure_id: str,
    arrival_id: Optional[str] = None,
    time_period: Optional[str] = None,
    gl: str = "us",
    hl: str = "en-US",
    currency: str = "USD",
    travel_mode: str = "all",
    travel_class: Optional[str] = None,
    interests: Optional[str] = None,
    stops: Optional[str] = None,
    max_price: Optional[str] = None,
    max_flight_duration: Optional[str] = None,
    carry_on_bags: Optional[str] = None,
    included_airlines: Optional[str] = None,
    adults: str = "1",
    children: Optional[str] = None,
    infants_in_seat: Optional[str] = None,
    infants_on_lap: Optional[str] = None
) -> Dict[str, Any]:
    """
    Explore travel destinations and find inspiration for trips.

    Discover travel options without specifying exact routes or dates.
    Perfect for travel planning and destination discovery.

    Args:
        departure_id: Departure airport code or location identifier (e.g., "JFK" or "/m/02_286") - required
        arrival_id: Destination location identifier or bounding box coordinates
                   Defaults to "/m/02j71" (anywhere on Earth)
                   Can use bounding box: "[[min_lon,min_lat],[max_lon,max_lat]]"
        time_period: Travel period - round-trip options:
                    - "one_week_trip_in_the_next_six_months"
                    - "two_week_trip_in_december" (or other months)
                    - "weekend_trip_in_january"
                    - Custom dates: "YYYY-MM-DD"
        gl: Country code (default: "us")
        hl: Language code (default: "en-US")
        currency: Currency code (default: "USD")
        travel_mode: "all" (default) or "flights_only"
        travel_class: "economy", "premium_economy", "business", "first_class"
        interests: Destination interests - "popular", "outdoors", "beaches", "museums", "history", "skiing"
        stops: Flight stops filter - "any", "nonstop", "one_stop_or_fewer", "two_stops_or_fewer"
        max_price: Maximum ticket price
        max_flight_duration: Maximum flight duration in minutes
        carry_on_bags: Number of carry-on bags
        included_airlines: Airline alliances - "ONEWORLD", "SKYTEAM", "STAR_ALLIANCE"
        adults: Number of adults (default: "1", max 9 total passengers)
        children: Number of children
        infants_in_seat: Number of infants in seat
        infants_on_lap: Number of infants on lap

    Returns:
        Dictionary containing:
        - destinations: Array of destination suggestions
        - search_metadata: Request metadata

    Destination object includes:
        - name: Destination name
        - kgmid: Location identifier
        - primary_airport: Airport code
        - country: Country name
        - coordinates: [latitude, longitude]
        - distance: Distance from departure
        - avg_cost_per_night: Accommodation cost estimate
        - outbound_date: Suggested departure date
        - return_date: Suggested return date
        - image: Destination photo
        - flight: Flight details with price, stops, duration, airline

    Examples:
        - search_google_travel_explore(departure_id="JFK")
        - search_google_travel_explore(departure_id="JFK", interests="beaches")
        - search_google_travel_explore(departure_id="/m/02_286", time_period="two_week_trip_in_december")
        - search_google_travel_explore(departure_id="LAX", arrival_id="[[89.81,-11.38],[133.94,16.77]]")

    Notes:
        - Great for discovering new destinations
        - Provides cost estimates for flights and hotels
        - Can filter by interests and travel preferences
        - Use location identifiers (kgmid) for precise targeting
    """
    params = {
        "engine": "google_travel_explore",
        "departure_id": departure_id,
        "gl": gl,
        "hl": hl,
        "currency": currency,
        "travel_mode": travel_mode,
        "adults": adults
    }

    # Set default arrival_id if not provided
    if arrival_id:
        params["arrival_id"] = arrival_id
    else:
        params["arrival_id"] = "/m/02j71"  # Earth (anywhere)

    optional_params = {
        "time_period": time_period,
        "travel_class": travel_class,
        "interests": interests,
        "stops": stops,
        "max_price": max_price,
        "max_flight_duration": max_flight_duration,
        "carry_on_bags": carry_on_bags,
        "included_airlines": included_airlines,
        "children": children,
        "infants_in_seat": infants_in_seat,
        "infants_on_lap": infants_on_lap
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


# ============================================================================
# Google Hotels Tools
# ============================================================================

@mcp.tool()
async def search_google_hotels(
    q: str,
    check_in_date: str,
    check_out_date: str,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    currency: Optional[str] = None,
    property_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    price_min: Optional[str] = None,
    price_max: Optional[str] = None,
    property_types: Optional[str] = None,
    amenities: Optional[str] = None,
    rating: Optional[str] = None,
    free_cancellation: Optional[str] = None,
    special_offers: Optional[str] = None,
    for_displaced_individuals: Optional[str] = None,
    eco_certified: Optional[str] = None,
    hotel_class: Optional[str] = None,
    brands: Optional[str] = None,
    bedrooms: Optional[str] = None,
    bathrooms: Optional[str] = None,
    adults: Optional[str] = None,
    children_ages: Optional[str] = None,
    next_page_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search Google Hotels for accommodation options.

    Find hotels, vacation rentals, and other properties with extensive filtering:
    - Price range and property type
    - Amenities and facilities
    - Ratings and reviews
    - Special offers and cancellation policies

    Args:
        q: Location query (e.g., "hotels in Paris", "Manhattan hotels") - required
        check_in_date: Check-in date in YYYY-MM-DD format - required
        check_out_date: Check-out date in YYYY-MM-DD format - required
        gl: Country code (default: "us")
        hl: Language code (default: "en")
        currency: Currency code (e.g., "USD", "EUR")
        property_type: Type filter ("hotel", "vacation_rental", "apartment", etc.)
        sort_by: Sort order ("price_low", "price_high", "rating", "distance")
        price_min: Minimum price per night
        price_max: Maximum price per night
        property_types: Comma-separated types
        amenities: Filter by amenities (e.g., "pool,wifi,parking")
        rating: Minimum rating ("3", "4", "5")
        free_cancellation: Require free cancellation ("true", "false")
        special_offers: Show only special offers ("true", "false")
        for_displaced_individuals: Housing for displaced individuals ("true", "false")
        eco_certified: Eco-certified properties only ("true", "false")
        hotel_class: Star rating ("2", "3", "4", "5")
        brands: Filter by hotel brands (comma-separated)
        bedrooms: Minimum number of bedrooms
        bathrooms: Minimum number of bathrooms
        adults: Number of adults (default: "2")
        children_ages: Ages of children (comma-separated, e.g., "5,12")
        next_page_token: Pagination token for next page

    Returns:
        Dictionary containing:
        - properties: Array of hotel listings with prices, ratings, amenities
        - filters: Available filter options
        - search_metadata: Request metadata
        - pagination: Next page token if available

    Examples:
        - search_google_hotels(q="New York City", check_in_date="2025-12-01", check_out_date="2025-12-05")
        - search_google_hotels(q="Paris hotels", check_in_date="2025-12-15", check_out_date="2025-12-20", rating="4", amenities="pool,wifi", price_max="200")
        - search_google_hotels(q="Tokyo", check_in_date="2026-01-10", check_out_date="2026-01-15", hotel_class="5", free_cancellation="true")

    Notes:
        - Use get_current_time() to get properly formatted dates
        - Dates must be in YYYY-MM-DD format
        - Check-out date must be after check-in date
    """
    params = {
        "engine": "google_hotels",
        "q": q,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date
    }

    optional_params = {
        "gl": gl, "hl": hl, "currency": currency, "property_type": property_type,
        "sort_by": sort_by, "price_min": price_min, "price_max": price_max,
        "property_types": property_types, "amenities": amenities, "rating": rating,
        "free_cancellation": free_cancellation, "special_offers": special_offers,
        "for_displaced_individuals": for_displaced_individuals, "eco_certified": eco_certified,
        "hotel_class": hotel_class, "brands": brands, "bedrooms": bedrooms,
        "bathrooms": bathrooms, "adults": adults, "children_ages": children_ages,
        "next_page_token": next_page_token
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


@mcp.tool()
async def search_google_hotels_property(
    property_token: str,
    check_in_date: str,
    check_out_date: str,
    gl: Optional[str] = None,
    hl: Optional[str] = None,
    currency: Optional[str] = None,
    adults: Optional[str] = None,
    children: Optional[str] = None,
    children_ages: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information for a specific hotel property.

    Retrieve comprehensive details for a hotel including:
    - All available room types and rates
    - Detailed amenities and facilities
    - Property photos and descriptions
    - Booking options from various providers
    - Reviews and ratings

    Args:
        property_token: Unique property identifier from search results - required
        check_in_date: Check-in date in YYYY-MM-DD format - required
        check_out_date: Check-out date in YYYY-MM-DD format - required
        gl: Country code
        hl: Language code
        currency: Currency code
        adults: Number of adults (default: "2")
        children: Number of children
        children_ages: Ages of children (comma-separated)

    Returns:
        Dictionary containing:
        - property_info: Detailed hotel information
        - rooms: Available room types and rates
        - amenities: Complete amenity list
        - reviews: Guest reviews and ratings
        - booking_options: Booking providers and prices

    Examples:
        - search_google_hotels_property(property_token="ChIJd...", check_in_date="2025-12-01", check_out_date="2025-12-05")
        - search_google_hotels_property(property_token="...", check_in_date="2025-12-15", check_out_date="2025-12-20", adults="2", children="1", children_ages="10")

    Notes:
        - Get property_token from search_google_hotels results
        - Use to see all room types and booking options
    """
    params = {
        "engine": "google_hotels_property",
        "property_token": property_token,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date
    }

    optional_params = {
        "gl": gl, "hl": hl, "currency": currency,
        "adults": adults, "children": children, "children_ages": children_ages
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


# ============================================================================
# Google Shopping Tools
# ============================================================================

@mcp.tool()
async def search_google_shopping(
    q: str,
    device: str = "desktop",
    google_domain: str = "google.com",
    gl: str = "us",
    hl: str = "en",
    location: Optional[str] = None,
    uule: Optional[str] = None,
    shoprs: Optional[str] = None,
    price_min: Optional[str] = None,
    price_max: Optional[str] = None,
    is_on_sale: Optional[bool] = None,
    is_small_business: Optional[bool] = None,
    is_free_delivery: Optional[bool] = None,
    sort_by: Optional[str] = None,
    condition: Optional[str] = None,
    include_favicon: Optional[bool] = None,
    include_base_images: Optional[bool] = None,
    page: Optional[int] = None,
    zero_retention: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Search Google Shopping for product listings and e-commerce results.

    Comprehensive Google Shopping search with support for:
    - Product search results with prices and ratings
    - Shopping ads and sponsored listings
    - Price filtering and range searches
    - Product condition filtering (new/used)
    - Free delivery options
    - Small business seller filtering
    - Sale item filtering
    - Sorting by price, rating, and other criteria
    - Popular products related to search

    Args:
        q: Search query (required) - Examples: "PS5", "iPhone", "laptop under $1000"
        device: Device type ("desktop" or "mobile")
        google_domain: Google domain to use (default: "google.com")
        gl: Country code for results (default: "us")
        hl: Language code (default: "en")
        location: Location name for localized results (e.g., "New York, NY")
        uule: Google's encoded location parameter (auto-generated if location provided)
        shoprs: Encoded shop result filters for strict filtering
        price_min: Minimum price filter (e.g., "2.50" for $2.50+)
        price_max: Maximum price filter (e.g., "100" for $100 or less)
        is_on_sale: Filter for products on sale (true/false)
        is_small_business: Show only small business sellers (true/false)
        is_free_delivery: Show only products with free delivery (true/false)
        sort_by: Sort order - "price_low_to_high", "price_high_to_low", "rating_high_to_low"
        condition: Product condition - "new", "used"
        include_favicon: Include seller favicons in results (true/false)
        include_base_images: Include base64-encoded product images (true/false)
        page: Page number for pagination (default: 1)
        zero_retention: Disable all logging for compliance (true/false)

    Returns:
        Dictionary containing:
        - shopping_results: Array of product listings with prices, ratings, sellers
        - shopping_ads: Sponsored product advertisements
        - popular_products: Popular items related to search
        - filters: Available filters for refining search
        - search_metadata: Request metadata and response information

    Product listing includes:
        - title: Product name
        - price: Current price
        - rating: Star rating (if available)
        - reviews: Review count (if available)
        - thumbnail: Product image URL
        - link: Product page URL
        - source: Seller/merchant name
        - delivery_info: Shipping details
        - condition: Product condition (new/used)
        - is_on_sale: Whether item is on sale

    Examples:
        - search_google_shopping(q="iPhone 15")
        - search_google_shopping(q="laptop", price_max="1000", is_free_delivery=True)
        - search_google_shopping(q="PS5", condition="new", sort_by="price_low_to_high")
        - search_google_shopping(q="Nike shoes", location="New York, NY", is_on_sale=True)
        - search_google_shopping(q="tshirt under $30", price_min="10", gl="us", hl="en")

    Notes:
        - Use price_min/price_max with currency values (e.g., "25.99" for $25.99+)
        - Filters like is_on_sale, is_small_business, is_free_delivery can be combined
        - shoprs parameter takes priority over individual filter parameters
        - q parameter supports natural language queries (e.g., "under $30", "on sale")
    """
    params = {
        "engine": "google_shopping",
        "q": q,
        "device": device,
        "google_domain": google_domain,
        "gl": gl,
        "hl": hl
    }

    optional_params = {
        "location": location,
        "uule": uule,
        "shoprs": shoprs,
        "price_min": price_min,
        "price_max": price_max,
        "is_on_sale": str(is_on_sale).lower() if is_on_sale is not None else None,
        "is_small_business": str(is_small_business).lower() if is_small_business is not None else None,
        "is_free_delivery": str(is_free_delivery).lower() if is_free_delivery is not None else None,
        "sort_by": sort_by,
        "condition": condition,
        "include_favicon": str(include_favicon).lower() if include_favicon is not None else None,
        "include_base_images": str(include_base_images).lower() if include_base_images is not None else None,
        "page": str(page) if page is not None else None,
        "zero_retention": str(zero_retention).lower() if zero_retention is not None else None
    }

    for key, value in optional_params.items():
        if value is not None:
            params[key] = value

    return await api_client.request(params)


# ============================================================================
# Server Lifecycle
# ============================================================================

def cleanup_client():
    """
    Safely cleanup the HTTP client.

    Handles the delicate case where an event loop may or may not be running.
    This is necessary because mcp.run() may leave an active event loop.
    """
    import asyncio

    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()

        # Check if loop is running
        if loop.is_running():
            # Loop is running - this shouldn't happen in finally block
            # mcp.run() should have stopped the loop before returning
            # This indicates incomplete shutdown by mcp.run()
            logger.warning(
                "Event loop still running during cleanup - this indicates "
                "incomplete shutdown by mcp.run(). Cannot perform async cleanup "
                "from synchronous context while loop is running."
            )

            # We CANNOT call run_until_complete() on a running loop
            # That would raise: RuntimeError: This event loop is already running
            #
            # Our options are limited:
            # 1. Schedule cleanup task (fire-and-forget) - unreliable
            # 2. Try to stop the loop - risky and may break mcp.run()
            # 3. Accept that cleanup won't happen - best option
            #
            # We choose option 3 with clear logging
            logger.warning(
                "Skipping async cleanup because event loop is running. "
                "Resources may not be fully released. This is a limitation of "
                "the MCP framework's event loop management."
            )

            # Note: We could try loop.stop() but that's dangerous:
            # - May break mcp.run()'s shutdown sequence
            # - No guarantee cleanup would complete
            # - Could cause other issues

        else:
            # Loop exists but not running - run cleanup
            loop.run_until_complete(api_client.close())
            logger.info("Client closed using existing event loop")
    except RuntimeError:
        # No event loop exists or loop is closed
        # Create a new one just for cleanup
        try:
            asyncio.run(api_client.close())
            logger.info("Client closed using new event loop")
        except RuntimeError as e:
            # If even this fails, we're in a weird state
            # Log and continue - don't crash during cleanup
            logger.warning(f"Could not close client cleanly: {e}")
    except Exception as e:
        # Catch any other cleanup errors to prevent crashes during shutdown
        logger.error(f"Error during client cleanup: {e}", exc_info=True)


def main():
    """Main entry point for the MCP server."""
    try:
        transport = get_transport()
        logger.info(f"Starting SearchAPI MCP Server with transport: {transport}")
        logger.info(f"Cache enabled: {config.enable_cache}")
        logger.info(f"Metrics enabled: {config.enable_metrics}")

        mcp.run(transport=transport)

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        # Cleanup - use safe cleanup function that handles event loop state
        cleanup_client()
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
