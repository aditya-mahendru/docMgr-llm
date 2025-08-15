# DocMgr Chatbot

A modern chatbot interface that allows users to interact with documents stored in the DocMgr system. The chatbot uses semantic search to find relevant document chunks and generates contextual responses using **Groq's fast LLM models** with **real-time streaming**, **typing indicators**, and **advanced function calling** capabilities.

## Features

- **Document Chat**: Ask questions about your uploaded documents and get AI-powered responses
- **Real-time Streaming**: Watch responses appear word-by-word in real-time
- **Typing Indicators**: See when the AI is thinking and typing responses
- **Function Calling**: AI can access all DocMgr APIs to gather comprehensive information
- **Semantic Search**: Search through document chunks with relevance scoring
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **Interactive Chat**: Real-time chat interface with message history
- **Context Awareness**: Bot responses include source document information
- **Document Search Panel**: Toggle between chat and search modes
- **Fast Inference**: Powered by Groq's high-performance LLM infrastructure
- **System Integration**: Full access to DocMgr system data and statistics

## Architecture

The project consists of two main components:

1. **Backend (Flask)**: Python Flask application with Server-Sent Events (SSE) for streaming and function calling
2. **Frontend (React)**: Modern web interface with real-time streaming support and function call indicators

## Prerequisites

