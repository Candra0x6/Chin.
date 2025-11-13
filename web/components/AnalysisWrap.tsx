'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAnalysisResult, getAnalysisStatus } from '@/lib/api';
import type { AnalysisResults, AnalysisStatus } from '@/lib/types';
import { ResultPanel, type HospitalAnalytics } from '@/components/ResultPanel';
import Loader, { InlineLoader } from './Loader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, AlertTriangle, CheckCircle2, Zap } from 'lucide-react';

export default function AnalysisWrap() {
  const router = useRouter();
  const analysisId = localStorage.getItem('analysisId')

  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [hospitalAnalytics, setHospitalAnalytics] = useState<HospitalAnalytics | null>(null);
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
          console.log('Transformed Results:', rawResults);
          
          // Extract hospital analytics if available
          setHospitalAnalytics(rawResults.hospital_analytics || null);
          
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
      <div className="min-h-screen bg-linear-to-br from-destructive/5 via-background to-destructive/10 dark:from-destructive/10 dark:via-background dark:to-destructive/5 flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <Card className="border-destructive/20 shadow-xl animate-fadeIn">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="bg-destructive/10 dark:bg-destructive/20 p-4 rounded-full">
                  <AlertTriangle className="w-8 h-8 text-destructive" />
                </div>
              </div>
              <CardTitle className="text-2xl text-destructive">Analysis Failed</CardTitle>
              <CardDescription className="mt-2">{error}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => router.push('/')}
                className="w-full"
                variant="outline"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Processing state
  if (!results || status?.status === 'processing') {
    const progress = status?.progress || 0;
    return (
      <div className="min-h-screen bg-gray-800">

        {/* Processing Content */}
        <main className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
          <Card className="border-primary/10 shadow-lg overflow-hidden animate-fadeIn">
            {/* Progress Indicator Header */}
            <div className="h-1 bg-linear-to-r from-primary via-primary/50 to-primary/25" 
              style={{ 
                width: `${progress}%`,
                transition: 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)'
              }} 
            />
            
            <CardHeader className="text-center">
              <div className="flex justify-center mb-6">
                <div className="relative">
                  <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl animate-pulse" />
                  <div className="relative bg-primary/10 p-4 rounded-full">
                    <Loader size="large" />
                  </div>
                </div>
              </div>
              <CardTitle className="text-3xl">Analyzing Video</CardTitle>
              <CardDescription className="text-base mt-2">
                {videoName || 'Processing your upload...'}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-8">
              {/* Progress Bar with Percentage */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-foreground">Progress</span>
                  <Badge variant="secondary" className="text-xs">
                    {progress}%
                  </Badge>
                </div>
                <Progress value={progress} className="h-2" />
              </div>

              <Separator className="my-6" />

              {/* Status Message with Alert */}
              <Alert className="border-primary/20 bg-primary/5 dark:bg-primary/10">
                <Zap className="h-4 w-4 text-primary" />
                <AlertDescription>
                  <InlineLoader message={status?.message || 'Processing video frames...'} />
                </AlertDescription>
              </Alert>

              {/* Process Steps with Animation */}
              <div className="space-y-3">
                <p className="text-sm font-medium text-foreground">Processing Steps</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {/* Step 1 */}
                  <div className="group relative p-4 bg-card border border-border/50 rounded-lg hover:border-primary/30 transition-all duration-300 animate-slideIn"
                    style={{ animationDelay: '0s' }}>
                    <div className="flex items-start gap-3">
                      <div className="flex items-center justify-center w-8 h-8 bg-green-500/20 rounded-full shrink-0">
                        <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-muted-foreground font-medium">Step 1</p>
                        <p className="text-sm font-medium text-foreground">Video Upload</p>
                        <p className="text-xs text-green-600 dark:text-green-400 mt-1">✓ Complete</p>
                      </div>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="group relative p-4 bg-card border border-primary/30 rounded-lg shadow-sm shadow-primary/10 transition-all duration-300 animate-slideIn"
                    style={{ animationDelay: '0.1s' }}>
                    <div className="flex items-start gap-3">
                      <div className="flex items-center justify-center w-8 h-8 bg-primary/20 rounded-full shrink-0 animate-spin">
                        <Zap className="w-4 h-4 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-muted-foreground font-medium">Step 2</p>
                        <p className="text-sm font-medium text-foreground">AI Analysis</p>
                        <p className="text-xs text-primary mt-1">⏳ In Progress</p>
                      </div>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="group relative p-4 bg-card border border-border/50 rounded-lg hover:border-primary/30 transition-all duration-300 opacity-60 animate-slideIn"
                    style={{ animationDelay: '0.2s' }}>
                    <div className="flex items-start gap-3">
                      <div className="flex items-center justify-center w-8 h-8 bg-muted rounded-full shrink-0">
                        <Badge variant="outline" className="text-xs">3</Badge>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-muted-foreground font-medium">Step 3</p>
                        <p className="text-sm font-medium text-foreground">Results</p>
                        <p className="text-xs text-muted-foreground mt-1">⏸ Pending</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Additional Info */}
              <div className="bg-muted/30 rounded-lg p-4 border border-border/50">
                <p className="text-xs text-muted-foreground text-center">
                  This may take a few minutes depending on video length and system performance.
                </p>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  // Results state
  return (
    <div className="min-h-screen bg-gray-800 p-8 rounded-2xl">

      <main >
        <div className="animate-fadeIn">
          <ResultPanel
            results={results}
            videoName={videoName}
            analysisId={analysisId || ''}
            onExport={handleExport}
            hospitalAnalytics={hospitalAnalytics}
          />
        </div>
      </main>
    </div>
  );
}
