/**
 * ResultPanel Component
 * Displays analysis results including crowd statistics, bottlenecks, and AI insights
 */

'use client';

import React from 'react';
import type { AnalysisResults, Bottleneck } from '@/lib/types';
import { CrowdTimelineChart } from './CrowdTimelineChart';
import { BottleneckChart } from './BottleneckChart';
import { SpatialDistributionChart } from './SpatialDistributionChart';

export interface ResultPanelProps {
  /** Analysis results to display */
  results: AnalysisResults;
  /** Video name */
  videoName?: string;
  /** Analysis ID for actions */
  analysisId?: string;
  /** Callback for export actions */
  onExport?: (format: 'json' | 'summary') => void;
  /** Custom class name */
  className?: string;
}

/**
 * Get color class based on crowd level
 */
function getCrowdLevelColor(level: string): string {
  switch (level) {
    case 'Low':
      return 'text-green-600 bg-green-100 dark:bg-green-900/30';
    case 'Medium':
      return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30';
    case 'High':
      return 'text-orange-600 bg-orange-100 dark:bg-orange-900/30';
    case 'Very High':
      return 'text-red-600 bg-red-100 dark:bg-red-900/30';
    default:
      return 'text-gray-600 bg-gray-100 dark:bg-gray-900/30';
  }
}

/**
 * Get color class based on bottleneck severity
 */
function getBottleneckSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'high':
      return 'border-red-500 bg-red-50 dark:bg-red-900/20';
    case 'medium':
      return 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20';
    case 'low':
      return 'border-green-500 bg-green-50 dark:bg-green-900/20';
    default:
      return 'border-gray-500 bg-gray-50 dark:bg-gray-900/20';
  }
}

/**
 * Stat card component
 */
