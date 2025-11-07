/**
 * DD Progress Overview Component
 * Displays high-level DD completion status with progress bars by category
 */
import React from 'react';
import { CheckCircle, AlertCircle, Clock, FileText } from 'lucide-react';

interface CategoryProgress {
  total: number;
  completed: number;
}

interface DDProgressData {
  total_items: number;
  completed_items: number;
  completion_percentage: number;
  by_category: {
    [key: string]: CategoryProgress;
  };
}

interface DDProgressOverviewProps {
  data: DDProgressData;
  loading?: boolean;
}

const DDProgressOverview: React.FC<DDProgressOverviewProps> = ({ data, loading = false }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-6 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  const categories = Object.entries(data.by_category || {});

  const getStatusColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-green-500';
    if (percentage >= 70) return 'bg-blue-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusIcon = (percentage: number) => {
    if (percentage >= 90) return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (percentage >= 70) return <Clock className="w-5 h-5 text-blue-500" />;
    if (percentage >= 50) return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    return <AlertCircle className="w-5 h-5 text-red-500" />;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">DD Progress Overview</h2>
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-gray-500" />
          <span className="text-sm text-gray-600">
            {data.completed_items} of {data.total_items} items
          </span>
        </div>
      </div>

      {/* Overall Progress */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-lg font-semibold text-gray-700">Overall Completion</span>
          <div className="flex items-center space-x-2">
            {getStatusIcon(data.completion_percentage)}
            <span className="text-2xl font-bold text-gray-900">
              {data.completion_percentage.toFixed(1)}%
            </span>
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className={`h-4 rounded-full transition-all duration-500 ${getStatusColor(
              data.completion_percentage
            )}`}
            style={{ width: `${data.completion_percentage}%` }}
          ></div>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Progress by Category</h3>
        {categories.map(([category, progress]) => {
          const percentage = progress.total > 0
            ? (progress.completed / progress.total) * 100
            : 0;

          return (
            <div key={category} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(percentage)}
                  <span className="font-medium text-gray-700">{category}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-600">
                    {progress.completed}/{progress.total}
                  </span>
                  <span className="text-sm font-semibold text-gray-900 w-12 text-right">
                    {percentage.toFixed(0)}%
                  </span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${getStatusColor(
                    percentage
                  )}`}
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Status Legend */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span className="text-gray-600">≥90%</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-blue-500 rounded"></div>
              <span className="text-gray-600">70-89%</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-yellow-500 rounded"></div>
              <span className="text-gray-600">50-69%</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span className="text-gray-600">&lt;50%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DDProgressOverview;
