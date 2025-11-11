/**
 * BottleneckChart Component
 * Displays bottleneck periods as a bar chart
 */

'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

export interface BottleneckPeriod {
  start_time: string;
  end_time: string;
  severity: string;
  duration_seconds: number;
  peak_person_count: number;
  average_person_count: number;
  severity_score?: number;
}

export interface BottleneckChartProps {
  /** Bottleneck periods data */
  data: BottleneckPeriod[];
  /** Chart height in pixels */
  height?: number;
  /** Custom class name */
  className?: string;
}

/**
 * Get color based on severity
 */
function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return '#dc2626'; // red-600
    case 'high':
      return '#f59e0b'; // amber-500
    case 'medium':
      return '#eab308'; // yellow-500
    case 'low':
      return '#10b981'; // green-500
    default:
      return '#6b7280'; // gray-500
  }
}

/**
 * Custom tooltip for the chart
 */
function CustomTooltip({ active, payload }: {
  active?: boolean;
  payload?: Array<{
    payload: BottleneckPeriod & { timeRange: string };
  }>;
}) {
  if (!active || !payload || !payload.length) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3">
      <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
        {data.timeRange}
      </p>
      <div className="space-y-1 text-sm">
        <div className="flex justify-between gap-4">
          <span className="text-gray-700 dark:text-gray-300">Severity:</span>
          <span
            className="font-medium px-2 py-0.5 rounded text-white"
            style={{ backgroundColor: getSeverityColor(data.severity) }}
          >
            {data.severity}
          </span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-gray-700 dark:text-gray-300">Duration:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {data.duration_seconds.toFixed(1)}s
          </span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-gray-700 dark:text-gray-300">Peak Count:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {data.peak_person_count} people
          </span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-gray-700 dark:text-gray-300">Avg Count:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {data.average_person_count.toFixed(1)} people
          </span>
        </div>
      </div>
    </div>
  );
}

/**
 * BottleneckChart component
 */
export function BottleneckChart({
  data,
  height = 300,
  className = '',
}: BottleneckChartProps): React.ReactElement {
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 dark:text-gray-400">No bottleneck data available</p>
      </div>
    );
  }

  // Transform data for the chart
  const chartData = data.map((item, index) => ({
    ...item,
    timeRange: `${item.start_time} - ${item.end_time}`,
    name: `Period ${index + 1}`,
  }));

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
          <XAxis
            dataKey="name"
            className="text-xs text-gray-600 dark:text-gray-400"
            tick={{ fill: 'currentColor' }}
          />
          <YAxis
            label={{ value: 'Average People Count', angle: -90, position: 'insideLeft' }}
            className="text-xs text-gray-600 dark:text-gray-400"
            tick={{ fill: 'currentColor' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ paddingTop: '10px' }} />
          <Bar dataKey="average_person_count" name="Average Count" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getSeverityColor(entry.severity)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BottleneckChart;
