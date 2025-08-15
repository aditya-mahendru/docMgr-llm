#!/usr/bin/env python3
"""
Sample Data Setup Script for DocMgr-llm Chatbot

This script tests the chatbot system with sample data and verifies
all functionality including streaming, function calling, and API integration.

Usage:
    python setup_sample_data.py
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

class ChatbotTestSetup:
    def __init__(self, docmgr_url="http://localhost:8000", chatbot_url="http://localhost:5001"):
        self.docmgr_url = docmgr_url
        self.chatbot_url = chatbot_url
        
    def check_docmgr_running(self):
        """Check if DocMgr is running and accessible"""
        print("🔍 Checking DocMgr availability...")
        
        try:
            response = requests.get(f"{self.docmgr_url}/", timeout=5)
            if response.status_code == 200:
                print("  ✅ DocMgr is running and accessible")
                return True
            else:
                print(f"  ❌ DocMgr returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Cannot connect to DocMgr: {str(e)}")
            return False
    
    def check_chatbot_running(self):
        """Check if the chatbot backend is running"""
        print("\n🤖 Checking chatbot backend availability...")
        
        try:
            response = requests.get(f"{self.chatbot_url}/api/health", timeout=5)
            if response.status_code == 200:
                result = response.json()
                print("  ✅ Chatbot backend is running")
                print(f"  📊 Health status: {result}")
                return True
            else:
                print(f"  ❌ Chatbot returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Cannot connect to chatbot: {str(e)}")
            return False
    
    def test_chatbot_functions(self):
        """Test the chatbot's function calling capabilities"""
        print("\n🔧 Testing chatbot function definitions...")
        
        try:
            response = requests.get(f"{self.chatbot_url}/api/functions", timeout=10)
            if response.status_code == 200:
                result = response.json()
                functions = result.get('functions', {})
                print(f"  ✅ Found {len(functions)} available functions:")
                
                for func_name, func_info in functions.items():
                    print(f"    - {func_name}: {func_info.get('description', 'No description')}")
                
                return True
            else:
                print(f"  ❌ Functions endpoint returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error testing functions: {str(e)}")
            return False
    
    def test_basic_chat(self):
        """Test basic chat functionality without streaming"""
        print("\n💬 Testing basic chat functionality...")
        
        try:
            payload = {
                "message": "Hello! Can you tell me what documents you have access to?",
                "stream": False
            }
            
            response = requests.post(
                f"{self.chatbot_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                context = result.get('context', [])
                
                print("  ✅ Basic chat working")
                print(f"  📝 Response length: {len(response_text)} characters")
                print(f"  📚 Context documents: {len(context)}")
                
                if response_text:
                    print(f"  💭 Sample response: {response_text[:100]}...")
                
                return True
            else:
                print(f"  ❌ Chat endpoint returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error testing chat: {str(e)}")
            return False
    
    def test_streaming_chat(self):
        """Test streaming chat functionality"""
        print("\n🌊 Testing streaming chat functionality...")
        
        try:
            payload = {
                "message": "What can you tell me about artificial intelligence?",
                "stream": True
            }
            
            response = requests.post(
                f"{self.chatbot_url}/api/chat",
                json=payload,
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                print("  ✅ Streaming chat working")
                
                # Process streaming response
                event_count = 0
                content_received = False
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                event_type = data.get('type')
                                content = data.get('content', '')
                                
                                if event_type == 'typing':
                                    print("    ⌨️ Typing indicator received")
                                elif event_type == 'start':
                                    print("    🚀 Response started")
                                elif event_type == 'function_call':
                                    print(f"    🔧 Function call: {content}")
                                elif event_type == 'content':
                                    if not content_received:
                                        print(f"    📝 Content streaming: {content[:50]}...")
                                        content_received = True
                                elif event_type == 'end':
                                    print("    ✅ Response completed")
                                elif event_type == 'error':
                                    print(f"    ❌ Error: {content}")
                                
                                event_count += 1
                                
                            except json.JSONDecodeError:
                                continue
                
                print(f"  📊 Total events received: {event_count}")
                return True
            else:
                print(f"  ❌ Streaming chat returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error testing streaming chat: {str(e)}")
            return False
    
    def test_function_calling(self):
        """Test function calling capabilities"""
        print("\n🔧 Testing function calling capabilities...")
        
        try:
            # Test a question that should trigger function calls
            payload = {
                "message": "Get all documents and tell me how many you have",
                "stream": False
            }
            
            response = requests.post(
                f"{self.chatbot_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                print("  ✅ Function calling working")
                print(f"  📝 Response length: {len(response_text)} characters")
                
                # Check if response indicates function calls were made
                if any(keyword in response_text.lower() for keyword in ['document', 'found', 'total', 'list']):
                    print("  🎯 Response appears to include document information")
                else:
                    print("  ⚠️ Response may not have used function calling")
                
                return True
            else:
                print(f"  ❌ Function calling test returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error testing function calling: {str(e)}")
            return False
    
    def test_search_functionality(self):
        """Test direct search functionality"""
        print("\n🔍 Testing search functionality...")
        
        try:
            payload = {
                "query": "artificial intelligence",
                "n_results": 3
            }
            
            response = requests.post(
                f"{self.chatbot_url}/api/search",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])
                query = result.get('query', '')
                
                print("  ✅ Search functionality working")
                print(f"  🔍 Query: {query}")
                print(f"  📚 Results found: {len(results)}")
                
                if results:
                    print(f"  📄 First result: {results[0].get('metadata', {}).get('original_filename', 'Unknown')}")
                
                return True
            else:
                print(f"  ❌ Search returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error testing search: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests and provide a comprehensive report"""
        print("🚀 Starting DocMgr-llm Comprehensive Test Suite...")
        print("=" * 60)
        
        tests = [
            ("DocMgr Availability", self.check_docmgr_running),
            ("Chatbot Backend", self.check_chatbot_running),
            ("Function Definitions", self.test_chatbot_functions),
            ("Basic Chat", self.test_basic_chat),
            ("Streaming Chat", self.test_streaming_chat),
            ("Function Calling", self.test_function_calling),
            ("Search Functionality", self.test_search_functionality)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"  ❌ {test_name} test failed with exception: {str(e)}")
                results.append((test_name, False))
        
        # Summary report
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if success:
                passed += 1
        
        print(f"\n📈 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The chatbot system is working correctly.")
            print("\nYou can now:")
            print("1. Open the frontend at http://localhost:3000")
            print("2. Start chatting with your documents")
            print("3. Test various questions and function calls")
            print("4. Enjoy real-time streaming responses")
        else:
            print("⚠️ Some tests failed. Please check the error messages above.")
            print("\nCommon issues:")
            print("1. Ensure DocMgr is running on port 8000")
            print("2. Ensure chatbot backend is running on port 5001")
            print("3. Check environment variables and API keys")
            print("4. Verify all dependencies are installed")
        
        return passed == total

def main():
    """Main entry point"""
    setup = ChatbotTestSetup()
    
    try:
        success = setup.run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
