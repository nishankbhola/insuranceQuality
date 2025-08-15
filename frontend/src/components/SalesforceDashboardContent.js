import React from 'react';
import { LayoutDashboard, Upload, FileText, Users, CheckCircle } from 'lucide-react';
import SalesforceCard from './SalesforceCard';
import SalesforceStageProgress from './SalesforceStageProgress';

const SalesforceDashboardContent = ({ 
  title = "Vieira Insurance Dashboard",
  subtitle = "Insurance Quality Control & Validation System",
  stageData,
  onTabChange,
  className = '' 
}) => {
  const stages = [
    { id: 1, label: 'System Ready' },
    { id: 2, label: 'Upload Documents' },
    { id: 3, label: 'Validation Complete' }
  ];

  const handleUploadClick = () => {
    if (onTabChange) {
      onTabChange('upload');
    }
  };

  const handleValidationClick = () => {
    if (onTabChange) {
      onTabChange('validation');
    }
  };

  const handleQCClick = () => {
    if (onTabChange) {
      onTabChange('application_qc');
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header Section */}
      <div className="sf-card">
        <div className="sf-card-header">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
              <p className="text-lg text-gray-600">{subtitle}</p>
            </div>
          </div>
          
          {/* Stage Progress */}
          <SalesforceStageProgress 
            stages={stages} 
            currentStage={1} 
            className="mt-6"
          />
        </div>
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* File Upload Card */}
        <SalesforceCard 
          className="hover:shadow-lg transition-shadow cursor-pointer"
          onClick={handleUploadClick}
        >
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Documents</h3>
            <p className="text-gray-600 mb-4">Upload insurance documents for validation and quality control</p>
            <div className="text-sm text-blue-600 font-medium">Click to get started →</div>
          </div>
        </SalesforceCard>

        {/* Validation Reports Card */}
        <SalesforceCard 
          className="hover:shadow-lg transition-shadow cursor-pointer"
          onClick={handleValidationClick}
        >
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Validation Reports</h3>
            <p className="text-gray-600 mb-4">View detailed validation results and analysis reports</p>
            <div className="text-sm text-green-600 font-medium">View reports →</div>
          </div>
        </SalesforceCard>

        {/* Application QC Card */}
        <SalesforceCard 
          className="hover:shadow-lg transition-shadow cursor-pointer"
          onClick={handleQCClick}
        >
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Application QC</h3>
            <p className="text-gray-600 mb-4">Quality control for insurance applications</p>
            <div className="text-sm text-purple-600 font-medium">Review applications →</div>
          </div>
        </SalesforceCard>
      </div>

      {/* System Status */}
      <div className="sf-card">
        <div className="sf-card-header">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">System Status</h3>
              <p className="text-sm text-gray-600">All systems operational and ready for document processing</p>
            </div>
          </div>
        </div>
        <div className="sf-card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600 mb-1">Ready</div>
              <div className="text-sm text-green-600">Document Upload</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600 mb-1">Active</div>
              <div className="text-sm text-blue-600">Validation Engine</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600 mb-1">Online</div>
              <div className="text-sm text-purple-600">Quality Control</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SalesforceDashboardContent;
