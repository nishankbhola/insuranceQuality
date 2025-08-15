import React, { useState, useRef, useEffect } from 'react';
import { User, Crown, Briefcase, Phone, Mail, Building } from 'lucide-react';

const SalesforcePopover = ({ 
  children, 
  content, 
  position = 'bottom',
  className = '' 
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [popoverPosition, setPopoverPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);

  const showPopover = () => {
    if (triggerRef.current && popoverRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const popoverRect = popoverRef.current.getBoundingClientRect();
      
      let top, left;
      
      switch (position) {
        case 'top':
          top = triggerRect.top - popoverRect.height - 8;
          left = triggerRect.left + (triggerRect.width / 2) - (popoverRect.width / 2);
          break;
        case 'bottom':
          top = triggerRect.bottom + 8;
          left = triggerRect.left + (triggerRect.width / 2) - (popoverRect.width / 2);
          break;
        case 'left':
          top = triggerRect.top + (triggerRect.height / 2) - (popoverRect.height / 2);
          left = triggerRect.left - popoverRect.width - 8;
          break;
        case 'right':
          top = triggerRect.top + (triggerRect.height / 2) - (popoverRect.height / 2);
          left = triggerRect.right + 8;
          break;
        default:
          top = triggerRect.bottom + 8;
          left = triggerRect.left + (triggerRect.width / 2) - (popoverRect.width / 2);
      }
      
      setPopoverPosition({ top, left });
    }
    setIsVisible(true);
  };

  const hidePopover = () => {
    setIsVisible(false);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target) &&
          triggerRef.current && !triggerRef.current.contains(event.target)) {
        hidePopover();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block">
      <div
        ref={triggerRef}
        onMouseEnter={showPopover}
        onMouseLeave={hidePopover}
        className="cursor-pointer"
      >
        {children}
      </div>
      
      {isVisible && (
        <div
          ref={popoverRef}
          className={`sf-popover ${className}`}
          style={{
            top: `${popoverPosition.top}px`,
            left: `${popoverPosition.left}px`,
          }}
        >
          {content}
        </div>
      )}
    </div>
  );
};

// Contact Popover Content Component
export const ContactPopoverContent = ({ contact }) => (
  <>
    <div className="sf-popover-header">
      <User className="w-5 h-5" />
      <span className="font-semibold">{contact.name}</span>
    </div>
    
    <div className="sf-popover-body">
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <Briefcase className="w-4 h-4 text-gray-500" />
          <span className="text-sm">
            <span className="text-gray-500 uppercase">Title:</span> {contact.title}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <Phone className="w-4 h-4 text-gray-500" />
          <span className="text-sm">
            <span className="text-gray-500 uppercase">Phone:</span> {contact.phone}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <Building className="w-4 h-4 text-gray-500" />
          <span className="text-sm">
            <span className="text-gray-500 uppercase">Account:</span> {contact.account}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <Mail className="w-4 h-4 text-gray-500" />
          <span className="text-sm">
            <span className="text-gray-500 uppercase">Email:</span> {contact.email}
          </span>
        </div>
        
        {contact.opportunities && (
          <div className="border-t pt-3">
            <div className="flex items-center space-x-2 mb-2">
              <Crown className="w-4 h-4 text-yellow-600" />
              <span className="text-sm font-medium">Related Opportunities</span>
            </div>
            <div className="space-y-2">
              {contact.opportunities.map((opp, index) => (
                <div key={index} className="text-sm">
                  <div className="font-medium">{opp.name}</div>
                  <div className="text-gray-500">Stage: {opp.stage} • Amount: {opp.amount}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  </>
);

export default SalesforcePopover;
