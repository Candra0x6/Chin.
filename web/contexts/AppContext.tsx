'use client';

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { AnalysisResults, ChatMessage } from '@/lib/types';

// Context state interface
export interface AnalysisHistoryItem {
  id: string;
  filename: string;
  uploadedAt: string;
  status: 'processing' | 'completed' | 'failed';
  results?: AnalysisResults;
  error?: string;
}

export interface AppState {
  // Upload state
  currentUploadId: string | null;
  uploadProgress: number;
  isUploading: boolean;
  
  // Analysis state
  currentAnalysisId: string | null;
  analysisStatus: 'idle' | 'processing' | 'completed' | 'failed';
  analysisResults: AnalysisResults | null;
  
  // History state
  analysisHistory: AnalysisHistoryItem[];
  
  // Chat state
  chatHistory: Record<string, ChatMessage[]>; // analysisId -> messages
  
  // UI state
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
}

export interface AppContextValue {
  state: AppState;
  
  // Upload actions
  setUploadProgress: (progress: number) => void;
  setCurrentUploadId: (id: string | null) => void;
  setIsUploading: (uploading: boolean) => void;
  
  // Analysis actions
  setCurrentAnalysisId: (id: string | null) => void;
  setAnalysisStatus: (status: AppState['analysisStatus']) => void;
  setAnalysisResults: (results: AnalysisResults | null) => void;
  
  // History actions
  addToHistory: (item: AnalysisHistoryItem) => void;
  updateHistoryItem: (id: string, updates: Partial<AnalysisHistoryItem>) => void;
  removeFromHistory: (id: string) => void;
  clearHistory: () => void;
  getHistoryItem: (id: string) => AnalysisHistoryItem | undefined;
  
  // Chat actions
  addChatMessage: (analysisId: string, message: ChatMessage) => void;
  getChatHistory: (analysisId: string) => ChatMessage[];
  clearChatHistory: (analysisId: string) => void;
  
  // UI actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  
  // Utility actions
  resetState: () => void;
}

// Initial state
const initialState: AppState = {
  currentUploadId: null,
  uploadProgress: 0,
  isUploading: false,
  currentAnalysisId: null,
  analysisStatus: 'idle',
  analysisResults: null,
  analysisHistory: [],
  chatHistory: {},
  sidebarOpen: true,
  theme: 'light',
};

// Create context
const AppContext = createContext<AppContextValue | undefined>(undefined);

// Local storage keys
const STORAGE_KEYS = {
  HISTORY: 'chin_analysis_history',
  CHAT: 'chin_chat_history',
  THEME: 'chin_theme',
  SIDEBAR: 'chin_sidebar_open',
} as const;

