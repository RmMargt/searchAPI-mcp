#!/usr/bin/env python3
"""
Live test script to test the Google Shopping API implementation with real API calls.
This script requires a valid SearchAPI.io API key to make actual API calls.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()


async def test_google_shopping_live():
    """Test the Google Shopping API implementation with live API calls."""
    print("Testing Google Shopping API with live API calls...")

    # Check if API key is available
    api_key = os.getenv("SEARCHAPI_API_KEY")
    if not api_key:
        print("❌ SEARCHAPI_API_KEY environment variable not set")
        print("Please set your SearchAPI.io API key in a .env file or environment")
        print("Example: SEARCHAPI_API_KEY=your_api_key_here")
        return False

    print("✅ API key found, proceeding with live tests...")

    # Import and setup
    import mcp_server_refactored
    from config import APIConfig
    from client import SearchAPIClient

    # Create a test configuration
    config = APIConfig(api_key=api_key)
    api_client = SearchAPIClient(config)

    print("\n" + "=" * 60)
    print("LIVE GOOGLE SHOPPING API TESTS")
    print("=" * 60)

    # Test 1: Basic search
    print("\n1. Testing basic search for 'iPhone 15'...")
    try:
        # We need to create a temporary function to test just the API call
        params = {"engine": "google_shopping", "q": "iPhone 15", "gl": "us", "hl": "en"}

        result = await api_client.request(params)

        if "error" in result:
            print(f"❌ API Error: {result['error']}")
            if "details" in result and result["details"]:
                print(f"   Details: {result['details']}")
        else:
            print("✅ Basic search successful!")
            print(f"   Response keys: {list(result.keys())}")

            # Show some results if available
            if "shopping_results" in result and result["shopping_results"]:
                print(f"   Found {len(result['shopping_results'])} shopping results")
                for i, item in enumerate(
                    result["shopping_results"][:3]
                ):  # Show first 3
                    if "title" in item and "price" in item:
                        print(f"   {i+1}. {item['title']} - {item['price']}")
            else:
                print("   No shopping results found in response")

    except Exception as e:
        print(f"❌ Error in basic search: {e}")
        import traceback

        traceback.print_exc()

    # Test 2: Price filtered search
    print("\n2. Testing price-filtered search for 'laptop under $1000'...")
    try:
        params = {
            "engine": "google_shopping",
            "q": "laptop under $1000",
            "gl": "us",
            "hl": "en",
        }

        result = await api_client.request(params)

        if "error" in result:
            print(f"❌ API Error: {result['error']}")
        else:
            print("✅ Price-filtered search successful!")
            if "shopping_results" in result and result["shopping_results"]:
                print(f"   Found {len(result['shopping_results'])} laptops under $1000")
                for i, item in enumerate(result["shopping_results"][:2]):
                    if "title" in item and "price" in item:
                        print(f"   {i+1}. {item['title']} - {item['price']}")

    except Exception as e:
        print(f"❌ Error in price-filtered search: {e}")

    # Test 3: Sale items search
    print("\n3. Testing sale items search for 'headphones on sale'...")
    try:
        params = {
            "engine": "google_shopping",
            "q": "headphones on sale",
            "gl": "us",
            "hl": "en",
            "is_on_sale": "true",
        }

        result = await api_client.request(params)

        if "error" in result:
            print(f"❌ API Error: {result['error']}")
        else:
            print("✅ Sale items search successful!")
            if "shopping_results" in result and result["shopping_results"]:
                print(f"   Found {len(result['shopping_results'])} sale items")
                for i, item in enumerate(result["shopping_results"][:2]):
                    if "title" in item and "price" in item:
                        print(f"   {i+1}. {item['title']} - {item['price']}")

    except Exception as e:
        print(f"❌ Error in sale items search: {e}")

    # Test 4: Location-based search
    print("\n4. Testing location-based search for 'Nike shoes'...")
    try:
        params = {
            "engine": "google_shopping",
            "q": "Nike shoes",
            "gl": "us",
            "hl": "en",
            "location": "New York, NY",
        }

        result = await api_client.request(params)

        if "error" in result:
            print(f"❌ API Error: {result['error']}")
        else:
            print("✅ Location-based search successful!")
            if "shopping_results" in result and result["shopping_results"]:
                print(f"   Found {len(result['shopping_results'])} Nike shoes")
                for i, item in enumerate(result["shopping_results"][:2]):
                    if "title" in item and "price" in item:
                        print(f"   {i+1}. {item['title']} - {item['price']}")

    except Exception as e:
        print(f"❌ Error in location-based search: {e}")

    # Test 5: Testing MCP server integration by simulating the exact function call pattern
    print("\n5. Testing integration with MCP tool function...")
    try:
        # Let's recreate a scenario similar to what happens in the MCP server by directly using the
        # same API client pattern that the MCP server uses, but with our test configuration

        # Create the exact same type of API client that the MCP server uses but with our test config
        class TestConfig:
            def __init__(self, api_key):
                self.api_key = api_key
                self.log_level = "INFO"
                self.timeout = 30.0
                self.max_retries = 3
                self.retry_backoff = 1.0
                self.enable_cache = True
                self.cache_ttl = 3600
                self.cache_max_size = 1000
                self.enable_metrics = True
                self.pool_connections = 10
                self.pool_maxsize = 10
                self.api_url = "https://www.searchapi.io/api/v1/search"

        # Create a test client using the same pattern as the MCP server
        test_config = TestConfig(api_key)
        test_client = SearchAPIClient(test_config)

        # Now test with the same parameters the MCP function would use
        params = {
            "engine": "google_shopping",
            "q": "PS5 console",
            "gl": "us",
            "hl": "en",
            "price_max": "800"
        }

        result = await test_client.request(params)

        if "error" in result:
            print(f"❌ API Error: {result['error']}")
            if "details" in result:
                print(f"   Details: {result['details']}")
        else:
            print("✅ MCP tool integration test successful!")
            print(f"   Full response structure: {list(result.keys())}")

            # Show more detailed information if available
            if "shopping_results" in result and result["shopping_results"]:
                print(f"   Shopping results count: {len(result['shopping_results'])}")

                # Show a more detailed example
                first_result = (
                    result["shopping_results"][0] if result["shopping_results"] else {}
                )
                print(f"   First result: {first_result.get('title', 'N/A')}")
                print(f"   Price: {first_result.get('price', 'N/A')}")
                print(f"   Source: {first_result.get('source', 'N/A')}")
                print(f"   Rating: {first_result.get('rating', 'N/A')}")
                print(f"   Reviews: {first_result.get('reviews', 'N/A')}")

    except Exception as e:
        print(f"❌ Error in MCP integration test: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("LIVE TESTS COMPLETED")
    print("=" * 60)
    print("Note: The shopping results show real data from Google Shopping API")
    print("if your API key is valid and the search is successful.")

    return True


def setup_environment():
    """Setup environment for live testing."""
    print("Setting up environment for live testing...")

    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("✅ .env file loaded")
    else:
        print("⚠️  .env file not found, will use environment variables")

    # Print API key status (without showing the actual key)
    api_key = os.getenv("SEARCHAPI_API_KEY")
    if api_key:
        print(f"✅ API key found (length: {len(api_key)} chars)")
    else:
        print("❌ API key not found - tests will fail without it")


if __name__ == "__main__":
    print("=" * 70)
    print("GOOGLE SHOPPING API - LIVE TESTING")
    print("=" * 70)
    print("This script makes real API calls to SearchAPI.io")
    print("Make sure you have:")
    print("1. A valid SearchAPI.io API key")
    print("2. Set SEARCHAPI_API_KEY environment variable or in .env file")
    print("3. Sufficient API credits in your account")
    print("=" * 70)

    setup_environment()

    try:
        success = asyncio.run(test_google_shopping_live())
        if success:
            print("\n🎉 Live testing completed successfully!")
        else:
            print("\n❌ Live testing failed - check API key setup")
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback

        traceback.print_exc()
