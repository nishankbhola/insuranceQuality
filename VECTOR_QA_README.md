# AI Document Assistant - Vector-Based QA System

This feature allows users to upload PDF documents and ask questions about their content using vector embeddings and the Gemini AI API.

## Features

- **PDF Processing**: Upload and process PDF documents with vector embeddings
- **Intelligent QA**: Ask natural language questions about document content
- **Vector Search**: Uses ChromaDB for efficient document retrieval
- **AI-Powered Answers**: Leverages Google Gemini API for intelligent responses
- **Session Management**: Maintains document context across multiple questions
- **Modern UI**: Drag & drop interface with real-time feedback

## Architecture

### Backend Components

1. **VectorQAService** (`backend/vector_qa_service.py`):
   - PDF processing with LangChain
   - Vector embeddings using SentenceTransformers
   - ChromaDB for vector storage
   - Gemini API integration for question answering

2. **API Endpoints**:
   - `POST /upload-pdf-for-qa`: Upload and process PDF
   - `POST /ask-question`: Ask questions about processed documents
   - `GET /session-info/<session_id>`: Get session information
   - `DELETE /cleanup-session/<session_id>`: Clean up sessions

### Frontend Components

1. **VectorQA Component** (`frontend/src/components/VectorQA.js`):
   - PDF upload interface
   - Question input and answer display
   - Session management
   - Error handling and loading states

## Installation

### Backend Dependencies

1. **Install Python dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Required packages**:
   - `chromadb>=0.4.0`: Vector database
   - `sentence-transformers>=2.2.0`: Text embeddings
   - `google-generativeai>=0.3.0`: Gemini API
   - `langchain>=0.1.0`: Document processing
   - `pypdf>=3.15.0`: PDF parsing

### Frontend Dependencies

The frontend dependencies are already included in the existing setup. No additional installation is required.

## Usage

### Starting the Application

1. **Start the backend server**:
   ```bash
   cd backend
   python app.py
   ```

2. **Start the frontend development server**:
   ```bash
   cd frontend
   npm start
   ```

3. **Access the application**:
   - Open your browser to `http://localhost:3000`
   - Click on the "AI Document Assistant" tab in the navigation

### Using the AI Document Assistant

1. **Upload a PDF**:
   - Drag and drop a PDF file or click "Choose PDF"
   - Click "Process Document" to create vector embeddings
   - Wait for processing to complete

2. **Ask Questions**:
   - Type your question in the input field
   - Click "Ask" or press Enter
   - View the AI-generated answer with source information

3. **Example Questions**:
   - "What are the main topics discussed in this document?"
   - "What are the key findings or conclusions?"
   - "What are the main recommendations?"
   - "What is the purpose of this document?"

## Technical Details

### Vector Processing Pipeline

1. **PDF Loading**: Uses LangChain's PyPDFLoader to extract text
2. **Text Splitting**: RecursiveCharacterTextSplitter with 1000-character chunks and 200-character overlap
3. **Embedding Generation**: SentenceTransformer model "all-MiniLM-L6-v2"
4. **Vector Storage**: ChromaDB with persistent storage per session
5. **Similarity Search**: Retrieves top 3 most relevant chunks for each question
6. **AI Response**: Gemini API generates answers based on retrieved context

### Session Management

- Each uploaded PDF creates a unique session
- Vector embeddings are stored in session-specific directories
- Sessions can be cleaned up to free storage space
- Multiple questions can be asked about the same document

### API Integration

- **Gemini API Key**: Configured in the VectorQAService
- **Model**: Uses `gemini-pro` for text generation
- **Context Window**: Provides relevant document chunks as context
- **Response Format**: Structured JSON with answer and metadata

## Performance Considerations

### Processing Time
- **First Run**: Downloads embedding model (~100MB)
- **PDF Processing**: Depends on document size and complexity
- **Question Answering**: Typically 1-3 seconds per question

### Storage
- Vector embeddings are stored per session
- Each chunk requires ~384-dimensional vector storage
- Sessions are cleaned up when no longer needed

### Memory Usage
- Embedding model loaded in memory
- Active sessions maintain vector store connections
- ChromaDB handles memory management efficiently

## Error Handling

### Common Issues

1. **PDF Processing Errors**:
   - Invalid PDF format
   - Corrupted files
   - Password-protected documents

2. **API Errors**:
   - Gemini API rate limits
   - Network connectivity issues
   - Invalid API responses

3. **Vector Store Errors**:
   - Storage space issues
   - Permission problems
   - Corrupted embeddings

### Error Recovery

- Automatic retry mechanisms for API calls
- Graceful degradation for processing errors
- Clear error messages for user feedback
- Session cleanup on errors

## Security Considerations

- PDF files are stored temporarily
- Vector embeddings are session-specific
- API keys are configured server-side
- No sensitive data is logged

## Future Enhancements

- **Multi-document Support**: Process multiple PDFs in one session
- **Document Comparison**: Compare content across multiple documents
- **Export Functionality**: Save Q&A sessions as reports
- **Advanced Search**: Semantic search across document collections
- **Custom Embeddings**: Support for domain-specific models
- **Batch Processing**: Process multiple documents simultaneously

## Troubleshooting

### Installation Issues

1. **Missing Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **ChromaDB Issues**:
   ```bash
   pip install chromadb --upgrade
   ```

3. **Sentence Transformers**:
   ```bash
   pip install sentence-transformers --upgrade
   ```

### Runtime Issues

1. **Memory Errors**: Reduce chunk size in VectorQAService
2. **API Rate Limits**: Implement request throttling
3. **Storage Issues**: Clean up old sessions regularly

### Performance Optimization

1. **Faster Processing**: Use GPU for embeddings if available
2. **Reduced Memory**: Adjust chunk size and overlap
3. **Better Search**: Tune similarity search parameters 