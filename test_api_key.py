#!/usr/bin/env python3
"""
Simple script to test SearchAPI API key
"""

import os
import sys
import httpx
from datetime import datetime


def test_api_key(api_key: str):
    """Test if the provided API key is valid"""

    print(f"\n{'='*60}")
    print(f"Testing SearchAPI API Key")
    print(f"{'='*60}")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Test with a simple Google search
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "google",
        "q": "test",
        "api_key": api_key
    }

    try:
        print("📡 Sending test request to SearchAPI...")
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)

        print(f"📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n✅ API Key is VALID!")
            print("\nResponse Summary:")
            print(f"  - Search Query: {data.get('search_parameters', {}).get('q', 'N/A')}")
            print(f"  - Engine: {data.get('search_parameters', {}).get('engine', 'N/A')}")

            if 'organic_results' in data:
                print(f"  - Organic Results: {len(data.get('organic_results', []))} results found")

            if 'answer_box' in data:
                print(f"  - Answer Box: Available")

            if 'knowledge_graph' in data:
                print(f"  - Knowledge Graph: Available")

            print(f"\n✨ Test completed successfully!")
            return True

        elif response.status_code == 401:
            print("\n❌ API Key is INVALID!")
            print("Error: Authentication failed (401 Unauthorized)")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"Details: {error_data['error']}")
            except:
                pass
            return False

        elif response.status_code == 403:
            print("\n⚠️  API Key has insufficient permissions (403 Forbidden)")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"Details: {error_data['error']}")
            except:
                pass
            return False

        elif response.status_code == 429:
            print("\n⚠️  Rate limit exceeded (429 Too Many Requests)")
            print("Your API key is valid but you've exceeded the rate limit.")
            return True

        else:
            print(f"\n⚠️  Unexpected response: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

    except httpx.TimeoutException:
        print("\n❌ Request timed out")
        print("Please check your internet connection")
        return False

    except httpx.ConnectError:
        print("\n❌ Connection failed")
        print("Please check your internet connection")
        return False

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        return False


if __name__ == "__main__":
    # Get API key from command line argument or environment variable
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.getenv("SEARCHAPI_API_KEY")

    if not api_key:
        print("❌ No API key provided!")
        print("\nUsage:")
        print("  python test_api_key.py YOUR_API_KEY")
        print("  or set SEARCHAPI_API_KEY environment variable")
        sys.exit(1)

    success = test_api_key(api_key)
    sys.exit(0 if success else 1)
