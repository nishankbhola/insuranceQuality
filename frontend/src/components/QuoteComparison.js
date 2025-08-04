import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, XCircle, AlertTriangle, Car, User, MapPin, Calendar, GitCompare } from 'lucide-react';

function QuoteComparison() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please select a valid PDF file');
      setSelectedFile(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/compare-quote', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setComparisonData(result);
      } else {
        setError(result.error || 'Comparison failed');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'MATCH':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'NO_MATCH':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'MATCH':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'NO_MATCH':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-4">
          <GitCompare className="w-16 h-16 text-primary-600" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Quote Data Comparison
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Upload a PDF document to compare its content with the existing quote_result.json data. 
          This tool helps validate data consistency and identify discrepancies.
        </p>
      </div>

      {/* File Upload Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Upload PDF for Comparison</h2>
          <p className="text-gray-600">Select a PDF file to compare with the quote data</p>
        </div>

        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="pdf-upload"
            />
            <label
              htmlFor="pdf-upload"
              className="cursor-pointer bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Select PDF File
            </label>
            {selectedFile && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {selectedFile.name}
              </p>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <XCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-red-700">{error}</span>
              </div>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!selectedFile || loading}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
              !selectedFile || loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {loading ? 'Comparing...' : 'Compare with Quote Data'}
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Processing PDF and comparing data...</p>
        </div>
      )}

      {/* Comparison Results */}
      {comparisonData && !loading && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Comparison Summary</h2>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <User className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-600">
                  {comparisonData.summary.matched_drivers}/{comparisonData.summary.total_drivers}
                </div>
                <div className="text-sm text-blue-600">Drivers Matched</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <Car className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-green-600">
                  {comparisonData.summary.matched_vehicles}/{comparisonData.summary.total_vehicles}
                </div>
                <div className="text-sm text-green-600">Vehicles Matched</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4 text-center">
                <AlertTriangle className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-yellow-600">
                  {comparisonData.summary.issues_found}
                </div>
                <div className="text-sm text-yellow-600">Issues Found</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <FileText className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-purple-600">
                  {comparisonData.address_match ? '✓' : '✗'}
                </div>
                <div className="text-sm text-purple-600">Address Match</div>
              </div>
            </div>
          </div>

          {/* Driver Comparisons */}
          {comparisonData.drivers.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Driver Comparisons</h2>
              <div className="space-y-4">
                {comparisonData.drivers.map((driver, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-medium text-gray-900">
                        {driver.json_driver.full_name}
                      </h3>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(driver.status)}
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(driver.status)}`}>
                          {driver.status}
                        </span>
                      </div>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">JSON Data</h4>
                        <div className="space-y-1 text-sm">
                          <div><strong>License:</strong> {driver.json_driver.licence_number}</div>
                          <div><strong>Birth Date:</strong> {driver.json_driver.birth_date}</div>
                          <div><strong>Class:</strong> {driver.json_driver.licence_class}</div>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">PDF Matches</h4>
                        {driver.pdf_matches.length > 0 ? (
                          <div className="space-y-2">
                            {driver.pdf_matches.map((match, matchIndex) => (
                              <div key={matchIndex} className="border-l-2 border-gray-200 pl-3">
                                <div className="text-sm">
                                  <div><strong>Name:</strong> {match.pdf_driver.full_name || 'Not found'}</div>
                                  <div><strong>License:</strong> {match.pdf_driver.licence_number || 'Not found'}</div>
                                  <div><strong>Match Score:</strong> {match.match_score}%</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500">No matches found in PDF</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Vehicle Comparisons */}
          {comparisonData.vehicles.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Vehicle Comparisons</h2>
              <div className="space-y-4">
                {comparisonData.vehicles.map((vehicle, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-medium text-gray-900">
                        VIN: {vehicle.json_vehicle.vin}
                      </h3>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(vehicle.status)}
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(vehicle.status)}`}>
                          {vehicle.status}
                        </span>
                      </div>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">JSON Data</h4>
                        <div className="space-y-1 text-sm">
                          <div><strong>Type:</strong> {vehicle.json_vehicle.vehicle_type}</div>
                          <div><strong>Fuel:</strong> {vehicle.json_vehicle.fuel_type}</div>
                          <div><strong>Use:</strong> {vehicle.json_vehicle.primary_use}</div>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">PDF Matches</h4>
                        {vehicle.pdf_matches.length > 0 ? (
                          <div className="space-y-2">
                            {vehicle.pdf_matches.map((match, matchIndex) => (
                              <div key={matchIndex} className="border-l-2 border-gray-200 pl-3">
                                <div className="text-sm">
                                  <div><strong>VIN:</strong> {match.pdf_vehicle.vin || 'Not found'}</div>
                                  <div><strong>Type:</strong> {match.pdf_vehicle.vehicle_type || 'Not found'}</div>
                                  <div><strong>Match Score:</strong> {match.match_score}%</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500">No matches found in PDF</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PDF Text Sample */}
          {comparisonData.pdf_text_sample && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">PDF Text Sample</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {comparisonData.pdf_text_sample}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QuoteComparison; 