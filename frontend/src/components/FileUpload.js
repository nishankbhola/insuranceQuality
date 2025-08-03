import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Upload, FileText, AlertCircle, CheckCircle, Bug } from 'lucide-react';

function FileUpload({ onValidationStart, onValidationComplete, onValidationError }) {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [debugData, setDebugData] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending'
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  });

  const handleUpload = async () => {
    if (uploadedFiles.length === 0) return;

    setUploading(true);
    onValidationStart();

    const formData = new FormData();
    uploadedFiles.forEach(({ file }) => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onValidationComplete(response.data);
      setUploadedFiles([]);
    } catch (error) {
      console.error('Upload error:', error);
      onValidationError(error.response?.data?.message || 'Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  const handleDebug = async () => {
    if (uploadedFiles.length === 0) return;

    setUploading(true);

    const formData = new FormData();
    uploadedFiles.forEach(({ file }) => {
      formData.append('files', file);
    });

    try {
      const response = await axios.post('/debug', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setDebugData(response.data);
      console.log('Debug data:', response.data);
    } catch (error) {
      console.error('Debug error:', error);
      onValidationError(error.response?.data?.message || 'Failed to debug files');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (id) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== id));
  };

  const getFileType = (filename) => {
    const upperName = filename.toUpperCase();
    if (upperName.includes('MVR')) return 'MVR Report';
    if (upperName.includes('DASH')) return 'DASH Report';
    if (upperName.includes('QUOTE')) return 'Insurance Quote';
    return 'Document';
  };

  const getFileIcon = (filename) => {
    const upperName = filename.toUpperCase();
    if (upperName.includes('MVR')) return '🚗';
    if (upperName.includes('DASH')) return '📊';
    if (upperName.includes('QUOTE')) return '📋';
    return '📄';
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Upload Documents</h2>
        <p className="text-gray-600">
          Upload MVR reports, DASH reports, and insurance quotes for validation. 
          Files should contain "MVR", "DASH", or "QUOTE" in their names.
        </p>
      </div>

      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        {isDragActive ? (
          <p className="text-lg text-primary-600">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-lg text-gray-600 mb-2">
              Drag & drop files here, or click to select files
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF files only
            </p>
          </div>
        )}
      </div>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-gray-900">Selected Files</h3>
          <div className="space-y-2">
            {uploadedFiles.map(({ id, file, status }) => (
              <div key={id} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getFileIcon(file.name)}</span>
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-500">{getFileType(file.name)}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(id)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <AlertCircle className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {uploadedFiles.length > 0 && (
        <div className="flex justify-center space-x-4">
          <button
            onClick={handleDebug}
            disabled={uploading}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              uploading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-yellow-600 text-white hover:bg-yellow-700'
            }`}
          >
            {uploading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Processing...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Bug className="w-5 h-5" />
                <span>Debug Extraction</span>
              </div>
            )}
          </button>
          
          <button
            onClick={handleUpload}
            disabled={uploading}
            className={`px-8 py-3 rounded-lg font-medium transition-colors ${
              uploading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {uploading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Processing...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5" />
                <span>Validate Documents</span>
              </div>
            )}
          </button>
        </div>
      )}

      {/* Debug Results */}
      {debugData && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-medium text-yellow-900 mb-2">Debug Results</h4>
          <pre className="text-sm text-yellow-800 overflow-auto max-h-96">
            {JSON.stringify(debugData, null, 2)}
          </pre>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">File Naming Requirements</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• MVR reports should contain "MVR" in the filename</li>
          <li>• DASH reports should contain "DASH" in the filename</li>
          <li>• Insurance quotes should contain "QUOTE" in the filename</li>
          <li>• Only PDF files are supported</li>
        </ul>
      </div>
    </div>
  );
}

export default FileUpload; 