- Python 3.8+
- Node.js 16+
- DocMgr project running on localhost:8000
- **Groq API key** (get one at [console.groq.com](https://console.groq.com))

## Setup Instructions

### 1. Backend Setup

1. Navigate to the project directory:
   ```bash
   cd docMgr-llm
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp env_example.txt .env
   ```

5. Edit `.env` file with your configuration:
   ```env
   DOCMGR_BASE_URL=http://localhost:8000
   GROQ_API_KEY=your_groq_api_key_here
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Install additional dependencies for Tailwind CSS:
   ```bash
   npm install -D tailwindcss@^3.4.0 autoprefixer@^10.4.16 postcss@^8.4.32
   ```

## Running the Application

### 1. Start the Backend

1. Activate your virtual environment (if not already active):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Start the Flask server:
   ```bash
   python app.py
   ```

The backend will run on `http://localhost:5001`

### 2. Start the Frontend

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd docMgr-llm/frontend
   ```

2. Start the React development server:
   ```bash
   npm start
   ```

The frontend will run on `http://localhost:3000`

## Usage

1. **Chat with Documents**: Type questions in the chat input to get AI-powered responses
2. **Real-time Streaming**: Watch responses appear word-by-word as the AI generates them
3. **Typing Indicators**: See animated indicators when the AI is thinking
4. **Function Calling**: AI automatically accesses DocMgr APIs to gather information
5. **Search Documents**: Use the search panel to find specific content within your documents
6. **View Sources**: Each bot response shows the source documents used to generate the answer

## Advanced Function Calling

### What is Function Calling?

The chatbot now has **intelligent function calling** capabilities that allow it to:
- Access all DocMgr GET APIs automatically
- Gather comprehensive information before responding
- Provide real-time system status and statistics
- List and analyze documents dynamically
- Search through document collections intelligently

### Available Functions

The AI can automatically call these functions:

1. **`get_all_documents`** - List all documents in the system
2. **`get_document_by_id`** - Get detailed information about a specific document
3. **`get_document_chunks`** - Retrieve all text chunks for a document
4. **`get_vector_stats`** - Get vector database statistics
5. **`search_documents`** - Perform semantic search queries
6. **`get_api_info`** - Get system API information and status

### Example Interactions

- **"How many documents do I have?"** → AI calls `get_all_documents` and counts them
- **"Show me document details for ID 5"** → AI calls `get_document_by_id(5)`
- **"What's the system status?"** → AI calls `get_api_info` and `get_vector_stats`
- **"Search for documents about machine learning"** → AI calls `search_documents` with the query

## Streaming Features

### Backend Streaming

The chatbot now supports **Server-Sent Events (SSE)** for real-time streaming:

- **Typing Indicator**: Shows when the AI is processing
- **Function Call Detection**: Shows when AI is gathering information
- **Content Streaming**: Responses appear word-by-word in real-time
- **Event Types**: 
  - `typing`: AI is thinking
  - `start`: Response generation begins
  - `function_call`: AI is executing functions
  - `content`: Streaming text content
  - `end`: Response complete
  - `error`: Error occurred

### Frontend Streaming

The React frontend handles streaming with:

- **Real-time Updates**: Messages update as content streams in
- **Typing Animation**: Animated dots show when AI is thinking
- **Function Call Indicators**: Shows when AI is gathering data
- **Streaming Cursor**: Blinking cursor during text generation
- **Smooth Scrolling**: Auto-scrolls to follow new content

## Groq Integration

### Why Groq?

- **🚀 Ultra-fast inference**: Responses in milliseconds
- **💰 Cost-effective**: Competitive pricing for high-performance models
- **🔒 Privacy-focused**: Enterprise-grade security
- **📈 Scalable**: Handles high-volume requests efficiently
- **🛠️ Function Calling**: Native support for tool/function execution

### Model Used

The chatbot uses **`llama3-8b-8192`**, a fast and efficient model that provides:
- Quick response generation
- Good context understanding
- Cost-effective token usage
- Reliable streaming support
- Advanced function calling capabilities

## API Endpoints

### Backend (Flask)

- `POST /api/chat` - Send a chat message and get AI response (supports streaming + function calling)
- `POST /api/search` - Search documents directly
- `GET /api/functions` - Get list of available functions
- `GET /api/health` - Health check endpoint

### Streaming Parameters

```json
{
  "message": "Your question here",
  "stream": true  // Enable streaming
}
```

### Frontend Proxy

The React app proxies API calls to the Flask backend running on port 5001.

## Configuration

### Environment Variables

- `DOCMGR_BASE_URL`: URL of your DocMgr API (default: http://localhost:8000)
- `GROQ_API_KEY`: Your Groq API key for generating responses
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable/disable Flask debug mode

### Tailwind CSS

The project uses Tailwind CSS for styling. Configuration is in `frontend/tailwind.config.js`.

## Testing

### Test Function Calling Capabilities

```bash
# Test function calling
python test_function_calling.py

# Test streaming chat
python test_streaming.py

# Test regular functionality
python test_backend.py
```

## Troubleshooting

### Common Issues

1. **Backend Connection Error**: Ensure DocMgr is running on the specified URL
2. **Groq API Errors**: Verify your API key is correct and has sufficient credits
3. **Streaming Issues**: Check browser console for SSE connection errors
4. **Frontend Build Issues**: Clear node_modules and reinstall dependencies
5. **CORS Issues**: The backend has CORS enabled, but ensure both servers are running
6. **Tailwind CSS Issues**: Ensure correct versions are installed (`tailwindcss@^3.4.0`)
7. **Function Calling Errors**: Check if DocMgr APIs are accessible and responding

### Logs

Check the Flask console output for backend errors and the browser console for frontend issues.

## Development

### Project Structure

```
docMgr-llm/
├── app.py                 # Flask backend with Groq streaming + function calling
├── requirements.txt       # Python dependencies (includes groq)
├── env_example.txt       # Environment variables template
├── start_backend.sh      # Backend startup script
├── start_frontend.sh     # Frontend startup script
├── test_backend.py       # Backend testing script
├── test_streaming.py     # Streaming functionality tests
├── test_function_calling.py # Function calling tests
├── frontend/             # React application
│   ├── package.json      # Node.js dependencies
│   ├── src/              # React components with streaming + function calling
│   └── tailwind.config.js # CSS configuration
└── README.md             # This file
```

### Adding New Features

1. **Backend**: Add new routes in `app.py`
2. **Frontend**: Create new components in `frontend/src/`
3. **Styling**: Use Tailwind CSS classes or extend the configuration
4. **Streaming**: Extend the SSE event types for new functionality
5. **Groq Models**: Switch between different Groq models as needed
6. **Function Calling**: Add new functions to `AVAILABLE_FUNCTIONS`

## Performance

### Streaming Benefits

- **Faster Perceived Response**: Users see content immediately
- **Better UX**: Typing indicators and real-time updates
- **Reduced Latency**: No waiting for complete response
- **Interactive Feel**: More engaging chat experience

### Function Calling Benefits

- **Comprehensive Responses**: AI can gather all relevant information
- **Real-time Data**: Always up-to-date information from DocMgr
- **Intelligent Analysis**: AI can combine multiple data sources
- **Dynamic Interactions**: Responses adapt to current system state

### Groq Advantages

- **Ultra-fast Inference**: Responses in milliseconds
- **Efficient Streaming**: Smooth real-time text generation
- **Cost Optimization**: Better token-to-cost ratio
- **Reliability**: Enterprise-grade infrastructure
- **Function Support**: Native tool calling capabilities

### Optimization Tips

- Use appropriate chunk sizes for streaming
- Implement proper error handling for network issues
- Consider implementing retry logic for failed streams
- Monitor memory usage during long conversations
- Leverage Groq's fast models for better user experience
- Cache function call results when appropriate
- Implement rate limiting for function calls

## License

This project is part of the DocMgr ecosystem and follows the same licensing terms.