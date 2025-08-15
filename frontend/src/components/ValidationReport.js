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
  Gavel
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

function ValidationReport({ data }) {
  const [showRawJson, setShowRawJson] = useState(false);
  const reportRef = useRef(null);

  // Handle the correct data structure
  const validationData = data.validation_report || data;
  
  // Check if DASH validation was skipped
  const noDashReport = data.no_dash_report || false;

  // Calculate overall match score
  const calculateOverallScore = () => {
    if (!validationData.drivers || validationData.drivers.length === 0) {
      return 0;
    }
    
    // Calculate average score across all drivers
    let totalScore = 0;
    let driverCount = 0;
    
    validationData.drivers.forEach(driver => {
      // Calculate individual scores for this driver
      const mvrScore = calculateMVRScore(driver);
      const licenseScore = calculateLicenseProgressionScore(driver);
      const convictionsScore = calculateConvictionsScore(driver);
      const dashScore = noDashReport ? 100 : calculateDASHScore(driver); // Give full score if DASH was skipped
      const driverTrainingScore = calculateDriverTrainingScore(driver);
      
      // Calculate average for this driver (adjust divisor based on whether DASH was skipped)
      const divisor = noDashReport ? 4 : 5;
      const driverScore = Math.round((mvrScore + licenseScore + convictionsScore + dashScore + driverTrainingScore) / divisor);
      
      // Ensure individual driver score doesn't exceed 100%
      const cappedDriverScore = Math.min(driverScore, 100);
      totalScore += cappedDriverScore;
      driverCount++;
    });
    
    // Return average across all drivers, capped at 100%
    const averageScore = driverCount > 0 ? Math.round(totalScore / driverCount) : 0;
    return Math.min(averageScore, 100);
  };

  // Calculate MVR match score
  const calculateMVRScore = (driver) => {
    const mvrValidation = driver.mvr_validation;
    if (!mvrValidation || mvrValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = mvrValidation.matches.length + mvrValidation.critical_errors.length;
    const matches = mvrValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    // Calculate score: matches get full points, critical errors get no points, warnings don't affect score
    const score = (matches / totalChecks) * 100;
    return Math.round(score);
  };

  // Calculate DASH match score
  const calculateDASHScore = (driver) => {
    // If DASH validation was skipped, return full score
    if (noDashReport) return 100;
    
    const dashValidation = driver.dash_validation;
    if (!dashValidation || dashValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = dashValidation.matches.length + dashValidation.critical_errors.length;
    const matches = dashValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    // Calculate score: matches get full points, critical errors get no points, warnings don't affect score
    const score = (matches / totalChecks) * 100;
    return Math.round(score);
  };

  // Calculate License Progression score
  const calculateLicenseProgressionScore = (driver) => {
    const licenseValidation = driver.license_progression_validation;
    if (!licenseValidation || licenseValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = licenseValidation.matches.length + licenseValidation.critical_errors.length;
    const matches = licenseValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    // Calculate score: matches get full points, critical errors get no points, warnings don't affect score
    const score = (matches / totalChecks) * 100;
    return Math.round(score);
  };

  // Calculate Convictions score
  const calculateConvictionsScore = (driver) => {
    const convictionsValidation = driver.convictions_validation;
    if (!convictionsValidation || convictionsValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = convictionsValidation.matches.length + convictionsValidation.critical_errors.length;
    const matches = convictionsValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    // Calculate score: matches get full points, critical errors get no points, warnings don't affect score
    const score = (matches / totalChecks) * 100;
    return Math.round(score);
  };

  // Calculate Driver Training score
  const calculateDriverTrainingScore = (driver) => {
    const driverTrainingValidation = driver.driver_training_validation;
    if (!driverTrainingValidation || driverTrainingValidation.status === 'NOT_FOUND') return 0;
    
    const totalChecks = driverTrainingValidation.matches.length + driverTrainingValidation.critical_errors.length;
    const matches = driverTrainingValidation.matches.length;
    
    if (totalChecks === 0) return 0;
    
    // Calculate score: matches get full points, critical errors get no points, warnings don't affect score
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

  // Download PDF report (high-quality image-based)
  const downloadPDF = async () => {
    if (!reportRef.current) return;

    // High-quality image-based PDF for better visual appearance
    const canvas = await html2canvas(reportRef.current, {
      scale: 2, // Increased scale for better quality
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      logging: false,
      imageTimeout: 0,
      removeContainer: true,
      width: reportRef.current.scrollWidth,
      height: reportRef.current.scrollHeight,
      scrollX: 0,
      scrollY: 0,
      windowWidth: reportRef.current.scrollWidth,
      windowHeight: reportRef.current.scrollHeight
    });

    const imgData = canvas.toDataURL('image/png', 1.0); // Use PNG for maximum quality
    const pdf = new jsPDF('p', 'mm', 'a4');
    const imgWidth = 210;
    const pageHeight = 295;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;

    let position = 0;

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight, undefined, 'MEDIUM'); // Use MEDIUM compression for balance
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight, undefined, 'MEDIUM');
      heightLeft -= pageHeight;
    }

    const timestamp = new Date().toISOString().split('T')[0];
    pdf.save(`validation-report-${timestamp}.pdf`);
  };

  // Download High-Quality PDF report (maximum quality for debugging)
  const downloadHighQualityPDF = async () => {
    if (!reportRef.current) return;

    // Balanced quality settings for readable debugging
    const canvas = await html2canvas(reportRef.current, {
      scale: 2, // Good balance between quality and size
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      logging: false,
      imageTimeout: 0,
      removeContainer: true,
      width: reportRef.current.scrollWidth,
      height: reportRef.current.scrollHeight,
      scrollX: 0,
      scrollY: 0,
      windowWidth: reportRef.current.scrollWidth,
      windowHeight: reportRef.current.scrollHeight
    });

    const imgData = canvas.toDataURL('image/jpeg', 0.9); // Use JPEG with 90% quality for smaller size
    const pdf = new jsPDF('p', 'mm', 'a4');
    const imgWidth = 210;
    const pageHeight = 295;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;

    let position = 0;

    pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight, undefined, 'FAST'); // Use FAST compression
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight, undefined, 'FAST');
      heightLeft -= pageHeight;
    }

    const timestamp = new Date().toISOString().split('T')[0];
    pdf.save(`validation-report-HIGH-QUALITY-${timestamp}.pdf`);
  };

  const overallScore = calculateOverallScore();
  const statusIndicator = getStatusIndicator(overallScore);

  return (
    <div className="space-y-6">
      {/* Report Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">Validation Report</h2>
              <p className="text-gray-600">Vieira Insurance Quality Control System</p>
            </div>
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

            <button
              onClick={downloadHighQualityPDF}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              High-Quality PDF
            </button>
          </div>
        </div>

        {/* Company Info and Timestamp */}
        <div className="flex justify-between items-center py-4 border-t border-gray-200">
          <div className="flex items-center">
            <Building className="w-5 h-5 text-blue-600 mr-2" />
            <span className="font-semibold text-gray-900">Vieira Insurance Quality Control System</span>
          </div>
          <div className="flex items-center text-gray-600">
            <Clock className="w-4 h-4 mr-2" />
            <span>{new Date().toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Raw JSON Toggle */}
      {showRawJson && (
        <div className="bg-gray-900 rounded-xl p-4 mb-6">
          <pre className="text-green-400 text-sm overflow-auto max-h-96">
            {JSON.stringify(validationData, null, 2)}
          </pre>
        </div>
      )}

      {/* Main Report Content */}
      <div ref={reportRef} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        {/* Validation Summary Section */}
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Validation Summary</h3>
          
          {/* Overall Score */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-6 border border-blue-100">
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
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
              <div className="flex items-center mb-3">
                <FileText className="w-6 h-6 text-blue-600 mr-2" />
                <h5 className="font-semibold text-gray-900">MVR vs Quote</h5>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {validationData.drivers?.length > 0 ? 
                  Math.round(validationData.drivers.reduce((sum, driver) => sum + calculateMVRScore(driver), 0) / validationData.drivers.length) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Critical field validation</div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
              <div className="flex items-center mb-3">
                <TrendingUp className="w-6 h-6 text-purple-600 mr-2" />
                <h5 className="font-semibold text-gray-900">License Progression</h5>
              </div>
              <div className="text-2xl font-bold text-purple-600">
                {validationData.drivers?.length > 0 ? 
                  Math.round(validationData.drivers.reduce((sum, driver) => sum + calculateLicenseProgressionScore(driver), 0) / validationData.drivers.length) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">G1/G2/G date logic</div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
              <div className="flex items-center mb-3">
                <Gavel className="w-6 h-6 text-orange-600 mr-2" />
                <h5 className="font-semibold text-gray-900">Convictions</h5>
              </div>
              <div className="text-2xl font-bold text-orange-600">
                {validationData.drivers?.length > 0 ? 
                  Math.round(validationData.drivers.reduce((sum, driver) => sum + calculateConvictionsScore(driver), 0) / validationData.drivers.length) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Conviction matching</div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
              <div className="flex items-center mb-3">
                <Shield className="w-6 h-6 text-green-600 mr-2" />
                <h5 className="font-semibold text-gray-900">DASH vs Quote</h5>
              </div>
              <div className="text-2xl font-bold text-green-600">
                {noDashReport ? 100 : 
                  validationData.drivers?.length > 0 ? 
                    Math.round(validationData.drivers.reduce((sum, driver) => sum + calculateDASHScore(driver), 0) / validationData.drivers.length) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {noDashReport ? 'Validation skipped' : 'Claims and policy validation'}
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
              <div className="flex items-center mb-3">
                <Calendar className="w-6 h-6 text-indigo-600 mr-2" />
                <h5 className="font-semibold text-gray-900">Driver Training</h5>
              </div>
              <div className="text-2xl font-bold text-indigo-600">
                {validationData.drivers?.length > 0 ? 
                  Math.round(validationData.drivers.reduce((sum, driver) => sum + calculateDriverTrainingScore(driver), 0) / validationData.drivers.length) : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">DTC attachment reminders</div>
            </div>
          </div>
        </div>

        {/* Detailed Comparison Breakdown */}
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Detailed Comparison Breakdown</h3>
          
          {validationData.drivers?.map((driver, driverIndex) => (
            <div key={driverIndex} className="mb-8">
              <div className="bg-gray-50 rounded-xl p-4 mb-4">
                <div className="flex items-center space-x-3">
                  <User className="w-6 h-6 text-gray-600" />
                  <div className="flex-1">
                    <h4 className="text-xl font-semibold text-gray-900">{driver.driver_name}</h4>
                    <p className="text-gray-600">License: {driver.driver_license}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    {/* Individual Driver Score */}
                    <div className="text-right">
                      <div className="text-sm text-gray-600">Driver Score</div>
                      <div className="text-lg font-bold text-blue-600">
                        {(() => {
                          const mvrScore = calculateMVRScore(driver);
                          const licenseScore = calculateLicenseProgressionScore(driver);
                          const convictionsScore = calculateConvictionsScore(driver);
                          const dashScore = noDashReport ? 100 : calculateDASHScore(driver);
                          const driverTrainingScore = calculateDriverTrainingScore(driver);
                          
                          const divisor = noDashReport ? 4 : 5;
                          const driverScore = Math.round((mvrScore + licenseScore + convictionsScore + dashScore + driverTrainingScore) / divisor);
                          return Math.min(driverScore, 100);
                        })()}%
                      </div>
                    </div>
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
              {driver.mvr_validation && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-blue-600" />
                    MVR Validation ({calculateMVRScore(driver)}%)
                    {driver.mvr_validation.status === 'NOT_FOUND' && (
                      <span className="ml-2 text-sm text-red-600 font-medium">(No MVR found for this driver)</span>
                    )}
                  </h3>
                  {driver.mvr_validation.status === 'NOT_FOUND' ? (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                      <div className="flex items-center">
                        <XCircle className="w-5 h-5 text-red-600 mr-2" />
                        <span className="text-red-800 font-medium">No MVR report found for driver {driver.driver_name} (License: {driver.driver_license})</span>
                      </div>
                      <p className="text-red-600 text-sm mt-2">Please ensure you have uploaded the correct MVR report for this driver.</p>
                    </div>
                  ) : (
                    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200 bg-gray-50">
                        <div className="px-4 py-3 font-medium text-gray-700">Field</div>
                        <div className="px-4 py-3 font-medium text-gray-700">Comparison</div>
                        <div className="px-4 py-3 font-medium text-gray-700">Status</div>
                      </div>
                      
                      {/* Name Check */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                        <div className="px-4 py-3 text-gray-700">Name</div>
                        <div className="px-4 py-3 text-gray-600">
                          {driver.mvr_validation.matches.find(m => m.includes('Name matches'))?.split('Name matches: ')[1] || 
                           driver.mvr_validation.warnings.find(w => w.includes('Name format difference'))?.split('Name format difference: ')[1] ||
                           driver.mvr_validation.warnings.find(w => w.includes('Name mismatch'))?.split('Name mismatch: ')[1] ||
                           driver.mvr_validation.critical_errors.find(e => e.includes('Name mismatch'))?.split('Name mismatch: ')[1] || 'N/A'}
                        </div>
                        <div className="px-4 py-3">
                          {driver.mvr_validation.matches.some(m => m.includes('Name matches')) ? 
                            getSeverityBadge('match') : 
                            driver.mvr_validation.warnings.some(w => w.includes('Name format difference') || w.includes('Name mismatch')) ?
                            getSeverityBadge('warning') : getSeverityBadge('critical')}
                        </div>
                      </div>

                      {/* License Number Check */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                        <div className="px-4 py-3 text-gray-700">License Number</div>
                        <div className="px-4 py-3 text-gray-600">
                          {driver.mvr_validation.matches.find(m => m.includes('License number matches'))?.split('License number matches: ')[1] || 
                           driver.mvr_validation.critical_errors.find(e => e.includes('License number mismatch'))?.split('License number mismatch: ')[1] || 'N/A'}
                        </div>
                        <div className="px-4 py-3">
                          {driver.mvr_validation.matches.some(m => m.includes('License number matches')) ? 
                            getSeverityBadge('match') : getSeverityBadge('critical')}
                        </div>
                      </div>

                      {/* Address Check */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                        <div className="px-4 py-3 text-gray-700">Address</div>
                        <div className="px-4 py-3 text-gray-600">
                          {driver.mvr_validation.matches.find(m => m.includes('Address matches'))?.split('Address matches: ')[1] || 
                           driver.mvr_validation.critical_errors.find(e => e.includes('Address mismatch'))?.split('Address mismatch: ')[1] || 'N/A'}
                        </div>
                        <div className="px-4 py-3">
                          {driver.mvr_validation.matches.some(m => m.includes('Address matches')) ? 
                            getSeverityBadge('match') : getSeverityBadge('critical')}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* License Progression Validation Section */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-purple-600" />
                  License Progression Validation ({calculateLicenseProgressionScore(driver)}%)
                  {driver.license_progression_validation?.status === 'NOT_FOUND' && (
                    <span className="ml-2 text-sm text-red-600 font-medium">(No MVR found for this driver)</span>
                  )}
                </h5>
                {driver.license_progression_validation?.status === 'NOT_FOUND' ? (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                    <div className="flex items-center">
                      <XCircle className="w-5 h-5 text-red-600 mr-2" />
                      <span className="text-red-800 font-medium">License progression validation requires MVR data</span>
                    </div>
                    <p className="text-red-600 text-sm mt-2">No MVR report found for this driver. License progression cannot be validated without MVR data.</p>
                  </div>
                ) : (
                  <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                                         {/* Check if this is a pre-April 1, 1994 license */}
                     {driver.license_progression_validation.matches.some(m => m.includes('Pre-April 1, 1994 license detected')) ? (
                       <div className="bg-blue-50 border-b border-blue-200 p-4">
                         <div className="flex items-center">
                           <AlertTriangle className="w-5 h-5 text-blue-600 mr-2" />
                           <span className="text-blue-800 font-medium">Pre-April 1, 1994 License Detected</span>
                         </div>
                         <p className="text-blue-600 text-sm mt-1">
                           This driver's license was issued before April 1, 1994. G1 and G2 license classes did not exist at that time. 
                           The issue date becomes the G date, and G1/G2 dates are not required.
                         </p>
                       </div>
                     ) : null}
                     

                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-0">
                      <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">License Stage</div>
                      <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Calculated Date</div>
                      <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Quote Date</div>
                      <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Status</div>
                    </div>
                    
                                         {/* G1 Date Check - Only show for post-April 1, 1994 licenses */}
                     {!driver.license_progression_validation.matches.some(m => m.includes('Pre-April 1, 1994 license detected')) && (
                       <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                         <div className="px-4 py-3 text-gray-700 font-medium">G1 Date</div>
                         <div className="px-4 py-3 text-gray-600">
                           {driver.license_progression_validation.matches.find(m => m.includes('G1 date matches'))?.split('Calculated \'')[1]?.split('\' vs')[0] || 
                            driver.license_progression_validation.critical_errors.find(e => e.includes('G1 date mismatch'))?.split('Calculated \'')[1]?.split('\' vs')[0] || 'N/A'}
                         </div>
                         <div className="px-4 py-3 text-gray-600">
                           {driver.license_progression_validation.matches.find(m => m.includes('G1 date matches'))?.split('Quote \'')[1]?.split('\'')[0] || 
                            driver.license_progression_validation.critical_errors.find(e => e.includes('G1 date mismatch'))?.split('Quote \'')[1]?.split('\'')[0] || 'N/A'}
                         </div>
                         <div className="px-4 py-3">
                           {driver.license_progression_validation.matches.some(m => m.includes('G1 date matches')) ? 
                             getSeverityBadge('match') : getSeverityBadge('critical')}
                         </div>
                       </div>
                     )}

                                         {/* G2 Date Check - Only show for post-April 1, 1994 licenses */}
                     {!driver.license_progression_validation.matches.some(m => m.includes('Pre-April 1, 1994 license detected')) && (
                       <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                         <div className="px-4 py-3 text-gray-700 font-medium">G2 Date</div>
                         <div className="px-4 py-3 text-gray-600">
                           {driver.license_progression_validation.matches.find(m => m.includes('G2 date matches'))?.split('Calculated \'')[1]?.split('\' vs')[0] || 
                            driver.license_progression_validation.critical_errors.find(e => e.includes('G2 date mismatch'))?.split('Calculated \'')[1]?.split('\' vs')[0] || 'N/A'}
                         </div>
                         <div className="px-4 py-3 text-gray-600">
                           {driver.license_progression_validation.matches.find(m => m.includes('G2 date matches'))?.split('Quote \'')[1]?.split('\'')[0] || 
                            driver.license_progression_validation.critical_errors.find(e => e.includes('G2 date mismatch'))?.split('Quote \'')[1]?.split('\'')[0] || 'N/A'}
                         </div>
                         <div className="px-4 py-3">
                           {driver.license_progression_validation.matches.some(m => m.includes('G2 date matches')) ? 
                             getSeverityBadge('match') : getSeverityBadge('critical')}
                         </div>
                       </div>
                     )}

                    {/* G Date Check - Show for all licenses */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-0 border-t border-gray-200">
                      <div className="px-4 py-3 text-gray-700 font-medium">G Date</div>
                      <div className="px-4 py-3 text-gray-600">
                        {driver.license_progression_validation.matches.find(m => m.includes('G date matches'))?.split('Expected \'')[1]?.split('\' vs')[0] || 
                         driver.license_progression_validation.matches.find(m => m.includes('G date matches'))?.split('Calculated \'')[1]?.split('\' vs')[0] || 
                         driver.license_progression_validation.critical_errors.find(e => e.includes('G date mismatch'))?.split('Expected \'')[1]?.split('\' vs')[0] || 
                         driver.license_progression_validation.critical_errors.find(e => e.includes('G date mismatch'))?.split('Calculated \'')[1]?.split('\' vs')[0] || 'N/A'}
                      </div>
                      <div className="px-4 py-3 text-gray-600">
                        {driver.license_progression_validation.matches.find(m => m.includes('G date matches'))?.split('Quote \'')[1]?.split('\'')[0] || 
                         driver.license_progression_validation.critical_errors.find(e => e.includes('G date mismatch'))?.split('Quote \'')[1]?.split('\'')[0] || 'N/A'}
                      </div>
                      <div className="px-4 py-3">
                        {driver.license_progression_validation.matches.some(m => m.includes('G date matches')) ? 
                          getSeverityBadge('match') : getSeverityBadge('critical')}
                      </div>
                    </div>

                                         {/* Show warnings for pre-April 1, 1994 licenses if G1/G2 dates were provided */}
                     {driver.license_progression_validation.warnings.some(w => w.includes('not required for pre-April 1, 1994 licenses')) && (
                       <div className="bg-yellow-50 border-t border-yellow-200 p-4">
                         <div className="flex items-center">
                           <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
                           <span className="text-yellow-800 font-medium">Optional Information Provided</span>
                         </div>
                         <div className="text-yellow-600 text-sm mt-1">
                           {driver.license_progression_validation.warnings
                             .filter(w => w.includes('not required for pre-April 1, 1994 licenses'))
                             .map((warning, index) => (
                               <div key={index}>{warning}</div>
                             ))}
                         </div>
                       </div>
                     )}
                  </div>
                )}
              </div>

              {/* Convictions Validation Section */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Gavel className="w-5 h-5 mr-2 text-orange-600" />
                  Convictions Validation ({calculateConvictionsScore(driver)}%)
                </h5>
                <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
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

              {/* Driver Training Validation Section */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Calendar className="w-5 h-5 mr-2 text-indigo-600" />
                  Driver Training Validation ({calculateDriverTrainingScore(driver)}%)
                </h5>
                <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Training Status</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Requirement</div>
                    <div className="bg-gray-50 px-4 py-3 font-medium text-gray-900">Status</div>
                  </div>
                  
                  {driver.driver_training_validation?.matches.map((match, index) => (
                    <div key={index} className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                      <div className="px-4 py-3 text-gray-700">
                        {match.includes('Driver training detected') ? 'Yes' : 
                         match.includes('No driver training required') ? 'No' : 'Unknown'}
                      </div>
                      <div className="px-4 py-3 text-gray-600">
                        {match.includes('DTC attachment reminder') ? 'DTC Required' : 
                         match.includes('No driver training required') ? 'No DTC Required' : 'Check Required'}
                      </div>
                      <div className="px-4 py-3">
                        {getSeverityBadge('match')}
                      </div>
                    </div>
                  ))}
                  
                  {driver.driver_training_validation?.warnings.map((warning, index) => (
                    <div key={index} className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                      <div className="px-4 py-3 text-gray-700">Yes</div>
                      <div className="px-4 py-3 text-gray-600">DTC Required</div>
                      <div className="px-4 py-3">
                        {getSeverityBadge('warning')}
                      </div>
                    </div>
                  ))}
                  
                  {driver.driver_training_validation?.critical_errors.map((error, index) => (
                    <div key={index} className="grid grid-cols-1 md:grid-cols-3 gap-0 border-t border-gray-200">
                      <div className="px-4 py-3 text-gray-700">Error</div>
                      <div className="px-4 py-3 text-gray-600">{error}</div>
                      <div className="px-4 py-3">
                        {getSeverityBadge('critical')}
                      </div>
                    </div>
                  ))}
                  
                  {(!driver.driver_training_validation || 
                    (driver.driver_training_validation.matches.length === 0 && 
                     driver.driver_training_validation.critical_errors.length === 0 && 
                     driver.driver_training_validation.warnings.length === 0)) && (
                    <div className="px-4 py-3 text-gray-500 text-center">
                      No driver training data available for validation
                    </div>
                  )}
                </div>
              </div>

                  {/* DASH Validation Section */}
                  {!noDashReport && driver.dash_validation && (
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">DASH Validation</h3>
                      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200 bg-gray-50">
                          <div className="px-4 py-3 font-medium text-gray-700">Field</div>
                          <div className="px-4 py-3 font-medium text-gray-700">Comparison</div>
                          <div className="px-4 py-3 font-medium text-gray-700">Status</div>
                        </div>
                        
                        {/* Name Check */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                          <div className="px-4 py-3 text-gray-700">Name</div>
                          <div className="px-4 py-3 text-gray-600">
                            {driver.dash_validation.matches.find(m => m.includes('Name matches'))?.split('Name matches: ')[1] || 
                             driver.dash_validation.warnings.find(w => w.includes('Name format difference'))?.split('Name format difference: ')[1] ||
                             driver.dash_validation.warnings.find(w => w.includes('Name mismatch'))?.split('Name mismatch: ')[1] ||
                             driver.dash_validation.critical_errors.find(e => e.includes('Name mismatch'))?.split('Name mismatch: ')[1] || 'N/A'}
                          </div>
                          <div className="px-4 py-3">
                            {driver.dash_validation.matches.some(m => m.includes('Name matches')) ? 
                              getSeverityBadge('match') : 
                              driver.dash_validation.warnings.some(w => w.includes('Name format difference') || w.includes('Name mismatch')) ?
                              getSeverityBadge('warning') : getSeverityBadge('critical')}
                          </div>
                        </div>

                        {/* License Number Check */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                          <div className="px-4 py-3 text-gray-700">License Number</div>
                          <div className="px-4 py-3 text-gray-600">
                            {driver.dash_validation.matches.find(m => m.includes('License number matches'))?.split('License number matches: ')[1] || 
                             driver.dash_validation.critical_errors.find(e => e.includes('License number mismatch'))?.split('License number mismatch: ')[1] || 'N/A'}
                          </div>
                          <div className="px-4 py-3">
                            {driver.dash_validation.matches.some(m => m.includes('License number matches')) ? 
                              getSeverityBadge('match') : getSeverityBadge('critical')}
                          </div>
                        </div>

                        {/* Date of Birth Check */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                          <div className="px-4 py-3 text-gray-700">Date of Birth</div>
                          <div className="px-4 py-3 text-gray-600">
                            {driver.dash_validation.matches.find(m => m.includes('Date of birth matches'))?.split('Date of birth matches: ')[1] || 
                             driver.dash_validation.critical_errors.find(e => e.includes('Date of birth mismatch'))?.split('Date of birth mismatch: ')[1] || 'N/A'}
                          </div>
                          <div className="px-4 py-3">
                            {driver.dash_validation.matches.some(m => m.includes('Date of birth matches')) ? 
                              getSeverityBadge('match') : getSeverityBadge('critical')}
                          </div>
                        </div>

                        {/* First Policy Check */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                          <div className="px-4 py-3 text-gray-700">First Policy Ever Held</div>
                          <div className="px-4 py-3 text-gray-600">
                            {driver.dash_validation.matches.find(m => m.includes('First policy ever held'))?.split('First policy ever held: ')[1] || 'N/A'}
                          </div>
                          <div className="px-4 py-3">
                            {driver.dash_validation.matches.some(m => m.includes('First policy ever held')) ? 
                              getSeverityBadge('match') : getSeverityBadge('warning')}
                          </div>
                        </div>

                        {/* Policy Gaps Check */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                          <div className="px-4 py-3 text-gray-700">Policy Gaps</div>
                          <div className="px-4 py-3 text-gray-600">
                            {driver.dash_validation.warnings.find(w => w.includes('Policy gap detected'))?.split('Policy gap detected: ')[1] || 'No gaps found'}
                          </div>
                          <div className="px-4 py-3">
                            {driver.dash_validation.warnings.some(w => w.includes('Policy gap detected')) ? 
                              getSeverityBadge('warning') : getSeverityBadge('match')}
                          </div>
                        </div>

                        {/* Claims History Check */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border-b border-gray-200">
                          <div className="px-4 py-3 text-gray-700">Claims History</div>
                          <div className="px-4 py-3 text-gray-600">
                            {(() => {
                              const claimsMessages = driver.dash_validation.matches.filter(m => 
                                m.includes('claim') || m.includes('Claim')
                              );
                              if (claimsMessages.length > 0) {
                                return claimsMessages.join('; ');
                              } else if (driver.dash_validation.matches.some(m => m.includes('No claims found in DASH'))) {
                                return 'No claims found';
                              } else {
                                return 'N/A';
                              }
                            })()}
                          </div>
                          <div className="px-4 py-3">
                            {driver.dash_validation.matches.some(m => m.includes('claim') || m.includes('Claim')) || 
                             driver.dash_validation.matches.some(m => m.includes('No claims found in DASH')) ? 
                              getSeverityBadge('match') : getSeverityBadge('critical')}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* DASH Validation Skipped Message */}
                  {noDashReport && (
                    <div className="mb-6">
                      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                        <div className="flex items-start space-x-3">
                          <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                          <div>
                            <h3 className="text-lg font-semibold text-yellow-900 mb-2">DASH Validation Skipped</h3>
                            <p className="text-yellow-700">
                              DASH report validation was skipped for this application as indicated by the user. Only MVR and quote information was validated.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

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
                        <div key={index} className="bg-red-50 border border-red-200 rounded-xl p-3">
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
                        <div key={index} className="bg-orange-50 border border-orange-200 rounded-xl p-3">
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
                        <div key={index} className="bg-green-50 border border-green-200 rounded-xl p-3">
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