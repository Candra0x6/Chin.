/**
 * API client for communicating with FastAPI backend
 * Handles all HTTP requests and error handling
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { config } from './config';
import type {
  VideoUploadResponse,
  UploadStatusResponse,
  AnalysisResultResponse,
  AnalysisStatus,
  AnalysisListResponse,
  ChatStartResponse,
  ChatRequest,
  ChatResponse,
  ChatHistoryResponse,
  StatisticsOverview,
  ApiError,
  VideoItem,
  ChatSession,
  HealthCheckDirectories,
} from './types';

/**
 * Create axios instance with base configuration
 */
function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: config.apiUrl,
    timeout: 60000, // 60 seconds timeout
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor for debugging
  client.interceptors.request.use(
    (requestConfig) => {
      if (config.isDebug) {
        console.log('API Request:', {
          method: requestConfig.method,
          url: requestConfig.url,
          data: requestConfig.data,
        });
      }
      return requestConfig;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => {
      if (config.isDebug) {
        console.log('API Response:', {
          status: response.status,
          data: response.data,
        });
      }
      return response;
    },
    (error: AxiosError) => {
      const apiError = handleApiError(error);
      return Promise.reject(apiError);
    }
  );

  return client;
}

/**
 * Handle API errors and convert to ApiError format
 */
function handleApiError(error: AxiosError): ApiError {
  if (error.response) {
    // Server responded with error status
    const data = error.response.data as Record<string, unknown>;
    return {
      status: error.response.status,
      message: (data?.message as string) || (data?.detail as string) || error.message,
      detail: data?.detail as string | undefined,
    };
  } else if (error.request) {
    // Request made but no response received
    return {
      status: 0,
      message: 'No response from server. Please check your connection.',
      detail: error.message,
    };
  } else {
    // Error in request setup
    return {
      status: 0,
      message: 'Request failed',
      detail: error.message,
    };
  }
}

// Create API client instance
const apiClient = createApiClient();

// ============================================================================
// Video Upload API
// ============================================================================

/**
 * Upload progress event type
 */
export interface UploadProgressEvent {
  loaded: number;
  total?: number;
  progress?: number;
}

/**
 * Upload video file for analysis
 */
export async function uploadVideo(
  file: File,
  onUploadProgress?: (progressEvent: UploadProgressEvent) => void
): Promise<VideoUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const requestConfig: AxiosRequestConfig = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
  };

  const response = await apiClient.post<VideoUploadResponse>(
    '/api/upload',
    formData,
    requestConfig
  );

  return response.data;
}

/**
 * Get upload status by video ID
 */
export async function getUploadStatus(videoId: string): Promise<UploadStatusResponse> {
  const response = await apiClient.get<UploadStatusResponse>(
    `/api/upload/status/${videoId}`
  );
  return response.data;
}

/**
 * Delete uploaded video
 */
export async function deleteVideo(videoId: string): Promise<{ message: string; video_id: string }> {
  const response = await apiClient.delete(`/api/upload/${videoId}`);
  return response.data;
}

/**
 * List all uploaded videos
 */
export async function listUploads(
  limit = 10,
  offset = 0,
  statusFilter?: string
): Promise<{ videos: VideoItem[]; count: number; limit: number; offset: number }> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());
  if (statusFilter) {
    params.append('status_filter', statusFilter);
  }

  const response = await apiClient.get(`/api/upload/list?${params.toString()}`);
  return response.data;
}

// ============================================================================
// Analysis API
// ============================================================================

/**
 * Start video analysis
 */
export async function analyzeVideo(
  videoId: string,
  config?: {
    show_visual?: boolean;
    save_annotated_video?: boolean;
    frame_sample_rate?: number;
    confidence_threshold?: number;
    enable_ai_insights?: boolean;
    gemini_api_key?: string;
  }
): Promise<{ analysis_id: string; message: string; status: string }> {
  const response = await apiClient.post(
    `/api/analyze/${videoId}`,
    {
      upload_id: videoId,
      show_visual: config?.show_visual ?? false,
      save_annotated_video: config?.save_annotated_video ?? false,
      frame_sample_rate: config?.frame_sample_rate ?? 30,
      confidence_threshold: config?.confidence_threshold ?? 0.5,
      enable_ai_insights: config?.enable_ai_insights ?? true,
      gemini_api_key: config?.gemini_api_key ?? '',
    }
  );
  return response.data;
}

