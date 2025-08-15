#!/usr/bin/env python3
"""
Test script for DocMgr Chatbot backend
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5001/api/health')
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"DocMgr URL: {data.get('docmgr_url')}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on localhost:5001")
        return False

def test_search_endpoint():
    """Test the search endpoint"""
    try:
        response = requests.post('http://localhost:5001/api/search', 
                               json={'query': 'test query', 'n_results': 3})
        print(f"Search Endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data.get('query')}")
            print(f"Results count: {len(data.get('results', []))}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on localhost:5001")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    try:
        response = requests.post('http://localhost:5001/api/chat', 
                               json={'message': 'Hello, how are you?'})
        print(f"Chat Endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response')[:100]}...")
            print(f"Context count: {len(data.get('context', []))}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on localhost:5001")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing DocMgr Chatbot Backend")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please create one from env_example.txt")
        return
    
    # Check required environment variables
    docmgr_url = os.getenv('DOCMGR_BASE_URL')
    groq_key = os.getenv('GROQ_API_KEY')
    
    print(f"DocMgr URL: {docmgr_url}")
    print(f"Groq API Key: {'✅ Set' if groq_key else '❌ Not set'}")
    print()
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Search Endpoint", test_search_endpoint),
        ("Chat Endpoint", test_chat_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            print(f"✅ {test_name} passed")
            passed += 1
        else:
            print(f"❌ {test_name} failed")
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
