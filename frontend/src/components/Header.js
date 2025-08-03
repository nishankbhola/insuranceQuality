import React from 'react';
import { Shield } from 'lucide-react';

function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">Quality Control</h1>
          </div>
          <div className="text-sm text-gray-500">
            Insurance Quote Validation System
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header; 