// ============================================================================
// Analysis Results API
// ============================================================================

/**
 * Get analysis result by ID
 */
export async function getAnalysisResult(analysisId: string): Promise<AnalysisResultResponse> {
  const response = await apiClient.get<AnalysisResultResponse>(
    `/api/results/${analysisId}`
  );
  return response.data;
}

/**
 * Get analysis status (for polling during processing)
 */
export async function getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
  const response = await apiClient.get<AnalysisStatus>(
    `/api/analyze/status/${analysisId}`
  );
  return response.data;
}

/**
 * List analysis results with pagination and filtering
 */
export async function listAnalysisResults(params?: {
  page?: number;
  limit?: number;
  video_name?: string;
  crowd_level?: string;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_order?: string;
}): Promise<AnalysisListResponse> {
  const queryParams = new URLSearchParams();
  
  if (params?.page) queryParams.append('page', params.page.toString());
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.video_name) queryParams.append('video_name', params.video_name);
  if (params?.crowd_level) queryParams.append('crowd_level', params.crowd_level);
  if (params?.date_from) queryParams.append('date_from', params.date_from);
  if (params?.date_to) queryParams.append('date_to', params.date_to);
  if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
  if (params?.sort_order) queryParams.append('sort_order', params.sort_order);

  const response = await apiClient.get<AnalysisListResponse>(
    `/api/results?${queryParams.toString()}`
  );
  return response.data;
}

/**
 * Delete analysis result
 */
export async function deleteAnalysis(analysisId: string): Promise<{ message: string; analysis_id: string }> {
  const response = await apiClient.delete(`/api/results/${analysisId}`);
  return response.data;
}

/**
 * Get statistics overview
 */
export async function getStatisticsOverview(): Promise<StatisticsOverview> {
  const response = await apiClient.get<StatisticsOverview>('/api/results/stats/overview');
  return response.data;
}

/**
 * Export analysis as JSON
 */
export async function exportAnalysisJson(analysisId: string): Promise<Blob> {
  const response = await apiClient.get(`/api/results/${analysisId}/export/json`, {
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Export analysis summary as text
 */
export async function exportAnalysisSummary(analysisId: string): Promise<Blob> {
  const response = await apiClient.get(`/api/results/${analysisId}/export/summary`, {
    responseType: 'blob',
  });
  return response.data;
}

// ============================================================================
// Chat API
// ============================================================================

/**
 * Start a new chat conversation about an analysis
 */
export async function startChat(analysisId: string): Promise<ChatStartResponse> {
  const response = await apiClient.post<ChatStartResponse>(
    `/api/chat/start/${analysisId}`
  );
  return response.data;
}

/**
 * Send a message in the chat conversation
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/api/chat/message', request);
  return response.data;
}

/**
 * Get conversation history/summary
 */
export async function getChatHistory(analysisId: string): Promise<ChatHistoryResponse> {
  const response = await apiClient.get<ChatHistoryResponse>(
    `/api/chat/history/${analysisId}`
  );
  return response.data;
}

/**
 * Clear conversation history
 */
export async function clearChat(analysisId: string): Promise<{ analysis_id: string; status: string; message: string }> {
  const response = await apiClient.delete(`/api/chat/clear/${analysisId}`);
  return response.data;
}

/**
 * List active chat sessions
 */
export async function listActiveSessions(): Promise<{ total_sessions: number; sessions: ChatSession[] }> {
  const response = await apiClient.get('/api/chat/sessions');
  return response.data;
}

// ============================================================================
// Health Check API
// ============================================================================

/**
 * Check API health status
 */
export async function checkHealth(): Promise<{ status: string; directories: HealthCheckDirectories }> {
  const response = await apiClient.get('/health');
  return response.data;
}

/**
 * Get API root info
 */
export async function getApiInfo(): Promise<{ message: string; status: string; version: string; docs: string }> {
  const response = await apiClient.get('/');
  return response.data;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Check if API is reachable
 */
export async function isApiReachable(): Promise<boolean> {
  try {
    await checkHealth();
    return true;
  } catch {
    return false;
  }
}

/**
 * Download file from blob
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

// Export API client for custom requests if needed
export { apiClient };
