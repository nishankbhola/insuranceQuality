import React, { useState } from 'react';
import { 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Download,
  Eye,
  Printer
} from 'lucide-react';
import SalesforceCard from './SalesforceCard';
import SalesforceTabs from './SalesforceTabs';

const SalesforceValidationReport = ({ validationData, onBack }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const [expandedSections, setExpandedSections] = useState(new Set());

  const tabs = [
    { id: 'summary', label: 'SUMMARY' },
    { id: 'details', label: 'DETAILS' },
    { id: 'errors', label: 'ERRORS' },
    { id: 'warnings', label: 'WARNINGS' }
  ];

  const toggleSection = (sectionId) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'passed':
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'passed':
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'failed':
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const exportReport = () => {
    // Implementation for exporting report
    console.log('Exporting report...');
  };

  const printReport = () => {
    window.print();
  };

  if (!validationData) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No validation data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sf-card">
        <div className="sf-card-header">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Validation Report</h1>
                <p className="text-gray-600">Document validation results and analysis</p>
              </div>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={exportReport}
                className="sf-btn sf-btn-secondary"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
              <button
                onClick={printReport}
                className="sf-btn sf-btn-secondary"
              >
                <Printer className="w-4 h-4 mr-2" />
                Print
              </button>
              <button
                onClick={onBack}
                className="sf-btn sf-btn-ghost"
              >
                Back
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <SalesforceCard>
          <div className="sf-card-body text-center">
            <div className="text-2xl font-bold text-green-600">
              {validationData.passed_checks || 0}
            </div>
            <div className="text-sm text-gray-600">Passed Checks</div>
          </div>
        </SalesforceCard>
        
        <SalesforceCard>
          <div className="sf-card-body text-center">
            <div className="text-2xl font-bold text-red-600">
              {validationData.failed_checks || 0}
            </div>
            <div className="text-sm text-gray-600">Failed Checks</div>
          </div>
        </SalesforceCard>
        
        <SalesforceCard>
          <div className="sf-card-body text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {validationData.warnings || 0}
            </div>
            <div className="text-sm text-gray-600">Warnings</div>
          </div>
        </SalesforceCard>
        
        <SalesforceCard>
          <div className="sf-card-body text-center">
            <div className="text-2xl font-bold text-blue-600">
              {validationData.total_checks || 0}
            </div>
            <div className="text-sm text-gray-600">Total Checks</div>
          </div>
        </SalesforceCard>
      </div>

      {/* Tabs and Content */}
      <div className="sf-card">
        <div className="sf-card-body">
          <SalesforceTabs
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
          
          {/* Tab Content */}
          {activeTab === 'summary' && (
            <div className="space-y-6">
              {/* Overall Status */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Overall Status</h3>
                    <p className="text-gray-600">Document validation completed</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(validationData.overall_status)}
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(validationData.overall_status)}`}>
                      {validationData.overall_status || 'Unknown'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Validation Summary */}
              {validationData.validation_summary && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Validation Summary</h3>
                  <div className="space-y-3">
                    {Object.entries(validationData.validation_summary).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700 capitalize">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(value.status)}
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(value.status)}`}>
                            {value.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'details' && (
            <div className="space-y-4">
              {validationData.details && Object.entries(validationData.details).map(([section, items]) => (
                <div key={section} className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => toggleSection(section)}
                    className="w-full p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
                  >
                    <span className="font-medium text-gray-900 capitalize">
                      {section.replace(/_/g, ' ')}
                    </span>
                    <span className="text-gray-500">
                      {expandedSections.has(section) ? '−' : '+'}
                    </span>
                  </button>
                  
                  {expandedSections.has(section) && (
                    <div className="p-4 border-t border-gray-200">
                      <div className="space-y-3">
                        {Array.isArray(items) ? items.map((item, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                            <span className="text-sm text-gray-700">{item.description || item}</span>
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(item.status)}
                              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(item.status)}`}>
                                {item.status}
                              </span>
                            </div>
                          </div>
                        )) : (
                          <div className="text-sm text-gray-600">
                            {typeof items === 'object' ? JSON.stringify(items, null, 2) : String(items)}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {activeTab === 'errors' && (
            <div className="space-y-3">
              {validationData.errors && validationData.errors.length > 0 ? (
                validationData.errors.map((error, index) => (
                  <div key={index} className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start space-x-3">
                      <XCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="font-medium text-red-900">{error.title || 'Validation Error'}</h4>
                        <p className="text-red-700 text-sm mt-1">{error.message || error}</p>
                        {error.location && (
                          <p className="text-red-600 text-xs mt-2">Location: {error.location}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <p>No errors found during validation</p>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'warnings' && (
            <div className="space-y-3">
              {validationData.warnings && validationData.warnings.length > 0 ? (
                validationData.warnings.map((warning, index) => (
                  <div key={index} className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="font-medium text-yellow-900">{warning.title || 'Validation Warning'}</h4>
                        <p className="text-yellow-700 text-sm mt-1">{warning.message || warning}</p>
                        {warning.suggestion && (
                          <p className="text-yellow-600 text-xs mt-2">Suggestion: {warning.suggestion}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <p>No warnings found during validation</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SalesforceValidationReport;
