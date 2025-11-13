/**
 * ChatAssistant Component
 * AI chat interface for discussing analysis results with Gemini
 */

'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { startChat, sendChatMessage } from '@/lib/api';
import { validateChatMessage } from '@/lib/validators';
import { InlineLoader } from './Loader';
import type { ChatMessage, ChatStartResponse } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';

export interface ChatAssistantProps {
  /** Analysis ID to discuss */
  analysisId: string;
  /** Initial messages */
  initialMessages?: ChatMessage[];
  /** Custom class name */
  className?: string;
}

/**
 * Message bubble component
 */
function MessageBubble({ message }: { message: ChatMessage }): React.ReactElement {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-start gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div
          className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center shrink-0',
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-purple-600 text-white'
          )}
        >
          {isUser ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          )}
        </div>

        {/* Message content */}
        <Card
          className={cn(
            'py-0',
            isUser
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-muted'
          )}
        >
          <CardContent className="px-4 py-3">
            <p className="text-sm whitespace-pre-wrap leading-relaxed">
              {message.content}
            </p>
            {message.timestamp && (
              <p
                className={cn(
                  'text-xs mt-2',
                  isUser
                    ? 'text-blue-100'
                    : 'text-muted-foreground'
                )}
              >
                {new Date(message.timestamp).toLocaleTimeString()}
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

/**
 * ChatAssistant component
 */
export function ChatAssistant({
  analysisId,
  initialMessages = [],
  className = '',
}: ChatAssistantProps): React.ReactElement {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isChatStarted, setIsChatStarted] = useState(false);
  const [sessionInfo, setSessionInfo] = useState<ChatStartResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Scroll to bottom of messages
   */
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  /**
   * Start chat session
   */
  const initializeChat = useCallback(async () => {
    if (isChatStarted) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await startChat(analysisId);
      setSessionInfo(response);
      setIsChatStarted(true);

      // Add welcome message
      const welcomeMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
      };
      setMessages([welcomeMessage]);
    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Failed to start chat');
    } finally {
      setIsLoading(false);
    }
  }, [analysisId, isChatStarted]);

  /**
   * Send message
   */
  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim()) return;

    // Validate message
    const validation = validateChatMessage(inputValue);
    if (!validation.isValid) {
      setError(validation.error || 'Invalid message');
      return;
    }

    // Add user message
    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setError(null);

    // Send to API
    setIsLoading(true);
    try {
      const response = await sendChatMessage({
        analysis_id: analysisId,
        message: inputValue,
        conversation_history: messages,
      });

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Failed to send message');

      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, analysisId, messages]);

  /**
   * Handle Enter key press
   */
  const handleKeyPress = useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();
      }
    },
    [handleSendMessage]
  );

  /**
   * Initialize chat on mount
   */
  useEffect(() => {
    if (!isChatStarted && analysisId) {
      initializeChat();
    }
  }, [analysisId, isChatStarted, initializeChat]);

  /**
   * Focus input when chat starts
   */
  useEffect(() => {
    if (isChatStarted && !isLoading) {
      inputRef.current?.focus();
    }
  }, [isChatStarted, isLoading]);

  return (
    <div className={`w-full max-w-4xl mx-auto h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="mb-4 pb-4 border-b">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-600 rounded-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold">
              AI Assistant
            </h3>
            <p className="text-sm text-muted-foreground">
              {sessionInfo ? `Mode: ${sessionInfo.mode}` : 'Initializing...'}
            </p>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto mb-4 pr-2 space-y-2">
        {messages.length === 0 && !isLoading && (
          <div className="text-center py-12 text-muted-foreground">
            <svg
              className="w-16 h-16 mx-auto mb-4 opacity-50"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-sm">Starting conversation...</p>
          </div>
        )}

        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex items-center gap-3 max-w-[80%]">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-purple-600 text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <Card className="py-0 bg-muted">
                <CardContent className="px-4 py-3">
                  <InlineLoader message="Thinking..." />
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription className="text-sm">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Input Area */}
      <div className="border-t pt-4">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about the analysis..."
            disabled={isLoading || !isChatStarted}
            rows={3}
            className="flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-background text-foreground placeholder-muted-foreground disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading || !isChatStarted}
            className="self-end bg-blue-600 hover:bg-blue-700"
            size="icon-lg"
          >
            {isLoading ? (
              <InlineLoader />
            ) : (
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}

export default ChatAssistant;
