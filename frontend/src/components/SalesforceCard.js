import React from 'react';

const SalesforceCard = ({ 
  children, 
  className = '', 
  onClick,
  hoverable = true 
}) => {
  const baseClasses = 'sf-card';
  const hoverClasses = hoverable ? 'cursor-pointer' : '';
  const clickClasses = onClick ? 'cursor-pointer' : '';
  
  return (
    <div 
      className={`${baseClasses} ${hoverClasses} ${clickClasses} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

const SalesforceCardHeader = ({ children, className = '' }) => (
  <div className={`sf-card-header ${className}`}>
    {children}
  </div>
);

const SalesforceCardBody = ({ children, className = '' }) => (
  <div className={`sf-card-body ${className}`}>
    {children}
  </div>
);

const SalesforceCardFooter = ({ children, className = '' }) => (
  <div className={`sf-card-footer ${className}`}>
    {children}
  </div>
);

SalesforceCard.Header = SalesforceCardHeader;
SalesforceCard.Body = SalesforceCardBody;
SalesforceCard.Footer = SalesforceCardFooter;

export default SalesforceCard;
