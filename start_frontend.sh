#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting DocMgr Chatbot Frontend${NC}"
echo "=================================="

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Frontend directory not found!${NC}"
    echo "Please run this script from the docMgr-llm root directory."
    exit 1
fi

# Navigate to frontend directory
cd frontend
echo -e "${GREEN}✅ Found frontend directory${NC}"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json not found in frontend directory${NC}"
    exit 1
fi

# Check if node_modules exists, install if not
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    if npm install; then
        echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# Always install/update Tailwind CSS dependencies
echo -e "${YELLOW}🎨 Installing/Updating Tailwind CSS dependencies...${NC}"
if npm install -D tailwindcss@^3.4.0 autoprefixer@^10.4.16 postcss@^8.4.32; then
    echo -e "${GREEN}✅ Tailwind CSS dependencies updated${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Failed to install Tailwind CSS dependencies${NC}"
    echo "The app will still work but may not look as intended."
fi

# Check if backend is running (note the port change to 5001)
echo -e "${YELLOW}🔍 Checking if backend is running...${NC}"
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running on http://localhost:5001${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Backend doesn't seem to be running on http://localhost:5001${NC}"
    echo "Make sure to start the backend first with: ./start_backend.sh"
    echo ""
fi

echo ""
echo -e "${BLUE}🌐 Starting React development server...${NC}"
echo "Frontend will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the React development server
npm start
