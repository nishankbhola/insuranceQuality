import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, RadialLinearScale, PointElement, LineElement, Filler } from 'chart.js';
import { Pie, Bar, Radar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, RadialLinearScale, PointElement, LineElement, Filler);

const CompactValidationReport = ({ reportData }) => {
  const [report, setReport] = useState(null);

  useEffect(() => {
    if (reportData) {
      setReport(reportData);
    }
  }, [reportData]);

  if (!report) {
    return <div className="text-center p-8">No report data available</div>;
  }

  const { 
    report_metadata, 
    summary_statistics, 
    validation_categories, 
    driver_summaries, 
    charts, 
    key_insights, 
    recommendations 
  } = report;

  // Chart configurations
  const pieChartData = {
    labels: charts.validation_pie_chart.labels,
    datasets: [{
      data: charts.validation_pie_chart.data,
      backgroundColor: charts.validation_pie_chart.colors,
      borderWidth: 2,
      borderColor: '#fff'
    }]
  };

  const barChartData = {
    labels: charts.validation_bar_chart.labels,
    datasets: [{
      label: 'Percentage',
      data: charts.validation_bar_chart.data,
      backgroundColor: charts.validation_bar_chart.colors,
      borderWidth: 1,
      borderColor: '#000'
    }]
  };

  const radarChartData = {
    labels: charts.category_radar_chart.labels,
    datasets: [
      {
        label: 'Pass',
        data: charts.category_radar_chart.pass_data,
        backgroundColor: 'rgba(40, 167, 69, 0.2)',
        borderColor: '#28a745',
        borderWidth: 2,
        pointBackgroundColor: '#28a745'
      },
      {
        label: 'Warning',
        data: charts.category_radar_chart.warning_data,
        backgroundColor: 'rgba(255, 193, 7, 0.2)',
        borderColor: '#ffc107',
        borderWidth: 2,
        pointBackgroundColor: '#ffc107'
      },
      {
        label: 'Fail',
        data: charts.category_radar_chart.fail_data,
        backgroundColor: 'rgba(220, 53, 69, 0.2)',
        borderColor: '#dc3545',
        borderWidth: 2,
        pointBackgroundColor: '#dc3545'
      }
    ]
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PASS': return 'text-green-600 bg-green-100';
      case 'WARNING': return 'text-yellow-600 bg-yellow-100';
      case 'FAIL': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'PASS': return '✓';
      case 'WARNING': return '⚠';
      case 'FAIL': return '✗';
      default: return '?';
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 bg-white">
      {/* Header */}
      <div className="mb-8 border-b pb-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Validation Report</h1>
            <p className="text-gray-600">Generated on {report_metadata.generated_at}</p>
          </div>
          <div className={`px-4 py-2 rounded-lg font-semibold ${getStatusColor(report_metadata.overall_status)}`}>
            {getStatusIcon(report_metadata.overall_status)} {report_metadata.overall_status}
          </div>
        </div>
        <div className="mt-4 grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{report_metadata.total_drivers}</div>
            <div className="text-sm text-gray-600">Total Drivers</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{summary_statistics.validation_rate}%</div>
            <div className="text-sm text-gray-600">Validation Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{summary_statistics.total_critical_errors}</div>
            <div className="text-sm text-gray-600">Critical Errors</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{summary_statistics.total_warnings}</div>
            <div className="text-sm text-gray-600">Warnings</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-center">Validation Status</h3>
          <div className="h-64">
            <Pie data={pieChartData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-center">Validation Rates</h3>
          <div className="h-64">
            <Bar 
              data={barChartData} 
              options={{ 
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100
                  }
                }
              }} 
            />
          </div>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-center">Category Performance</h3>
          <div className="h-64">
            <Radar 
              data={radarChartData} 
              options={{ 
                maintainAspectRatio: false,
                scales: {
                  r: {
                    beginAtZero: true
                  }
                }
              }} 
            />
          </div>
        </div>
      </div>

      {/* Driver Summaries */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Driver Summary</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2 border">Driver Name</th>
                <th className="px-4 py-2 border">License</th>
                <th className="px-4 py-2 border">Status</th>
                <th className="px-4 py-2 border">MVR</th>
                <th className="px-4 py-2 border">DASH</th>
                <th className="px-4 py-2 border">Errors</th>
                <th className="px-4 py-2 border">Warnings</th>
                <th className="px-4 py-2 border">Matches</th>
              </tr>
            </thead>
            <tbody>
              {driver_summaries.map((driver, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-2 border">{driver.name}</td>
                  <td className="px-4 py-2 border font-mono text-sm">{driver.license}</td>
                  <td className="px-4 py-2 border">
                    <span className={`px-2 py-1 rounded text-sm font-semibold ${getStatusColor(driver.status)}`}>
                      {getStatusIcon(driver.status)} {driver.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 border text-center">
                    {driver.mvr_found ? '✓' : '✗'}
                  </td>
                  <td className="px-4 py-2 border text-center">
                    {driver.dash_found ? '✓' : '✗'}
                  </td>
                  <td className="px-4 py-2 border text-center">
                    <span className="text-red-600 font-semibold">{driver.critical_errors}</span>
                  </td>
                  <td className="px-4 py-2 border text-center">
                    <span className="text-yellow-600 font-semibold">{driver.warnings}</span>
                  </td>
                  <td className="px-4 py-2 border text-center">
                    <span className="text-green-600 font-semibold">{driver.matches}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Insights and Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="text-xl font-semibold mb-4 text-blue-800">Key Insights</h3>
          <ul className="space-y-2">
            {key_insights.map((insight, index) => (
              <li key={index} className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span className="text-blue-900">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="bg-green-50 p-6 rounded-lg">
          <h3 className="text-xl font-semibold mb-4 text-green-800">Recommendations</h3>
          <ul className="space-y-2">
            {recommendations.map((rec, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-600 mr-2">•</span>
                <span className="text-green-900">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Category Details */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Validation Categories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(validation_categories).map(([category, results]) => (
            <div key={category} className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">{category}</h4>
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-green-600">Pass:</span>
                  <span className="font-semibold">{results.pass}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-yellow-600">Warning:</span>
                  <span className="font-semibold">{results.warning}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-red-600">Fail:</span>
                  <span className="font-semibold">{results.fail}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CompactValidationReport;
