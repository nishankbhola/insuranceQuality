import React from 'react';
import { Menu } from 'lucide-react';

// Custom Logo Component
const CustomLogo = () => (
  <div className="flex items-center space-x-3">
    {/* Stylized V Logo */}
    <div className="relative w-8 h-8">
      {/* Left segment - darker blue */}
      <div className="absolute left-0 top-0 w-4 h-8 bg-blue-700 transform skew-x-12 origin-left"></div>
      {/* Right segment - lighter blue */}
      <div className="absolute right-0 top-0 w-4 h-8 bg-blue-400 transform -skew-x-12 origin-right"></div>
    </div>
    {/* Company Name */}
    <span className="text-xl font-bold text-gray-900">Vieira Insurance</span>
  </div>
 );

const SalesforceHeader = ({ onToggleSidebar, sidebarOpen }) => {
  return (
    <header className="sf-header">
      <div className="flex items-center px-6 py-4">
        {/* Left Section - Logo and Sidebar Toggle */}
        <div className="flex items-center space-x-4">
          {/* Mobile Sidebar Toggle */}
          <button
            onClick={onToggleSidebar}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          
          {/* Logo */}
          <CustomLogo />
        </div>
      </div>
    </header>
  );
};

export default SalesforceHeader;
