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
import { useHospitalStore } from '@/lib/stores/hospitalStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

export interface HospitalAnalytics {
  summary?: string;
  location?: string;
  staffing_analysis?: {
    recommended_nurses?: number;
    predicted_wait_time_minutes?: number;
    probability_waiting?: number;
    system_utilization?: number;
    additional_nurses_needed?: number;
    algorithm?: string;
  };
  bed_analysis?: {
    current_occupancy_rate?: number;
    additional_capacity_needed?: number;
    estimated_beds_needed?: number;
    projected_occupancy_rate?: number;
    urgency_level?: string;
    recommendation?: string;
    algorithm?: string;
  };
  capacity_score?: number;
  critical_alerts?: string[];
  overall_status?: string;
}

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
  /** Hospital analytics data */
  hospitalAnalytics?: HospitalAnalytics | null;
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
    <Card className={cn('shadow-lg border-2 border-gray-700', className)}>
      <CardContent className="flex items-start justify-between pt-6">
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            {label}
          </p>
          <p className="text-3xl font-bold mt-2">
            {value}
          </p>
        </div>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </CardContent>
    </Card>
  );
}

/**
 * Bottleneck card component
 */
function BottleneckCard({ bottleneck }: { bottleneck: Bottleneck }): React.ReactElement {
  const severityColor = getBottleneckSeverityColor(bottleneck.severity);

  return (
    <Card className={cn('border-l-4 py-0', severityColor)}>
      <CardContent className="pt-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-sm font-semibold uppercase tracking-wide">
                {bottleneck.severity} Severity
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Time: {bottleneck.start_time} - {bottleneck.end_time}
            </p>
            <p className="text-sm mt-2">
              Average Count: <span className="font-semibold">{bottleneck.avg_count.toFixed(1)}</span> people
            </p>
            {bottleneck.description && (
              <p className="text-sm text-muted-foreground mt-2">
                {bottleneck.description}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
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
  hospitalAnalytics,
  className = '',
}: ResultPanelProps): React.ReactElement {
  const crowdLevelColor = getCrowdLevelColor(results.crowd_level);
  const { peakCount, availableBeds, availableNurses } = useHospitalStore();
  
  console.log('Hospital Analytics:', hospitalAnalytics);
  
  // Update peak count in store when results change
  React.useEffect(() => {
    if (results.peak_count !== undefined) {
      useHospitalStore.setState({ peakCount: results.peak_count });
      localStorage.setItem('peak_count', results.peak_count.toString());
    }
  }, [results.peak_count]);
  
  return (
    <div className={`w-full ${className}`}>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">
            Analysis Results
          </h2>
          {videoName && (
            <p className="text-sm text-muted-foreground mt-1">
              Video: {videoName}
            </p>
          )}
        </div>
        {onExport && analysisId && (
          <div className="flex gap-2">
            <Button
              onClick={() => onExport('json')}
              variant="outline"
            >
              Export JSON
            </Button>
            <Button
              onClick={() => onExport('summary')}
              variant="outline"
            >
              Export Summary
            </Button>
          </div>
        )}
      </div>

      {/* Crowd Statistics */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4">
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
          <Card className={cn('py-0', crowdLevelColor)}>
            <CardContent className="pt-6">
              <p className="text-sm font-medium opacity-90">Crowd Level</p>
              <p className="text-3xl font-bold mt-2">{results.crowd_level}</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Staffing Recommendations */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4">
          Staffing Recommendations
        </h3>
        <Card className="">
          <CardContent className="">
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
          </CardContent>
        </Card>
      </div>

      {/* Hospital Context Data from Store */}
      {(peakCount > 0 || availableBeds > 0 || availableNurses > 0) && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">
            Hospital Context Summary
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card >
              <CardContent>
                <p className="text-sm font-medium text-cyan-900 dark:text-cyan-100">
                  Peak Count (Current)
                </p>
                <p className="text-4xl font-bold text-cyan-900 dark:text-cyan-100 mt-2">
                  {peakCount}
                </p>
                <p className="text-xs text-cyan-700 dark:text-cyan-300 mt-2">
                  Maximum people detected
                </p>
              </CardContent>
            </Card>
            <Card >
              <CardContent>
                <p className="text-sm font-medium text-emerald-900 dark:text-emerald-100">
                  Available Beds
                </p>
                <p className="text-4xl font-bold text-emerald-900 dark:text-emerald-100 mt-2">
                  {availableBeds}
                </p>
                <p className="text-xs text-emerald-700 dark:text-emerald-300 mt-2">
                  From hospital context
                </p>
              </CardContent>
            </Card>
            <Card >
              <CardContent>
                <p className="text-sm font-medium text-purple-900 dark:text-purple-100">
                  Available Nurses
                </p>
                <p className="text-4xl font-bold text-purple-900 dark:text-purple-100 mt-2">
                  {availableNurses}
                </p>
                <p className="text-xs text-purple-700 dark:text-purple-300 mt-2">
                  From hospital context
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Hospital Context Analytics */}
      {hospitalAnalytics && (
        <div className="mb-6 space-y-6">
          {/* Header with Location */}
          {hospitalAnalytics.location && (
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-linear-to-r from-cyan-500 to-blue-500 rounded-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5.581m0 0H9m0 0h5.581" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold">
                  Hospital Analytics - {hospitalAnalytics.location}
                </h3>
                {hospitalAnalytics.overall_status && (
                  <p className="text-sm text-muted-foreground">
                    Status: <span className="font-medium">{hospitalAnalytics.overall_status}</span>
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Capacity Score and Critical Alerts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {hospitalAnalytics.capacity_score !== undefined && (
              <Card >
                <CardContent>
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-medium text-purple-900 dark:text-purple-100">
                      Capacity Score
                    </p>
                    <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div className="flex items-end gap-2">
                    <p className="text-4xl font-bold text-purple-900 dark:text-purple-100">
                      {hospitalAnalytics.capacity_score.toFixed(1)}
                    </p>
                    <p className="text-sm text-purple-700 dark:text-purple-200 mb-1">/100</p>
                  </div>
                  {/* Score progress bar */}
                  <div className="mt-4">
                    <Progress 
                      value={Math.min(hospitalAnalytics.capacity_score, 100)} 
                      className="bg-purple-200 dark:bg-purple-800 [&>div]:bg-linear-to-r [&>div]:from-purple-600 [&>div]:to-pink-600"
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {hospitalAnalytics.critical_alerts && hospitalAnalytics.critical_alerts.length > 0 && (
              <Alert variant="destructive" className="border-red-200 dark:border-red-800">
                <div className="p-2 bg-red-600 rounded-lg shrink-0">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <AlertTitle className="text-red-900 dark:text-red-100">
                  Critical Alerts ({hospitalAnalytics.critical_alerts.length})
                </AlertTitle>
                <AlertDescription>
                  <ul className="space-y-1">
                    {hospitalAnalytics.critical_alerts.map((alert, idx) => (
                      <li key={idx} className="text-sm text-red-800 dark:text-red-200 flex items-start gap-2">
                        <span className="text-red-600 dark:text-red-400 mt-0.5">⚠</span>
                        <span>{alert}</span>
                      </li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}
          </div>

          {/* Staffing Analysis */}
          {hospitalAnalytics.staffing_analysis && (
            <Card >
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2 text-blue-900 dark:text-blue-100">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  Staffing Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {hospitalAnalytics.staffing_analysis.recommended_nurses !== undefined && (
                    <Card>
                      <CardContent >
                        <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">Recommended</p>
                        <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-1">
                          {hospitalAnalytics.staffing_analysis.recommended_nurses}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Nurses</p>
                      </CardContent>
                    </Card>
                  )}
                  {hospitalAnalytics.staffing_analysis.additional_nurses_needed !== undefined && (
                    <Card >
                      <CardContent >
                        <p className="text-xs text-orange-600 dark:text-orange-400 font-medium">Additional Needed</p>
                        <p className="text-2xl font-bold text-orange-900 dark:text-orange-100 mt-1">
                          {hospitalAnalytics.staffing_analysis.additional_nurses_needed}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Nurses</p>
                      </CardContent>
                    </Card>
                  )}
                  {hospitalAnalytics.staffing_analysis.predicted_wait_time_minutes !== undefined && (
                    <Card >
                      <CardContent >
                        <p className="text-xs text-yellow-600 dark:text-yellow-400 font-medium">Wait Time</p>
                        <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100 mt-1">
                          {hospitalAnalytics.staffing_analysis.predicted_wait_time_minutes.toFixed(1)}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Minutes</p>
                      </CardContent>
                    </Card>
                  )}
                  {hospitalAnalytics.staffing_analysis.system_utilization !== undefined && (
                    <Card >
                      <CardContent >
                        <p className="text-xs text-green-600 dark:text-green-400 font-medium">Utilization</p>
                        <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-1">
                          {(hospitalAnalytics.staffing_analysis.system_utilization * 100).toFixed(1)}%
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">System</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
                {hospitalAnalytics.staffing_analysis.algorithm && (
                  <p className="text-xs text-blue-700 dark:text-blue-300 mt-3 pt-3 border-t border-blue-200 dark:border-blue-700">
                    <span className="font-medium">Algorithm:</span> {hospitalAnalytics.staffing_analysis.algorithm}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Bed Analysis */}
          {hospitalAnalytics.bed_analysis && (
            <Card >
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2 text-emerald-900 dark:text-emerald-100">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12M8 7a2 2 0 100-4H8a2 2 0 000 4zm0 0v10m0-10L4 7m16 0l4 0M4 7a2 2 0 110 4h2m12-4a2 2 0 110 4h-2m0-4v10" />
                  </svg>
                  Bed Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {hospitalAnalytics.bed_analysis.current_occupancy_rate !== undefined && (
                    <Card className="py-0 border-emerald-100 dark:border-emerald-700">
                      <CardContent className="p-3">
                        <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">Occupancy</p>
                        <p className="text-2xl font-bold text-emerald-900 dark:text-emerald-100 mt-1">
                          {(hospitalAnalytics.bed_analysis.current_occupancy_rate * 100).toFixed(1)}%
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Current</p>
                      </CardContent>
                    </Card>
                  )}
                  {hospitalAnalytics.bed_analysis.additional_capacity_needed !== undefined && (
                    <Card >
                      <CardContent >
                        <p className="text-xs text-red-600 dark:text-red-400 font-medium">Capacity Needed</p>
                        <p className="text-2xl font-bold text-red-900 dark:text-red-100 mt-1">
                          {hospitalAnalytics.bed_analysis.additional_capacity_needed}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Beds</p>
                      </CardContent>
                    </Card>
                  )}
                  {hospitalAnalytics.bed_analysis.estimated_beds_needed !== undefined && (
                    <Card >
                      <CardContent>
                        <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">Forecast</p>
                        <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-1">
                          {hospitalAnalytics.bed_analysis.estimated_beds_needed.toFixed(1)}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Beds</p>
                      </CardContent>
                    </Card>
                  )}
                  {hospitalAnalytics.bed_analysis.projected_occupancy_rate !== undefined && (
                    <Card >
                      <CardContent >
                        <p className="text-xs text-purple-600 dark:text-purple-400 font-medium">Projected</p>
                        <p className="text-2xl font-bold text-purple-900 dark:text-purple-100 mt-1">
                          {(hospitalAnalytics.bed_analysis.projected_occupancy_rate * 100).toFixed(1)}%
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Occupancy</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                  {hospitalAnalytics.bed_analysis.urgency_level && (
                    <Card >
                      <CardContent >
                        <p className="text-xs font-medium text-emerald-700 dark:text-emerald-300">Urgency Level</p>
                        <p className="text-sm font-semibold text-emerald-900 dark:text-emerald-100 mt-1">
                          {hospitalAnalytics.bed_analysis.urgency_level}
                        </p>
                      </CardContent>
                    </Card>
                  )}
                  {hospitalAnalytics.bed_analysis.recommendation && (
                    <Card >
                      <CardContent >
                        <p className="text-xs font-medium text-emerald-700 dark:text-emerald-300">Recommendation</p>
                        <p className="text-sm text-emerald-900 dark:text-emerald-100 mt-1">
                          {hospitalAnalytics.bed_analysis.recommendation}
                        </p>
                      </CardContent>
                    </Card>
                  )}
                </div>
                {hospitalAnalytics.bed_analysis.algorithm && (
                  <p className="text-xs text-emerald-700 dark:text-emerald-300 mt-3 pt-3 border-t border-emerald-200 dark:border-emerald-700">
                    <span className="font-medium">Algorithm:</span> {hospitalAnalytics.bed_analysis.algorithm}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Summary */}
          {hospitalAnalytics.summary && (
            <Alert >
              <AlertDescription className="text-sm text-indigo-900 dark:text-indigo-100 leading-relaxed">
                <span className="font-semibold">Summary:</span> {hospitalAnalytics.summary}
              </AlertDescription>
            </Alert>
          )}
        </div>
      )}

      {/* Bottleneck Analysis */}
      {results.bottlenecks && results.bottlenecks.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">
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
          <Alert className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
            <AlertTitle className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
              Peak Congestion Time
            </AlertTitle>
            <AlertDescription className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mt-1">
              {results.peak_congestion_time}
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* AI Insights */}
      {results.ai_insights && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">
            AI Insights
          </h3>
          <Card >
            <CardContent >
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
            </CardContent>
          </Card>
        </div>
      )}

      {/* Data Visualizations */}
      {results.enhanced_analytics?.visualization_data && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">
            📈 Crowd Metrics Over Time
          </h3>
          <Card>
            <CardContent>
              <CrowdTimelineChart
                data={results.enhanced_analytics.visualization_data.chart_data}
                height={350}
              />
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="text-center p-2 bg-muted rounded">
                  <div className="text-muted-foreground">Average</div>
                  <div className="text-lg font-semibold">
                    {results.enhanced_analytics.visualization_data.summary.overall_average.toFixed(1)}
                  </div>
                </div>
                <div className="text-center p-2 bg-muted rounded">
                  <div className="text-muted-foreground">Maximum</div>
                  <div className="text-lg font-semibold">
                    {results.enhanced_analytics.visualization_data.summary.overall_max}
                  </div>
                </div>
                <div className="text-center p-2 bg-muted rounded">
                  <div className="text-muted-foreground">Minimum</div>
                  <div className="text-lg font-semibold">
                    {results.enhanced_analytics.visualization_data.summary.overall_min}
                  </div>
                </div>
                <div className="text-center p-2 bg-muted rounded">
                  <div className="text-muted-foreground">Std Dev</div>
                  <div className="text-lg font-semibold">
                    {results.enhanced_analytics.visualization_data.summary.std_deviation.toFixed(1)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Bottleneck Visualization */}
      {results.enhanced_analytics?.bottleneck_analysis?.bottleneck_periods && results.enhanced_analytics.bottleneck_analysis.bottleneck_periods.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">
            🚨 Bottleneck Periods Comparison
          </h3>
          <Card>
            <CardContent>
              <BottleneckChart
                data={results.enhanced_analytics.bottleneck_analysis.bottleneck_periods}
                height={320}
              />
              <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div className="text-center p-2 bg-muted rounded">
                  <div className="text-muted-foreground">Total Bottlenecks</div>
                  <div className="text-lg font-semibold">
                    {results.enhanced_analytics.bottleneck_analysis.bottlenecks_detected}
                  </div>
                </div>
                <div className="text-center p-2 bg-muted rounded">
                  <div className="text-muted-foreground">Total Duration</div>
                  <div className="text-lg font-semibold">
                    {results.enhanced_analytics.bottleneck_analysis.total_bottleneck_duration_seconds.toFixed(1)}s
                  </div>
                </div>
                <div className="text-center p-2 bg-muted rounded">
                  <div className="text-muted-foreground">Avg During Bottleneck</div>
                  <div className="text-lg font-semibold">
                    {(results.enhanced_analytics.bottleneck_analysis.bottleneck_periods.reduce((sum, b) => sum + b.average_person_count, 0) / results.enhanced_analytics.bottleneck_analysis.bottleneck_periods.length).toFixed(1)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Spatial Distribution */}
      {results.enhanced_analytics?.spatial_distribution && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">
            🗺️ Spatial Distribution Heatmap
          </h3>
          <Card >
            <CardContent >
              <SpatialDistributionChart
                zones={results.enhanced_analytics.spatial_distribution.zones}
                gridSize={results.enhanced_analytics.spatial_distribution.grid_size}
                height={400}
              />
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <Card >
                  <CardContent >
                    <div className="text-muted-foreground mb-1">Distribution Pattern</div>
                    <div className="text-base font-semibold">
                      {results.enhanced_analytics.spatial_distribution.distribution_pattern}
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent>
                    <div className="text-muted-foreground mb-1">Hotspot Zones</div>
                    <div className="text-base font-semibold">
                      {results.enhanced_analytics.spatial_distribution.hotspots.map(h => h.position).join(', ')}
                    </div>
                  </CardContent>
                </Card>
              </div>  
            </CardContent>
          </Card>
        </div>
      )}

      {/* Additional Metadata */}
      {(results.video_duration || results.frames_analyzed || results.detection_confidence) && (
        <div className="mt-6 pt-6 border-t">
          <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
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
