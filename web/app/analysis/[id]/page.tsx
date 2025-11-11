'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ResultPanel, Loader, InlineLoader } from '@/components';
import { getAnalysisResult, getAnalysisStatus } from '@/lib/api';
import type { AnalysisResults, AnalysisStatus } from '@/lib/types';

export default function AnalysisPage() {
  const router = useRouter();
  const params = useParams();
  const analysisId = params.id as string;

  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [videoName, setVideoName] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  // Poll for analysis status
  useEffect(() => {
    if (!analysisId || !isPolling) return;

    const pollStatus = async () => {
      try {
        const statusData = await getAnalysisStatus(analysisId);
        setStatus(statusData);
        setVideoName(statusData.video_name || 'Unknown Video');

        if (statusData.status === 'completed') {
          // Fetch full results
          const resultData = await getAnalysisResult(analysisId);
          
          // The backend returns a different structure, so we need to transform it
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const rawResults = resultData.results as any;
          
          // Transform backend response to match expected AnalysisResults structure
          const transformedResults: AnalysisResults = {
            // Map from statistics and insights objects
            avg_count: rawResults.statistics?.avg_person_count || 0,
            peak_count: rawResults.statistics?.max_person_count || 0,
            total_people: rawResults.statistics?.total_detections || 0,
            crowd_level: rawResults.insights?.crowd_level || 'Low',
            peak_congestion_time: rawResults.insights?.peak_time,
            
            // Staffing recommendations
            suggested_nurses: rawResults.insights?.suggested_nurses || 1,
            reasoning: rawResults.insights?.reasoning,
            
            // Bottlenecks - transform from insights
            bottlenecks: rawResults.insights?.bottlenecks?.map((b: {
              start_time?: string;
              end_time?: string;
              avg_count?: number;
              severity?: string;
              description?: string;
            }) => ({
              start_time: b.start_time || '',
              end_time: b.end_time || '',
              avg_count: b.avg_count || 0,
              severity: b.severity || 'low',
              description: b.description,
            })) || [],
            
            // AI insights
            ai_insights: rawResults.ai_insights ? {
              summary: rawResults.ai_insights.ai_summary || rawResults.ai_insights.summary || '',
              recommendations: rawResults.ai_insights.recommendations || [],
              key_findings: rawResults.ai_insights.key_findings || [],
            } : undefined,
            
            // Enhanced analytics (pass through)
            enhanced_analytics: rawResults.enhanced_analytics,
            
            // Additional metadata
            video_duration: rawResults.video_metadata?.duration_seconds,
            frames_analyzed: rawResults.statistics?.total_frames,
            detection_confidence: rawResults.processing_info?.confidence_threshold,
          };
          
          setResults(transformedResults);
          setIsPolling(false);
        } else if (statusData.status === 'failed') {
          setError(statusData.error_message || 'Analysis failed');
          setIsPolling(false);
        }
      } catch (err) {
        console.error('Error fetching analysis status:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch analysis');
        setIsPolling(false);
      }
    };

    // Initial fetch
    pollStatus();

    // Poll every 3 seconds
    const interval = setInterval(pollStatus, 3000);

    return () => clearInterval(interval);
  }, [analysisId, isPolling]);

  // Handle export
  const handleExport = async (format: 'json' | 'summary') => {
    if (format === 'json' && results) {
      const dataStr = JSON.stringify(results, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analysis_${analysisId}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } else if (format === 'summary' && results) {
      const summary = `
ER Flow Analysis Summary
========================
Video: ${videoName}
Analysis ID: ${analysisId}
Date: ${new Date().toLocaleDateString()}

Crowd Statistics:
- Average Count: ${results.avg_count.toFixed(1)}
- Peak Count: ${results.peak_count}
- Total People: ${results.total_people}
- Crowd Level: ${results.crowd_level}

Staffing Recommendations:
- Suggested Nurses: ${results.suggested_nurses}
${results.reasoning ? `- Reasoning: ${results.reasoning}` : ''}

Bottlenecks:
${results.bottlenecks.map((b, i) => `${i + 1}. ${b.severity.toUpperCase()} (${b.start_time} - ${b.end_time}) - Avg Count: ${b.avg_count}`).join('\n')}

${results.ai_insights ? `AI Insights:
${results.ai_insights.summary}

Recommendations:
${results.ai_insights.recommendations?.map((r, i) => `${i + 1}. ${r}`).join('\n') || 'None'}` : ''}
      `.trim();

      const dataBlob = new Blob([summary], { type: 'text/plain' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analysis_summary_${analysisId}.txt`;
      link.click();
      URL.revokeObjectURL(url);
    }
  };

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Analysis Failed
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error}
          </p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  }

  // Processing state
  if (!results || status?.status === 'processing') {
    const progress = status?.progress || 0;
    return (
      <div className="min-h-screen bg-linear-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        {/* Header */}
        <header className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
          <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  🏥 Chin ER Flow Analyzer
                </h1>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  Processing your video...
                </p>
              </div>
              <button
                onClick={() => router.push('/')}
                className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
              >
                ← Back
              </button>
            </div>
          </div>
        </header>

        {/* Processing Content */}
        <main className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
                <Loader size="large" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Analyzing Video
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                {videoName}
              </p>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                <span>Progress</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-linear-to-r from-blue-500 to-purple-500 h-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Status Message */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <InlineLoader message={status?.message || 'Processing video frames...'} />
              </p>
            </div>

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl mb-2">🎥</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Step 1</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">Video Upload</div>
                <div className="text-xs text-green-600 dark:text-green-400 mt-1">✓ Complete</div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="text-2xl mb-2">🤖</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Step 2</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">AI Analysis</div>
                <div className="text-xs text-blue-600 dark:text-blue-400 mt-1">⏳ In Progress</div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-50">
                <div className="text-2xl mb-2">📊</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Step 3</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">Results</div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">⏸ Pending</div>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Results state
  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                🏥 Analysis Results
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {videoName}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => router.push(`/chat/${analysisId}`)}
                className="rounded-lg px-4 py-2 text-sm font-medium bg-purple-600 text-white hover:bg-purple-700 transition-colors"
              >
                💬 Chat with AI
              </button>
              <button
                onClick={() => router.push('/')}
                className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
              >
                ← Back to Home
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <ResultPanel
          results={results}
          videoName={videoName}
          analysisId={analysisId}
          onExport={handleExport}
        />
      </main>
    </div>
  );
}
