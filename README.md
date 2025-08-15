# DocMgr Chatbot

A modern, intelligent chatbot interface that allows users to interact with documents stored in the DocMgr system. Built with React, Flask, and Groq's high-performance LLMs, featuring real-time streaming, typing indicators, and advanced function calling capabilities.

## 🚀 Features

- **🤖 AI-Powered Chat**: Ask questions about your documents and get intelligent responses
- **⚡ Real-time Streaming**: Watch responses appear word-by-word in real-time
- **⌨️ Typing Indicators**: See when the AI is thinking and processing
- **🔧 Function Calling**: AI can access all DocMgr APIs to gather comprehensive information
- **🔍 Semantic Search**: Intelligent document search with relevance scoring
- **📁 Document Management**: Browse, upload, and delete documents directly from the interface
- **📤 File Upload**: Drag-and-drop file upload with progress tracking
- **🗑️ Document Deletion**: Remove documents with modern confirmation dialogs
- **📥 Document Download**: Download original files from the system
- **👁️ Chunk Viewer**: View document chunks and embeddings in new tabs
- **🔔 Toast Notifications**: User-friendly success/error feedback
- **✅ Confirmation Dialogs**: Safe deletion with clear warnings
- **📱 Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **🔄 Interactive Chat**: Real-time chat interface with message history
- **📊 Context Awareness**: Bot responses include source document information
- **🎯 Function Call Indicators**: Visual feedback when AI is gathering data
- **🚀 Fast Inference**: Powered by Groq's high-performance LLM infrastructure

## 🏗️ Architecture

