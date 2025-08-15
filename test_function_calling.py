#!/usr/bin/env python3
"""
Test script for DocMgr Chatbot function calling capabilities
"""

import requests
import json
import time

def test_available_functions():
    """Test the functions endpoint"""
    print("🧪 Testing Available Functions Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:5001/api/functions')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Functions endpoint working (Status: {response.status_code})")
            print(f"📋 Available functions: {len(data['functions'])}")
            for func_name in data['functions'].keys():
                print(f"   • {func_name}")
            return True
        else:
            print(f"❌ Functions endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on localhost:5001")
        return False
    except Exception as e:
        print(f"❌ Error testing functions endpoint: {e}")
        return False

def test_function_calling_chat():
    """Test chat with function calling capabilities"""
    print("\n🧪 Testing Function Calling Chat")
    print("=" * 40)
    
    test_questions = [
        "How many documents do I have in the system?",
        "What documents are available?",
        "Show me the system statistics",
        "What API endpoints are available?",
        "Can you list all my documents with their file sizes?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nQuestion {i}: {question}")
        print("-" * 30)
        
        try:
            response = requests.post(
                'http://localhost:5001/api/chat',
                json={
                    'message': question,
                    'stream': False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received")
                print(f"📝 Response: {data.get('response', 'No response')[:200]}...")
                print(f"🔍 Context count: {len(data.get('context', []))}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Backend server is not running on localhost:5001")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Small delay between requests

def test_streaming_function_calling():
    """Test streaming chat with function calling"""
    print("\n🧪 Testing Streaming Function Calling")
    print("=" * 40)
    
    try:
        response = requests.post(
            'http://localhost:5001/api/chat',
            json={
                'message': 'List all my documents and show me the system statistics',
                'stream': True
            },
            stream=True
        )
        
        if response.status_code == 200:
            print(f"✅ Streaming response received (Status: {response.status_code})")
            print("📡 Processing streaming data with function calls...")
            print()
            
            event_count = 0
            function_call_events = 0
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            event_count += 1
                            
                            print(f"Event {event_count}: {data['type']}")
                            
                            if data['type'] == 'typing':
                                print("   🖊️  AI is typing...")
                            elif data['type'] == 'start':
                                print("   🚀 Starting response...")
                            elif data['type'] == 'function_call':
                                function_call_events += 1
                                print("   🔍 Function call detected!")
                                print(f"   📋 {data['content']}")
                            elif data['type'] == 'content':
                                print(f"   📝 Content: {data['content'][:50]}{'...' if len(data['content']) > 50 else ''}")
                            elif data['type'] == 'end':
                                print("   ✅ Response complete")
                                break
                            elif data['type'] == 'error':
                                print(f"   ❌ Error: {data['content']}")
                                break
                            
                        except json.JSONDecodeError as e:
                            print(f"   ⚠️  Failed to parse JSON: {e}")
                            print(f"   Raw line: {line_str}")
            
            print(f"\n📊 Total events processed: {event_count}")
            print(f"🔍 Function call events: {function_call_events}")
            
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on localhost:5001")
        print("Please start the backend first with: ./start_backend.sh")
    except Exception as e:
        print(f"❌ Error testing streaming: {e}")

def main():
    """Run all function calling tests"""
    print("🚀 DocMgr Chatbot Function Calling Tests")
    print("=" * 50)
    
    # Test available functions endpoint
    test_available_functions()
    
    # Test function calling in regular chat
    test_function_calling_chat()
    
    # Test streaming function calling
    test_streaming_function_calling()
    
    print("\n" + "=" * 50)
    print("✨ Function calling tests complete!")
    print("\n💡 Try asking the chatbot questions like:")
    print("   • 'How many documents do I have?'")
    print("   • 'Show me all my documents'")
    print("   • 'What's the system status?'")
    print("   • 'Search for documents about [topic]'")

if __name__ == "__main__":
    main()
