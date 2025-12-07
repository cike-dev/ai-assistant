#!/usr/bin/env python3
"""
Test script for the MCP server API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint_name, payload):
    """Test a specific API endpoint"""
    url = f"{BASE_URL}{endpoint_name}"

    try:
        response = requests.post(url, json=payload, timeout=30)

        print(f"\n=== Testing {endpoint_name} ===")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Query: {result.get('query', 'N/A')}")

            answer = result.get('answer', '')
            if answer:
                print(f"Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")

            sources = result.get('sources', [])
            if sources:
                print(f"Sources: {len(sources)} found")
                for i, source in enumerate(sources[:2], 1):  # Show first 2
                    print(f"  {i}. {source}")
                if len(sources) > 2:
                    print(f"  ... and {len(sources) - 2} more")
        else:
            print("❌ Error:")
            print(response.text)

    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    print("🧪 Testing MCP Server API")
    print("=" * 40)

    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print("API Root Status:", response.status_code)
        if response.status_code == 200:
            print("Available tools:", response.json().get('tools', []))
    except:
        print("❌ Could not connect to API server")
        print("Make sure to run: python mcp-server/api.py")
        return

    # Test each search endpoint
    test_queries = [
        ("/search/job_market_trends", {"query": "data science jobs in UK"}),
        ("/search/salary_data", {"query": "software engineer salary London"}),
        ("/search/industry_insights", {"query": "AI industry growth"}),
        ("/search/career_paths", {"query": "from accountant to data analyst"})
    ]

    for endpoint, payload in test_queries:
        test_endpoint(endpoint, payload)

    print("\n" + "=" * 40)
    print("Testing complete!")

if __name__ == "__main__":
    main()
