'use client';

import { useRouter, useParams } from 'next/navigation';
import { ChatAssistant } from '@/components';

export default function ChatPage() {
  const router = useRouter();
  const params = useParams();
  const analysisId = params.id as string;

  return (
    <div className="min-h-screen bg-linear-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                💬 AI Chat Assistant
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Ask questions about your analysis results
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => router.push(`/analysis/${analysisId}`)}
                className="rounded-lg px-4 py-2 text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              >
                📊 View Results
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
      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <ChatAssistant analysisId={analysisId} />
        </div>

        {/* Tips Section */}
        <div className="mt-6 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-200 mb-3">
            💡 Tips for Better Conversations
          </h3>
          <ul className="space-y-2 text-sm text-purple-800 dark:text-purple-300">
            <li className="flex items-start gap-2">
              <span className="text-purple-600 dark:text-purple-400">•</span>
              <span>Ask specific questions about the analysis results</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-purple-600 dark:text-purple-400">•</span>
              <span>Try &ldquo;What if&rdquo; scenarios (e.g., &ldquo;What if we add 2 more nurses?&rdquo;)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-purple-600 dark:text-purple-400">•</span>
              <span>Ask for clarification on bottlenecks and recommendations</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-purple-600 dark:text-purple-400">•</span>
              <span>Request insights on peak hours and crowd patterns</span>
            </li>
          </ul>
        </div>

        {/* Example Questions */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Example Questions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                &ldquo;When was the crowd highest?&rdquo;
              </p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                &ldquo;Why do you recommend 3 nurses?&rdquo;
              </p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                &ldquo;What areas had the most congestion?&rdquo;
              </p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                &ldquo;How can we reduce wait times?&rdquo;
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
