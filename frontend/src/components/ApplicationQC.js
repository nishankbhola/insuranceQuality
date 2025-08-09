import React, { useState } from 'react';
import { Upload, FileText, Download, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { API_ENDPOINTS } from '../config';

function ApplicationQC() {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (selectedFile) => {
    if (selectedFile.type !== 'application/pdf') {
      setError('Please select a PDF file');
      return;
    }
    
    setFile(selectedFile);
    setError(null);
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('application', file);

      const response = await fetch(API_ENDPOINTS.applicationQC, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error uploading application:', error);
      setError('Error uploading application. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadJSON = () => {
    if (result && result.data) {
      const dataStr = JSON.stringify(result.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'application_data.json';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl flex items-center justify-center">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Application QC</h1>
            <p className="text-gray-600">Extract and analyze insurance application data</p>
          </div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-5 h-5 text-purple-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-purple-900">How it works</h3>
              <p className="text-sm text-purple-700 mt-1">
                Upload an insurance application PDF to automatically extract key information including applicant details, 
                vehicle information, coverage details, and policy information. The extracted data will be saved as a JSON file for review.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Application</h3>
          
          <form onSubmit={handleSubmit}>
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-purple-400'
              }`}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              
              {file ? (
                <div>
                  <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
                  <p className="text-green-700 font-medium">{file.name}</p>
                  <p className="text-sm text-green-600">File selected successfully</p>
                </div>
              ) : (
                <div>
                  <p className="text-gray-600 mb-2">
                    Drag and drop your application PDF here, or click to browse
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports PDF files only
                  </p>
                </div>
              )}
              
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileInputChange}
                className="hidden"
                id="file-input"
              />
              <label
                htmlFor="file-input"
                className="inline-block mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors cursor-pointer"
              >
                Choose File
              </label>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <span className="text-red-800">{error}</span>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={!file || isLoading}
              className={`w-full mt-4 px-4 py-3 rounded-lg font-medium transition-colors ${
                !file || isLoading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-purple-600 text-white hover:bg-purple-700'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
                  Processing...
                </div>
              ) : (
                'Extract Application Data'
              )}
            </button>
          </form>
        </div>

        {/* Results Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Extraction Results</h3>
          
          {result ? (
            <div>
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                  <span className="text-green-800 font-medium">Extraction Successful!</span>
                </div>
                <p className="text-sm text-green-700 mt-1">
                  Data has been extracted and saved to application_data.json
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">JSON File:</span>
                  <span className="text-sm font-medium text-gray-900">{result.filename}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Applicant:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {result.data?.applicant_info?.full_name || 'Not found'}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Vehicles:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {result.data?.vehicles?.length || 0} found
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Drivers:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {result.data?.drivers?.length || 0} found
                  </span>
                </div>
              </div>

              <button
                onClick={downloadJSON}
                className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Download JSON File
              </button>
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Upload an application to see extraction results</p>
            </div>
          )}
        </div>
      </div>

      {/* Data Preview */}
      {result && result.data && (
        <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Preview</h3>
          <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default ApplicationQC; 