import os
import tempfile
import uuid
from typing import List, Dict, Any
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb

class VectorQAService:
    def __init__(self, persist_directory: str = "vectorstores"):
        self.persist_directory = persist_directory
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize Gemini API
        genai.configure(api_key="AIzaSyB5fI8Lzr8ROr0H3ZotRZ9dtLXQJODn1SY")
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Store active sessions
        self.active_sessions = {}
        
    def process_pdf(self, pdf_file_path: str, session_id: str = None) -> str:
        """Process a PDF file and create vector embeddings"""
        if session_id is None:
            session_id = str(uuid.uuid4())
            
        # Create session-specific persist directory
        session_persist_dir = os.path.join(self.persist_directory, session_id)
        os.makedirs(session_persist_dir, exist_ok=True)
        
        try:
            # Load PDF
            loader = PyPDFLoader(pdf_file_path)
            pages = loader.load()
            
            # Split into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_documents(pages)
            
            # Create vector store
            vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=session_persist_dir
            )
            vectordb.persist()
            
            # Store session info
            self.active_sessions[session_id] = {
                'vectordb_path': session_persist_dir,
                'chunk_count': len(chunks),
                'file_name': os.path.basename(pdf_file_path)
            }
            
            print(f"Processed PDF: {len(chunks)} chunks created for session {session_id}")
            return session_id
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            raise e
    
    def ask_question(self, session_id: str, question: str) -> Dict[str, Any]:
        """Ask a question about a processed PDF"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session_info = self.active_sessions[session_id]
        vectordb_path = session_info['vectordb_path']
        
        try:
            # Load the vector store
            vectordb = Chroma(
                persist_directory=vectordb_path,
                embedding_function=self.embeddings
            )
            
            # Search for relevant chunks
            docs = vectordb.similarity_search(question, k=3)
            
            # Prepare context from relevant chunks
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt for Gemini
            prompt = f"""
            Based on the following document content, please answer the question.
            
            Document Content:
            {context}
            
            Question: {question}
            
            Please provide a clear and accurate answer based only on the information provided in the document content. If the information is not available in the document, please state that clearly.
            """
            
            # Get response from Gemini
            response = self.gemini_model.generate_content(prompt)
            
            return {
                'answer': response.text,
                'sources': [doc.metadata for doc in docs],
                'session_id': session_id,
                'question': question
            }
            
        except Exception as e:
            print(f"Error asking question: {e}")
            raise e
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
            
        return self.active_sessions[session_id]
    
    def cleanup_session(self, session_id: str):
        """Clean up a session and its vector store"""
        if session_id in self.active_sessions:
            session_info = self.active_sessions[session_id]
            vectordb_path = session_info['vectordb_path']
            
            # Remove vector store directory
            if os.path.exists(vectordb_path):
                import shutil
                shutil.rmtree(vectordb_path)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            print(f"Cleaned up session {session_id}")

# Global instance
qa_service = VectorQAService() 