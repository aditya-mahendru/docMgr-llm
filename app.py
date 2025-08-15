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

chatbot_api = ChatbotAPI(DOCMGR_BASE_URL)

def generate_chat_response_stream(user_message, context_chunks):
    """Generate a streaming response using Groq API with document context"""
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
        
        system_prompt = f"""You are a helpful assistant that answers questions based on the provided document context. 
        Use only the information from the documents to answer questions. If the question cannot be answered from the provided context, 
        say so clearly. Be concise and accurate in your responses.

        Document Context:
        {context}"""
        
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
        
        # Use Groq's streaming API
        stream = client.chat.completions.create(
            model="openai/gpt-oss-20b",  # Fast and efficient model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield "data: " + json.dumps({
                    "type": "content",
                    "content": chunk.choices[0].delta.content
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
    """Generate a response using Groq API with document context (non-streaming fallback)"""
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
        
        system_prompt = f"""You are a helpful assistant that answers questions based on the provided document context. 
        Use only the information from the documents to answer questions. If the question cannot be answered from the provided context, 
        say so clearly. Be concise and accurate in your responses.

        Document Context:
        {context}"""
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Fast and efficient model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error generating chat response: {e}")
        return "Sorry, I encountered an error while processing your request."

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with streaming support"""
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'docmgr_url': DOCMGR_BASE_URL})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
