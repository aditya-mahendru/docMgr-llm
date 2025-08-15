from flask import Flask, request, jsonify, Response, stream_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import json
import time
import queue
import threading

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
DOCMGR_BASE_URL = os.getenv('DOCMGR_BASE_URL', 'http://localhost:8000')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

class ChatbotAPI:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def search_documents(self, query, n_results=5):
        """Search for relevant document chunks"""
        try:
            response = requests.post(
                f"{self.base_url}/api/search",
                json={"query": query, "n_results": n_results}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_document_chunks(self, document_id):
        """Get chunks for a specific document"""
        try:
            response = requests.get(
                f"{self.base_url}/api/documents/{document_id}/chunks"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting document chunks: {e}")
            return []
    
    def get_all_documents(self):
        """Get all documents"""
        try:
            response = requests.get(f"{self.base_url}/api/documents")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting all documents: {e}")
            return []
    
    def get_document_by_id(self, document_id):
        """Get a specific document by ID"""
        try:
            response = requests.get(f"{self.base_url}/api/documents/{document_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting document {document_id}: {e}")
            return None
    
    def get_vector_stats(self):
        """Get vector collection statistics"""
        try:
            response = requests.get(f"{self.base_url}/api/vector/stats")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting vector stats: {e}")
            return None
    
    def get_api_info(self):
        """Get API information and available endpoints"""
        try:
            response = requests.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting API info: {e}")
            return None

chatbot_api = ChatbotAPI(DOCMGR_BASE_URL)

# Function definitions for Groq function calling
AVAILABLE_FUNCTIONS = {
    "get_all_documents": {
        "name": "get_all_documents",
        "description": "Get a list of all documents in the system",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_document_by_id": {
        "name": "get_document_by_id",
        "description": "Get detailed information about a specific document",
        "parameters": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": "The ID of the document to retrieve"
                }
            },
            "required": ["document_id"]
        }
    },
    "get_document_chunks": {
        "name": "get_document_chunks",
        "description": "Get all text chunks for a specific document",
        "parameters": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "integer",
                    "description": "The ID of the document to get chunks for"
                }
            },
            "required": ["document_id"]
        }
    },
    "get_vector_stats": {
        "name": "get_vector_stats",
        "description": "Get statistics about the vector database and document chunks",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "search_documents": {
        "name": "search_documents",
        "description": "Search for documents using semantic similarity",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documents"
                },
                "n_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5, max: 20)"
                }
            },
            "required": ["query"]
        }
    },
    "get_api_info": {
        "name": "get_api_info",
        "description": "Get information about available API endpoints and system status",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

def execute_function_call(function_name, arguments):
    """Execute a function call based on the function name and arguments"""
    try:
        if function_name == "get_all_documents":
            return chatbot_api.get_all_documents()
        
        elif function_name == "get_document_by_id":
            document_id = arguments.get("document_id")
            if document_id is None:
                return {"error": "document_id is required"}
            return chatbot_api.get_document_by_id(document_id)
        
        elif function_name == "get_document_chunks":
            document_id = arguments.get("document_id")
            if document_id is None:
                return {"error": "document_id is required"}
            return chatbot_api.get_document_chunks(document_id)
        
        elif function_name == "get_vector_stats":
            return chatbot_api.get_vector_stats()
        
        elif function_name == "search_documents":
            query = arguments.get("query")
            n_results = arguments.get("n_results", 5)
            if query is None:
                return {"error": "query is required"}
            return chatbot_api.search_documents(query, min(n_results, 20))
        
        elif function_name == "get_api_info":
            return chatbot_api.get_api_info()
        
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    except Exception as e:
        return {"error": f"Function execution failed: {str(e)}"}

def generate_chat_response_stream(user_message, context_chunks):
    """Generate a streaming response using Groq API with document context and function calling"""
    if not GROQ_API_KEY:
        yield "data: " + json.dumps({
            "type": "error",
            "content": "Groq API key not configured. Please set GROQ_API_KEY environment variable."
        }) + "\n\n"
        return
    
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        # Prepare context from document chunks
        context = "\n\n".join([
            f"Document: {chunk['metadata']['original_filename']}\nContent: {chunk['content']}"
            for chunk in context_chunks
        ])
        
        system_prompt = f"""You are a helpful AI assistant that can access and analyze documents in the DocMgr system. You have access to several functions that allow you to:

1. Get information about all documents
2. Retrieve specific documents by ID
3. Get document chunks and content
4. Search documents semantically
5. Get system statistics
6. Access API information

Use these functions when users ask questions that require:
- Listing documents
- Getting document details
- Searching for specific content
- Understanding system status
- Analyzing document collections

Always explain what you're doing and provide helpful context. If a user asks about documents, use the appropriate functions to get current information.

Document Context (if available):
{context}

Available Functions:
{json.dumps(list(AVAILABLE_FUNCTIONS.keys()), indent=2)}

Remember: You can call multiple functions to gather comprehensive information before providing a response."""
        
        # Send typing indicator
        yield "data: " + json.dumps({
            "type": "typing",
            "content": "typing"
        }) + "\n\n"
        
        # Small delay to show typing indicator
        time.sleep(0.5)
        
        # Start streaming response
        yield "data: " + json.dumps({
            "type": "start",
            "content": ""
        }) + "\n\n"
        
        # Use Groq's function calling API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Check if function calling is needed
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            tools=[{"type": "function", "function": func} for func in AVAILABLE_FUNCTIONS.values()],
            tool_choice="auto",
            max_tokens=1000,
            temperature=0.7,
            stream=True
        )
        
        function_calls = []
        current_response = ""
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                current_response += chunk.choices[0].delta.content
                yield "data: " + json.dumps({
                    "type": "content",
                    "content": chunk.choices[0].delta.content
                }) + "\n\n"
            
            # Check for tool calls
            if chunk.choices[0].delta.tool_calls:
                for tool_call in chunk.choices[0].delta.tool_calls:
                    if tool_call.function:
                        function_calls.append(tool_call)
        
        # Execute function calls if any
        if function_calls:
            yield "data: " + json.dumps({
                "type": "function_call",
                "content": "Executing function calls to gather information..."
            }) + "\n\n"
            
            for tool_call in function_calls:
                if tool_call.function:
                    function_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                        result = execute_function_call(function_name, arguments)
                        
                        # Add function result to context
                        messages.append({
                            "role": "assistant",
                            "content": f"I called the function {function_name} to get more information."
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(result)
                        })
                        
                        # Generate final response with function results
                        final_response = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7,
                            stream=True
                        )
                        
                        yield "data: " + json.dumps({
                            "type": "content",
                            "content": f"\n\nBased on the information I gathered: "
                        }) + "\n\n"
                        
                        for chunk in final_response:
                            if chunk.choices[0].delta.content:
                                yield "data: " + json.dumps({
                                    "type": "content",
                                    "content": chunk.choices[0].delta.content
                                }) + "\n\n"
                        
                    except Exception as e:
                        yield "data: " + json.dumps({
                            "type": "content",
                            "content": f"\n\nI encountered an error while gathering information: {str(e)}"
                        }) + "\n\n"
        
        # Send end marker
        yield "data: " + json.dumps({
            "type": "end",
            "content": ""
        }) + "\n\n"
        
    except Exception as e:
        print(f"Error generating chat response: {e}")
        yield "data: " + json.dumps({
            "type": "error",
            "content": "Sorry, I encountered an error while processing your request."
        }) + "\n\n"

