#!/usr/bin/env python3
"""
Test script for Ethics-Bench Green Agent
Tests local functionality before deployment
"""

import requests
import json
import sys
import time
from datetime import datetime

def test_agent(base_url="http://localhost:9012"):
    """Test all agent endpoints"""
    print(f"🧪 Testing Ethics Green Agent at {base_url}")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health check
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            tests_passed += 1
        else:
            print(f"❌ Health check: FAILED (status {response.status_code})")
    except Exception as e:
        print(f"❌ Health check: FAILED ({e})")
    
    # Test 2: Agent card
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/.well-known/agent-card.json", timeout=5)
        if response.status_code == 200:
            card = response.json()
            if "name" in card and "capabilities" in card:
                print("✅ Agent card: PASSED")
                tests_passed += 1
            else:
                print("❌ Agent card: FAILED (missing required fields)")
        else:
            print(f"❌ Agent card: FAILED (status {response.status_code})")
    except Exception as e:
        print(f"❌ Agent card: FAILED ({e})")
    
    # Test 3: Root endpoint
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint: PASSED")
            tests_passed += 1
        else:
            print(f"❌ Root endpoint: FAILED (status {response.status_code})")
    except Exception as e:
        print(f"❌ Root endpoint: FAILED ({e})")
    
    # Test 4: Evaluation endpoint
    tests_total += 1
    try:
        test_scenario = {
            "scenario": "A self-driving car must choose between hitting one person or five people",
            "context": "Urban intersection, emergency situation"
        }
        response = requests.post(
            f"{base_url}/evaluate",
            json=test_scenario,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if "evaluation_id" in result and "score" in result:
                print("✅ Evaluation endpoint: PASSED")
                print(f"   Score: {result.get('overall_score', 'N/A')}")
                tests_passed += 1
            else:
                print("❌ Evaluation endpoint: FAILED (missing required fields)")
        else:
            print(f"❌ Evaluation endpoint: FAILED (status {response.status_code})")
    except Exception as e:
        print(f"❌ Evaluation endpoint: FAILED ({e})")
    
    # Test 5: API docs
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs: PASSED")
            tests_passed += 1
        else:
            print(f"❌ API docs: FAILED (status {response.status_code})")
    except Exception as e:
        print(f"❌ API docs: FAILED ({e})")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! Agent is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the agent configuration.")
        return False

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:9012"
    
    print(f"Testing agent at: {base_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Wait a moment for agent to be ready
    time.sleep(1)
    
    success = test_agent(base_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()