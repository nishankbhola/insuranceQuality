import React, { useState, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Loader2,
  X,
  ChevronRight,
  Info
} from 'lucide-react';

function FileUpload({ onFileUpload, onCompactValidation, isLoading }) {
  const [files, setFiles] = useState({ quote: null, mvr: [], dash: [] });
  const [errors, setErrors] = useState({ quote: '', mvr: '', dash: '' });
  const [dragActive, setDragActive] = useState(false);
  const [validationType, setValidationType] = useState('standard'); // 'standard' or 'compact'
  const [noDashReport, setNoDashReport] = useState(false); // New state for no DASH report option
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

  // Handle noDashReport checkbox change
  const handleNoDashReportChange = (checked) => {
    setNoDashReport(checked);
    if (checked) {
      // Clear DASH files when checkbox is checked
      setFiles(prev => ({ ...prev, dash: [] }));
      setErrors(prev => ({ ...prev, dash: '' }));
    }
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
    
    // Check if we have at least 2 files total (Quote + MVR) when no DASH report is selected
    const totalFiles = (files.quote ? 1 : 0) + files.mvr.length + (noDashReport ? 0 : files.dash.length);
    const minRequiredFiles = noDashReport ? 2 : 3;
    
    if (totalFiles < minRequiredFiles) {
      const requiredDocs = noDashReport ? 'Quote and MVR' : 'Quote, MVR, and DASH report';
      alert(`Please upload all required documents: ${requiredDocs}.`);
      return;
    }
    
    // Check if we have at least one of each required type
    if (!files.quote) {
      alert('Please upload a Quote document.');
      return;
    }
    if (files.mvr.length === 0) {
      alert('Please upload at least one MVR document.');
      return;
    }
    if (!noDashReport && files.dash.length === 0) {
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
    
    // Add all DASH files only if noDashReport is false
    if (!noDashReport) {
      files.dash.forEach((file, index) => {
        formData.append('dash', file);
      });
    }
    
    // Add the noDashReport flag
    formData.append('noDashReport', noDashReport);
    
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
      case 'quote': return 'border-blue-200 bg-blue-50/50';
      case 'mvr': return 'border-green-200 bg-green-50/50';
      case 'dash': return 'border-orange-200 bg-orange-50/50';
      default: return 'border-gray-200 bg-gray-50/50';
    }
  };

  return (
    <div className="w-full p-4">


      {/* Compact Info Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
        <div className="flex items-center space-x-2">
          <Info className="w-4 h-4 text-blue-600 flex-shrink-0" />
          <p className="text-blue-800 text-xs">
            <strong>Smart Detection:</strong> System automatically categorizes Quote, MVR, and DASH documents. Multiple files supported.
          </p>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid lg:grid-cols-2 gap-6 mb-4">
        {/* Left Column - Upload Area */}
        <div>
          <div
            className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 ${
              dragActive 
                ? 'border-blue-500 bg-blue-50/50' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50/30'
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
            
            <div className="space-y-3">
              <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                <Upload className="w-7 h-7 text-blue-600" />
              </div>
              
              <div>
                <h3 className="text-base font-semibold text-gray-900 mb-1">
                  Drop documents here or click to browse
                </h3>
                <p className="text-gray-600 text-sm mb-3">PDF files only, max 10MB each</p>
                
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
                >
                  Choose Files
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Features and Options */}
        <div className="space-y-4">
          {/* No DASH Report Option */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <AlertTriangle className="w-3 h-3 text-blue-600" />
              </div>
              <div className="flex-1">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={noDashReport}
                    onChange={(e) => handleNoDashReportChange(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-0.5"
                  />
                  <div>
                    <span className="font-medium text-gray-900 text-sm">Skip DASH Report</span>
                    <p className="text-xs text-gray-600 mt-1">
                      Check this if DASH report is not available for this validation
                    </p>
                  </div>
                </label>
              </div>
            </div>
          </div>

          {/* Validation Type Selector */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-2">Report Type</h3>
            <div className="grid grid-cols-2 gap-2">
              <label className={`cursor-pointer ${
                validationType === 'standard' ? 'ring-2 ring-blue-500 ring-offset-1' : ''
              }`}>
                <input
                  type="radio"
                  name="validationType"
                  value="standard"
                  checked={validationType === 'standard'}
                  onChange={(e) => setValidationType(e.target.value)}
                  className="sr-only"
                />
                <div className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                  validationType === 'standard' 
                    ? 'border-blue-500 bg-blue-50/50' 
                    : 'border-gray-200 bg-white hover:border-blue-300'
                }`}>
                  <div className="flex items-center space-x-2">
                    <FileText className={`w-4 h-4 ${validationType === 'standard' ? 'text-blue-600' : 'text-gray-600'}`} />
                    <div>
                      <span className={`font-medium block text-xs ${validationType === 'standard' ? 'text-blue-900' : 'text-gray-900'}`}>
                        Standard
                      </span>
                      <p className={`text-xs ${validationType === 'standard' ? 'text-blue-700' : 'text-gray-600'}`}>
                        Detailed
                      </p>
                    </div>
                  </div>
                </div>
              </label>
              
              <label className={`cursor-pointer ${
                validationType === 'compact' ? 'ring-2 ring-blue-500 ring-offset-1' : ''
              }`}>
                <input
                  type="radio"
                  name="validationType"
                  value="compact"
                  checked={validationType === 'compact'}
                  onChange={(e) => setValidationType(e.target.value)}
                  className="sr-only"
                />
                <div className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                  validationType === 'compact' 
                    ? 'border-blue-500 bg-blue-50/50' 
                    : 'border-gray-200 bg-white hover:border-blue-300'
                }`}>
                  <div className="flex items-center space-x-2">
                    <Shield className={`w-4 h-4 ${validationType === 'compact' ? 'text-blue-600' : 'text-gray-600'}`} />
                    <div>
                      <span className={`font-medium block text-xs ${validationType === 'compact' ? 'text-blue-900' : 'text-gray-900'}`}>
                        Compact
                      </span>
                      <p className={`text-xs ${validationType === 'compact' ? 'text-blue-700' : 'text-gray-600'}`}>
                        Summary
                      </p>
                    </div>
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* Submit Button - Now in the right column */}
          <div className="pt-2">
            <button
              onClick={handleSubmit}
              disabled={isLoading || !files.quote || files.mvr.length === 0 || (!noDashReport && files.dash.length === 0)}
              className={`w-full flex items-center justify-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                isLoading || !files.quote || files.mvr.length === 0 || (!noDashReport && files.dash.length === 0)
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
      </div>

      {/* Uploaded Files Display */}
      {(files.quote || files.mvr.length > 0 || files.dash.length > 0) && (
        <div className="mb-4">
          <h3 className="text-base font-semibold text-gray-900 mb-3">Uploaded Documents</h3>
          <div className="space-y-2">
            {/* Quote File */}
            {files.quote && (
              <div className={`flex items-center justify-between p-3 rounded-lg border ${getFileTypeColor('quote')}`}>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    {getFileTypeIcon('quote')}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{files.quote.name}</p>
                    <p className="text-xs text-gray-600">
                      {getFileTypeLabel('quote')} • {(files.quote.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <button
                    onClick={() => removeFile('quote')}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    <X className="w-3 h-3 text-gray-500" />
                  </button>
                </div>
              </div>
            )}
            
            {/* MVR Files */}
            {files.mvr.map((file, index) => (
              <div
                key={`mvr-${index}`}
                className={`flex items-center justify-between p-3 rounded-lg border ${getFileTypeColor('mvr')}`}
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    {getFileTypeIcon('mvr')}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{file.name}</p>
                    <p className="text-xs text-gray-600">
                      {getFileTypeLabel('mvr')} • {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <button
                    onClick={() => removeFile('mvr', index)}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    <X className="w-3 h-3 text-gray-500" />
                  </button>
                </div>
              </div>
            ))}
            
            {/* DASH Files */}
            {!noDashReport && files.dash.map((file, index) => (
              <div
                key={`dash-${index}`}
                className={`flex items-center justify-between p-3 rounded-lg border ${getFileTypeColor('dash')}`}
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                    {getFileTypeIcon('dash')}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{file.name}</p>
                    <p className="text-xs text-gray-600">
                      {getFileTypeLabel('dash')} • {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <button
                    onClick={() => removeFile('dash', index)}
                    className="p-1 hover:bg-gray-200 rounded"
                  >
                    <X className="w-3 h-3 text-gray-500" />
                  </button>
                </div>
              </div>
            ))}
            
            {/* No DASH Report Message */}
            {noDashReport && (
              <div className="flex items-center justify-between p-3 rounded-lg border border-yellow-200 bg-yellow-50/50">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-600" />
                  <div>
                    <p className="font-medium text-yellow-900 text-sm">No DASH Report</p>
                    <p className="text-xs text-yellow-700">DASH validation will be skipped</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 px-2 py-1 bg-yellow-100 rounded-full">
                  <CheckCircle className="w-3 h-3 text-yellow-600" />
                  <span className="text-xs font-medium text-yellow-700">Set</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default FileUpload; 