#!/usr/bin/env python3
"""
Test script for DocMgr Chatbot streaming functionality with Groq
"""

import requests
import json
import time

def test_streaming_chat():
    """Test the streaming chat endpoint"""
    print("🧪 Testing Streaming Chat Endpoint (Groq)")
    print("=" * 40)
    
    try:
        # Test streaming chat
        response = requests.post(
            'http://localhost:5001/api/chat',
            json={
                'message': 'Hello, can you tell me about the documents you have?',
                'stream': True
            },
            stream=True
        )
        
        if response.status_code == 200:
            print(f"✅ Streaming response received (Status: {response.status_code})")
            print("📡 Processing streaming data from Groq...")
            print()
            
            event_count = 0
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
            
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on localhost:5001")
        print("Please start the backend first with: ./start_backend.sh")
    except Exception as e:
        print(f"❌ Error testing streaming: {e}")

def test_regular_chat():
    """Test the regular (non-streaming) chat endpoint"""
    print("\n🧪 Testing Regular Chat Endpoint (Groq)")
    print("=" * 40)
    
    try:
        response = requests.post(
            'http://localhost:5001/api/chat',
            json={
                'message': 'Hello, this is a test message',
                'stream': False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Regular response received (Status: {response.status_code})")
            print(f"📝 Response: {data.get('response', 'No response')[:100]}...")
            print(f"🔍 Context count: {len(data.get('context', []))}")
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on localhost:5001")
    except Exception as e:
        print(f"❌ Error testing regular chat: {e}")

def main():
    """Run all streaming tests"""
    print("🚀 DocMgr Chatbot Streaming Tests with Groq")
    print("=" * 50)
    
    # Test streaming functionality
    test_streaming_chat()
    
    # Test regular functionality
    test_regular_chat()
    
    print("\n" + "=" * 50)
    print("✨ Testing complete!")

if __name__ == "__main__":
    main()
