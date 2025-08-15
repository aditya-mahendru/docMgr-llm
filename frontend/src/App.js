import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, FileText, Search, MessageCircle, Database, Info, Upload, Trash2, Eye, Download, Plus, AlertTriangle } from 'lucide-react';

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
    const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'search', 'documents'
    const [documents, setDocuments] = useState([]);
    const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
    const [uploadFile, setUploadFile] = useState(null);
    const [uploadDescription, setUploadDescription] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [documentToDelete, setDocumentToDelete] = useState(null);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');
    const [toastType, setToastType] = useState('success'); // 'success' or 'error'
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

    // Load documents when documents tab is active
    useEffect(() => {
        if (activeTab === 'documents') {
            loadDocuments();
        }
    }, [activeTab]);

    const loadDocuments = async () => {
        setIsLoadingDocuments(true);
        try {
            const response = await axios.get('http://localhost:8000/api/documents');
            setDocuments(response.data);
        } catch (error) {
            console.error('Failed to load documents:', error);
        } finally {
            setIsLoadingDocuments(false);
        }
    };

    const handleFileUpload = async () => {
        if (!uploadFile) return;

        setIsUploading(true);
        setUploadProgress(0);

        const formData = new FormData();
        formData.append('file', uploadFile);
        formData.append('description', uploadDescription);

        try {
            const response = await axios.post('http://localhost:8000/api/documents/upload', formData, {
                onUploadProgress: (progressEvent) => {
                    const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setUploadProgress(progress);
                }
            });

            // Refresh documents list
            await loadDocuments();

            // Reset form
            setUploadFile(null);
            setUploadDescription('');
            setUploadProgress(0);

            showToastNotification('Document uploaded successfully!', 'success');
        } catch (error) {
            console.error('Upload failed:', error);
            showToastNotification('Upload failed: ' + (error.response?.data?.detail || error.message), 'error');
        } finally {
            setIsUploading(false);
        }
    };

    const handleDeleteDocument = async (documentId) => {
        try {
            await axios.delete(`http://localhost:8000/api/documents/${documentId}`);
            await loadDocuments();
            showToastNotification('Document deleted successfully!', 'success');
        } catch (error) {
            console.error('Delete failed:', error);
            showToastNotification('Delete failed: ' + (error.response?.data?.detail || error.message), 'error');
        }
    };

    const confirmDelete = (document) => {
        setDocumentToDelete(document);
        setShowDeleteConfirm(true);
    };

    const cancelDelete = () => {
        setShowDeleteConfirm(false);
        setDocumentToDelete(null);
    };

    const showToastNotification = (message, type = 'success') => {
        setToastMessage(message);
        setToastType(type);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
    };

    const handleDownloadDocument = async (document) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/documents/${document.id}`, {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', document.original_filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed:', error);
            showToastNotification('Download failed: ' + error.message, 'error');
        }
    };

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
                                            ? { ...msg, text: msg.text + '\n\n🔧 ' + data.content }
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
                                            ? { ...msg, text: msg.text + '\n\n❌ Error: ' + data.content, isStreaming: false }
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
            console.error('Error:', error);
            setMessages(prev => [...prev, {
                id: Date.now() + 2,
                text: 'Sorry, I encountered an error while processing your request.',
                sender: 'bot',
                timestamp: new Date().toLocaleTimeString()
            }]);
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
                n_results: 10
            });
            setSearchResults(response.data.results);
        } catch (error) {
            console.error('Search failed:', error);
            setSearchResults([]);
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString();
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'chat':
                return (
                    <div className="flex-1 flex flex-col">
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {messages.map((message) => (
                                <div
                                    key={message.id}
                                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] rounded-lg px-4 py-2 ${message.sender === 'user'
                                            ? 'bg-primary-500 text-white'
                                            : 'bg-gray-100 text-gray-800'
                                            }`}
                                    >
                                        <div className="whitespace-pre-wrap">{message.text}</div>
                                        {message.isStreaming && (
                                            <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse"></span>
                                        )}
                                        <div className="text-xs opacity-70 mt-1">{message.timestamp}</div>
                                    </div>
                                </div>
                            ))}
                            {isTyping && (
                                <div className="flex justify-start">
                                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                                        <div className="flex space-x-1">
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                        <div className="border-t p-4">
                            <div className="flex space-x-2">
                                <input
                                    type="text"
                                    value={inputMessage}
                                    onChange={(e) => setInputMessage(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                    placeholder="Ask me about your documents..."
                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    disabled={isLoading}
                                />
                                <button
                                    onClick={handleSendMessage}
                                    disabled={isLoading || !inputMessage.trim()}
                                    className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                                >
                                    <Send size={16} />
                                    <span>Send</span>
                                </button>
                            </div>
                        </div>
                    </div>
                );

            case 'search':
                return (
                    <div className="flex-1 p-4">
                        <div className="mb-4">
                            <div className="flex space-x-2">
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                                    placeholder="Search your documents..."
                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                                <button
                                    onClick={handleSearch}
                                    className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 flex items-center space-x-2"
                                >
                                    <Search size={16} />
                                    <span>Search</span>
                                </button>
                            </div>
                        </div>
                        <div className="space-y-4">
                            {searchResults.map((result, index) => (
                                <div key={index} className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <h3 className="font-semibold text-gray-800">
                                            {result.metadata?.original_filename || 'Unknown Document'}
                                        </h3>
                                        <span className="text-sm text-gray-500">
                                            Score: {(result.score * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <p className="text-gray-600 text-sm">{result.content}</p>
                                </div>
                            ))}
                            {searchResults.length === 0 && searchQuery && (
                                <p className="text-gray-500 text-center py-8">No results found for "{searchQuery}"</p>
                            )}
                        </div>
                    </div>
                );

            case 'documents':
                return (
                    <div className="flex-1 p-4">
                        {/* Upload Section */}
                        <div className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
                            <h3 className="text-lg font-semibold mb-4 flex items-center">
                                <Upload size={20} className="mr-2" />
                                Upload New Document
                            </h3>
                            <div className="space-y-3">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        File
                                    </label>
                                    <input
                                        type="file"
                                        onChange={(e) => setUploadFile(e.target.files[0])}
                                        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                                        disabled={isUploading}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Description
                                    </label>
                                    <input
                                        type="text"
                                        value={uploadDescription}
                                        onChange={(e) => setUploadDescription(e.target.value)}
                                        placeholder="Enter document description..."
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                                        disabled={isUploading}
                                    />
                                </div>
                                {isUploading && (
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                                            style={{ width: `${uploadProgress}%` }}
                                        ></div>
                                    </div>
                                )}
                                <button
                                    onClick={handleFileUpload}
                                    disabled={!uploadFile || isUploading}
                                    className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                                >
                                    <Plus size={16} />
                                    <span>{isUploading ? 'Uploading...' : 'Upload Document'}</span>
                                </button>
                            </div>
                        </div>

                        {/* Documents List */}
                        <div>
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold flex items-center">
                                    <FileText size={20} className="mr-2" />
                                    Your Documents ({documents.length})
                                </h3>
                                <button
                                    onClick={loadDocuments}
                                    disabled={isLoadingDocuments}
                                    className="text-primary-500 hover:text-primary-600 disabled:opacity-50"
                                >
                                    Refresh
                                </button>
                            </div>

                            {isLoadingDocuments ? (
                                <div className="text-center py-8">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
                                    <p className="mt-2 text-gray-500">Loading documents...</p>
                                </div>
                            ) : documents.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    <FileText size={48} className="mx-auto mb-2 opacity-50" />
                                    <p>No documents uploaded yet.</p>
                                    <p className="text-sm">Upload your first document above!</p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {documents.map((doc) => (
                                        <div key={doc.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center space-x-3">
                                                        <FileText size={20} className="text-gray-400" />
                                                        <div>
                                                            <h4 className="font-medium text-gray-800">
                                                                {doc.original_filename}
                                                            </h4>
                                                            <p className="text-sm text-gray-500">
                                                                {doc.description || 'No description'}
                                                            </p>
                                                            <div className="flex items-center space-x-4 text-xs text-gray-400 mt-1">
                                                                <span>Size: {formatFileSize(doc.file_size)}</span>
                                                                <span>Type: {doc.content_type}</span>
                                                                <span>Uploaded: {formatDate(doc.upload_date)}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex items-center space-x-2">
                                                    <button
                                                        onClick={() => handleDownloadDocument(doc)}
                                                        className="p-2 text-gray-500 hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors"
                                                        title="Download"
                                                    >
                                                        <Download size={16} />
                                                    </button>
                                                    <button
                                                        onClick={() => window.open(`http://localhost:8000/api/documents/${doc.id}/chunks`, '_blank')}
                                                        className="p-2 text-gray-500 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                                                        title="View Chunks"
                                                    >
                                                        <Eye size={16} />
                                                    </button>
                                                    <button
                                                        onClick={() => confirmDelete(doc)}
                                                        className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                                        title="Delete"
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-6xl mx-auto bg-white shadow-lg min-h-screen">
                {/* Header */}
                <div className="bg-white border-b border-gray-200 px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <Database className="text-primary-500" size={24} />
                            <h1 className="text-xl font-bold text-gray-800">DocMgr Chatbot</h1>
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                                <Info size={16} />
                                <span>{availableFunctions.length} functions available</span>
                            </div>
                            {isFunctionCalling && (
                                <div className="flex items-center space-x-2 text-sm text-blue-600">
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                    <span>Function calling...</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Navigation Tabs */}
                <div className="border-b border-gray-200">
                    <nav className="flex space-x-8 px-6">
                        <button
                            onClick={() => setActiveTab('chat')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'chat'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            <div className="flex items-center space-x-2">
                                <MessageCircle size={16} />
                                <span>Chat</span>
                            </div>
                        </button>
                        <button
                            onClick={() => setActiveTab('search')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'search'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            <div className="flex items-center space-x-2">
                                <Search size={16} />
                                <span>Search</span>
                            </div>
                        </button>
                        <button
                            onClick={() => setActiveTab('documents')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'documents'
                                ? 'border-primary-500 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            <div className="flex items-center space-x-2">
                                <FileText size={16} />
                                <span>Documents</span>
                            </div>
                        </button>
                    </nav>
                </div>

                {/* Main Content */}
                <div className="flex-1">
                    {renderTabContent()}
                </div>
            </div>

            {/* Delete Confirmation Modal */}
            {showDeleteConfirm && documentToDelete && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <div className="flex items-center space-x-3 mb-4">
                            <AlertTriangle className="text-red-500" size={24} />
                            <h3 className="text-lg font-semibold text-gray-900">Delete Document</h3>
                        </div>
                        <p className="text-gray-600 mb-6">
                            Are you sure you want to delete <strong>"{documentToDelete.original_filename}"</strong>?
                            This action cannot be undone.
                        </p>
                        <div className="flex space-x-3 justify-end">
                            <button
                                onClick={cancelDelete}
                                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => {
                                    handleDeleteDocument(documentToDelete.id);
                                    cancelDelete();
                                }}
                                className="px-4 py-2 text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Toast Notification */}
            {showToast && (
                <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${toastType === 'success'
                    ? 'bg-green-500 text-white'
                    : 'bg-red-500 text-white'
                    }`}>
                    <div className="flex items-center space-x-2">
                        {toastType === 'success' ? (
                            <div className="w-4 h-4 bg-white rounded-full"></div>
                        ) : (
                            <AlertTriangle size={16} />
                        )}
                        <span className="font-medium">{toastMessage}</span>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
