import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import SalesforceCard from './SalesforceCard';

const SalesforceFileUpload = ({ onFileUpload, onCompactValidation, isLoading }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadType, setUploadType] = useState('standard');

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending',
      progress: 0
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: true
  });

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const handleUpload = async () => {
    if (uploadedFiles.length === 0) return;

    const formData = new FormData();
    uploadedFiles.forEach(fileObj => {
      formData.append('files', fileObj.file);
    });

    if (uploadType === 'compact') {
      await onCompactValidation(formData);
    } else {
      await onFileUpload(formData);
    }
  };

  const getFileIcon = (fileName) => {
    if (fileName.endsWith('.pdf')) return '📄';
    if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) return '📊';
    return '📁';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sf-card">
        <div className="sf-card-header">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Upload className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">File Upload</h1>
              <p className="text-gray-600">Upload insurance documents for validation</p>
            </div>
          </div>
        </div>
        
        <div className="sf-card-body">
          {/* Upload Type Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Validation Type
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="uploadType"
                  value="standard"
                  checked={uploadType === 'standard'}
                  onChange={(e) => setUploadType(e.target.value)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Standard Validation</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="uploadType"
                  value="compact"
                  checked={uploadType === 'compact'}
                  onChange={(e) => setUploadType(e.target.value)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Compact Validation</span>
              </label>
            </div>
          </div>

          {/* Drop Zone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg text-gray-600 mb-2">
              {isDragActive
                ? 'Drop the files here...'
                : 'Drag & drop files here, or click to select'}
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF, Excel files (XLS, XLSX)
            </p>
          </div>

          {/* File List */}
          {uploadedFiles.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Uploaded Files</h3>
              <div className="space-y-3">
                {uploadedFiles.map((fileObj) => (
                  <div
                    key={fileObj.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{getFileIcon(fileObj.file.name)}</span>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {fileObj.file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(fileObj.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {fileObj.status === 'uploading' && (
                        <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                      )}
                      {fileObj.status === 'success' && (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                      {fileObj.status === 'error' && (
                        <AlertCircle className="w-5 h-5 text-red-500" />
                      )}
                      <button
                        onClick={() => removeFile(fileObj.id)}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        <X className="w-4 h-4 text-gray-500" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upload Button */}
          {uploadedFiles.length > 0 && (
            <div className="mt-6">
              <button
                onClick={handleUpload}
                disabled={isLoading}
                className="sf-btn sf-btn-primary w-full"
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </div>
                ) : (
                  `Upload ${uploadedFiles.length} file${uploadedFiles.length > 1 ? 's' : ''} for ${uploadType === 'compact' ? 'Compact' : 'Standard'} Validation`
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="sf-card">
        <div className="sf-card-header">
          <h3 className="text-lg font-medium text-gray-900">Upload Instructions</h3>
        </div>
        <div className="sf-card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Standard Validation</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Complete document analysis</li>
                <li>• Detailed validation report</li>
                <li>• Quality control checklist</li>
                <li>• Comprehensive error tracking</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Compact Validation</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Quick document review</li>
                <li>• Summary validation report</li>
                <li>• Essential quality checks</li>
                <li>• Fast processing time</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SalesforceFileUpload;
