import React from 'react';
import { Shield, FileText, GitCompare } from 'lucide-react';

function Header({ activeTab, onTabChange }) {
  const tabs = [
    {
      id: 'validation',
      label: 'Document Validation',
      icon: FileText,
      description: 'Validate insurance documents'
    },
    {
      id: 'comparison',
      label: 'Quote Comparison',
      icon: GitCompare,
      description: 'Compare PDFs with quote data'
    }
  ];

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">Quality Control</h1>
          </div>
          <div className="text-sm text-gray-500">
            Insurance Document Processing System
          </div>
        </div>
        
        {/* Navigation Tabs */}
        <nav className="flex space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-100 text-primary-700 border-b-2 border-primary-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

export default Header; 