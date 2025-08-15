import React from 'react';

const SalesforceTabs = ({ tabs, activeTab, onTabChange, className = '' }) => {
  return (
    <div className={`sf-tabs ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`sf-tab ${activeTab === tab.id ? 'active' : ''}`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export default SalesforceTabs;
