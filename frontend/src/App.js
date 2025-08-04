import React, { useState } from 'react';
import { 
  FileText, 
  Upload, 
  FileCheck,
  Menu,
  X,
  Home,
  Shield,
  TrendingUp,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import FileUpload from './components/FileUpload';
import ValidationReport from './components/ValidationReport';
import './App.css';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState(null);
  const [validationData, setValidationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleFileUpload = async (formData) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/validate', {
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

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, active: true },
    { id: 'upload', label: 'File Upload', icon: Upload },
    { id: 'validation', label: 'Validation Reports', icon: FileCheck },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="p-6">
            <div className="mb-8">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Welcome to Vieira Insurance</h1>
                  <p className="text-gray-600">Quality Control System</p>
                </div>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <h3 className="font-medium text-blue-900">System Overview</h3>
                    <p className="text-sm text-blue-700 mt-1">
                      Upload MVR reports, DASH reports, and insurance quotes to automatically validate data consistency 
                      and generate comprehensive validation reports. Our system ensures accuracy and completeness across all documents.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-1 gap-4">
                  <button 
                    onClick={() => setActiveTab('upload')}
                    className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-left"
                  >
                    <div className="flex items-center space-x-3">
                      <Upload className="w-8 h-8 text-blue-600" />
                      <div>
                        <p className="font-medium text-blue-900">Start New Validation</p>
                        <p className="text-sm text-blue-700">Upload documents for validation</p>
                      </div>
                    </div>
                  </button>
                  
                  {validationData && (
                    <button 
                      onClick={() => setActiveTab('validation')}
                      className="p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors text-left"
                    >
                      <div className="flex items-center space-x-3">
                        <FileCheck className="w-8 h-8 text-green-600" />
                        <div>
                          <p className="font-medium text-green-900">View Latest Report</p>
                          <p className="text-sm text-green-700">Review validation results</p>
                        </div>
                      </div>
                    </button>
                  )}
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Features</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Document Processing</p>
                      <p className="text-sm text-gray-600">Advanced OCR technology for PDF extraction</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Data Validation</p>
                      <p className="text-sm text-gray-600">Cross-reference information across documents</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                      <AlertTriangle className="w-4 h-4 text-orange-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Issue Detection</p>
                      <p className="text-sm text-gray-600">Identify discrepancies and missing information</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                      <TrendingUp className="w-4 h-4 text-purple-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Professional Reports</p>
                      <p className="text-sm text-gray-600">Generate detailed validation reports</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {validationData && (
              <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Latest Validation</h3>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {validationData.drivers?.[0]?.driver_name || 'Driver Validation'}
                      </p>
                      <p className="text-sm text-gray-500">
                        License: {validationData.drivers?.[0]?.driver_license || 'N/A'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab('validation')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View Report
                  </button>
                </div>
              </div>
            )}
          </div>
        );
      case 'upload':
        return <FileUpload onFileUpload={handleFileUpload} isLoading={isLoading} />;
      case 'validation':
        return validationData ? <ValidationReport data={validationData} /> : <div className="p-6">No validation data available</div>;
      default:
        return (
          <div className="p-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Coming Soon</h3>
              <p className="text-gray-500">This feature is under development and will be available soon.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:relative lg:translate-x-0`}>
        <div className="flex flex-col h-full">
          {/* Logo and Brand */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">V</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">Vieira Insurance</h1>
                <p className="text-xs text-gray-500">Quality Control System</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeTab === item.id
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* User Section */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">V</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Vieira Insurance</p>
                <p className="text-xs text-gray-500">Quality Control System</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
              >
                <Menu className="w-5 h-5 text-gray-500" />
              </button>
              <div className="hidden md:flex items-center space-x-4">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search validations..."
                    className="pl-4 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden md:block">
                <p className="text-sm text-gray-500">Vieira Insurance Quality Control System</p>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          {renderContent()}
        </main>
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}

export default App; 