'use client';

import ChatAssistant from '@/components/ChatAssistant';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function ChatPage() {
  const router = useRouter();
  const params = useParams();
  const analysisId = params.id as string;

  return (
    <div className="min-h-screen bg-linear-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b bg-card/80 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">
                💬 AI Chat Assistant
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Ask questions about your analysis results
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button
                onClick={() => router.push(`/analysis/${analysisId}`)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                📊 View Results
              </Button>
              <Button
                onClick={() => router.push('/')}
                variant="ghost"
              >
                ← Back to Home
              </Button>
            </div>
          </div>
        </div>
      </header>

     
    </div>
  );
}
