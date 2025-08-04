import React, { useState, useRef } from 'react';
import { Upload, Search, FileText, MessageSquare, Loader2, Trash2, Brain } from 'lucide-react';

function VectorQA() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [sessionInfo, setSessionInfo] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setAnswer(null);
      setError(null);
      setSessionId(null);
      setSessionInfo(null);
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file first');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:8000/upload-pdf-for-qa', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setSessionId(data.session_id);
        setSessionInfo({
          file_name: data.file_name,
          chunk_count: data.chunk_count
        });
        setError(null);
      } else {
        setError(data.error || 'Failed to process PDF');
      }
    } catch (err) {
      setError('Error uploading file: ' + err.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    if (!sessionId || !question.trim()) {
      setError('Please upload a PDF and enter a question');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/ask-question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          question: question.trim()
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setAnswer(data);
      } else {
        setError(data.error || 'Failed to get answer');
      }
    } catch (err) {
      setError('Error processing request: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setAnswer(null);
      setError(null);
      setSessionId(null);
      setSessionInfo(null);
    } else {
      setError('Please drop a valid PDF file');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const clearSession = async () => {
    if (sessionId) {
      try {
        await fetch(`http://localhost:8000/cleanup-session/${sessionId}`, {
          method: 'DELETE',
        });
      } catch (err) {
        console.error('Error cleaning up session:', err);
      }
    }
    
    setSelectedFile(null);
    setQuestion('');
    setAnswer(null);
    setError(null);
    setSessionId(null);
    setSessionInfo(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center mb-6">
          <Brain className="w-8 h-8 text-primary-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">AI Document Assistant</h2>
        </div>
        
        <p className="text-gray-600 mb-6">
          Upload a PDF document and ask questions about its content. The AI will analyze the document using vector embeddings and provide intelligent answers.
        </p>

        {/* File Upload Section */}
        <div className="mb-6">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              selectedFile 
                ? 'border-primary-300 bg-primary-50' 
                : 'border-gray-300 hover:border-primary-400'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            {!selectedFile ? (
              <div>
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Upload a PDF document
                </p>
                <p className="text-gray-500 mb-4">
                  Drag and drop a PDF file here, or click to browse
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Choose PDF
                </button>
              </div>
            ) : (
              <div>
                <FileText className="w-12 h-12 text-primary-600 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {selectedFile.name}
                </p>
                <p className="text-gray-500 mb-4">
                  PDF selected successfully
                </p>
                {!sessionId ? (
                  <button
                    onClick={handleFileUpload}
                    disabled={processing}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 transition-colors flex items-center mx-auto"
                  >
                    {processing ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <Brain className="w-4 h-4 mr-2" />
                    )}
                    {processing ? 'Processing...' : 'Process Document'}
                  </button>
                ) : (
                  <div className="flex gap-2 justify-center">
                    <button
                      onClick={clearSession}
                      className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Clear
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Session Info */}
        {sessionInfo && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">Document Processed Successfully</h3>
                <p className="text-gray-600">File: {sessionInfo.file_name}</p>
                <p className="text-gray-600">Chunks created: {sessionInfo.chunk_count}</p>
              </div>
              <div className="text-green-600">
                <Brain className="w-8 h-8" />
              </div>
            </div>
          </div>
        )}

        {/* Question Input */}
        {sessionId && (
          <form onSubmit={handleQuestionSubmit} className="mb-6">
            <div className="mb-4">
              <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
                Ask a question about the document
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  id="question"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g., What are the main topics discussed? What are the key findings?"
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={!question.trim() || loading}
                  className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Search className="w-5 h-5" />
                  )}
                  <span className="ml-2">Ask</span>
                </button>
              </div>
            </div>
          </form>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Answer Display */}
        {answer && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Answer</h3>
            <div className="bg-white rounded-lg p-4 border">
              <p className="text-gray-900 mb-4 whitespace-pre-wrap">{answer.answer}</p>
              <div className="border-t pt-3">
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Question:</strong> {answer.question}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Sources:</strong> {answer.sources.length} document chunks referenced
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Example Questions */}
        {sessionId && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Example Questions</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {[
                "What are the main topics discussed in this document?",
                "What are the key findings or conclusions?",
                "What are the main recommendations?",
                "What is the purpose of this document?",
                "What are the important dates mentioned?",
                "What are the main requirements or criteria?"
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setQuestion(example)}
                  className="text-left p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-sm text-gray-700"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default VectorQA; 