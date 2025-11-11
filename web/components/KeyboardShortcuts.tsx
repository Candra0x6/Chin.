'use client';

import React, { useEffect } from 'react';

export interface KeyboardShortcutsProps {
  onUpload?: () => void;
  onHistory?: () => void;
  onHelp?: () => void;
}

export function KeyboardShortcuts({ onUpload, onHistory, onHelp }: KeyboardShortcutsProps) {
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Ignore if user is typing in an input/textarea
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      // Cmd/Ctrl + U: Upload
      if ((event.metaKey || event.ctrlKey) && event.key === 'u') {
        event.preventDefault();
        onUpload?.();
      }

      // Cmd/Ctrl + H: History
      if ((event.metaKey || event.ctrlKey) && event.key === 'h') {
        event.preventDefault();
        onHistory?.();
      }

      // Cmd/Ctrl + /: Help
      if ((event.metaKey || event.ctrlKey) && event.key === '/') {
        event.preventDefault();
        onHelp?.();
      }

      // ? key: Show keyboard shortcuts
      if (event.key === '?' && !event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        onHelp?.();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [onUpload, onHistory, onHelp]);

  return null; // This component doesn't render anything
}

export function KeyboardShortcutsModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      window.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      window.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const shortcuts = [
    { keys: ['Ctrl', 'U'], mac: ['⌘', 'U'], description: 'Open upload dialog' },
    { keys: ['Ctrl', 'H'], mac: ['⌘', 'H'], description: 'View history' },
    { keys: ['Ctrl', '/'], mac: ['⌘', '/'], description: 'Show keyboard shortcuts' },
    { keys: ['?'], mac: ['?'], description: 'Show keyboard shortcuts' },
    { keys: ['Esc'], mac: ['Esc'], description: 'Close dialogs' },
  ];

  const isMac = typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;

  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6 animate-fadeIn"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
              />
            </svg>
            Keyboard Shortcuts
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            aria-label="Close"
          >
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="space-y-3">
          {shortcuts.map((shortcut, index) => {
            const keys = isMac ? shortcut.mac : shortcut.keys;
            return (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300">{shortcut.description}</span>
                <div className="flex items-center gap-1">
                  {keys.map((key, i) => (
                    <React.Fragment key={i}>
                      {i > 0 && <span className="text-gray-400 mx-1">+</span>}
                      <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 dark:text-gray-200 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded shadow-sm">
                        {key}
                      </kbd>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Press <kbd className="px-1 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 rounded">Esc</kbd> to close
          </p>
        </div>
      </div>
    </div>
  );
}
