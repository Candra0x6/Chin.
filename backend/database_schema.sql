-- HospiTwin Lite Database Schema
-- Run this in your Supabase SQL Editor to create the required tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Video Uploads Table
CREATE TABLE IF NOT EXISTS video_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'uploaded',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analysis Results Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES video_uploads(id) ON DELETE CASCADE,
    video_name VARCHAR(255) NOT NULL,
    duration_seconds FLOAT NOT NULL,
    frames_processed INTEGER NOT NULL,
    
    -- Results stored as JSONB for flexibility
    results JSONB NOT NULL,
    
    -- Status and error tracking
    status VARCHAR(50) DEFAULT 'completed',
    error_message TEXT,
    error_details TEXT,
    
    -- Extracted fields for easier querying
    crowd_level VARCHAR(50),
    peak_count INTEGER,
    avg_count FLOAT,
    suggested_nurses INTEGER,
    
    -- AI insights
    ai_summary TEXT,
    
    -- Metadata
    processing_time_seconds FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat History Table
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_video_uploads_created_at ON video_uploads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_video_uploads_status ON video_uploads(status);

CREATE INDEX IF NOT EXISTS idx_analysis_results_video_id ON analysis_results(video_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_crowd_level ON analysis_results(crowd_level);
CREATE INDEX IF NOT EXISTS idx_analysis_results_peak_count ON analysis_results(peak_count);

CREATE INDEX IF NOT EXISTS idx_chat_history_analysis_id ON chat_history(analysis_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_video_uploads_updated_at BEFORE UPDATE ON video_uploads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_results_updated_at BEFORE UPDATE ON analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for complete analysis data
CREATE OR REPLACE VIEW analysis_complete AS
SELECT 
    ar.id as analysis_id,
    ar.video_name,
    ar.duration_seconds,
    ar.frames_processed,
    ar.results,
    ar.crowd_level,
    ar.peak_count,
    ar.avg_count,
    ar.suggested_nurses,
    ar.ai_summary,
    ar.processing_time_seconds,
    ar.created_at,
    vu.filename as original_filename,
    vu.file_path,
    vu.file_size,
    vu.status as video_status
FROM analysis_results ar
LEFT JOIN video_uploads vu ON ar.video_id = vu.id;

-- Grant permissions (adjust as needed)
GRANT ALL ON video_uploads TO postgres;
GRANT ALL ON analysis_results TO postgres;
GRANT ALL ON chat_history TO postgres;
GRANT SELECT ON analysis_complete TO postgres;

-- Success message
SELECT 'Database schema created successfully!' as message;
