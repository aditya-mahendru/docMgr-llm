# DocMgr-llm Chatbot Setup Guide

This guide will walk you through setting up the DocMgr-llm chatbot system, which provides an intelligent AI interface for interacting with your DocMgr documents.

## 🎯 Quick Start (10 minutes)

If you want to get up and running quickly:

```bash
# 1. Ensure DocMgr is running first
cd docMgr
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 2. In a new terminal, setup chatbot
cd docMgr-llm
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Setup environment
cp env_example.txt .env
# Edit .env with your GROQ_API_KEY

# 4. Setup frontend
cd frontend
npm install
npm install -D tailwindcss@^3.4.0 autoprefixer@^10.4.16 postcss@^8.4.32

# 5. Start backend (in new terminal)
cd ../
source venv/bin/activate
python app.py

# 6. Start frontend (in new terminal)
cd frontend
npm start

# 7. Test the system
cd ../
python setup_sample_data.py
```

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **Memory**: At least 4GB RAM (8GB recommended)
- **Storage**: 1GB free space for dependencies

### Required Software
- **Python 3.8+**: [Download from python.org](https://www.python.org/downloads/)
- **Node.js 16+**: [Download from nodejs.org](https://nodejs.org/)
- **Git**: [Download from git-scm.com](https://git-scm.com/downloads)
- **DocMgr System**: Must be running on localhost:8000

### API Keys Required
- **Groq API Key**: For LLM-powered responses [Get one here](https://console.groq.com)

## 🛠️ Detailed Setup Instructions

### Step 1: DocMgr Prerequisites

**IMPORTANT**: The DocMgr system must be running before setting up the chatbot.

```bash
# 1. Navigate to DocMgr directory
cd docMgr

# 2. Start DocMgr (if not already running)
source .venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 3. Verify DocMgr is running
curl http://localhost:8000/
# Should return API information JSON
```

### Step 2: Chatbot Backend Setup

#### 2.1 Clone and Navigate
```bash
# Navigate to chatbot directory
cd docMgr-llm
```

#### 2.2 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 2.3 Install Python Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### 2.4 Environment Configuration
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```env
# DocMgr API base URL
DOCMGR_BASE_URL=http://localhost:8000

# Groq API key for LLM responses
GROQ_API_KEY=your_groq_api_key_here

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=1
```

**Getting a Groq API Key:**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### Step 3: Frontend Setup

#### 3.1 Navigate to Frontend Directory
```bash
cd frontend
```

#### 3.2 Install Node.js Dependencies
```bash
# Install base dependencies
npm install

# Install Tailwind CSS dependencies
npm install -D tailwindcss@^3.4.0 autoprefixer@^10.4.16 postcss@^8.4.32
```

#### 3.3 Verify Frontend Configuration
```bash
# Check package.json proxy setting
cat package.json | grep proxy
# Should show: "proxy": "http://localhost:5001"
```

### Step 4: System Startup

#### 4.1 Start Backend Server
```bash
# In a new terminal, navigate to chatbot directory
cd docMgr-llm

# Activate virtual environment
source venv/bin/activate

# Start Flask server
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5001
```

#### 4.2 Start Frontend Development Server
```bash
# In another new terminal, navigate to frontend directory
cd docMgr-llm/frontend

# Start React development server
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view docmgr-llm in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

### Step 5: System Testing

#### 5.1 Run Comprehensive Tests
```bash
# In a new terminal, with virtual environment activated
cd docMgr-llm
source venv/bin/activate

# Run the comprehensive test suite
python setup_sample_data.py
```

This script will test:
- ✅ DocMgr connectivity
- ✅ Chatbot backend availability
- ✅ Function calling capabilities
- ✅ Streaming chat functionality
- ✅ Search functionality
- ✅ API integration

#### 5.2 Manual Testing
```bash
# Test backend health
curl http://localhost:5001/api/health

# Test function definitions
curl http://localhost:5001/api/functions

# Test basic chat
curl -X POST "http://localhost:5001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What documents do you have?", "stream": false}'
```

### Step 6: Frontend Verification

#### 6.1 Open Browser
Navigate to `http://localhost:3000` in your web browser.

#### 6.2 Test Chat Interface
1. **Type a question**: "What documents do you have?"
2. **Watch for**: Typing indicators, streaming responses, function call indicators
3. **Verify**: Responses include document information and context

#### 6.3 Test Function Calling
Ask questions that should trigger function calls:
- "Get all documents and count them"
- "Show me statistics about the system"
- "Search for documents about machine learning"

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend Connection Failed
```bash
# Check if DocMgr is running
curl http://localhost:8000/

# Check environment variables
cat .env

# Verify DocMgr URL in .env
echo $DOCMGR_BASE_URL
```

#### 2. Frontend Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Reinstall Tailwind CSS
npm install -D tailwindcss@^3.4.0 autoprefixer@^10.4.16 postcss@^8.4.32

# Check Node.js version
node --version  # Should be 16+
```

#### 3. Function Calling Issues
```bash
# Check Groq API key
echo $GROQ_API_KEY

# Test function calling
python test_function_calling.py

# Check backend logs for errors
```

#### 4. Streaming Not Working
```bash
# Check browser console for errors
# Verify SSE endpoint is accessible
curl -N "http://localhost:5001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "stream": true}'
```

#### 5. Port Conflicts
```bash
# Check what's using port 5001
lsof -ti:5001

# Check what's using port 3000
lsof -ti:3000

# Kill conflicting processes
kill -9 <PID>
```

### Performance Issues

#### 1. Slow Responses
- Check Groq API rate limits
- Monitor network connectivity
- Verify document collection size

#### 2. Memory Issues
- Monitor Python process memory usage
- Check for memory leaks in long conversations
- Limit concurrent requests

## 📊 System Verification

### Health Check Endpoints
```bash
# Backend health
curl http://localhost:5001/api/health

# Function definitions
curl http://localhost:5001/api/functions

# DocMgr connectivity
curl http://localhost:5001/api/health | jq '.docmgr_url'
```

### Expected Outputs
- **Backend Health**: Status and DocMgr URL
- **Functions**: List of available function definitions
- **Connectivity**: Successful connection to DocMgr

## 🚀 Advanced Configuration

### Customizing Function Calling
Edit `app.py` to add new functions:

```python
# Add to AVAILABLE_FUNCTIONS
"custom_function": {
    "name": "custom_function",
    "description": "Description of your custom function",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

# Add to execute_function_call function
elif function_name == "custom_function":
    return your_custom_function()
```

### Frontend Customization
- **Styling**: Modify `frontend/src/index.css` and Tailwind classes
- **Components**: Edit React components in `frontend/src/`
- **Configuration**: Update `frontend/tailwind.config.js`

### Backend Extensions
- **New Endpoints**: Add routes in `app.py`
- **Enhanced Function Calling**: Extend `AVAILABLE_FUNCTIONS`
- **Custom Models**: Integrate different LLM providers

## 📚 Usage Examples

### Basic Chat
```
User: "Hello! What can you help me with?"
Bot: "I can help you explore and analyze your documents..."
```

### Function Calling
```
User: "How many documents do I have?"
Bot: "Let me check your document collection... [Function Call] You have 5 documents..."
```

### Document Analysis
```
User: "What's the main topic of my documents?"
Bot: "Let me analyze your documents... [Function Call] Based on the content..."
```

## 🆘 Getting Help

### Debugging Steps
1. **Check logs**: Backend terminal and browser console
2. **Verify services**: Ensure both DocMgr and chatbot are running
3. **Test connectivity**: Use curl commands to test endpoints
4. **Check configuration**: Verify environment variables and API keys

### Common Solutions
- **Restart services**: Stop and restart both backend and frontend
- **Clear caches**: Remove `node_modules` and reinstall
- **Check versions**: Ensure Python 3.8+ and Node.js 16+
- **Verify ports**: Ensure ports 8000, 5001, and 3000 are available

### Support Resources
- **Documentation**: Check the README files
- **Test Scripts**: Use provided test scripts to isolate issues
- **API Docs**: Visit DocMgr docs at `http://localhost:8000/docs`
- **Issues**: Create GitHub issues with detailed error messages

## 🔄 Maintenance

### Regular Tasks
- **Update dependencies**: Keep Python and Node.js packages current
- **Monitor API usage**: Track Groq API usage and costs
- **Backup data**: Regular backups of DocMgr database and documents
- **Performance monitoring**: Monitor response times and resource usage

### Updates
```bash
# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update Node.js dependencies
cd frontend
npm update

# Test after updates
python setup_sample_data.py
```

---

**Ready to chat with your documents? 🎉**

Follow this guide step by step, and you'll have a fully functional AI-powered chatbot interface for your DocMgr system!