```
docMgr-llm/
├── app.py                    # Flask backend with function calling
├── frontend/                 # React frontend application
│   ├── src/                  # React source code
│   ├── public/               # Static assets
│   └── package.json          # Node.js dependencies
├── requirements.txt           # Python dependencies
├── start_backend.sh          # Backend startup script
├── start_frontend.sh         # Frontend startup script
└── test_*.py                 # Test scripts
```

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **DocMgr project** running on localhost:8000
- **Groq API key** (get one at [console.groq.com](https://console.groq.com))

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd docMgr-llm
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env with your settings
DOCMGR_BASE_URL=http://localhost:8000
GROQ_API_KEY=your_groq_api_key_here
FLASK_ENV=development
FLASK_DEBUG=1
```

### 3. Frontend Setup

#### Navigate to Frontend Directory
```bash
cd frontend
```

#### Install Node.js Dependencies
```bash
npm install
```

#### Install Tailwind CSS Dependencies
```bash
npm install -D tailwindcss@^3.4.0 autoprefixer@^10.4.16 postcss@^8.4.32
```

## 🚀 Quick Start

### 1. Start the Backend

```bash
# Activate virtual environment
source venv/bin/activate

# Start Flask server
python app.py
```

The backend will run on `http://localhost:5001`

### 2. Start the Frontend

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Start React development server
npm start
```

The frontend will run on `http://localhost:3000`

### 3. Alternative: Use Startup Scripts

```bash
# Make scripts executable
chmod +x start_backend.sh start_frontend.sh

# Start backend
./start_backend.sh

# Start frontend (in new terminal)
./start_frontend.sh
```

## 📚 Sample Data & Testing

### 1. Prerequisites
Ensure the DocMgr backend is running with some sample documents:
```bash
# In docMgr directory
cd ../docMgr
source .venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 2. Upload Sample Documents
Use the DocMgr API to upload some test documents:
```bash
# Upload a sample PDF
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_document.pdf" \
  -F "description=Sample document for testing"

# Upload sample text
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@AI_Text.txt" \
  -F "description=AI concepts and definitions"
```

### 3. Use the Document Management Interface
The chatbot now includes a comprehensive document management tab:
- **Browse Documents**: View all uploaded documents with metadata
- **Upload Files**: Drag-and-drop file upload with progress tracking
- **Delete Documents**: Remove documents with confirmation dialogs
- **Download Files**: Download original documents from the system
- **View Chunks**: Open document chunks in new browser tabs

### 3. Test the Chatbot
```bash
# Test backend functionality
python test_backend.py

# Test streaming chat
python test_streaming.py

# Test function calling
python test_function_calling.py
```

### 4. Sample Chat Interactions

#### Basic Questions
- "What documents do you have?"
- "Tell me about artificial intelligence"
- "What's the largest bill amount?"

#### Function Calling Examples
- "Get all documents and analyze their content"
- "Search for documents about machine learning"
- "Show me statistics about the document collection"

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DOCMGR_BASE_URL` | DocMgr API base URL | `http://localhost:8000` |
| `GROQ_API_KEY` | Groq API key for LLM | Required |
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Flask debug mode | `1` |

### Backend Configuration
- **Port**: 5001 (configurable in `app.py`)
- **CORS**: Enabled for frontend communication
- **Streaming**: Server-Sent Events (SSE) for real-time responses
- **Function Calling**: Full access to DocMgr APIs

### Frontend Configuration
- **Port**: 3000 (configurable in `package.json`)
- **Proxy**: Backend API calls proxied to localhost:5001
- **Tailwind CSS**: Configured for responsive design
- **Real-time Updates**: SSE integration for streaming responses

## 📖 API Reference

### Backend Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Chat with documents (streaming) |
| `POST` | `/api/search` | Direct document search |
| `GET` | `/api/functions` | Available function definitions |
| `GET` | `/api/health` | Backend health check |

### Chat Parameters
- `message`: User's question (required)
- `stream`: Enable streaming (default: false)

### Function Calling
The chatbot has access to all DocMgr functions:
- `get_all_documents()`: List all documents
- `get_document_by_id(id)`: Get specific document
- `get_document_chunks(id)`: Get document content chunks
- `search_documents(query)`: Semantic search
- `get_vector_stats()`: System statistics
- `get_api_info()`: API information

## 🧪 Testing

### Run All Tests
```bash
# Test backend functionality
python test_backend.py

# Test streaming capabilities
python test_streaming.py

# Test function calling
python test_function_calling.py
```

### Test Coverage
- ✅ Backend API endpoints
- ✅ Streaming chat functionality
- ✅ Function calling capabilities
- ✅ Frontend-backend communication
- ✅ Error handling and fallbacks

### Manual Testing
1. **Start both services** (backend + frontend)
2. **Open browser** to `http://localhost:3000`
3. **Ask questions** about your documents
4. **Watch real-time responses** with typing indicators
5. **Observe function calls** when AI gathers information

### Document Management Testing
1. **Switch to Documents tab**: Click the "Documents" tab
2. **Upload a file**: Use the upload form to add a new document
3. **Browse documents**: View the list of uploaded documents
4. **Test actions**: Try downloading, viewing chunks, and deleting documents
5. **Test confirmations**: Delete operations show confirmation dialogs
6. **Check notifications**: Toast messages appear for success/error feedback
7. **Refresh list**: Use the refresh button to update the document list

## 🚨 Troubleshooting

### Common Issues

#### 1. Backend Connection Failed
```bash
# Check if DocMgr is running
curl http://localhost:8000/

# Verify environment variables
cat .env
```

#### 2. Frontend Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Reinstall Tailwind CSS
npm install -D tailwindcss@^3.4.0 autoprefixer@^10.4.16 postcss@^8.4.32
```

#### 3. Function Calling Issues
```bash
# Check Groq API key
echo $GROQ_API_KEY

# Test function calling
python test_function_calling.py
```

#### 4. Streaming Not Working
```bash
# Check browser console for errors
# Verify SSE endpoint is accessible
curl -N "http://localhost:5001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "stream": true}'
```

### Performance Tips
- Use modern browsers for best SSE support
- Monitor Groq API usage and rate limits
- Keep document collections manageable for faster responses
- Use SSD storage for better performance

## 🔄 Development

### Adding New Functions
1. **Define function** in `AVAILABLE_FUNCTIONS`
2. **Implement logic** in `execute_function_call()`
3. **Update tests** to cover new functionality
4. **Document** the new capability

### Frontend Customization
1. **Modify components** in `frontend/src/`
2. **Update styles** using Tailwind CSS classes
3. **Add new features** to the chat interface
4. **Test responsiveness** across different screen sizes

### Backend Extensions
1. **Add new endpoints** in `app.py`
2. **Extend function calling** capabilities
3. **Improve error handling** and logging
4. **Optimize performance** for large document collections

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests** for new functionality
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create a GitHub issue
- **Documentation**: Check the DocMgr API docs at `/docs`
- **Testing**: Use the provided test scripts to verify functionality
- **Community**: Join discussions in the repository

## 🔄 Updates & Maintenance

### Regular Maintenance
- Monitor Groq API usage and costs
- Update dependencies regularly
- Test with new document types
- Monitor performance metrics

### Version Updates
```bash
# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update Node.js dependencies
cd frontend
npm update

# Test functionality after updates
python test_backend.py
npm test
```

---

**Ready to chat with your documents?** Follow the setup instructions above and start exploring your document collection with AI-powered intelligence!