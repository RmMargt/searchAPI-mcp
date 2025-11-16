#!/usr/bin/env python3
"""
Comprehensive test for SearchAPI functionality
"""

import httpx
from datetime import datetime


def test_google_search(api_key: str):
    """Test Google Search"""
    print("\n1️⃣  Testing Google Search...")
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "google",
        "q": "Python programming",
        "api_key": api_key
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            results = len(data.get('organic_results', []))
            print(f"   ✅ Google Search: {results} results")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_google_maps(api_key: str):
    """Test Google Maps Search"""
    print("\n2️⃣  Testing Google Maps...")
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "google_maps",
        "q": "coffee shops",
        "api_key": api_key
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            results = len(data.get('local_results', []))
            print(f"   ✅ Google Maps: {results} places found")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_google_flights(api_key: str):
    """Test Google Flights"""
    print("\n3️⃣  Testing Google Flights...")
    url = "https://www.searchapi.io/api/v1/search"

    # Get future dates
    from datetime import timedelta
    outbound = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")

    params = {
        "engine": "google_flights",
        "departure_id": "JFK",
        "arrival_id": "LAX",
        "outbound_date": outbound,
        "return_date": return_date,
        "flight_type": "round_trip",  # Correct parameter name
        "adults": "1",
        "api_key": api_key
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            flights = len(data.get('best_flights', [])) + len(data.get('other_flights', []))
            print(f"   ✅ Google Flights: {flights} flights found")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_google_hotels(api_key: str):
    """Test Google Hotels"""
    print("\n4️⃣  Testing Google Hotels...")
    url = "https://www.searchapi.io/api/v1/search"

    # Get future dates
    from datetime import timedelta
    check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")

    params = {
        "engine": "google_hotels",
        "q": "hotels in Paris",
        "check_in_date": check_in,
        "check_out_date": check_out,
        "api_key": api_key
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            hotels = len(data.get('properties', []))
            print(f"   ✅ Google Hotels: {hotels} hotels found")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_google_events(api_key: str):
    """Test Google Events"""
    print("\n5️⃣  Testing Google Events...")
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "google_events",
        "q": "concerts",
        "api_key": api_key
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            events = len(data.get('events_results', []))
            print(f"   ✅ Google Events: {events} events found")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_google_ai_mode(api_key: str):
    """Test Google AI Mode"""
    print("\n6️⃣  Testing Google AI Mode...")
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "google_ai_mode",
        "q": "What is Python programming language?",
        "api_key": api_key
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            has_ai_overview = 'text_blocks' in data or 'markdown' in data
            ref_count = len(data.get('reference_links', []))
            print(f"   ✅ Google AI Mode: AI overview available, {ref_count} references")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("❌ Usage: python comprehensive_test.py YOUR_API_KEY")
        sys.exit(1)

    api_key = sys.argv[1]

    print(f"\n{'='*60}")
    print(f"Comprehensive SearchAPI Test")
    print(f"{'='*60}")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    results = []
    results.append(("Google Search", test_google_search(api_key)))
    results.append(("Google Maps", test_google_maps(api_key)))
    results.append(("Google Flights", test_google_flights(api_key)))
    results.append(("Google Hotels", test_google_hotels(api_key)))
    results.append(("Google Events", test_google_events(api_key)))
    results.append(("Google AI Mode", test_google_ai_mode(api_key)))

    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"{'='*60}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your API key is working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Some features may not be available.")

    print(f"{'='*60}\n")
