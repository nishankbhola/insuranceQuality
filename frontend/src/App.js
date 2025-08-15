import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Upload, 
  FileText, 
  Users, 
  Database, 
  TrendingUp, 
  HelpCircle,
  ClipboardCheck,
  X,
  Menu,
  BarChart3,
  Shield
} from 'lucide-react';
import SalesforceDashboard from './components/SalesforceDashboard';
import SalesforceDashboardContent from './components/SalesforceDashboardContent';
import FileUpload from './components/FileUpload';
import ValidationReport from './components/ValidationReport';
import CompactValidationReport from './components/CompactValidationReport';
import ApplicationQC from './components/ApplicationQC';
import { API_ENDPOINTS } from './config';
import './styles/salesforce-design-system.css';

function App() {
  const [validationData, setValidationData] = useState(null);
  const [compactValidationData, setCompactValidationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleFileUpload = async (formData) => {
    setIsLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.validate, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      setValidationData(data);
      setActiveTab('validation');
    } catch (error) {
      console.error('Error uploading files:', error);
      alert('Error uploading files. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompactValidation = async (formData) => {
    setIsLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.validateCompact, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Store both the compact report and the no_dash_report flag
      setCompactValidationData({
        ...data.compact_report,
        no_dash_report: data.no_dash_report
      });
      setActiveTab('compact_validation');
    } catch (error) {
      console.error('Error uploading files for compact validation:', error);
      alert('Error uploading files for compact validation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    setActiveTab('dashboard');
    setValidationData(null);
    setCompactValidationData(null);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <SalesforceDashboardContent
            title="Vieira Insurance Dashboard"
            subtitle="Insurance Quality Control & Validation System"
            stageData={{
              currentStage: 1,
              stages: [
                { id: 1, label: 'System Ready' },
                { id: 2, label: 'Upload Documents' },
                { id: 3, label: 'Validation Complete' }
              ]
            }}
            onTabChange={setActiveTab}
          />
        );
      
      case 'upload':
        return (
          <div className="space-y-6">
            {/* Header Section */}
            <div className="sf-card">
              <div className="sf-card-header">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                    <Upload className="w-6 h-6 text-white" />
                  </div>
                                     <div>
                     <h1 className="text-2xl font-bold text-gray-900">Auto Validator</h1>
                     <p className="text-gray-600">Upload insurance documents for validation</p>
                   </div>
                </div>
              </div>
            </div>

            {/* File Upload Component */}
            <div className="sf-card">
              <div className="sf-card-body">
                <FileUpload
                  onFileUpload={handleFileUpload}
                  onCompactValidation={handleCompactValidation}
                  isLoading={isLoading}
                />
              </div>
            </div>
          </div>
        );
      
      case 'validation':
        return (
          <div className="space-y-6">
            {validationData ? (
              <>
                <div className="sf-card">
                  <div className="sf-card-header">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                          <FileText className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h1 className="text-2xl font-bold text-gray-900">Validation Report</h1>
                          <p className="text-gray-600">Document validation results and analysis</p>
                        </div>
                      </div>
                      <button
                        onClick={handleBackToDashboard}
                        className="sf-btn sf-btn-secondary"
                      >
                        ← Back to Dashboard
                      </button>
                    </div>
                  </div>
                  <div className="sf-card-body">
                    <ValidationReport data={validationData} />
                  </div>
                </div>
              </>
            ) : (
              <div className="sf-card">
                <div className="sf-card-body">
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <FileText className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Validation Data</h3>
                    <p className="text-gray-600 mb-6">Please upload documents first to see validation results.</p>
                    <button
                      onClick={handleBackToDashboard}
                      className="sf-btn sf-btn-primary"
                    >
                      ← Back to Dashboard
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      
      case 'compact_validation':
        return (
          <div className="space-y-6">
            {compactValidationData ? (
              <>
                <div className="sf-card">
                  <div className="sf-card-header">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                          <BarChart3 className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h1 className="text-2xl font-bold text-gray-900">Compact Validation Report</h1>
                          <p className="text-gray-600">Summary validation results</p>
                        </div>
                      </div>
                      <button
                        onClick={handleBackToDashboard}
                        className="sf-btn sf-btn-secondary"
                      >
                        ← Back to Dashboard
                      </button>
                    </div>
                  </div>
                  <div className="sf-card-body">
                    <CompactValidationReport reportData={compactValidationData} />
                  </div>
                </div>
              </>
            ) : (
              <div className="sf-card">
                <div className="sf-card-body">
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <BarChart3 className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Compact Validation Data</h3>
                    <p className="text-gray-600 mb-6">Please upload documents first to see compact validation results.</p>
                    <button
                      onClick={handleBackToDashboard}
                      className="sf-btn sf-btn-primary"
                    >
                      ← Back to Dashboard
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      
      case 'application_qc':
        return (
          <div className="space-y-6">
            <div className="sf-card">
              <div className="sf-card-header">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">Application QC</h1>
                    <p className="text-gray-600">Quality control for insurance applications</p>
                  </div>
                </div>
              </div>
              <div className="sf-card-body">
                <ApplicationQC />
              </div>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="text-center py-8">
            <p className="text-gray-500">Select a tab from the sidebar to get started</p>
          </div>
        );
    }
  };

  return (
    <SalesforceDashboard
      activeTab={activeTab}
      onTabChange={setActiveTab}
    >
      {renderContent()}
    </SalesforceDashboard>
  );
}

export default App; 