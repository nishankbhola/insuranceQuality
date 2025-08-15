import React, { useState } from 'react';
import SalesforceSidebar from './SalesforceSidebar';
import SalesforceHeader from './SalesforceHeader';

const SalesforceDashboard = ({ children, activeTab, onTabChange }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <SalesforceSidebar 
        activeTab={activeTab} 
        onTabChange={onTabChange}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={toggleSidebar}
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <SalesforceHeader 
          onToggleSidebar={toggleSidebar}
          sidebarOpen={sidebarOpen}
        />
        
        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default SalesforceDashboard;
