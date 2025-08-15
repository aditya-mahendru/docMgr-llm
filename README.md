# DocMgr Chatbot

A modern chatbot interface that allows users to interact with documents stored in the DocMgr system. The chatbot uses semantic search to find relevant document chunks and generates contextual responses using **Groq's fast LLM models** with **real-time streaming** and **typing indicators**.

## Features

- **Document Chat**: Ask questions about your uploaded documents and get AI-powered responses
- **Real-time Streaming**: Watch responses appear word-by-word in real-time
- **Typing Indicators**: See when the AI is thinking and typing responses
- **Semantic Search**: Search through document chunks with relevance scoring
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **Interactive Chat**: Real-time chat interface with message history
- **Context Awareness**: Bot responses include source document information
- **Document Search Panel**: Toggle between chat and search modes
- **Fast Inference**: Powered by Groq's high-performance LLM infrastructure

## Architecture

The project consists of two main components:

1. **Backend (Flask)**: Python Flask application with Server-Sent Events (SSE) for streaming
2. **Frontend (React)**: Modern web interface with real-time streaming support

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
4. **Search Documents**: Use the search panel to find specific content within your documents
5. **View Sources**: Each bot response shows the source documents used to generate the answer

## Streaming Features

### Backend Streaming

The chatbot now supports **Server-Sent Events (SSE)** for real-time streaming:

- **Typing Indicator**: Shows when the AI is processing
- **Content Streaming**: Responses appear word-by-word in real-time
- **Event Types**: 
  - `typing`: AI is thinking
  - `start`: Response generation begins
  - `content`: Streaming text content
  - `end`: Response complete
  - `error`: Error occurred

### Frontend Streaming

The React frontend handles streaming with:

- **Real-time Updates**: Messages update as content streams in
- **Typing Animation**: Animated dots show when AI is thinking
- **Streaming Cursor**: Blinking cursor during text generation
- **Smooth Scrolling**: Auto-scrolls to follow new content

## Groq Integration

### Why Groq?

- **🚀 Ultra-fast inference**: Responses in milliseconds
- **💰 Cost-effective**: Competitive pricing for high-performance models
- **🔒 Privacy-focused**: Enterprise-grade security
- **📈 Scalable**: Handles high-volume requests efficiently

### Model Used

The chatbot uses **`llama3-8b-8192`**, a fast and efficient model that provides:
- Quick response generation
- Good context understanding
- Cost-effective token usage
- Reliable streaming support

## API Endpoints

### Backend (Flask)

- `POST /api/chat` - Send a chat message and get AI response (supports streaming)
- `POST /api/search` - Search documents directly
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

### Test Streaming Functionality

```bash
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

### Logs

Check the Flask console output for backend errors and the browser console for frontend issues.

## Development

### Project Structure

```
docMgr-llm/
├── app.py                 # Flask backend with Groq streaming support
├── requirements.txt       # Python dependencies (includes groq)
├── env_example.txt       # Environment variables template
├── start_backend.sh      # Backend startup script
├── start_frontend.sh     # Frontend startup script
├── test_backend.py       # Backend testing script
├── test_streaming.py     # Streaming functionality tests
├── frontend/             # React application
│   ├── package.json      # Node.js dependencies
│   ├── src/              # React components with streaming
│   └── tailwind.config.js # CSS configuration
└── README.md             # This file
```

### Adding New Features

1. **Backend**: Add new routes in `app.py`
2. **Frontend**: Create new components in `frontend/src/`
3. **Styling**: Use Tailwind CSS classes or extend the configuration
4. **Streaming**: Extend the SSE event types for new functionality
5. **Groq Models**: Switch between different Groq models as needed

## Performance

### Streaming Benefits

- **Faster Perceived Response**: Users see content immediately
- **Better UX**: Typing indicators and real-time updates
- **Reduced Latency**: No waiting for complete response
- **Interactive Feel**: More engaging chat experience

### Groq Advantages

- **Ultra-fast Inference**: Responses in milliseconds
- **Efficient Streaming**: Smooth real-time text generation
- **Cost Optimization**: Better token-to-cost ratio
- **Reliability**: Enterprise-grade infrastructure

### Optimization Tips

- Use appropriate chunk sizes for streaming
- Implement proper error handling for network issues
- Consider implementing retry logic for failed streams
- Monitor memory usage during long conversations
- Leverage Groq's fast models for better user experience

## License

This project is part of the DocMgr ecosystem and follows the same licensing terms.