// Provider component
export function AppProvider({ children }: { children: ReactNode }) {
  // Initialize state with localStorage data
  const [state, setState] = useState<AppState>(() => {
    // Only access localStorage on client-side
    if (typeof window === 'undefined') {
      return initialState;
    }

    try {
      const savedHistory = localStorage.getItem(STORAGE_KEYS.HISTORY);
      const savedChat = localStorage.getItem(STORAGE_KEYS.CHAT);
      const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME);
      const savedSidebar = localStorage.getItem(STORAGE_KEYS.SIDEBAR);

      return {
        ...initialState,
        analysisHistory: savedHistory ? JSON.parse(savedHistory) : [],
        chatHistory: savedChat ? JSON.parse(savedChat) : {},
        theme: (savedTheme as 'light' | 'dark') || 'light',
        sidebarOpen: savedSidebar ? JSON.parse(savedSidebar) : true,
      };
    } catch (error) {
      console.error('Failed to load state from localStorage:', error);
      return initialState;
    }
  });

  // Save history to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(state.analysisHistory));
    } catch (error) {
      console.error('Failed to save history to localStorage:', error);
    }
  }, [state.analysisHistory]);

  // Save chat history to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.CHAT, JSON.stringify(state.chatHistory));
    } catch (error) {
      console.error('Failed to save chat history to localStorage:', error);
    }
  }, [state.chatHistory]);

  // Save theme to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.THEME, state.theme);
      // Apply theme to document
      if (state.theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch (error) {
      console.error('Failed to save theme to localStorage:', error);
    }
  }, [state.theme]);

  // Save sidebar state to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.SIDEBAR, JSON.stringify(state.sidebarOpen));
    } catch (error) {
      console.error('Failed to save sidebar state to localStorage:', error);
    }
  }, [state.sidebarOpen]);

  // Upload actions
  const setUploadProgress = useCallback((progress: number) => {
    setState((prev) => ({ ...prev, uploadProgress: progress }));
  }, []);

  const setCurrentUploadId = useCallback((id: string | null) => {
    setState((prev) => ({ ...prev, currentUploadId: id }));
  }, []);

  const setIsUploading = useCallback((uploading: boolean) => {
    setState((prev) => ({ ...prev, isUploading: uploading }));
  }, []);

  // Analysis actions
  const setCurrentAnalysisId = useCallback((id: string | null) => {
    setState((prev) => ({ ...prev, currentAnalysisId: id }));
  }, []);

  const setAnalysisStatus = useCallback((status: AppState['analysisStatus']) => {
    setState((prev) => ({ ...prev, analysisStatus: status }));
  }, []);

  const setAnalysisResults = useCallback((results: AnalysisResults | null) => {
    setState((prev) => ({ ...prev, analysisResults: results }));
  }, []);

  // History actions
  const addToHistory = useCallback((item: AnalysisHistoryItem) => {
    setState((prev) => ({
      ...prev,
      analysisHistory: [item, ...prev.analysisHistory].slice(0, 50), // Keep last 50
    }));
  }, []);

  const updateHistoryItem = useCallback((id: string, updates: Partial<AnalysisHistoryItem>) => {
    setState((prev) => ({
      ...prev,
      analysisHistory: prev.analysisHistory.map((item) =>
        item.id === id ? { ...item, ...updates } : item
      ),
    }));
  }, []);

  const removeFromHistory = useCallback((id: string) => {
    setState((prev) => ({
      ...prev,
      analysisHistory: prev.analysisHistory.filter((item) => item.id !== id),
    }));
  }, []);

  const clearHistory = useCallback(() => {
    setState((prev) => ({ ...prev, analysisHistory: [] }));
  }, []);

  const getHistoryItem = useCallback(
    (id: string) => {
      return state.analysisHistory.find((item) => item.id === id);
    },
    [state.analysisHistory]
  );

  // Chat actions
  const addChatMessage = useCallback((analysisId: string, message: ChatMessage) => {
    setState((prev) => ({
      ...prev,
      chatHistory: {
        ...prev.chatHistory,
        [analysisId]: [...(prev.chatHistory[analysisId] || []), message],
      },
    }));
  }, []);

  const getChatHistory = useCallback(
    (analysisId: string) => {
      return state.chatHistory[analysisId] || [];
    },
    [state.chatHistory]
  );

  const clearChatHistory = useCallback((analysisId: string) => {
    setState((prev) => {
      const newChatHistory = { ...prev.chatHistory };
      delete newChatHistory[analysisId];
      return { ...prev, chatHistory: newChatHistory };
    });
  }, []);

  // UI actions
  const toggleSidebar = useCallback(() => {
    setState((prev) => ({ ...prev, sidebarOpen: !prev.sidebarOpen }));
  }, []);

  const setSidebarOpen = useCallback((open: boolean) => {
    setState((prev) => ({ ...prev, sidebarOpen: open }));
  }, []);

  const setTheme = useCallback((theme: 'light' | 'dark') => {
    setState((prev) => ({ ...prev, theme }));
  }, []);

  // Utility actions
  const resetState = useCallback(() => {
    setState(initialState);
    // Clear localStorage
    try {
      localStorage.removeItem(STORAGE_KEYS.HISTORY);
      localStorage.removeItem(STORAGE_KEYS.CHAT);
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
  }, []);

  const value: AppContextValue = {
    state,
    setUploadProgress,
    setCurrentUploadId,
    setIsUploading,
    setCurrentAnalysisId,
    setAnalysisStatus,
    setAnalysisResults,
    addToHistory,
    updateHistoryItem,
    removeFromHistory,
    clearHistory,
    getHistoryItem,
    addChatMessage,
    getChatHistory,
    clearChatHistory,
    toggleSidebar,
    setSidebarOpen,
    setTheme,
    resetState,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// Custom hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
