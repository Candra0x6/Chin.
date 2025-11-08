"""
Database schema definitions for Supabase tables.
These schemas should be created in Supabase dashboard or via SQL.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class VideoUploadDB(BaseModel):
    """Database schema for video_uploads table."""
    
    id: str = Field(..., description="Unique identifier (UUID)")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Storage path")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    status: str = Field(default="pending", description="Upload status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisResultDB(BaseModel):
    """Database schema for analysis_results table."""
    
    id: str = Field(..., description="Unique identifier (UUID)")
    video_id: str = Field(..., description="Reference to video_uploads.id")
    video_name: str = Field(..., description="Video filename")
    duration_seconds: float = Field(..., description="Video duration")
    frames_processed: int = Field(..., description="Number of frames analyzed")
    
    # Crowd analytics (stored as JSONB)
    total_people: int
    avg_density: str
    max_congestion_time: Optional[str] = None
    peak_count: int
    avg_count: float
    
    # Bottleneck info (stored as JSONB)
    bottleneck_area: str
    bottleneck_severity: str
    bottleneck_duration: Optional[str] = None
    bottleneck_action: str
    
    # Staff recommendations (stored as JSONB)
    suggested_nurses: int
    suggested_doctors: int = 0
    recommendation_reasoning: str
    
    # AI summary
    ai_summary: str = Field(..., description="AI-generated insights")
    
    # Metadata
    processing_time_seconds: float
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessageDB(BaseModel):
    """Database schema for chat_history table."""
    
    id: str = Field(..., description="Unique identifier (UUID)")
    analysis_id: str = Field(..., description="Reference to analysis_results.id")
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# SQL Schema for Supabase (to be executed in Supabase SQL Editor)
SUPABASE_SCHEMA = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Video Uploads Table
CREATE TABLE IF NOT EXISTS video_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analysis Results Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES video_uploads(id) ON DELETE CASCADE,
    video_name TEXT NOT NULL,
    duration_seconds REAL NOT NULL,
    frames_processed INTEGER NOT NULL,
    
    -- Crowd analytics
    total_people INTEGER NOT NULL,
    avg_density TEXT NOT NULL,
    max_congestion_time TEXT,
    peak_count INTEGER NOT NULL,
    avg_count REAL NOT NULL,
    
    -- Bottleneck info
    bottleneck_area TEXT NOT NULL,
    bottleneck_severity TEXT NOT NULL,
    bottleneck_duration TEXT,
    bottleneck_action TEXT NOT NULL,
    
    -- Staff recommendations
    suggested_nurses INTEGER NOT NULL,
    suggested_doctors INTEGER DEFAULT 0,
    recommendation_reasoning TEXT NOT NULL,
    
    -- AI summary
    ai_summary TEXT NOT NULL,
    
    -- Metadata
    processing_time_seconds REAL NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat History Table
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_video_uploads_status ON video_uploads(status);
CREATE INDEX IF NOT EXISTS idx_video_uploads_created_at ON video_uploads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_video_id ON analysis_results(video_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_history_analysis_id ON chat_history(analysis_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at DESC);

-- Row Level Security (RLS) - Optional, configure based on your needs
ALTER TABLE video_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your security requirements)
CREATE POLICY "Enable read access for all users" ON video_uploads
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON video_uploads
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON analysis_results
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON analysis_results
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON chat_history
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON chat_history
    FOR INSERT WITH CHECK (true);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_video_uploads_updated_at
    BEFORE UPDATE ON video_uploads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""
