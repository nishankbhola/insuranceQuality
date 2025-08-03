import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ValidationReport from './components/ValidationReport';
import Header from './components/Header';
import { Shield, FileText, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

function App() {
  const [validationData, setValidationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleValidationComplete = (data) => {
    setValidationData(data);
    setLoading(false);
    setError(null);
  };

  const handleValidationError = (error) => {
    setError(error);
    setLoading(false);
  };

  const handleValidationStart = () => {
    setLoading(true);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <div className="flex justify-center mb-4">
              <Shield className="w-16 h-16 text-primary-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Insurance Quality Control System
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Upload MVR reports, DASH reports, and insurance quotes to automatically validate 
              data consistency and generate comprehensive validation reports.
            </p>
          </div>

          {/* File Upload Section */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <FileUpload 
              onValidationStart={handleValidationStart}
              onValidationComplete={handleValidationComplete}
              onValidationError={handleValidationError}
            />
          </div>

          {/* Loading State */}
          {loading && (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-lg text-gray-600">Processing documents and validating data...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-danger-500">
              <div className="flex items-center">
                <XCircle className="w-6 h-6 text-danger-500 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">Error</h3>
              </div>
              <p className="text-gray-600 mt-2">{error}</p>
            </div>
          )}

          {/* Validation Report */}
          {validationData && !loading && (
            <ValidationReport data={validationData} />
          )}

          {/* Features Section */}
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <FileText className="w-12 h-12 text-primary-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Document Processing</h3>
              <p className="text-gray-600">
                Automatically extract and parse data from MVR reports, DASH reports, and insurance quotes.
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <CheckCircle className="w-12 h-12 text-success-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Data Validation</h3>
              <p className="text-gray-600">
                Compare information across documents to ensure consistency and completeness.
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <AlertTriangle className="w-12 h-12 text-warning-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Issue Detection</h3>
              <p className="text-gray-600">
                Identify missing convictions, mismatched data, and other potential problems.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App; 