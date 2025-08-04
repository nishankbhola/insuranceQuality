import React, { useState, useRef } from 'react';
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Download,
  Eye,
  EyeOff,
  FileText,
  User,
  Shield,
  TrendingUp,
  Clock,
  Building,
  Calendar,
  Gavel,
  MapPin
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

function ValidationReport({ data }) {
  const [showRawJson, setShowRawJson] = useState(false);
  const reportRef = useRef(null);

  // Handle the correct data structure
  const validationData = data.validation_report || data;

  // Calculate overall match score
  const calculateOverallScore = () => {
    if (!validationData.summary) {
      return 0;
    }
    
    const totalDrivers = validationData.summary.total_drivers;
    const validatedDrivers = validationData.summary.validated_drivers;
    
    // Calculate percentage based on validated drivers
    if (totalDrivers > 0) {
      return Math.round((validatedDrivers / totalDrivers) * 100);
    }
    
    // If no summary data, calculate from individual driver statuses
    if (validationData.drivers && validationData.drivers.length > 0) {
      let totalScore = 0;
      validationData.drivers.forEach(driver => {
        if (driver.validation_status === 'PASS') {
          totalScore += 100;
        } else if (driver.validation_status === 'WARNING') {
          totalScore += 50; // Partial validation
        } else {
          totalScore += 0;
        }
      });
      return Math.round(totalScore / validationData.drivers.length);
    }
    
    return 0;
  };

  // Calculate MVR match score
  const calculateMVRScore = (driver) => {
    const mvrValidation = driver.mvr_validation;
    if (!mvrValidation || mvrValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = mvrValidation.matches.length + mvrValidation.critical_errors.length + mvrValidation.warnings.length;
    const matches = mvrValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    // Calculate score: matches get full points, warnings get partial points, critical errors get no points
    const score = (matches / totalChecks) * 100;
    return Math.round(score);
  };

  // Calculate DASH match score
  const calculateDASHScore = (driver) => {
    const dashValidation = driver.dash_validation;
    if (!dashValidation || dashValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = dashValidation.matches.length + dashValidation.critical_errors.length + dashValidation.warnings.length;
    const matches = dashValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    // Calculate score: matches get full points, warnings get partial points, critical errors get no points
    const score = (matches / totalChecks) * 100;
    return Math.round(score);
  };

  // Calculate License Progression score
  const calculateLicenseProgressionScore = (driver) => {
    const licenseValidation = driver.license_progression_validation;
    if (!licenseValidation || licenseValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = licenseValidation.matches.length + licenseValidation.critical_errors.length + licenseValidation.warnings.length;
    const matches = licenseValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    const score = (matches / totalChecks) * 100;
    return Math.round(score);
  };

  // Calculate Convictions score
  const calculateConvictionsScore = (driver) => {
    const convictionsValidation = driver.convictions_validation;
    if (!convictionsValidation || convictionsValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = convictionsValidation.matches.length + convictionsValidation.critical_errors.length + convictionsValidation.warnings.length;
    const matches = convictionsValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    const score = (matches / totalChecks) * 100;
    return Math.round(score);
  };

  // Get status indicator
  const getStatusIndicator = (score) => {
    if (score >= 90) return { icon: <CheckCircle className="w-6 h-6 text-green-500" />, text: 'Excellent Match', color: 'text-green-600' };
    if (score >= 70) return { icon: <AlertTriangle className="w-6 h-6 text-yellow-500" />, text: 'Acceptable', color: 'text-yellow-600' };
    if (score >= 50) return { icon: <AlertTriangle className="w-6 h-6 text-orange-500" />, text: 'Partial Match', color: 'text-orange-600' };
    return { icon: <XCircle className="w-6 h-6 text-red-500" />, text: 'Needs Review', color: 'text-red-600' };
  };

  // Get severity badge
  const getSeverityBadge = (type) => {
    switch (type) {
      case 'critical':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">🟥 Critical</span>;
      case 'warning':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">🟧 Warning</span>;
      case 'match':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">✅ Match</span>;
      default:
        return null;
    }
  };

  // Download PDF report
  const downloadPDF = async () => {
    if (!reportRef.current) return;

    const canvas = await html2canvas(reportRef.current, {
      scale: 2,
      useCORS: true,
      allowTaint: true
    });

    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    const imgWidth = 210;
    const pageHeight = 295;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;

    let position = 0;

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    const timestamp = new Date().toISOString().split('T')[0];
    pdf.save(`validation-report-${timestamp}.pdf`);
  };

  const overallScore = calculateOverallScore();
  const statusIndicator = getStatusIndicator(overallScore);

  return (
    <div className="space-y-6">
      {/* Report Header */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Enhanced Validation Report</h2>
            <p className="text-gray-600">Comprehensive analysis with domain-specific rules and severity indicators</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowRawJson(!showRawJson)}
              className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              {showRawJson ? <EyeOff className="w-4 h-4 mr-2" /> : <Eye className="w-4 h-4 mr-2" />}
              {showRawJson ? 'Hide' : 'View'} Raw JSON
            </button>
            <button
              onClick={downloadPDF}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Download PDF
            </button>
          </div>
        </div>

        {/* Company Info and Timestamp */}
        <div className="flex justify-between items-center py-4 border-t border-b border-gray-200">
          <div className="flex items-center">
            <Building className="w-6 h-6 text-blue-600 mr-2" />
            <span className="font-semibold text-gray-900">Insurance Quality Control System</span>
          </div>
          <div className="flex items-center text-gray-600">
            <Clock className="w-4 h-4 mr-2" />
            <span>{new Date().toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Raw JSON Toggle */}
      {showRawJson && (
        <div className="bg-gray-900 rounded-lg p-4">
          <pre className="text-green-400 text-sm overflow-auto max-h-96">
            {JSON.stringify(validationData, null, 2)}
          </pre>
        </div>
      )}

      {/* Main Report Content */}
      <div ref={reportRef} className="bg-white rounded-lg shadow-lg p-6">
        {/* Validation Summary Section */}
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Validation Summary</h3>
          
          {/* Overall Score */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Overall Match Score</h4>
                <div className="flex items-center space-x-3">
                  <div className="text-4xl font-bold text-blue-600">{overallScore}%</div>
                  <div className="flex items-center space-x-2">
                    {statusIndicator.icon}
                    <span className={`font-semibold ${statusIndicator.color}`}>
                      {statusIndicator.text}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">
                  <div>Total Drivers: {validationData.summary?.total_drivers || 0}</div>
                  <div>Validated: {validationData.summary?.validated_drivers || 0}</div>
                  <div>Critical Errors: {validationData.summary?.critical_errors || 0}</div>
                  <div>Warnings: {validationData.summary?.warnings || 0}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <FileText className="w-6 h-6 text-blue-600 mr-2" />
                <h5 className="font-semibold text-gray-900">MVR vs Quote</h5>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {validationData.drivers?.length > 0 ? calculateMVRScore(validationData.drivers[0]) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Critical field validation</div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <TrendingUp className="w-6 h-6 text-purple-600 mr-2" />
                <h5 className="font-semibold text-gray-900">License Progression</h5>
              </div>
              <div className="text-2xl font-bold text-purple-600">
                {validationData.drivers?.length > 0 ? calculateLicenseProgressionScore(validationData.drivers[0]) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">G1/G2/G date logic</div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <Gavel className="w-6 h-6 text-orange-600 mr-2" />
                <h5 className="font-semibold text-gray-900">Convictions</h5>
              </div>
              <div className="text-2xl font-bold text-orange-600">
                {validationData.drivers?.length > 0 ? calculateConvictionsScore(validationData.drivers[0]) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Conviction matching</div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <Shield className="w-6 h-6 text-green-600 mr-2" />
                <h5 className="font-semibold text-gray-900">DASH vs Quote</h5>
              </div>
              <div className="text-2xl font-bold text-green-600">
                {validationData.drivers?.length > 0 ? calculateDASHScore(validationData.drivers[0]) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Claims and policy validation</div>
            </div>
          </div>
        </div>

        {/* Detailed Comparison Breakdown */}
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Detailed Comparison Breakdown</h3>
          
          {validationData.drivers?.map((driver, driverIndex) => (
            <div key={driverIndex} className="mb-8">
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <div className="flex items-center space-x-3">
                  <User className="w-6 h-6 text-gray-600" />
                  <div>
                    <h4 className="text-xl font-semibold text-gray-900">{driver.driver_name}</h4>
                    <p className="text-gray-600">License: {driver.driver_license}</p>
                  </div>
                  <div className="ml-auto">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      driver.validation_status === 'PASS' 
                        ? 'bg-green-100 text-green-800' 
                        : driver.validation_status === 'WARNING'
                        ? 'bg-orange-100 text-orange-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {driver.validation_status}
                    </span>
                  </div>
                </div>
              </div>

              {/* MVR Validation Section */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-blue-600" />
                  MVR Validation ({calculateMVRScore(driver)}%)
                </h5>
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0">
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Field</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Comparison</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Status</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Severity</div>
                  </div>
                  
                  {/* License Number Check */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">License Number</div>
                    <div className="px-4 py-3 text-gray-600">Exact match validation</div>
                    <div className="px-4 py-3">
                      {driver.mvr_validation.matches.some(m => m.includes('License number matches')) ? (
                        <div className="flex items-center text-green-600">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Match
                        </div>
                      ) : (
                        <div className="flex items-center text-red-600">
                          <XCircle className="w-4 h-4 mr-1" />
                          Mismatch
                        </div>
                      )}
                    </div>
                    <div className="px-4 py-3">
                      {driver.mvr_validation.matches.some(m => m.includes('License number matches')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>

                  {/* Name Check */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">Driver Name</div>
                    <div className="px-4 py-3 text-gray-600">Fuzzy string comparison</div>
                    <div className="px-4 py-3">
                      {driver.mvr_validation.matches.some(m => m.includes('Name matches')) ? (
                        <div className="flex items-center text-green-600">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Match
                        </div>
                      ) : (
                        <div className="flex items-center text-red-600">
                          <XCircle className="w-4 h-4 mr-1" />
                          Mismatch
                        </div>
                      )}
                    </div>
                    <div className="px-4 py-3">
                      {driver.mvr_validation.matches.some(m => m.includes('Name matches')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>

                  {/* Address Check */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">Address</div>
                    <div className="px-4 py-3 text-gray-600">Fuzzy string comparison</div>
                    <div className="px-4 py-3">
                      {driver.mvr_validation.matches.some(m => m.includes('Address matches')) ? (
                        <div className="flex items-center text-green-600">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Match
                        </div>
                      ) : (
                        <div className="flex items-center text-red-600">
                          <XCircle className="w-4 h-4 mr-1" />
                          Mismatch
                        </div>
                      )}
                    </div>
                    <div className="px-4 py-3">
                      {driver.mvr_validation.matches.some(m => m.includes('Address matches')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>

                  {/* DOB Check */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">Date of Birth</div>
                    <div className="px-4 py-3 text-gray-600">Cross-format date comparison</div>
                    <div className="px-4 py-3">
                      {driver.mvr_validation.matches.some(m => m.includes('Date of birth matches')) ? (
                        <div className="flex items-center text-green-600">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Match
                        </div>
                      ) : (
                        <div className="flex items-center text-red-600">
                          <XCircle className="w-4 h-4 mr-1" />
                          Mismatch
                        </div>
                      )}
                    </div>
                    <div className="px-4 py-3">
                      {driver.mvr_validation.matches.some(m => m.includes('Date of birth matches')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>
                </div>
              </div>

              {/* License Progression Validation Section */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-purple-600" />
                  License Progression Validation ({calculateLicenseProgressionScore(driver)}%)
                </h5>
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0">
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">License Stage</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Calculated Date</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Quote Date</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Status</div>
                  </div>
                  
                  {/* G1 Date Check */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700 font-medium">G1 Date</div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.license_progression_validation.matches.find(m => m.includes('G1 date matches'))?.split(': ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3 text-gray-600">
                      {/* Extract quote G1 date from validation message */}
                      {driver.license_progression_validation.critical_errors.find(e => e.includes('G1 date mismatch'))?.split('Quote: ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3">
                      {driver.license_progression_validation.matches.some(m => m.includes('G1 date matches')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>

                  {/* G2 Date Check */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700 font-medium">G2 Date</div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.license_progression_validation.matches.find(m => m.includes('G2 date matches'))?.split(': ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.license_progression_validation.critical_errors.find(e => e.includes('G2 date mismatch'))?.split('Quote: ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3">
                      {driver.license_progression_validation.matches.some(m => m.includes('G2 date matches')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>

                  {/* G Date Check */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700 font-medium">G Date</div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.license_progression_validation.matches.find(m => m.includes('G date matches'))?.split(': ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.license_progression_validation.critical_errors.find(e => e.includes('G date mismatch'))?.split('Quote: ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3">
                      {driver.license_progression_validation.matches.some(m => m.includes('G date matches') || m.includes('G date validation skipped')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>
                </div>
              </div>

              {/* Convictions Validation Section */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Gavel className="w-5 h-5 mr-2 text-orange-600" />
                  Convictions Validation ({calculateConvictionsScore(driver)}%)
                </h5>
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Offence Date</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Description</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Status</div>
                  </div>
                  
                  {driver.convictions_validation.matches.map((match, index) => {
                    const matchText = match.replace('Conviction matched: ', '');
                    const [date, description] = matchText.split(' - ');
                    return (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                        <div className="px-4 py-3 text-gray-700">{date}</div>
                        <div className="px-4 py-3 text-gray-600">{description}</div>
                        <div className="px-4 py-3">
                          {getSeverityBadge('match')}
                        </div>
                      </div>
                    );
                  })}
                  
                  {driver.convictions_validation.critical_errors.map((error, index) => {
                    const errorText = error.replace('Conviction not found in quote: ', '');
                    const [date, description] = errorText.split(' - ');
                    return (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                        <div className="px-4 py-3 text-gray-700">{date}</div>
                        <div className="px-4 py-3 text-gray-600">{description}</div>
                        <div className="px-4 py-3">
                          {getSeverityBadge('critical')}
                        </div>
                      </div>
                    );
                  })}
                  
                  {driver.convictions_validation.warnings.map((warning, index) => {
                    const warningText = warning.replace('Extra conviction in quote not in MVR: ', '');
                    const [date, description] = warningText.split(' - ');
                    return (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                        <div className="px-4 py-3 text-gray-700">{date}</div>
                        <div className="px-4 py-3 text-gray-600">{description}</div>
                        <div className="px-4 py-3">
                          {getSeverityBadge('warning')}
                        </div>
                      </div>
                    );
                  })}
                  
                  {driver.convictions_validation.matches.length === 0 && 
                   driver.convictions_validation.critical_errors.length === 0 && 
                   driver.convictions_validation.warnings.length === 0 && (
                    <div className="px-4 py-3 text-gray-500 text-center">
                      No convictions data available for validation
                    </div>
                  )}
                </div>
              </div>

              {/* DASH Validation Section */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-green-600" />
                  DASH Validation ({calculateDASHScore(driver)}%)
                </h5>
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">What Was Checked</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Comparison Result</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Status</div>
                  </div>
                  
                  {/* First Policy Validation */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">First Policy Ever Held</div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.dash_validation.matches.find(m => m.includes('First policy ever held'))?.split(': ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3">
                      {driver.dash_validation.matches.some(m => m.includes('First policy ever held')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>

                  {/* Date Insured vs First Policy */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">Date Insured vs First Policy</div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.dash_validation.matches.find(m => m.includes('Date insured'))?.split('(')[1]?.split(')')[0] || 
                       driver.dash_validation.critical_errors.find(e => e.includes('Date insured'))?.split('(')[1]?.split(')')[0] || 'N/A'}
                    </div>
                    <div className="px-4 py-3">
                      {driver.dash_validation.matches.some(m => m.includes('Date insured')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>

                  {/* Policy Gaps Check */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">Policy Gaps</div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.dash_validation.matches.some(m => m.includes('No policy gaps detected')) ? 
                        'No gaps detected' : 
                        driver.dash_validation.warnings.filter(w => w.includes('Policy gap detected')).length + ' gap(s) found'}
                    </div>
                    <div className="px-4 py-3">
                      {driver.dash_validation.matches.some(m => m.includes('No policy gaps detected')) ? 
                        getSeverityBadge('match') : getSeverityBadge('warning')}
                    </div>
                  </div>

                  {/* Active Policy Status Check */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">Active Policy Status</div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.dash_validation.matches.find(m => m.includes('active policy'))?.split('Found ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3">
                      {driver.dash_validation.matches.some(m => m.includes('active policy')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>

                  {/* Claims History Check */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                    <div className="px-4 py-3 text-gray-700">Claims History</div>
                    <div className="px-4 py-3 text-gray-600">
                      {driver.dash_validation.matches.find(m => m.includes('Found') && m.includes('claim'))?.split('Found ')[1] || 'N/A'}
                    </div>
                    <div className="px-4 py-3">
                      {driver.dash_validation.matches.some(m => m.includes('Found') && m.includes('claim')) ? 
                        getSeverityBadge('match') : getSeverityBadge('critical')}
                    </div>
                  </div>
                </div>

                {/* Policy Gaps Details */}
                {driver.dash_validation.warnings.filter(w => w.includes('Policy gap detected')).length > 0 && (
                  <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h6 className="font-semibold text-yellow-800 mb-2">Policy Gaps Detected:</h6>
                    {driver.dash_validation.warnings
                      .filter(w => w.includes('Policy gap detected'))
                      .map((warning, index) => (
                        <div key={index} className="text-sm text-yellow-700 mb-1">
                          • {warning.replace('Policy gap detected: ', '')}
                        </div>
                      ))}
                  </div>
                )}

                {/* Claims Details */}
                {(driver.dash_validation.matches.some(m => m.includes('Claim') && m.includes('validated')) ||
                  driver.dash_validation.critical_errors.some(e => e.includes('At-fault claim'))) && (
                  <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h6 className="font-semibold text-blue-800 mb-2">Claims Validation Details:</h6>
                    {driver.dash_validation.matches
                      .filter(m => m.includes('Claim') && (m.includes('validated') || m.includes('skipped')))
                      .map((match, index) => (
                        <div key={index} className="text-sm text-blue-700 mb-1">
                          ✅ {match.replace('Claim ', 'Claim #').replace(' validated', ' - Validated').replace(' skipped', ' - Skipped')}
                        </div>
                      ))}
                    {driver.dash_validation.critical_errors
                      .filter(e => e.includes('At-fault claim'))
                      .map((error, index) => (
                        <div key={index} className="text-sm text-red-700 mb-1">
                          ❌ {error.replace('At-fault claim ', 'Claim #').replace(' not declared in quote', ' - Not declared in quote')}
                        </div>
                      ))}
                  </div>
                )}
              </div>

              {/* Issues and Warnings Summary */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-3">Issues and Warnings Summary</h5>
                
                {/* Critical Errors */}
                {driver.critical_errors && driver.critical_errors.length > 0 && (
                  <div className="mb-4">
                    <h6 className="font-medium text-red-700 mb-2 flex items-center">
                      <XCircle className="w-4 h-4 mr-1" />
                      Critical Errors (🟥)
                    </h6>
                    <div className="space-y-2">
                      {driver.critical_errors.map((error, index) => (
                        <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-3">
                          <div className="flex items-start">
                            <XCircle className="w-4 h-4 text-red-600 mr-2 mt-0.5" />
                            <span className="text-red-800">{error}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {driver.warnings && driver.warnings.length > 0 && (
                  <div className="mb-4">
                    <h6 className="font-medium text-orange-700 mb-2 flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-1" />
                      Warnings (🟧)
                    </h6>
                    <div className="space-y-2">
                      {driver.warnings.map((warning, index) => (
                        <div key={index} className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                          <div className="flex items-start">
                            <AlertTriangle className="w-4 h-4 text-orange-600 mr-2 mt-0.5" />
                            <span className="text-orange-800">{warning}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Matches */}
                {driver.matches && driver.matches.length > 0 && (
                  <div>
                    <h6 className="font-medium text-green-700 mb-2 flex items-center">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Successful Matches (✅)
                    </h6>
                    <div className="space-y-2">
                      {driver.matches.map((match, index) => (
                        <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                          <div className="flex items-start">
                            <CheckCircle className="w-4 h-4 text-green-600 mr-2 mt-0.5" />
                            <span className="text-green-800">{match}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ValidationReport; 