import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const SalesforceCollapsible = ({ 
  title, 
  children, 
  defaultExpanded = false,
  icon,
  count,
  className = '' 
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`sf-collapsible ${isExpanded ? 'expanded' : ''} ${className}`}>
      <div className="sf-collapsible-header" onClick={toggleExpanded}>
        <div className="flex items-center space-x-2">
          {icon && <span className="text-gray-600">{icon}</span>}
          <span className="font-medium">{title}</span>
          {count !== undefined && (
            <span className="text-sm text-gray-500">({count})</span>
          )}
        </div>
        <ChevronDown className="sf-collapsible-icon w-4 h-4 text-gray-500" />
      </div>
      
      {isExpanded && (
        <div className="sf-collapsible-content">
          {children}
        </div>
      )}
    </div>
  );
};

export default SalesforceCollapsible;
