/**
 * Loader Component
 * Displays loading spinner and status messages during processing
 */

import React from 'react';

export interface LoaderProps {
  /** Loading message to display */
  message?: string;
  /** Size of the spinner */
  size?: 'small' | 'medium' | 'large';
  /** Show as fullscreen overlay */
  fullscreen?: boolean;
}

/**
 * Get spinner size classes based on size prop
 */
function getSpinnerSize(size: LoaderProps['size']): string {
  switch (size) {
    case 'small':
      return 'w-8 h-8 border-2';
    case 'large':
      return 'w-16 h-16 border-4';
    case 'medium':
    default:
      return 'w-12 h-12 border-3';
  }
}

/**
 * Loader component for displaying loading states
 */
export function Loader({
  message = 'Loading...',
  size = 'medium',
  fullscreen = false,
}: LoaderProps): React.ReactElement {
  const spinnerSizeClass = getSpinnerSize(size);

  const spinner = (
    <div className="flex flex-col items-center justify-center gap-4">
      <div
        className={`${spinnerSizeClass} border-blue-600 border-t-transparent rounded-full animate-spin`}
        role="status"
        aria-label="Loading"
      />
      {message && (
        <p className="text-gray-700 dark:text-gray-300 text-center font-medium">
          {message}
        </p>
      )}
    </div>
  );

  if (fullscreen) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-8 shadow-xl">
          {spinner}
        </div>
      </div>
    );
  }

  return <div className="flex items-center justify-center p-8">{spinner}</div>;
}

/**
 * Inline loader for smaller loading states
 */
export function InlineLoader({ message }: { message?: string }): React.ReactElement {
  return (
    <div className="flex items-center gap-2">
      <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      {message && <span className="text-sm text-gray-600">{message}</span>}
    </div>
  );
}

/**
 * Progress loader with percentage
 */
export interface ProgressLoaderProps {
  /** Progress percentage (0-100) */
  progress: number;
  /** Message to display */
  message?: string;
}

export function ProgressLoader({
  progress,
  message = 'Processing...',
}: ProgressLoaderProps): React.ReactElement {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  return (
    <div className="w-full max-w-md">
      <div className="mb-2 flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {message}
        </span>
        <span className="text-sm font-semibold text-blue-600">
          {clampedProgress.toFixed(0)}%
        </span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${clampedProgress}%` }}
          role="progressbar"
          aria-valuenow={clampedProgress}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}

export default Loader;
