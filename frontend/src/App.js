import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, FileText, Search, MessageCircle, Database, Info } from 'lucide-react';

function App() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [showSearch, setShowSearch] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [isFunctionCalling, setIsFunctionCalling] = useState(false);
    const [availableFunctions, setAvailableFunctions] = useState([]);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Load available functions on component mount
    useEffect(() => {
        const loadFunctions = async () => {
            try {
                const response = await axios.get('/api/functions');
                setAvailableFunctions(Object.keys(response.data.functions));
            } catch (error) {
                console.error('Failed to load available functions:', error);
            }
        };
        loadFunctions();
    }, []);

    const handleSendMessage = async () => {
        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
            id: Date.now(),
            text: inputMessage,
            sender: 'user',
            timestamp: new Date().toLocaleTimeString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);
        setIsTyping(false);
        setIsFunctionCalling(false);

        try {
            // Create a new message for the bot response
            const botMessageId = Date.now() + 1;
            const botMessage = {
                id: botMessageId,
                text: '',
                sender: 'bot',
                timestamp: new Date().toLocaleTimeString(),
                context: [],
                isStreaming: true
            };

            setMessages(prev => [...prev, botMessage]);

            // Use streaming API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: inputMessage,
                    stream: true
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));

                            switch (data.type) {
                                case 'typing':
                                    setIsTyping(true);
                                    break;

                                case 'start':
                                    setIsTyping(false);
                                    break;

                                case 'function_call':
                                    setIsFunctionCalling(true);
                                    setMessages(prev => prev.map(msg =>
                                        msg.id === botMessageId
                                            ? { ...msg, text: msg.text + '\n\n🔍 ' + data.content }
                                            : msg
                                    ));
                                    break;

                                case 'content':
                                    setIsFunctionCalling(false);
                                    setMessages(prev => prev.map(msg =>
                                        msg.id === botMessageId
                                            ? { ...msg, text: msg.text + data.content }
                                            : msg
                                    ));
                                    break;

                                case 'end':
                                    setMessages(prev => prev.map(msg =>
                                        msg.id === botMessageId
                                            ? { ...msg, isStreaming: false }
                                            : msg
                                    ));
                                    break;

                                case 'error':
                                    setMessages(prev => prev.map(msg =>
                                        msg.id === botMessageId
                                            ? {
                                                ...msg,
                                                text: data.content,
                                                isError: true,
                                                isStreaming: false
                                            }
                                            : msg
                                    ));
                                    break;
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                id: Date.now() + 1,
                text: 'Sorry, I encountered an error. Please try again.',
                sender: 'bot',
                timestamp: new Date().toLocaleTimeString(),
                isError: true,
                isStreaming: false
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            setIsTyping(false);
            setIsFunctionCalling(false);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;

        try {
            const response = await axios.post('/api/search', {
                query: searchQuery,
                n_results: 5
            });
            setSearchResults(response.data.results);
        } catch (error) {
            console.error('Error searching:', error);
            setSearchResults([]);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (showSearch) {
                handleSearch();
            } else {
                handleSendMessage();
            }
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center">
                            <MessageCircle className="h-8 w-8 text-primary-600 mr-3" />
                            <h1 className="text-xl font-semibold text-gray-900">DocMgr Chatbot</h1>
                        </div>
                        <div className="flex items-center space-x-2">
                            <button
                                onClick={() => setShowSearch(!showSearch)}
                                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${showSearch
                                    ? 'bg-primary-600 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                <Search className="h-4 w-4 inline mr-2" />
                                {showSearch ? 'Hide Search' : 'Show Search'}
                            </button>
                            <div className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                                <Database className="h-3 w-3 inline mr-1" />
                                {availableFunctions.length} Functions
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Search Panel */}
                    {showSearch && (
                        <div className="lg:col-span-1">
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Documents</h2>
                                <div className="space-y-4">
                                    <div>
                                        <input
                                            type="text"
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value)}
                                            onKeyPress={handleKeyPress}
                                            placeholder="Enter search query..."
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                        />
                                    </div>
                                    <button
                                        onClick={handleSearch}
                                        className="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
                                    >
                                        Search
                                    </button>

                                    {searchResults.length > 0 && (
                                        <div className="mt-4">
                                            <h3 className="text-sm font-medium text-gray-700 mb-2">Search Results:</h3>
                                            <div className="space-y-2">
                                                {searchResults.map((result, index) => (
                                                    <div key={index} className="p-3 bg-gray-50 rounded-md">
                                                        <div className="flex items-start">
                                                            <FileText className="h-4 w-4 text-gray-500 mt-1 mr-2 flex-shrink-0" />
                                                            <div className="flex-1 min-w-0">
                                                                <p className="text-sm font-medium text-gray-900">
                                                                    {result.metadata.original_filename}
                                                                </p>
                                                                <p className="text-xs text-gray-500 mt-1">
                                                                    Score: {result.similarity_score.toFixed(3)}
                                                                </p>
                                                                <p className="text-sm text-gray-700 mt-2 line-clamp-3">
                                                                    {result.content}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Chat Panel */}
                    <div className={`${showSearch ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
                        <div className="bg-white rounded-lg shadow h-[600px] flex flex-col">
                            {/* Messages */}
                            <div className="flex-1 overflow-y-auto p-6 space-y-4 chat-scroll">
                                {messages.length === 0 ? (
                                    <div className="text-center text-gray-500 mt-20">
                                        <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                                        <p className="text-lg">Start a conversation with your documents!</p>
                                        <p className="text-sm">Ask questions about the content you've uploaded.</p>
                                        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                                            <Info className="h-4 w-4 inline mr-2 text-blue-600" />
                                            <span className="text-sm text-blue-700">
                                                I can now access all your documents, search through them, and provide detailed information!
                                            </span>
                                        </div>
                                    </div>
                                ) : (
                                    messages.map((message) => (
                                        <div
                                            key={message.id}
                                            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                        >
                                            <div
                                                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${message.sender === 'user'
                                                    ? 'bg-primary-600 text-white'
                                                    : message.isError
                                                        ? 'bg-red-100 text-red-800'
                                                        : 'bg-gray-100 text-gray-800'
                                                    }`}
                                            >
                                                <p className="text-sm streaming-text whitespace-pre-wrap">
                                                    {message.text}
                                                    {message.isStreaming && (
                                                        <span className="streaming-cursor inline-block w-0.5 h-4 bg-gray-600 ml-1"></span>
                                                    )}
                                                </p>
                                                <p className="text-xs opacity-70 mt-1">{message.timestamp}</p>

                                                {message.context && message.context.length > 0 && (
                                                    <div className="mt-3 pt-3 border-t border-gray-200">
                                                        <p className="text-xs font-medium mb-2">Sources:</p>
                                                        {message.context.map((chunk, index) => (
                                                            <div key={index} className="text-xs opacity-70 mb-1">
                                                                <FileText className="h-3 w-3 inline mr-1" />
                                                                {chunk.metadata.original_filename}
                                                                <span className="ml-2">({chunk.similarity_score.toFixed(3)})</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))
                                )}

                                {/* Typing Indicator */}
                                {isTyping && (
                                    <div className="flex justify-start">
                                        <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                                            <div className="flex items-center space-x-2">
                                                <div className="flex space-x-1">
                                                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-bounce"></div>
                                                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-bounce" style={{ animationDelay: '0.1s' }}></div>
                                                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-bounce" style={{ animationDelay: '0.2s' }}></div>
                                                </div>
                                                <span className="text-sm text-gray-600">AI is typing...</span>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Function Calling Indicator */}
                                {isFunctionCalling && (
                                    <div className="flex justify-start">
                                        <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg">
                                            <div className="flex items-center space-x-2">
                                                <Database className="h-4 w-4 animate-pulse" />
                                                <span className="text-sm">Gathering information from documents...</span>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input */}
                            <div className="border-t p-4">
                                <div className="flex space-x-2">
                                    <input
                                        type="text"
                                        value={inputMessage}
                                        onChange={(e) => setInputMessage(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        placeholder="Ask about your documents, search for content, or get system info..."
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                        disabled={isLoading}
                                    />
                                    <button
                                        onClick={handleSendMessage}
                                        disabled={isLoading || !inputMessage.trim()}
                                        className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <Send className="h-4 w-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
