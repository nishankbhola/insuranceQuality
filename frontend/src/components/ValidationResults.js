import React, { useState } from 'react';
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  ChevronDown, 
  ChevronRight,
  User,
  FileText,
  Calendar,
  Shield,
  Car
} from 'lucide-react';

function ValidationResults({ data }) {
  const [expandedDrivers, setExpandedDrivers] = useState(new Set());

  // Check if DASH validation was skipped
  const noDashReport = data.no_dash_report || false;

  const toggleDriver = (driverName) => {
    const newExpanded = new Set(expandedDrivers);
    if (newExpanded.has(driverName)) {
      newExpanded.delete(driverName);
    } else {
      newExpanded.add(driverName);
    }
    setExpandedDrivers(newExpanded);
  };

  const getSeverityColor = (issue) => {
    if (issue.includes('mismatch') || issue.includes('Missing')) {
      return 'danger';
    }
    if (issue.includes('No matching')) {
      return 'warning';
    }
    return 'info';
  };

  const getSeverityIcon = (issue) => {
    const severity = getSeverityColor(issue);
    switch (severity) {
      case 'danger':
        return <XCircle className="w-5 h-5 text-danger-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-warning-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-blue-500" />;
    }
  };

  const getSeverityBadge = (issue) => {
    const severity = getSeverityColor(issue);
    const colors = {
      danger: 'bg-danger-100 text-danger-800 border-danger-200',
      warning: 'bg-warning-100 text-warning-800 border-warning-200',
      info: 'bg-blue-100 text-blue-800 border-blue-200'
    };
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors[severity]}`}>
        {severity === 'danger' ? 'Critical' : severity === 'warning' ? 'Warning' : 'Info'}
      </span>
    );
  };

  const totalIssues = data.validation_report?.reduce((sum, driver) => sum + driver.issues.length, 0) || 0;
  const criticalIssues = data.validation_report?.reduce((sum, driver) => 
    sum + driver.issues.filter(issue => getSeverityColor(issue) === 'danger').length, 0) || 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-primary-500">
          <div className="flex items-center">
            <FileText className="w-8 h-8 text-primary-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Documents Processed</p>
              <p className="text-2xl font-bold text-gray-900">
                {(data.extracted?.mvrs?.length || 0) + 
                 (data.extracted?.dashes?.length || 0) + 
                 (data.extracted?.quotes?.length || 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-success-500">
          <div className="flex items-center">
            <User className="w-8 h-8 text-success-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Drivers Analyzed</p>
              <p className="text-2xl font-bold text-gray-900">
                {data.validation_report?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-warning-500">
          <div className="flex items-center">
            <AlertTriangle className="w-8 h-8 text-warning-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Total Issues</p>
              <p className="text-2xl font-bold text-gray-900">{totalIssues}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-danger-500">
          <div className="flex items-center">
            <XCircle className="w-8 h-8 text-danger-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Critical Issues</p>
              <p className="text-2xl font-bold text-gray-900">{criticalIssues}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Validation Report */}
      <div className="bg-white rounded-lg shadow-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">Validation Report</h3>
          <p className="text-gray-600 mt-1">
            Detailed analysis of each driver's information across all documents
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {data.validation_report?.map((driver, index) => (
            <div key={index} className="p-6">
              <div 
                className="flex items-center justify-between cursor-pointer"
                onClick={() => toggleDriver(driver.driver_name)}
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-medium text-gray-900">
                      {driver.driver_name}
                    </h4>
                    <div className="text-sm text-gray-500 space-y-1">
                      <p>License: {driver.driver_license}</p>
                      {driver.matched_mvr && (
                        <p className="text-green-600">✓ MVR: {driver.matched_mvr}</p>
                      )}
                      {driver.matched_dash && (
                        <p className="text-green-600">✓ DASH: {driver.matched_dash}</p>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  {driver.issues.length === 0 ? (
                    <div className="flex items-center space-x-2 text-success-600">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-medium">Passed</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      {getSeverityIcon(driver.issues[0])}
                      <span className="font-medium text-gray-900">
                        {driver.issues.length} Issue{driver.issues.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                  )}
                  
                  {expandedDrivers.has(driver.driver_name) ? (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </div>

              {expandedDrivers.has(driver.driver_name) && (
                <div className="mt-4 space-y-3">
                  {driver.issues.length === 0 ? (
                    <div className="bg-success-50 border border-success-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-5 h-5 text-success-600" />
                        <span className="font-medium text-success-800">
                          All validations passed for this driver
                        </span>
                      </div>
                    </div>
                  ) : (
                    driver.issues.map((issue, issueIndex) => (
                      <div key={issueIndex} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-start space-x-3">
                          {getSeverityIcon(issue)}
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="font-medium text-gray-900">{issue}</span>
                              {getSeverityBadge(issue)}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Extracted Data Summary */}
      <div className="bg-white rounded-lg shadow-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">Extracted Data Summary</h3>
        </div>
        <div className="p-6">
          <div className="grid md:grid-cols-4 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                MVR Reports ({data.extracted?.mvrs?.length || 0})
              </h4>
              <div className="space-y-2">
                {data.extracted?.mvrs?.map((mvr, index) => (
                  <div key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                    License: {mvr.licence_number} | Name: {mvr.name}
                  </div>
                ))}
              </div>
            </div>
            
            {!noDashReport && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  DASH Reports ({data.extracted?.dashes?.length || 0})
                </h4>
                <div className="space-y-2">
                  {data.extracted?.dashes?.map((dash, index) => (
                    <div key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                      DLN: {dash.dln} | Name: {dash.name}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* DASH Validation Skipped Message */}
            {noDashReport && (
              <div>
                <h4 className="font-medium text-yellow-900 mb-3 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-yellow-600" />
                  DASH Validation Skipped
                </h4>
                <div className="space-y-2">
                  <div className="text-sm text-yellow-700 bg-yellow-50 p-2 rounded border border-yellow-200">
                    DASH report validation was skipped for this application. Only MVR and quote information was validated.
                  </div>
                </div>
              </div>
            )}
            
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Quotes ({data.extracted?.quotes?.length || 0})
              </h4>
              <div className="space-y-2">
                {data.extracted?.quotes?.map((quote, index) => (
                  <div key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                    Drivers: {quote.drivers?.length || 0} | Vehicles: {quote.vehicles?.length || 0}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <Car className="w-5 h-5 mr-2" />
                Vehicles ({data.extracted?.quotes?.reduce((sum, q) => sum + (q.vehicles?.length || 0), 0) || 0})
              </h4>
              <div className="space-y-2">
                {data.extracted?.quotes?.map((quote, quoteIndex) => 
                  quote.vehicles?.map((vehicle, vehicleIndex) => (
                    <div key={`${quoteIndex}-${vehicleIndex}`} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                      {vehicle.vehicle_type} | VIN: {vehicle.vin?.substring(0, 8)}...
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ValidationResults; 