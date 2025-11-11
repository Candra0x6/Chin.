/**
 * Type definitions for API requests and responses
 * Based on FastAPI backend models
 */

// ============================================================================
// Video Upload Types
// ============================================================================

export interface VideoUploadResponse {
  id: string;
  filename: string;
  path: string;
  status: string;
  message: string;
  created_at: string;
}

export interface UploadStatusResponse {
  id: string;
  filename: string;
  status: string;
  file_size: number;
  uploaded_at: string;
  message: string;
}

// ============================================================================
// Analysis Result Types
// ============================================================================

export interface Bottleneck {
  start_time: string;
  end_time: string;
  severity: 'low' | 'medium' | 'high';
  avg_count: number;
  description?: string;
}

export interface SpatialDistribution {
  zone: string;
  count: number;
  percentage: number;
}

export interface FlowMetrics {
  avg_wait_time?: number;
  throughput?: number;
  congestion_index?: number;
  trend?: string;
  flow_rate?: number;
  variability?: string;
  average_count?: number;
  std_deviation?: number;
  coefficient_of_variation?: number;
}

export interface TimelineDataPoint {
  time: string;
  timestamp: number;
  average: number;
  max: number;
  min: number;
  samples: number;
}

export interface VisualizationData {
  chart_data: TimelineDataPoint[];
  total_intervals: number;
  interval_seconds: number;
  summary: {
    overall_average: number;
    overall_max: number;
    overall_min: number;
    std_deviation: number;
    total_samples: number;
  };
}

export interface BottleneckPeriod {
  start_time: string;
  end_time: string;
  severity: string;
  duration_seconds: number;
  peak_person_count: number;
  average_person_count: number;
  severity_score?: number;
  frame_count?: number;
}

export interface BottleneckAnalysis {
  bottlenecks_detected: number;
  bottleneck_periods: BottleneckPeriod[];
  total_bottleneck_duration_seconds: number;
  average_person_count: number;
  max_person_count: number;
  threshold_used: number;
}

export interface ZoneData {
  zone_id: string;
  row: number;
  col: number;
  position: string;
  detection_count: number;
  percentage: number;
  density_level: string;
}

export interface SpatialDistribution {
  zones: ZoneData[];
  hotspots: ZoneData[];
  grid_size: {
    rows: number;
    cols: number;
  };
  distribution_pattern: string;
  total_detections_analyzed: number;
}

export interface EnhancedAnalytics {
  visualization_data?: VisualizationData;
  bottleneck_analysis?: BottleneckAnalysis;
  spatial_distribution?: SpatialDistribution;
  flow_metrics?: FlowMetrics;
  crowd_density?: {
    density_per_sqm: number;
    density_level: string;
    severity_score: number;
    person_count: number;
    area_sqm: number;
  };
  generated_at?: string;
}

export interface AIInsights {
  summary: string;
  recommendations?: string[];
  key_findings?: string[];
}

export interface AnalysisResults {
  // Crowd statistics
  avg_count: number;
  peak_count: number;
  total_people: number;
  crowd_level: 'Low' | 'Medium' | 'High' | 'Very High';
  peak_congestion_time?: string;
  
  // Staffing recommendations
  suggested_nurses: number;
  reasoning?: string;
  
  // Bottleneck analysis
  bottlenecks: Bottleneck[];
  
  // Spatial distribution (legacy format)
  spatial_distribution?: SpatialDistribution[];
  
  // Flow analysis
  flow_metrics?: FlowMetrics;
  
  // AI insights
  ai_insights?: AIInsights;
  
  // Enhanced analytics (new format from backend)
  enhanced_analytics?: EnhancedAnalytics;
  
  // Additional metadata
  video_duration?: number;
  frames_analyzed?: number;
  detection_confidence?: number;
}

export interface AnalysisResultResponse {
  analysis_id: string;
  video_id: string;
  video_name: string;
  created_at: string;
  status: string;
  results: AnalysisResults;
}

export interface AnalysisStatus {
  analysis_id: string;
  video_id: string;
  video_name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface AnalysisListItem {
  analysis_id: string;
  video_id: string;
  video_name: string;
  created_at: string;
  crowd_level: string | null;
  peak_count: number | null;
  suggested_nurses: number | null;
  status: string;
}

export interface AnalysisListResponse {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  results: AnalysisListItem[];
}

// ============================================================================
// Chat Types
// ============================================================================

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatStartResponse {
  session_id: string;
  analysis_id: string;
  message: string;
  mode: 'gemini-ai' | 'rule-based';
  instructions: string;
}

export interface ChatRequest {
  analysis_id: string;
  message: string;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  timestamp: string;
}

export interface ChatHistoryResponse {
  analysis_id: string;
  session_id?: string;
  status: 'active' | 'inactive' | 'no_conversation';
  mode?: string;
  message: string;
}

// ============================================================================
// Statistics Types
// ============================================================================

export interface StatisticsOverview {
  total_analyses: number;
  analyses_by_crowd_level: Record<string, number>;
  avg_peak_count: number;
  total_bottlenecks: number;
  analyses_with_ai_insights: number;
  avg_bottlenecks_per_analysis: number;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ErrorResponse {
  error: string;
  message: string;
  detail?: string;
}

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
}

// ============================================================================
// Common Types
// ============================================================================

export type UploadStatus = 'uploading' | 'uploaded' | 'processing' | 'completed' | 'failed';
export type CrowdLevel = 'Low' | 'Medium' | 'High' | 'Very High';
export type BottleneckSeverity = 'low' | 'medium' | 'high';

// ============================================================================
// Additional API Response Types
// ============================================================================

export interface VideoItem {
  id: string;
  filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ChatSession {
  session_id: string;
  mode: string;
  active: boolean;
}

export interface HealthCheckDirectories {
  uploads: string;
  results: string;
  models: string;
}

