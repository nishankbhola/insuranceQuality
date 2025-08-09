import React, { useState, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Loader2,
  X
} from 'lucide-react';

function FileUpload({ onFileUpload, onCompactValidation, isLoading }) {
  const [files, setFiles] = useState({ quote: null, mvr: [], dash: [] });
  const [errors, setErrors] = useState({ quote: '', mvr: '', dash: '' });
  const [dragActive, setDragActive] = useState(false);
  const [validationType, setValidationType] = useState('standard'); // 'standard' or 'compact'
  const fileInputRef = useRef(null);

  // Auto-detect file type based on filename and content
  const detectFileType = (file) => {
    const filename = file.name.toLowerCase();
    
    // Check for common patterns in filenames
    if (filename.includes('quote') || filename.includes('insurance') || filename.includes('policy')) {
      return 'quote';
    } else if (filename.includes('mvr') || filename.includes('motor') || filename.includes('vehicle')) {
      return 'mvr';
    } else if (filename.includes('dash') || filename.includes('abstract') || filename.includes('history')) {
      return 'dash';
    }
    
    // If filename doesn't give clear indication, we'll let the backend handle it
    return 'auto';
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (fileList) => {
    const newFiles = { ...files };
    const newErrors = { ...errors };
    
    Array.from(fileList).forEach(file => {
      // Validate file type
      if (!file.type.includes('pdf')) {
        alert('Please upload only PDF files.');
        return;
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB.');
        return;
      }
      
      const detectedType = detectFileType(file);
      
      if (detectedType === 'auto') {
        // For auto-detected files, we'll let the backend sort them out
        // We'll store them temporarily and let the backend determine the type
        if (!newFiles.quote) {
          newFiles.quote = file;
          newErrors.quote = '';
        } else if (newFiles.mvr.length === 0) {
          newFiles.mvr = [file];
          newErrors.mvr = '';
        } else if (newFiles.dash.length === 0) {
          newFiles.dash = [file];
          newErrors.dash = '';
        } else {
          alert('Maximum 3 files allowed (Quote, MVR, DASH)');
        }
      } else if (detectedType === 'quote') {
        // Quote can only have one file
        newFiles.quote = file;
        newErrors.quote = '';
      } else if (detectedType === 'mvr') {
        // MVR can have multiple files
        newFiles.mvr.push(file);
        newErrors.mvr = '';
      } else if (detectedType === 'dash') {
        // DASH can have multiple files
        newFiles.dash.push(file);
        newErrors.dash = '';
      }
    });
    
    setFiles(newFiles);
    setErrors(newErrors);
  };

  const removeFile = (fileType, index = null) => {
    setFiles(prev => {
      const newFiles = { ...prev };
      if (fileType === 'quote') {
        newFiles.quote = null;
      } else if (index !== null) {
        // Remove specific file from array
        newFiles[fileType] = newFiles[fileType].filter((_, i) => i !== index);
      } else {
        // Clear entire array
        newFiles[fileType] = [];
      }
      return newFiles;
    });
    setErrors(prev => ({ ...prev, [fileType]: '' }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Check if we have at least 3 files total
    const totalFiles = (files.quote ? 1 : 0) + files.mvr.length + files.dash.length;
    if (totalFiles < 3) {
      alert('Please upload all three required documents: Quote, MVR, and DASH report.');
      return;
    }
    
    // Check if we have at least one of each type
    if (!files.quote) {
      alert('Please upload a Quote document.');
      return;
    }
    if (files.mvr.length === 0) {
      alert('Please upload at least one MVR document.');
      return;
    }
    if (files.dash.length === 0) {
      alert('Please upload at least one DASH document.');
      return;
    }
    
    // Create FormData with all files
    const formData = new FormData();
    
    // Add quote file
    formData.append('quote', files.quote);
    
    // Add all MVR files
    files.mvr.forEach((file, index) => {
      formData.append('mvr', file);
    });
    
    // Add all DASH files
    files.dash.forEach((file, index) => {
      formData.append('dash', file);
    });
    
    // Call appropriate handler based on validation type
    if (validationType === 'compact' && onCompactValidation) {
      onCompactValidation(formData);
    } else {
      onFileUpload(formData);
    }
  };

  const getFileTypeLabel = (fileType) => {
    switch (fileType) {
      case 'quote': return 'Insurance Quote';
      case 'mvr': return 'MVR Report';
      case 'dash': return 'DASH Report';
      default: return 'Document';
    }
  };

  const getFileTypeIcon = (fileType) => {
    switch (fileType) {
      case 'quote': return <FileText className="w-5 h-5 text-blue-600" />;
      case 'mvr': return <Shield className="w-5 h-5 text-green-600" />;
      case 'dash': return <AlertTriangle className="w-5 h-5 text-orange-600" />;
      default: return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  const getFileTypeColor = (fileType) => {
    switch (fileType) {
      case 'quote': return 'border-blue-200 bg-blue-50';
      case 'mvr': return 'border-green-200 bg-green-50';
      case 'dash': return 'border-orange-200 bg-orange-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center">
            <Upload className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Document Upload</h1>
            <p className="text-gray-600">Upload your insurance documents for validation</p>
          </div>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900">Smart Document Detection</h3>
              <p className="text-sm text-blue-700 mt-1">
                Simply upload your Quote, MVR, and DASH documents. Our system will automatically detect and categorize them based on their content and filename patterns. Multiple MVR and DASH files are supported for multi-driver scenarios.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Single Upload Area */}
      <div className="mb-8">
        <div
          className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
            dragActive 
              ? 'border-blue-400 bg-blue-50' 
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileInputChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          
          <div className="space-y-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Drop your documents here or click to browse
              </h3>
              <p className="text-gray-600 mb-4">
                Upload your Insurance Quote, MVR Report(s), and DASH Report(s) (PDF files only, max 10MB each). 
                You can upload multiple MVR and DASH files for different drivers.
              </p>
              
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Choose Files
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Uploaded Files Display */}
      {(files.quote || files.mvr.length > 0 || files.dash.length > 0) && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Uploaded Documents</h3>
          <div className="space-y-4">
            {/* Quote File */}
            {files.quote && (
              <div className={`flex items-center justify-between p-4 rounded-lg border ${getFileTypeColor('quote')}`}>
                <div className="flex items-center space-x-3">
                  {getFileTypeIcon('quote')}
                  <div>
                    <p className="font-medium text-gray-900">{files.quote.name}</p>
                    <p className="text-sm text-gray-600">
                      {getFileTypeLabel('quote')} • {(files.quote.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <button
                    onClick={() => removeFile('quote')}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    <X className="w-4 h-4 text-gray-500" />
                  </button>
                </div>
              </div>
            )}
            
            {/* MVR Files */}
            {files.mvr.map((file, index) => (
              <div
                key={`mvr-${index}`}
                className={`flex items-center justify-between p-4 rounded-lg border ${getFileTypeColor('mvr')}`}
              >
                <div className="flex items-center space-x-3">
                  {getFileTypeIcon('mvr')}
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-600">
                      {getFileTypeLabel('mvr')} • {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <button
                    onClick={() => removeFile('mvr', index)}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    <X className="w-4 h-4 text-gray-500" />
                  </button>
                </div>
              </div>
            ))}
            
            {/* DASH Files */}
            {files.dash.map((file, index) => (
              <div
                key={`dash-${index}`}
                className={`flex items-center justify-between p-4 rounded-lg border ${getFileTypeColor('dash')}`}
              >
                <div className="flex items-center space-x-3">
                  {getFileTypeIcon('dash')}
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-600">
                      {getFileTypeLabel('dash')} • {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <button
                    onClick={() => removeFile('dash', index)}
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

      {/* Information Cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <h4 className="font-semibold text-gray-900">Document Processing</h4>
          </div>
          <p className="text-gray-600 text-sm">
            Our advanced OCR technology extracts and validates information from your PDF documents with high accuracy.
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <h4 className="font-semibold text-gray-900">Data Validation</h4>
          </div>
          <p className="text-gray-600 text-sm">
            Cross-reference information across all documents to ensure consistency and identify any discrepancies.
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
            </div>
            <h4 className="font-semibold text-gray-900">Issue Detection</h4>
          </div>
          <p className="text-gray-600 text-sm">
            Automatically identify missing information, inconsistencies, and potential issues that require attention.
          </p>
        </div>
      </div>

      {/* Validation Type Selector */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Validation Report Type</h3>
        <div className="flex space-x-4">
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="radio"
              name="validationType"
              value="standard"
              checked={validationType === 'standard'}
              onChange={(e) => setValidationType(e.target.value)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <div>
              <span className="font-medium text-gray-900">Standard Report</span>
              <p className="text-sm text-gray-600">Detailed validation report with comprehensive analysis</p>
            </div>
          </label>
          
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="radio"
              name="validationType"
              value="compact"
              checked={validationType === 'compact'}
              onChange={(e) => setValidationType(e.target.value)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <div>
              <span className="font-medium text-gray-900">Compact Report</span>
              <p className="text-sm text-gray-600">One-page professional report with charts and analytics</p>
            </div>
          </label>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-center">
        <button
          onClick={handleSubmit}
          disabled={isLoading || !files.quote || files.mvr.length === 0 || files.dash.length === 0}
          className={`flex items-center space-x-2 px-8 py-3 rounded-lg font-medium transition-colors ${
            isLoading || !files.quote || files.mvr.length === 0 || files.dash.length === 0
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Shield className="w-5 h-5" />
              <span>Start {validationType === 'compact' ? 'Compact ' : ''}Validation</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default FileUpload; 