def generate_chat_response(user_message, context_chunks):
    """Generate a response using Groq API with document context and function calling (non-streaming fallback)"""
    if not GROQ_API_KEY:
        return "Groq API key not configured. Please set GROQ_API_KEY environment variable."
    
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        # Prepare context from document chunks
        context = "\n\n".join([
            f"Document: {chunk['metadata']['original_filename']}\nContent: {chunk['content']}"
            for chunk in context_chunks
        ])
        
        system_prompt = f"""You are a helpful AI assistant that can access and analyze documents in the DocMgr system. You have access to several functions that allow you to:

1. Get information about all documents
2. Retrieve specific documents by ID
3. Get document chunks and content
4. Search documents semantically
5. Get system statistics
6. Access API information

Use these functions when users ask questions that require:
- Listing documents
- Getting document details
- Searching for specific content
- Understanding system status
- Analyzing document collections

Always explain what you're doing and provide helpful context. If a user asks about documents, use the appropriate functions to get current information.

Document Context (if available):
{context}

Available Functions:
{json.dumps(list(AVAILABLE_FUNCTIONS.keys()), indent=2)}

Remember: You can call multiple functions to gather comprehensive information before providing a response."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Check if function calling is needed
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            tools=[{"type": "function", "function": func} for func in AVAILABLE_FUNCTIONS.values()],
            tool_choice="auto",
            max_tokens=1000,
            temperature=0.7
        )
        
        # Handle function calls if any
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.function:
                    function_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                        result = execute_function_call(function_name, arguments)
                        
                        # Add function result to context
                        messages.append({
                            "role": "assistant",
                            "content": f"I called the function {function_name} to get more information."
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(result)
                        })
                        
                        # Generate final response with function results
                        final_response = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7
                        )
                        
                        return final_response.choices[0].message.content
                        
                    except Exception as e:
                        return f"I encountered an error while gathering information: {str(e)}"
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error generating chat response: {e}")
        return "Sorry, I encountered an error while processing your request."

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with streaming support and function calling"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        stream = data.get('stream', False)
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Search for relevant document chunks
        search_results = chatbot_api.search_documents(user_message, n_results=3)
        
        if not search_results:
            if stream:
                def generate_error_stream():
                    yield "data: " + json.dumps({
                        "type": "error",
                        "content": "I don't have any relevant documents to answer your question. Please try rephrasing or ask about something else."
                    }) + "\n\n"
                
                return Response(generate_error_stream(), mimetype='text/event-stream')
            else:
                return jsonify({
                    'response': 'I don\'t have any relevant documents to answer your question. Please try rephrasing or ask about something else.',
                    'context': []
                })
        
        if stream:
            # Return streaming response
            return Response(
                generate_chat_response_stream(user_message, search_results),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Cache-Control'
                }
            )
        else:
            # Return regular response (fallback)
            response = generate_chat_response(user_message, search_results)
            
            return jsonify({
                'response': response,
                'context': search_results
            })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Search documents directly"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        n_results = data.get('n_results', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        search_results = chatbot_api.search_documents(query, n_results)
        
        return jsonify({
            'results': search_results,
            'query': query
        })
    
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/functions', methods=['GET'])
def get_available_functions():
    """Get list of available functions for the chatbot"""
    return jsonify({
        'functions': AVAILABLE_FUNCTIONS,
        'description': 'Available functions for the AI chatbot to access DocMgr data'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'docmgr_url': DOCMGR_BASE_URL})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
