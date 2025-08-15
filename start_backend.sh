#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    pyenv shell docmgr-llm
    pip install -r requirements.txt --upgrade
else
    echo "Activating virtual environment..."
    pyenv shell docmgr-llm
    pip install -r requirements.txt --upgrade
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env_example.txt .env
    echo "Please edit .env file with your configuration before starting the server."
    echo "Required: DOCMGR_BASE_URL and GROQ_API_KEY"
    echo "Get your Groq API key at: https://console.groq.com"
    exit 1
fi

echo "Starting DocMgr Chatbot backend with Groq..."
echo "Server will run on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
