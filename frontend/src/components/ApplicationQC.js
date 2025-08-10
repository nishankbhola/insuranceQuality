import React, { useState } from 'react';
import { Upload, FileText, Download, CheckCircle, AlertCircle, Loader, X, ExternalLink, AlertTriangle } from 'lucide-react';
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
    
    if (!applicationFile || !quoteFile) {
      setError('Please select both application and quote PDF files');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('application', applicationFile);
      formData.append('quote', quoteFile);

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
        {/* Summary */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">QC Summary</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{summary.total_checks}</div>
              <div className="text-sm text-gray-600">Total Checks</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{summary.failed_checks}</div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{summary.passed_checks}</div>
              <div className="text-sm text-gray-600">Passed</div>
            </div>
          </div>
          <div className="mt-4 flex justify-between items-center">
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              summary.overall_status === 'FAIL' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
            }`}>
              Overall Status: {summary.overall_status}
            </div>
            <div className="space-x-2">
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

        {/* Simple QC Results List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">QC Validation Results</h3>
          <div className="space-y-3">
            {/* Failed Checks */}
            {failed_checks && failed_checks.map((item, index) => (
              <div key={`fail-${index}`} className={`p-4 rounded-lg border ${getStatusColor(item.status)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      {getStatusIcon(item.status)}
                      <span className="ml-3 font-medium text-gray-900">{item.check_description}: </span>
                      <span className="font-bold text-red-600">FAIL</span>
                    </div>
                    <textarea
                      value={editableRemarks[index] || item.remarks || ''}
                      onChange={(e) => updateRemarks(index, e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded text-sm"
                      rows="2"
                      placeholder="Add remarks..."
                    />
                  </div>
                </div>
              </div>
            ))}
            
            {/* Passed Checks */}
            {passed_checks && passed_checks.map((item, index) => (
              <div key={`pass-${index}`} className={`p-4 rounded-lg border ${getStatusColor(item.status)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      {getStatusIcon(item.status)}
                      <span className="ml-3 font-medium text-gray-900">{item.check_description}: </span>
                      <span className="font-bold text-green-600">PASS</span>
                    </div>
                    {item.remarks && (
                      <div className="ml-9 text-sm text-gray-700 bg-green-50 p-3 rounded border border-green-200 mb-3">
                        <strong>Details:</strong> {item.remarks}
                      </div>
                    )}
                    <textarea
                      value={editableRemarks[`pass-${index}`] || item.remarks || ''}
                      onChange={(e) => updateRemarks(`pass-${index}`, e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded text-sm"
                      rows="2"
                      placeholder="Add or edit remarks..."
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
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
                Upload both the insurance application PDF and the corresponding quote PDF to perform automated 
                quality control checks. The system will validate the application against a comprehensive QC checklist, 
                highlighting critical errors, warnings, and passes for easy review.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* File Upload Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {renderFileUpload('application', applicationFile, 'Upload Application PDF')}
        {renderFileUpload('quote', quoteFile, 'Upload Quote PDF')}
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
          disabled={!applicationFile || !quoteFile || isLoading}
          className={`w-full px-4 py-3 rounded-lg font-medium transition-colors ${
            !applicationFile || !quoteFile || isLoading
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
      {result && renderQCResults()}
    </div>
  );
}

export default ApplicationQC; 