function StatCard({
  label,
  value,
  icon,
  className = '',
}: {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  className?: string;
}): React.ReactElement {
  return (
    <div className={`p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {label}
          </p>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
            {value}
          </p>
        </div>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
    </div>
  );
}

/**
 * Bottleneck card component
 */
function BottleneckCard({ bottleneck }: { bottleneck: Bottleneck }): React.ReactElement {
  const severityColor = getBottleneckSeverityColor(bottleneck.severity);

  return (
    <div className={`p-4 rounded-lg border-l-4 ${severityColor}`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold uppercase tracking-wide">
              {bottleneck.severity} Severity
            </span>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Time: {bottleneck.start_time} - {bottleneck.end_time}
          </p>
          <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
            Average Count: <span className="font-semibold">{bottleneck.avg_count.toFixed(1)}</span> people
          </p>
          {bottleneck.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              {bottleneck.description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * ResultPanel component
 */
export function ResultPanel({
  results,
  videoName,
  analysisId,
  onExport,
  className = '',
}: ResultPanelProps): React.ReactElement {
  const crowdLevelColor = getCrowdLevelColor(results.crowd_level);

  return (
    <div className={`w-full max-w-6xl mx-auto ${className}`}>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Analysis Results
          </h2>
          {videoName && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Video: {videoName}
            </p>
          )}
        </div>
        {onExport && analysisId && (
          <div className="flex gap-2">
            <button
              onClick={() => onExport('json')}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Export JSON
            </button>
            <button
              onClick={() => onExport('summary')}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Export Summary
            </button>
          </div>
        )}
      </div>

      {/* Crowd Statistics */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Crowd Statistics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Average Count"
            value={results.avg_count.toFixed(1)}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            }
          />
          <StatCard
            label="Peak Count"
            value={results.peak_count}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            }
          />
          <StatCard
            label="Total People"
            value={results.total_people}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            }
          />
          <div className={`p-6 rounded-lg ${crowdLevelColor}`}>
            <p className="text-sm font-medium opacity-90">Crowd Level</p>
            <p className="text-3xl font-bold mt-2">{results.crowd_level}</p>
          </div>
        </div>
      </div>

      {/* Staffing Recommendations */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Staffing Recommendations
        </h3>
        <div className="p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-600 rounded-lg">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                Suggested Nurses
              </p>
              <p className="text-4xl font-bold text-blue-900 dark:text-blue-100 mt-2">
                {results.suggested_nurses}
              </p>
              {results.reasoning && (
                <p className="text-sm text-blue-800 dark:text-blue-200 mt-3">
                  {results.reasoning}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottleneck Analysis */}
      {results.bottlenecks && results.bottlenecks.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Bottleneck Analysis
          </h3>
          <div className="space-y-3">
            {results.bottlenecks.map((bottleneck, index) => (
              <BottleneckCard key={index} bottleneck={bottleneck} />
            ))}
          </div>
        </div>
      )}

      {/* Peak Congestion Time */}
      {results.peak_congestion_time && (
        <div className="mb-6">
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
              Peak Congestion Time
            </p>
            <p className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mt-1">
              {results.peak_congestion_time}
            </p>
          </div>
        </div>
      )}

      {/* AI Insights */}
      {results.ai_insights && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            AI Insights
          </h3>
          <div className="p-6 bg-linear-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-linear-to-r from-purple-600 to-pink-600 rounded-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-purple-900 dark:text-purple-100 leading-relaxed">
                  {results.ai_insights.summary}
                </p>
                {results.ai_insights.recommendations && results.ai_insights.recommendations.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-semibold text-purple-900 dark:text-purple-100 mb-2">
                      Recommendations:
                    </p>
                    <ul className="space-y-1">
                      {results.ai_insights.recommendations.map((rec, index) => (
                        <li key={index} className="text-sm text-purple-800 dark:text-purple-200 flex items-start gap-2">
                          <span className="text-purple-600 dark:text-purple-400 mt-1">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Data Visualizations */}
      {results.enhanced_analytics?.visualization_data && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            📈 Crowd Metrics Over Time
          </h3>
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <CrowdTimelineChart
              data={results.enhanced_analytics.visualization_data.chart_data}
              height={350}
            />
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400">Average</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {results.enhanced_analytics.visualization_data.summary.overall_average.toFixed(1)}
                </div>
              </div>
              <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400">Maximum</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {results.enhanced_analytics.visualization_data.summary.overall_max}
                </div>
              </div>
              <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400">Minimum</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {results.enhanced_analytics.visualization_data.summary.overall_min}
                </div>
              </div>
              <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400">Std Dev</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {results.enhanced_analytics.visualization_data.summary.std_deviation.toFixed(1)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bottleneck Visualization */}
      {results.enhanced_analytics?.bottleneck_analysis?.bottleneck_periods && results.enhanced_analytics.bottleneck_analysis.bottleneck_periods.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            🚨 Bottleneck Periods Comparison
          </h3>
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <BottleneckChart
              data={results.enhanced_analytics.bottleneck_analysis.bottleneck_periods}
              height={320}
            />
            <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400">Total Bottlenecks</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {results.enhanced_analytics.bottleneck_analysis.bottlenecks_detected}
                </div>
              </div>
              <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400">Total Duration</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {results.enhanced_analytics.bottleneck_analysis.total_bottleneck_duration_seconds.toFixed(1)}s
                </div>
              </div>
              <div className="text-center p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400">Avg During Bottleneck</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {(results.enhanced_analytics.bottleneck_analysis.bottleneck_periods.reduce((sum, b) => sum + b.average_person_count, 0) / results.enhanced_analytics.bottleneck_analysis.bottleneck_periods.length).toFixed(1)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Spatial Distribution */}
      {results.enhanced_analytics?.spatial_distribution && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            🗺️ Spatial Distribution Heatmap
          </h3>
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <SpatialDistributionChart
              zones={results.enhanced_analytics.spatial_distribution.zones}
              gridSize={results.enhanced_analytics.spatial_distribution.grid_size}
              height={400}
            />
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400 mb-1">Distribution Pattern</div>
                <div className="text-base font-semibold text-gray-900 dark:text-white">
                  {results.enhanced_analytics.spatial_distribution.distribution_pattern}
                </div>
              </div>
              <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div className="text-gray-600 dark:text-gray-400 mb-1">Hotspot Zones</div>
                <div className="text-base font-semibold text-gray-900 dark:text-white">
                  {results.enhanced_analytics.spatial_distribution.hotspots.map(h => h.position).join(', ')}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Additional Metadata */}
      {(results.video_duration || results.frames_analyzed || results.detection_confidence) && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-wrap gap-6 text-sm text-gray-600 dark:text-gray-400">
            {results.video_duration && (
              <div>
                <span className="font-medium">Duration:</span> {results.video_duration}s
              </div>
            )}
            {results.frames_analyzed && (
              <div>
                <span className="font-medium">Frames Analyzed:</span> {results.frames_analyzed}
              </div>
            )}
            {results.detection_confidence && (
              <div>
                <span className="font-medium">Confidence:</span> {(results.detection_confidence * 100).toFixed(1)}%
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultPanel;
