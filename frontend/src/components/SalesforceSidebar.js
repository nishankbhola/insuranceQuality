import React, { useState } from 'react';
import { 
  Home, 
  Menu, 
  List, 
  FileText, 
  BarChart3, 
  Users, 
  Settings,
  ChevronRight,
  HelpCircle
} from 'lucide-react';

const SalesforceSidebar = ({ activeTab, onTabChange, sidebarOpen, onToggleSidebar }) => {
  const [expanded, setExpanded] = useState(false);

  const navigationItems = [
    { id: 'dashboard', label: 'Home', icon: Home, active: activeTab === 'dashboard' },
    { id: 'upload', label: 'Auto Validation', icon: FileText, active: activeTab === 'upload' },
    { id: 'validation', label: 'Validation Reports', icon: List, active: activeTab === 'validation' },
    { id: 'compact_validation', label: 'Compact Reports', icon: BarChart3, active: activeTab === 'compact_validation' },
    { id: 'application_qc', label: 'Application QC', icon: Users, active: activeTab === 'application_qc' },
  ];

  const handleItemClick = (tabId) => {
    onTabChange(tabId);
  };

  const toggleExpanded = () => {
    setExpanded(!expanded);
  };

  return (
    <div className={`sf-sidebar ${expanded ? 'expanded' : ''} ${sidebarOpen ? '' : 'hidden'}`}>
      {/* Toggle Button */}
      <div className="p-3 border-b border-gray-700">
        <button
          onClick={toggleExpanded}
          className="w-full flex items-center justify-center p-2 rounded-md hover:bg-gray-700 transition-colors"
        >
          <Menu className="w-5 h-5 text-gray-300" />
          {expanded && (
            <ChevronRight className="w-4 h-4 text-gray-300 ml-2" />
          )}
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 py-4">
        {navigationItems.map((item) => (
          <button
            key={item.id}
            onClick={() => handleItemClick(item.id)}
            className={`sf-sidebar-item w-full ${
              item.active ? 'active' : ''
            }`}
          >
            <item.icon className="sf-sidebar-icon" />
            {expanded && (
              <span className="sf-sidebar-label">{item.label}</span>
            )}
          </button>
        ))}
      </nav>

      {/* Bottom Section */}
      {expanded && (
        <div className="p-4 border-t border-gray-700">
          <div className="space-y-2">
            <button className="sf-sidebar-item w-full">
              <Settings className="sf-sidebar-icon" />
              <span className="sf-sidebar-label">Settings</span>
            </button>
            <button className="sf-sidebar-item w-full">
              <HelpCircle className="sf-sidebar-icon" />
              <span className="sf-sidebar-label">Help</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesforceSidebar;
