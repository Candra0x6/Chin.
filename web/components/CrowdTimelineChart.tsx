/**
 * CrowdTimelineChart Component
 * Displays crowd count over time using a line chart
 */

'use client';

import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export interface TimelineDataPoint {
  time: string;
  timestamp: number;
  average: number;
  max: number;
  min: number;
  samples: number;
}

export interface CrowdTimelineChartProps {
  /** Timeline data points */
  data: TimelineDataPoint[];
  /** Chart height in pixels */
  height?: number;
  /** Show area chart instead of line */
  showArea?: boolean;
  /** Custom class name */
  className?: string;
}

/**
 * Custom tooltip for the chart
 */
function CustomTooltip({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{
    value: number;
    name: string;
    color: string;
    dataKey: string;
  }>;
  label?: string;
}) {
  if (!active || !payload || !payload.length) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3">
      <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
        Time: {label}
      </p>
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center justify-between gap-4 text-sm">
          <span className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-700 dark:text-gray-300 capitalize">
              {entry.name}:
            </span>
          </span>
          <span className="font-medium text-gray-900 dark:text-white">
            {entry.value.toFixed(1)} people
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * CrowdTimelineChart component
 */
export function CrowdTimelineChart({
  data,
  height = 300,
  showArea = false,
  className = '',
}: CrowdTimelineChartProps): React.ReactElement {
  if (!data || data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 dark:text-gray-400">No timeline data available</p>
      </div>
    );
  }

  const ChartComponent = showArea ? AreaChart : LineChart;

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <ChartComponent data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
          <XAxis
            dataKey="time"
            className="text-xs text-gray-600 dark:text-gray-400"
            tick={{ fill: 'currentColor' }}
          />
          <YAxis
            label={{ value: 'People Count', angle: -90, position: 'insideLeft' }}
            className="text-xs text-gray-600 dark:text-gray-400"
            tick={{ fill: 'currentColor' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{
              paddingTop: '10px',
            }}
            iconType="line"
          />
          
          {showArea ? (
            <>
              <Area
                type="monotone"
                dataKey="max"
                stroke="#ef4444"
                fill="#fee2e2"
                fillOpacity={0.3}
                name="Maximum"
              />
              <Area
                type="monotone"
                dataKey="average"
                stroke="#3b82f6"
                fill="#dbeafe"
                fillOpacity={0.5}
                name="Average"
              />
              <Area
                type="monotone"
                dataKey="min"
                stroke="#10b981"
                fill="#d1fae5"
                fillOpacity={0.3}
                name="Minimum"
              />
            </>
          ) : (
            <>
              <Line
                type="monotone"
                dataKey="max"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Maximum"
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="average"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ r: 4 }}
                name="Average"
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="min"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Minimum"
                activeDot={{ r: 5 }}
              />
            </>
          )}
        </ChartComponent>
      </ResponsiveContainer>
    </div>
  );
}

export default CrowdTimelineChart;
