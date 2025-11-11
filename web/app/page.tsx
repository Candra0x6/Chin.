'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { UploadBox, Loader, ThemeToggle, KeyboardShortcuts, KeyboardShortcutsModal, HospitalContextForm } from '@/components';
import { useToast } from '@/contexts';
import { useApp } from '@/contexts';
import { analyzeVideo } from '@/lib/api';
import type { VideoUploadResponse } from '@/lib/types';
import type { HospitalContext } from '@/components';

export default function Home() {
  const router = useRouter();
  const { addToHistory, setCurrentUploadId } = useApp();
  const toast = useToast();
  const [isProcessing, setIsProcessing] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [uploadedResult, setUploadedResult] = useState<VideoUploadResponse | null>(null);
  const [showHospitalForm, setShowHospitalForm] = useState(false);
  const uploadBoxRef = useRef<HTMLDivElement>(null);

  const logDebug = (message: string, data?: Record<string, unknown> | string | number | HospitalContext): void => {
    const timestamp = new Date().toISOString();
    console.log(`[HomePage] ${timestamp} - ${message}`, data || '');
  };

  const handleUploadSuccess = async (result: VideoUploadResponse) => {
    logDebug('Upload successful', { videoId: result.id, filename: result.filename });
    setUploadedResult(result);
    setCurrentUploadId(result.id);
    setShowHospitalForm(true);
    toast.info('Video uploaded! Please provide hospital context for enhanced analysis.');
  };

  const handleUploadError = (error: Error) => {
    logDebug('Upload failed', { errorMessage: error.message });
    toast.error(`Upload failed: ${error.message}`);
  };

  const handleHospitalContextSubmit = async (context: HospitalContext) => {
    if (!uploadedResult) {
      logDebug('Hospital context submitted but no uploaded result found');
      return;
    }

    logDebug('Hospital context form submitted', {
      location: context.location_name,
      nurses: context.staffing.available_nurses,
      beds: context.resources.available_beds,
    });

    setIsProcessing(true);
    setShowHospitalForm(false);

    try {
      logDebug('Starting analysis with hospital context', { videoId: uploadedResult.id });

      const analysisResult = await analyzeVideo(uploadedResult.id, {
        show_visual: false,
        save_annotated_video: false,
        frame_sample_rate: 30,
        confidence_threshold: 0.5,
        enable_ai_insights: true,
        hospital_context: context as unknown as Record<string, unknown>,
      });

      logDebug('Analysis started successfully', { analysisId: analysisResult.analysis_id });

      addToHistory({
        id: analysisResult.analysis_id,
        filename: uploadedResult.filename || 'Unknown',
        uploadedAt: new Date().toISOString(),
        status: 'processing',
      });

      toast.success('Analysis started with hospital context!');
      setTimeout(() => {
        logDebug('Navigating to analysis page', { analysisId: analysisResult.analysis_id });
        router.push(`/analysis/${analysisResult.analysis_id}`);
      }, 500);
    } catch (error) {
      logDebug('Failed to start analysis', { error: error instanceof Error ? error.message : 'Unknown error' });
      toast.error(`Failed to start analysis: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setIsProcessing(false);
      setShowHospitalForm(true);
    }
  };

  const handleHospitalContextCancel = () => {
    logDebug('Hospital context form cancelled');
    setShowHospitalForm(false);
    setUploadedResult(null);
    toast.info('Ready to upload another video');
  };

  const scrollToUpload = () => {
    uploadBoxRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  if (isProcessing) {
    return (
      <Loader 
        message="Redirecting to analysis..." 
        fullscreen 
      />
    );
  }

  if (showHospitalForm && uploadedResult) {
    return (
      <>
        <KeyboardShortcuts
          onUpload={scrollToUpload}
          onHistory={() => router.push('/history')}
          onHelp={() => setShowShortcuts(true)}
        />
        
        <KeyboardShortcutsModal
          isOpen={showShortcuts}
          onClose={() => setShowShortcuts(false)}
        />

        <div className="min-h-screen bg-linear-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
          <header className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm sticky top-0 z-10 transition-colors duration-300">
            <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                    🏥 Chin ER Flow Analyzer
                  </h1>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Hospital Context Setup
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <ThemeToggle />
                </div>
              </div>
            </div>
          </header>

          <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
            <HospitalContextForm
              onSubmit={handleHospitalContextSubmit}
              onCancel={handleHospitalContextCancel}
              isLoading={isProcessing}
            />
          </main>
        </div>
      </>
    );
  }

  return (
    <>
      <KeyboardShortcuts
        onUpload={scrollToUpload}
        onHistory={() => router.push('/history')}
        onHelp={() => setShowShortcuts(true)}
      />
      
      <KeyboardShortcutsModal
        isOpen={showShortcuts}
        onClose={() => setShowShortcuts(false)}
      />
      
      <div className="min-h-screen bg-linear-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm sticky top-0 z-10 transition-colors duration-300">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                🏥 Chin ER Flow Analyzer
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                AI-powered emergency room queue analysis
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowShortcuts(true)}
                className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
                title="Keyboard shortcuts (Ctrl+/)"
              >
                ⌨️ Shortcuts
              </button>
              <a
                href="/history"
                className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
              >
                📋 History
              </a>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="mb-12 text-center">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Upload Your ER Queue Video
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Our AI-powered system analyzes emergency room queue videos to detect crowd patterns,
            identify bottlenecks, and provide staffing recommendations.
          </p>
        </div>

        {/* Upload Section */}
        <div className="mb-12" ref={uploadBoxRef}>
          <UploadBox
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="group p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md hover:scale-105 transition-all duration-300">
            <div className="text-3xl mb-3 group-hover:animate-bounce-slow">👥</div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Crowd Detection
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Real-time detection and counting of people in your ER queue using advanced YOLOv8 AI.
            </p>
          </div>

          <div className="group p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md hover:scale-105 transition-all duration-300">
            <div className="text-3xl mb-3 group-hover:animate-bounce-slow">📊</div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Bottleneck Analysis
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Identify congestion points and peak hours to optimize patient flow and reduce wait times.
            </p>
          </div>

          <div className="group p-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md hover:scale-105 transition-all duration-300">
            <div className="text-3xl mb-3 group-hover:animate-bounce-slow">🤖</div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              AI Assistant
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Chat with Gemini AI to get insights and recommendations based on your analysis results.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            How It Works
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-blue-600 dark:text-blue-400">1</span>
              </div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Upload Video</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Upload your ER queue video (MP4, AVI, MOV, or MKV)
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-purple-600 dark:text-purple-400">2</span>
              </div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">AI Analysis</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Our system processes the video and detects crowd patterns
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-green-600 dark:text-green-400">3</span>
              </div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">View Results</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Get detailed metrics, bottlenecks, and recommendations
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-pink-100 dark:bg-pink-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-pink-600 dark:text-pink-400">4</span>
              </div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Chat with AI</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Ask questions and get insights from our AI assistant
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm mt-12 transition-colors duration-300">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            © 2025 Chin ER Flow Analyzer. Powered by YOLOv8 & Gemini AI.
          </p>
        </div>
      </footer>
    </div>
    </>
  );
}
