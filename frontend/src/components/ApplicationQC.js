import React, { useState } from 'react';
import { Upload, FileText, Download, CheckCircle, AlertCircle, Loader, X, ExternalLink, AlertTriangle, ChevronDown, ChevronUp, Code } from 'lucide-react';
import { API_ENDPOINTS } from '../config';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

function ApplicationQC() {
  const [applicationFile, setApplicationFile] = useState(null);
  const [quoteFile, setQuoteFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [editableRemarks, setEditableRemarks] = useState({});
  const [showExtractedData, setShowExtractedData] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e, fileType) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0], fileType);
    }
  };

  const handleFileInputChange = (e, fileType) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0], fileType);
    }
  };

  const handleFile = (selectedFile, fileType) => {
    if (selectedFile.type !== 'application/pdf') {
      setError('Please select a PDF file');
      return;
    }
    
    if (fileType === 'application') {
      setApplicationFile(selectedFile);
    } else {
      setQuoteFile(selectedFile);
    }
    
    setError(null);
  };

  const removeFile = (fileType) => {
    if (fileType === 'application') {
      setApplicationFile(null);
    } else {
      setQuoteFile(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!applicationFile) {
      setError('Please select an application PDF file');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('application', applicationFile);
      if (quoteFile) {
        formData.append('quote', quoteFile);
      }

      const response = await fetch(API_ENDPOINTS.applicationQC, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      
      // Initialize editable remarks
      const remarks = {};
      if (data.qc_results) {
        // Initialize failed checks with their index
        (data.qc_results.failed_checks || []).forEach((item, index) => {
          remarks[index] = item.remarks || '';
        });
        // Initialize passed checks with pass-{index} format
        (data.qc_results.passed_checks || []).forEach((item, index) => {
          remarks[`pass-${index}`] = item.remarks || '';
        });
      }
      setEditableRemarks(remarks);
      
    } catch (error) {
      console.error('Error processing application QC:', error);
      setError(`Error processing files: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const updateRemarks = (index, newRemarks) => {
    setEditableRemarks(prev => ({
      ...prev,
      [index]: newRemarks
    }));
  };

  const exportToPDF = () => {
    if (!result || !result.qc_results) return;

    const doc = new jsPDF();
    const { summary, qc_results } = result;
    
    // Header
    doc.setFontSize(20);
    doc.setTextColor(88, 28, 135); // Purple color
    doc.text('Application QC Report', 20, 25);
    
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 35);
    
    // Summary section
    doc.setFontSize(16);
    doc.text('Summary', 20, 50);
    
    doc.setFontSize(12);
    doc.text(`Total Checks: ${summary.total_checks}`, 20, 60);
    doc.text(`Failed Checks: ${summary.failed_checks}`, 20, 68);
    doc.text(`Passed Checks: ${summary.passed_checks}`, 20, 76);
    doc.text(`Overall Status: ${summary.overall_status}`, 20, 84);
    
    let yPosition = 100;
    
    // All Results in Simple Format
    const allResults = [
      ...(qc_results.failed_checks || []),
      ...(qc_results.passed_checks || [])
    ];
    
    if (allResults.length > 0) {
      doc.setFontSize(16);
      doc.setTextColor(0, 0, 0);
      doc.text('QC Validation Results', 20, yPosition);
      yPosition += 10;
      
      const resultsData = allResults.map((item, index) => {
        let remarksKey = index;
        if (item.status === 'PASS') {
          remarksKey = `pass-${index}`;
        }
        return [
          item.check_description || '',
          item.status || '',
          editableRemarks[remarksKey] || item.remarks || ''
        ];
      });
      
      doc.autoTable({
        startY: yPosition,
        head: [['Check Description', 'Status', 'Remarks']],
        body: resultsData,
        theme: 'grid',
        headStyles: { fillColor: [88, 28, 135] },
        margin: { left: 20, right: 20 },
        styles: {
          cellPadding: 3,
          fontSize: 10,
        },
        columnStyles: {
          0: { cellWidth: 80 },
          1: { cellWidth: 20, halign: 'center' },
          2: { cellWidth: 70 }
        },
        didParseCell: function(data) {
          if (data.column.index === 1 && data.cell.raw === 'FAIL') {
            data.cell.styles.textColor = [220, 38, 38];
            data.cell.styles.fontStyle = 'bold';
          } else if (data.column.index === 1 && data.cell.raw === 'PASS') {
            data.cell.styles.textColor = [34, 197, 94];
            data.cell.styles.fontStyle = 'bold';
          }
        }
      });
    }
    
    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      doc.text(`Page ${i} of ${pageCount}`, 20, 285);
      doc.text('Confidential - Application QC Report', 150, 285);
    }
    
    // Save the PDF
    doc.save(`application_qc_report_${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const exportToCSV = () => {
    if (!result || !result.qc_results) return;

    const allResults = [
      ...(result.qc_results.failed_checks || []),
      ...(result.qc_results.passed_checks || [])
    ];

    const csvContent = [
      ['Check Description', 'Status', 'Remarks'],
      ...allResults.map((item, index) => {
        let remarksKey = index;
        if (item.status === 'PASS') {
          remarksKey = `pass-${index}`;
        }
        return [
          item.check_description || '',
          item.status || '',
          editableRemarks[remarksKey] || item.remarks || ''
        ];
      })
    ].map(row => row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
    link.download = 'application_qc_results.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
  };

  const downloadExtractedData = (dataType) => {
    if (!result || !result.extracted_data) return;
    
    let data;
    let filename;
    
    if (dataType === 'application') {
      data = result.extracted_data.application;
      filename = 'extracted_application_data.json';
    } else if (dataType === 'quote') {
      data = result.extracted_data.quote;
      filename = 'extracted_quote_data.json';
    } else {
      return;
    }
    
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const downloadQCReport = (filename) => {
    if (!filename) return;
    
    // Create download link to the backend endpoint
    const downloadUrl = `${API_ENDPOINTS.baseURL}/api/download-qc-report/${filename}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatJSON = (data) => {
    try {
      return JSON.stringify(data, null, 2);
    } catch (error) {
      return 'Error formatting JSON data';
    }
  };

  const highlightJSON = (jsonString) => {
    return jsonString
      .replace(/"([^"]+)":/g, '<span class="text-blue-400">"$1"</span>:')
      .replace(/: "([^"]*)"/g, ': <span class="text-green-400">"$1"</span>')
      .replace(/: (\d+)/g, ': <span class="text-yellow-400">$1</span>')
      .replace(/: (true|false|null)/g, ': <span class="text-purple-400">$1</span>')
      .replace(/(\{|\}|\[|\])/g, '<span class="text-gray-300">$1</span>');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'FAIL':
        return <X className="w-5 h-5 text-red-600" />;
      case 'PASS':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'FAIL':
        return 'bg-red-50 border-red-200';
      case 'PASS':
        return 'bg-green-50 border-green-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const renderFileUpload = (fileType, file, title) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-purple-400'
        }`}
        onDragOver={handleDrag}
        onDrop={(e) => handleDrop(e, fileType)}
      >
        {file ? (
          <div>
            <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <p className="text-green-700 font-medium">{file.name}</p>
            <p className="text-sm text-green-600">File selected successfully</p>
            <button
              onClick={() => removeFile(fileType)}
              className="mt-2 text-red-600 hover:text-red-800 transition-colors"
            >
              Remove file
            </button>
          </div>
        ) : (
          <div>
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600 mb-2">
              Drag and drop your {fileType} PDF here, or click to browse
            </p>
            <p className="text-sm text-gray-500">Supports PDF files only</p>
          </div>
        )}
        
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => handleFileInputChange(e, fileType)}
          className="hidden"
          id={`${fileType}-file-input`}
        />
        <label
          htmlFor={`${fileType}-file-input`}
          className="inline-block mt-3 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors cursor-pointer"
        >
          Choose File
        </label>
      </div>
    </div>
  );

  const renderQCResults = () => {
    if (!result || !result.qc_results) return null;

    const { failed_checks, passed_checks } = result.qc_results;
    const { summary } = result;

    return (
      <div className="space-y-6">
        {/* Executive Summary */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="border-b border-gray-200 pb-4 mb-6">
            <h3 className="text-xl font-bold text-gray-900 mb-2">Executive Summary</h3>
            <div className="flex items-center space-x-4">
              <div className={`px-4 py-2 rounded-lg text-lg font-semibold ${
                (result.qc_validation_results?.critical_errors?.length || 0) === 0 
                  ? (result.qc_validation_results?.warnings?.length || 0) === 0 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {(result.qc_validation_results?.critical_errors?.length || 0) === 0 
                  ? (result.qc_validation_results?.warnings?.length || 0) === 0 
                    ? '✅ APPROVED' 
                    : '⚠️ CONDITIONAL PASS'
                  : '❌ FAILED'}
              </div>
              <div className="text-gray-600">
                <strong>Recommendation:</strong> {
                  (result.qc_validation_results?.critical_errors?.length || 0) === 0 
                    ? (result.qc_validation_results?.warnings?.length || 0) === 0 
                      ? 'APPROVED FOR PROCESSING' 
                      : 'REVIEW REQUIRED'
                    : 'IMMEDIATE ACTION REQUIRED'
                }
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-5 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {result.qc_validation_results?.summary?.total_validations || 0}
              </div>
              <div className="text-sm text-gray-600">Total Validations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {result.qc_validation_results?.critical_errors?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Critical Errors</div>
              <div className="text-xs text-gray-500">
                {result.qc_validation_results?.summary?.total_validations > 0 ? 
                  `${((result.qc_validation_results?.critical_errors?.length || 0) / result.qc_validation_results.summary.total_validations * 100).toFixed(1)}%` : '0%'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {result.qc_validation_results?.warnings?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Warnings</div>
              <div className="text-xs text-gray-500">
                {result.qc_validation_results?.summary?.total_validations > 0 ? 
                  `${((result.qc_validation_results?.warnings?.length || 0) / result.qc_validation_results.summary.total_validations * 100).toFixed(1)}%` : '0%'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {result.qc_validation_results?.passed_validations?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Passed</div>
              <div className="text-xs text-gray-500">
                {result.qc_validation_results?.summary?.total_validations > 0 ? 
                  `${((result.qc_validation_results?.passed_validations?.length || 0) / result.qc_validation_results.summary.total_validations * 100).toFixed(1)}%` : '0%'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {result.qc_validation_results?.summary?.total_vehicles || 0}
              </div>
              <div className="text-sm text-gray-600">Total Vehicles</div>
            </div>
          </div>
          
          {/* API Usage Information */}
          {result.qc_validation_results?.api_usage && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h4 className="font-medium text-blue-900 mb-2">🤖 AI Analysis Information</h4>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-blue-700">AI Analysis:</span> {
                    result.qc_validation_results.api_usage.gemini_analysis_enabled ? 'Enabled' : 'Disabled'
                  }
                </div>
                <div>
                  <span className="text-blue-700">API Calls Used:</span> {
                    result.qc_validation_results.api_usage.calls_made_this_session || 0
                  }/{result.qc_validation_results.api_usage.daily_limit || 50}
                </div>
                <div>
                  <span className="text-blue-700">Remaining:</span> {
                    result.qc_validation_results.api_usage.remaining_calls || 0
                  } calls
                </div>
              </div>
            </div>
          )}
          
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Report ID: QC-{new Date().toISOString().slice(0,10).replace(/-/g,'')}-{new Date().toISOString().slice(11,19).replace(/:/g,'')}
            </div>
            <div className="space-x-2">
              {result.files?.qc_report && (
                <button
                  onClick={() => downloadQCReport(result.files.qc_report)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  📄 Download Professional Report
                </button>
              )}
              <button
                onClick={exportToCSV}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Export CSV
              </button>
              <button
                onClick={exportToPDF}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Export PDF
              </button>
            </div>
          </div>
        </div>

        {/* Comprehensive QC Validation Results */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">QC Validation Results</h3>
          
          {/* Critical Errors Section */}
          {result.qc_validation_results?.critical_errors && result.qc_validation_results.critical_errors.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-red-700 mb-3 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                Critical Errors ({result.qc_validation_results.critical_errors.length})
              </h4>
              <div className="space-y-3">
                {result.qc_validation_results.critical_errors.map((error, index) => (
                  <div key={`critical-${index}`} className="p-4 rounded-lg border border-red-200 bg-red-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                          <span className="font-medium text-red-800">{error.type}: </span>
                          <span className="font-bold text-red-600">CRITICAL</span>
                        </div>
                        <div className="ml-7 text-red-700 mb-3 space-y-2">
                          <div>
                            <strong>Issue:</strong> {error.message}
                          </div>
                          {error.vehicle && error.vehicle !== 'General' && (
                            <div>
                              <strong>Vehicle:</strong> {error.vehicle}
                            </div>
                          )}
                          {error.business_rule && (
                            <div className="text-sm bg-red-100 p-2 rounded">
                              <strong>Business Rule:</strong> {error.business_rule}
                            </div>
                          )}
                          {error.explanation && (
                            <div className="text-sm">
                              <strong>Impact:</strong> {error.explanation}
                            </div>
                          )}
                          {error.data_checked && (
                            <div className="text-xs text-red-600">
                              <strong>Data Checked:</strong> {error.data_checked}
                            </div>
                          )}
                        </div>
                        <textarea
                          value={editableRemarks[`critical-${index}`] || ''}
                          onChange={(e) => updateRemarks(`critical-${index}`, e.target.value)}
                          className="w-full p-2 border border-red-300 rounded text-sm"
                          rows="2"
                          placeholder="Add remarks for this critical error..."
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Warnings Section */}
          {result.qc_validation_results?.warnings && result.qc_validation_results.warnings.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-yellow-700 mb-3 flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Warnings ({result.qc_validation_results.warnings.length})
              </h4>
              <div className="space-y-3">
                {result.qc_validation_results.warnings.map((warning, index) => (
                  <div key={`warning-${index}`} className="p-4 rounded-lg border border-yellow-200 bg-yellow-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                          <span className="font-medium text-yellow-800">{warning.type}: </span>
                          <span className="font-bold text-yellow-600">WARNING</span>
                        </div>
                        <div className="ml-7 text-yellow-700 mb-3 space-y-2">
                          <div>
                            <strong>Issue:</strong> {warning.message}
                          </div>
                          {warning.vehicle && warning.vehicle !== 'General' && (
                            <div>
                              <strong>Vehicle:</strong> {warning.vehicle}
                            </div>
                          )}
                          {warning.business_rule && (
                            <div className="text-sm bg-yellow-100 p-2 rounded">
                              <strong>Business Rule:</strong> {warning.business_rule}
                            </div>
                          )}
                          {warning.explanation && (
                            <div className="text-sm">
                              <strong>Context:</strong> {warning.explanation}
                            </div>
                          )}
                          {warning.data_checked && (
                            <div className="text-xs text-yellow-600">
                              <strong>Data Checked:</strong> {warning.data_checked}
                            </div>
                          )}
                          {warning.remarks_verification && (
                            <div className="text-sm bg-blue-50 p-2 rounded border border-blue-200">
                              <div className="flex items-center mb-1">
                                <span className="text-blue-700 font-medium">🤖 AI Analysis:</span>
                                <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                                  warning.remarks_verification.verification_result === 'PASS' 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {warning.remarks_verification.verification_result === 'PASS' ? '✅ RESOLVED' : '⚠️ NEEDS ATTENTION'}
                                </span>
                              </div>
                              <div className="text-blue-700 text-xs">
                                {warning.remarks_verification.gemini_analysis}
                              </div>
                            </div>
                          )}
                        </div>
                        <textarea
                          value={editableRemarks[`warning-${index}`] || ''}
                          onChange={(e) => updateRemarks(`warning-${index}`, e.target.value)}
                          className="w-full p-2 border border-yellow-300 rounded text-sm"
                          rows="2"
                          placeholder="Add remarks for this warning..."
                        />
                  </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Passed Validations Section */}
          {result.qc_validation_results?.passed_validations && result.qc_validation_results.passed_validations.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-green-700 mb-3 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Passed Validations ({result.qc_validation_results.passed_validations.length})
              </h4>
              <div className="space-y-3">
                {result.qc_validation_results.passed_validations.map((validation, index) => (
                  <div key={`passed-${index}`} className="p-4 rounded-lg border border-green-200 bg-green-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                          <span className="font-medium text-green-800">{validation.type}: </span>
                          <span className="font-bold text-green-600">PASSED</span>
                        </div>
                        <div className="ml-7 text-green-700 mb-3 space-y-2">
                          <div>
                            <strong>Result:</strong> {validation.message}
                          </div>
                          {validation.vehicle && validation.vehicle !== 'General' && (
                            <div>
                              <strong>Vehicle:</strong> {validation.vehicle}
                            </div>
                          )}
                          {validation.business_rule && (
                            <div className="text-sm bg-green-100 p-2 rounded">
                              <strong>Business Rule:</strong> {validation.business_rule}
                            </div>
                          )}
                          {validation.explanation && (
                            <div className="text-sm text-green-600">
                              <strong>Details:</strong> {validation.explanation}
                            </div>
                          )}
                          {validation.data_checked && (
                            <div className="text-xs text-green-600">
                              <strong>Data Verified:</strong> {validation.data_checked}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* All Validations Summary Section */}
          {result.qc_validation_results?.all_validations && result.qc_validation_results.all_validations.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-blue-700 mb-3 flex items-center">
                <Code className="w-5 h-5 mr-2" />
                All Validations Summary ({result.qc_validation_results.all_validations.length})
              </h4>
              <div className="space-y-3">
                {result.qc_validation_results.all_validations.map((validation, index) => (
                  <div key={`all-${index}`} className={`p-3 rounded-lg border ${
                    validation.status === 'passed' ? 'border-green-200 bg-green-50' :
                    validation.status === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                    'border-red-200 bg-red-50'
                  }`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          {validation.status === 'passed' ? (
                            <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                          ) : validation.status === 'warning' ? (
                            <AlertTriangle className="w-4 h-4 text-yellow-600 mr-2" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
                          )}
                          <span className="font-medium text-gray-800">{validation.type}: </span>
                          <span className={`font-bold ml-2 ${
                            validation.status === 'passed' ? 'text-green-600' :
                            validation.status === 'warning' ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {validation.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="ml-6 text-gray-700">
                          {validation.message}
                          {validation.vehicle && validation.vehicle !== 'General' && (
                            <div className="mt-1 text-sm text-gray-600">
                              <strong>Vehicle:</strong> {validation.vehicle}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Issues Found - Only show if no critical errors and no warnings */}
          {(!result.qc_validation_results?.critical_errors || result.qc_validation_results.critical_errors.length === 0) &&
           (!result.qc_validation_results?.warnings || result.qc_validation_results.warnings.length === 0) && (
            <div className="p-6 text-center">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h4 className="text-xl font-semibold text-green-700 mb-2">No Issues Found!</h4>
              <p className="text-green-600">All validation checks have passed successfully.</p>
            </div>
          )}
          
          {/* Recommendations Section */}
          <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-3">📋 Final Recommendations</h4>
            {(result.qc_validation_results?.critical_errors?.length || 0) > 0 ? (
              <div className="bg-red-50 border border-red-200 rounded p-3">
                <h5 className="font-medium text-red-800 mb-2">🚨 IMMEDIATE ACTIONS REQUIRED:</h5>
                <ul className="text-red-700 text-sm space-y-1">
                  <li>1. Resolve all critical errors listed above before proceeding with policy issuance</li>
                  <li>2. Obtain and verify all missing mandatory documentation</li>
                  <li>3. Re-submit application after corrections are completed</li>
                  <li>4. Conduct follow-up QC validation to confirm resolution</li>
                </ul>
              </div>
            ) : (result.qc_validation_results?.warnings?.length || 0) > 0 ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <h5 className="font-medium text-yellow-800 mb-2">⚠️ RECOMMENDED ACTIONS:</h5>
                <ul className="text-yellow-700 text-sm space-y-1">
                  <li>1. Review and address all warnings listed above</li>
                  <li>2. Verify remarks section adequately explains any identified concerns</li>
                  <li>3. Consider additional documentation where recommended</li>
                  <li>4. Policy issuance may proceed with management approval</li>
                </ul>
              </div>
            ) : (
              <div className="bg-green-50 border border-green-200 rounded p-3">
                <h5 className="font-medium text-green-800 mb-2">✅ APPROVAL STATUS:</h5>
                <ul className="text-green-700 text-sm space-y-1">
                  <li>✅ Application meets all quality control requirements</li>
                  <li>✅ All mandatory validations have passed successfully</li>
                  <li>✅ Application is approved for policy issuance</li>
                  <li>✅ No further action required</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderExtractedData = () => {
    if (!result || !result.extracted_data) return null;

    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Code className="w-5 h-5 mr-2 text-blue-600" />
            Extracted Data for Manual Inspection
          </h3>
          <button
            onClick={() => setShowExtractedData(!showExtractedData)}
            className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
          >
            {showExtractedData ? (
              <>
                <ChevronUp className="w-4 h-4 mr-1" />
                Hide Data
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-1" />
                Show Data
              </>
            )}
          </button>
        </div>
        
        {showExtractedData && (
          <div className="space-y-6">
            {/* Quick Summary */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-3">Quick Summary of Extracted Data</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h5 className="font-medium text-blue-800 mb-2">Application Data:</h5>
                  <ul className="space-y-1 text-blue-700">
                    <li>• Applicant: {result.extracted_data.application?.applicant_info?.full_name || 'Not found'}</li>
                    <li>• License: {result.extracted_data.application?.applicant_info?.license_number || 'Not found'}</li>
                    <li>• Vehicles: {result.extracted_data.application?.vehicles?.length || 0} found</li>
                    <li>• Drivers: {result.extracted_data.application?.drivers?.length || 0} found</li>
                    <li>• Effective Date: {result.extracted_data.application?.policy_info?.effective_date || 'Not found'}</li>
                  </ul>
                </div>
                <div>
                  <h5 className="font-medium text-blue-800 mb-2">Quote Data:</h5>
                  <ul className="space-y-1 text-blue-700">
                    <li>• Quote Effective: {result.extracted_data.quote?.quote_effective_date || 'Not found'}</li>
                    <li>• Premium: {result.extracted_data.quote?.premium_amount || 'Not found'}</li>
                    <li>• Coverage: {result.extracted_data.quote?.coverage_type || 'Not found'}</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Application Data */}
            <div className="border border-gray-200 rounded-lg">
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                <h4 className="font-medium text-gray-900">Application Data (application_extractor.py output)</h4>
                <button
                  onClick={() => downloadExtractedData('application')}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors flex items-center"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download JSON
                </button>
              </div>
              <div className="p-4 bg-gray-900 rounded-b-lg">
                <pre className="text-green-400 text-sm overflow-x-auto whitespace-pre-wrap" 
                     dangerouslySetInnerHTML={{ 
                       __html: highlightJSON(formatJSON(result.extracted_data.application)) 
                     }} />
              </div>
            </div>

            {/* Quote Data */}
            <div className="border border-gray-200 rounded-lg">
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                <h4 className="font-medium text-gray-900">Quote Data (quote_extractor.py output)</h4>
                <button
                  onClick={() => downloadExtractedData('quote')}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors flex items-center"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download JSON
                </button>
              </div>
              <div className="p-4 bg-gray-900 rounded-b-lg">
                <pre className="text-green-400 text-sm overflow-x-auto whitespace-pre-wrap" 
                     dangerouslySetInnerHTML={{ 
                       __html: highlightJSON(formatJSON(result.extracted_data.quote)) 
                     }} />
              </div>
            </div>

            {/* QC Results */}
            <div className="border border-gray-200 rounded-lg">
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                <h4 className="font-medium text-gray-900">QC Results (qc_checklist.py output)</h4>
                <button
                  onClick={() => {
                    const qcData = {
                      summary: result.summary,
                      qc_results: result.qc_results
                    };
                    const jsonString = JSON.stringify(qcData, null, 2);
                    const blob = new Blob([jsonString], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'qc_results.json';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                  }}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors flex items-center"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download JSON
                </button>
              </div>
              <div className="p-4 bg-gray-900 rounded-b-lg">
                <pre className="text-green-400 text-sm overflow-x-auto whitespace-pre-wrap" 
                     dangerouslySetInnerHTML={{ 
                       __html: highlightJSON(formatJSON({
                         summary: result.summary,
                         qc_results: result.qc_results
                       })) 
                     }} />
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900">Manual Inspection Guide</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Use this extracted data to manually verify what the application_extractor.py extracted from your PDF. 
                    You can download each dataset as JSON files for detailed analysis. This is useful for debugging 
                    extraction issues or verifying specific field values.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
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
            <p className="text-gray-600">Quality control validation for insurance applications</p>
          </div>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-5 h-5 text-purple-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-purple-900">How it works</h3>
              <p className="text-sm text-purple-700 mt-1">
                Upload the insurance application PDF to perform automated quality control checks using Gemini AI. 
                The system will validate the application against a comprehensive QC checklist, highlighting critical errors, 
                warnings, and passes for easy review. Quote PDF is optional.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* File Upload Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {renderFileUpload('application', applicationFile, 'Upload Application PDF (Required)')}
        {renderFileUpload('quote', quoteFile, 'Upload Quote PDF (Optional)')}
            </div>

      {/* Submit Button */}
      <div className="mb-8">
            {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <span className="text-red-800">{error}</span>
                </div>
              </div>
            )}

            <button
          onClick={handleSubmit}
          disabled={!applicationFile || isLoading}
          className={`w-full px-4 py-3 rounded-lg font-medium transition-colors ${
            !applicationFile || isLoading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-purple-600 text-white hover:bg-purple-700'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
              Running QC Analysis...
            </div>
          ) : (
            'Run Application QC'
          )}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <>
          {renderQCResults()}
          {renderExtractedData()}
        </>
      )}
    </div>
  );
}

export default ApplicationQC; 