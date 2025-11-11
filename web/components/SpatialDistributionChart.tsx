/**
 * SpatialDistributionChart Component
 * Displays spatial distribution of crowd as a heatmap grid
 */

'use client';

import React from 'react';

export interface ZoneData {
  zone_id: string;
  row: number;
  col: number;
  position: string;
  detection_count: number;
  percentage: number;
  density_level: string;
}

export interface SpatialDistributionChartProps {
  /** Zone data for the grid */
  zones: ZoneData[];
  /** Grid dimensions */
  gridSize: {
    rows: number;
    cols: number;
  };
  /** Chart height in pixels */
  height?: number;
  /** Custom class name */
  className?: string;
}

/**
 * Get color based on density level
 */
function getDensityColor(densityLevel: string, percentage: number): {
  bg: string;
  text: string;
  border: string;
} {
  if (percentage === 0) {
    return {
      bg: 'bg-gray-50 dark:bg-gray-800',
      text: 'text-gray-400 dark:text-gray-500',
      border: 'border-gray-200 dark:border-gray-700',
    };
  }

  switch (densityLevel.toLowerCase()) {
    case 'very high':
      return {
        bg: 'bg-red-500',
        text: 'text-white',
        border: 'border-red-600',
      };
    case 'high':
      return {
        bg: 'bg-orange-400',
        text: 'text-white',
        border: 'border-orange-500',
      };
    case 'medium':
      return {
        bg: 'bg-yellow-400',
        text: 'text-gray-900',
        border: 'border-yellow-500',
      };
    case 'low':
      return {
        bg: 'bg-green-400',
        text: 'text-white',
        border: 'border-green-500',
      };
    case 'very low':
      return {
        bg: 'bg-blue-300',
        text: 'text-gray-900',
        border: 'border-blue-400',
      };
    default:
      return {
        bg: 'bg-gray-300',
        text: 'text-gray-800',
        border: 'border-gray-400',
      };
  }
}

/**
 * SpatialDistributionChart component
 */
export function SpatialDistributionChart({
  zones,
  gridSize,
  height = 300,
  className = '',
}: SpatialDistributionChartProps): React.ReactElement {
  if (!zones || zones.length === 0) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500 dark:text-gray-400">No spatial data available</p>
      </div>
    );
  }

  // Create a 2D grid from zones
  const grid: (ZoneData | null)[][] = Array(gridSize.rows)
    .fill(null)
    .map(() => Array(gridSize.cols).fill(null));

  zones.forEach((zone) => {
    if (zone.row < gridSize.rows && zone.col < gridSize.cols) {
      grid[zone.row][zone.col] = zone;
    }
  });

  return (
    <div className={className}>
      <div className="space-y-4">
        {/* Grid */}
        <div
          className="grid gap-2"
          style={{
            gridTemplateColumns: `repeat(${gridSize.cols}, 1fr)`,
            height: height - 80,
          }}
        >
          {grid.map((row, rowIndex) =>
            row.map((zone, colIndex) => {
              if (!zone) {
                return (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    className="border-2 border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800"
                  />
                );
              }

              const colors = getDensityColor(zone.density_level, zone.percentage);

              return (
                <div
                  key={zone.zone_id}
                  className={`border-2 ${colors.border} ${colors.bg} rounded-lg p-2 flex flex-col items-center justify-center transition-all hover:scale-105 cursor-pointer`}
                  title={`${zone.position}: ${zone.detection_count} detections (${zone.percentage.toFixed(1)}%)`}
                >
                  <div className={`text-xs font-medium ${colors.text} mb-1`}>
                    {zone.position.split('-')[1] || zone.position}
                  </div>
                  <div className={`text-lg font-bold ${colors.text}`}>
                    {zone.detection_count}
                  </div>
                  <div className={`text-xs ${colors.text} opacity-90`}>
                    {zone.percentage.toFixed(1)}%
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center justify-center gap-3 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded" />
            <span className="text-gray-700 dark:text-gray-300">No Data</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-blue-300 border border-blue-400 rounded" />
            <span className="text-gray-700 dark:text-gray-300">Very Low</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-400 border border-green-500 rounded" />
            <span className="text-gray-700 dark:text-gray-300">Low</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-400 border border-yellow-500 rounded" />
            <span className="text-gray-700 dark:text-gray-300">Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-orange-400 border border-orange-500 rounded" />
            <span className="text-gray-700 dark:text-gray-300">High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 border border-red-600 rounded" />
            <span className="text-gray-700 dark:text-gray-300">Very High</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SpatialDistributionChart;
